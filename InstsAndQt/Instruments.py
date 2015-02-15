# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 16:38:33 2015

@author: dvalovcin
"""

import numpy as np
import visa
import time

class FakeInstr(object):
    timeout = 3000
    curStep = 70000 #Making life interesting for SPEX instrument
    def write(self, string):
        print ' '*15 + string
        if 'F0' in string: #SPEX Relative move
            self.curStep += int(string[3:])
        if ':DIG' in string: #Agilent telling it to start data collection
            time.sleep(0.75)
    def ask(self, string):
        print ' '*12 + string
        #Test for some basic instrument questions and output the expected output
        if 'SLVL' in string or 'OUTP' in string:
            return str(np.random.random())
        elif 'SNAP?' in string:
            return str(np.random.random())+','+str(np.random.random())
        elif 'H0' in string: #SPEX Relative move
            return str(self.curStep) + '\r'
        elif string == 'E': #SPEX, is it moving
            return 'oz'
        elif ':WAV:PRE?' == string:#agilent oscilloscope, waveform preamble
            a = np.random.random((10,))
            a[4] = 3 #Forcing some numbers for reasonable consistancy
            a[5] = 0
            a[6] = 0
            st = ''
            for i in a:
                st+=str(i)+','
            return st
        elif ':WAV:DATA?' == string: #agilent querying data
            return np.random.random((1000,))
        elif '*OPC?'==string:
            time.sleep(0.5)
            return u'1\r'
            
            
            
            
        b = [str(i) for i in np.random.random((5,))]
        st = ''
        for i in b:
            st = st+i+','
            
        return b
        
        
    def query_binary_values(self, string, datatype):
        if ':WAV:DATA?' == string: #agilent querying data
            return np.random.random((1000,))
        
    def close(self):
        print 'closed'


class BaseInstr(object):
    '''Base class which handles opening the GPIB and safely reading/writing to the instrument'''
    def __init__(self, GPIB_Number = None, timeout = 3000):
        if GPIB_Number == None or GPIB_Number == 'Fake':
            print 'Error. No GPIB assigned'
            self.instrument = FakeInstr()
        else:
            rm = visa.ResourceManager()
            try:
                self.instrument = rm.get_instrument(GPIB_Number)
                self.instrument.timeout = timeout
            except:
                print 'Error opening GPIB'
        #Ensure the instrument writes out to the GPIB
        
    def write(self, command, strip=True):
        '''A safer function to catch errors in writing commands. Also ensures
        proper ending to command. '''
        try:
            self.instrument.write(command)
        except:
            print 'Error writting command,', str(command)
            return False
        return True
    
    def ask(self, command, strip=1, timeout = 3000):
        '''A function to catch reading errors. 
        strip = 1 will strip tailing \n and encode from unicode
        strip = 0 will simply encode from unicode
        strip < 0 will do nothing'''
        self.instrument.timeout = timeout
        ret = False
        try:
            ret = self.instrument.ask(command)
            if strip>=0:
                ret = ret.encode('ascii')
            if strip>=1:
                ret = ret[:-1]
        except:
            print 'Error asking,', command
        return ret
        
    def query(self, command, strip=1):
        '''A function to catch reading errors. 
        strip = 1 will strip tailing \n and encode from unicode
        strip = 0 will simply encode from unicode
        strip < 0 will do nothing'''
        ret = False
        try:
            ret = self.instrument.query(command)
            if strip>=0:
                ret = ret.encode('ascii')
            if strip>=1:
                ret = ret[:-1]
        except:
            print 'Error asking,', command
        return ret
        
    def query_binary_values(self, command):
        ret = False
        try:
            ret = self.instrument.query_binary_values(command, datatype='b')
        except Exception as e:
            print 'error querying binary,', command
            print 'Error is', e
        return ret
        
    def close(self):
        self.instrument.close()
        
class Agilent6000(BaseInstr):
    def __init__(self, GPIB_Number=None, timeout = 3000):
        super(Agilent6000, self).__init__(GPIB_Number, timeout)

        #Keep in memory which channel it is        
        self.channel = 1
        self.setSource(self.channel)
#        self.write(':DISP:PERS INF')
        
    def setSource(self, channel):
    #Specify the source channel for reading information
    #can either specify channel number alone, or 'CHAN#'
        if channel in (1, 2, 3, 4):
            channel = str(channel)
        else:
            channel = channel[-1]
        self.write(':WAV:SOUR CHAN'+channel)
        self.channel = int(channel)
        
        #Set it to output data as bytes (for speed)
        self.write(':WAV:FORM BYTE')
        #set it so data is sent as unsigned bytes        
        self.write(':WAV:UNS OFF')
        
    def readChannel(self, channel = None):
        if channel == None:
            channel = self.channel
        elif channel != self.channel:
            self.setSource(channel)
        values = self.query_binary_values(':WAV:DATA?')
#        self.write(':DIG CHAN'+str(channel))
        return values
        
    def scaleData(self, data=None):
        #See page 638
        #get the preamble
        pre = self.ask(':WAV:PRE?').split(',')
        xinc = float(pre[4])
        xori = float(pre[5])
        xref = float(pre[6])
        yinc = float(pre[7])
        yori = float(pre[8])
        yref = float(pre[9])
        
        x = np.arange(len(data))
        data = np.array(data)
        volt = (data - yref) * yinc + yori
        time = (x - xref) * xinc + xori
        
        return np.vstack((time, volt)).T
        
    def readMultipleChannels(self, *channels):
        #Channels should be a tuple of channel numbers to read
        if len(channels) == 1:
            self.setSource(channels[0])
            return self.readChannel([0])
        #Need to 'digitize' each of the channels we want to read
        st = ':DIG '
        for i in channels:
            st += 'CHAN'+str(i)+','
        st = st[:-1]
        self.write(st)
            
        
        self.waitForComplete()
        
        results = []
        for i in channels:
            raw = self.readChannel(i)
            results.append(self.scaleData(raw))
        
        return tuple(results)
        
        
    def waitForComplete(self, timeout=3000):
        origTO = self.instrument.timeout        
        self.instrument.timeout = timeout
        #Ask for operations complete        
        self.ask('*OPC?')
        self.instrument.timeout = origTO
        
    def setTrigger(self, isNormal = True, mode = 'EDGE', level=2.5, slope = 'POS', source = 4):
        '''Set up the triggering of the oscilloscope. See the doucmentation for details.
        isNormal switches between normal (as expected) or auto, where it internally triggers if no external trigger
        level is the voltage at which it triggers
        slope = [POS | NEG | EITHER | ALTERNATE]
        source is the channel source, EXT for external
        '''
        
        sweep = 'AUTO'
        if isNormal:
            sweep = 'NORM'
        
        self.write(':TRIG:SWE '+sweep)
        
        self.write(':TRIG:MODE '+mode)
        if mode == 'EDGE':
            self.write(':TRIG:EDGE:LEV '+str(level))
            self.write(':TRIG:EDGE:SLOP '+slope)
            ch = source
            if source in (1, 2, 3, 4):
                ch = 'CHAN'+str(source)
#                print ch
            self.write(':TRIG:EDGE:SOUR ' + ch)
            
        
    
   
#a = Agilent6000('GPIB::5::INSTR')     
class SPEX(BaseInstr):
    
    def __init__(self, GPIB_Number=None, timeout=3000):
        super(SPEX, self).__init__(GPIB_Number, timeout)
        
        self.maxWavenumber = 31000
        self.stepsPerWavenumber = 400
        self.backlash = 8000
        self.currentPositionWN = 13160
        self.currentPositionSteps = self.wavenumberToSteps(self.currentPositionWN)
    def ask(self, command):
        #Call the parent asking function, but only encode
        return super(SPEX, self).ask(command, strip=0)
        
    def query(self, command):
        ret = super(SPEX, self).query(command, strip=-1)
        return ret.encode('ascii')

    
    def whereAmI(self):
        ''' Should return 'B' if in boot sequence or 'F' in main sequence'''
        val = self.ask(' ')
        print val
        return val
        
    def initBoot(self):
        '''This function should be called if the SPEX isn't in the proper boot mode
        (e.g. if after being power cycled)'''
        print 'Checking position'
        pos = self.whereAmI()
        #First make sure the query didn't return FALSE if it timed out
        if not pos:
            print 'Error finding position. SPEX hung?'
            return
        elif pos.lower() == 'f':
            print 'SPEX already in operating mode. I\'ll keep going, but I\'m not sure I should...'
        elif not pos.lower() == 'b':
            print 'This shouldn\'t have happened', pos
            return
        #start main program
        print 'Starting main SPEX software'
        ret = self.ask('O2000', timeout = .5)
        if not ret:
            print 'Error starting SPEX main program. Retry init suggested'
            return
        elif not ret == '*':
            print "This also shouldn't have happened. ret =", ret
        print 'Initializing motors'
        
        #Needs to wait for 100 seconds, according to p37        
        ret = self.ask('A', timeout=100)
        if not ret:
            print 'Error initalizing motors'
            return
        elif not ret.lower()=='o':
            print "Bad motor initialization", ret
            return
        
        #These settings are coming from the SPEX init.vi
        #Come from appendix 1
        #
        #speed type 0, 1000Hz min, 18000Hz max, 2000ms ramp time
        print 'setting motor speed'
        speedStr = '0,1000,18000,2000'
        ret = self.ask('B'+speedStr)
        if not ret:
            print 'Error initalizing motor speed'
            return
        elif not ret.lower()=='o':
            print "Bad motor speed set", ret
            return
        ret = self.ask('C0')
        if not ret:
            print 'Error confirming motor speed'
            return
        elif not ret == 'o'+speedStr:
            print "Motor speed not correctly set?", ret
            
        print 'Setting internal position...'
        #This is what the dial reads on the SPEX.
        #Either enter manually or read from a file        
        currentPosition = self.currentPositionWN
        currentStep = self.wavenumberToSteps(currentPosition)
        ret = self.ask('G0,'+str(currentStep))
        if not ret:
            print 'Error setting position'
            return
        elif not ret == 'o':
            print "Motor position not correctly set?", ret
        
        #verify position
        ret = self.ask('H0')
        if not ret:
            print 'Error quering current position'
            return
        elif not ret[0]=='o':
            print 'I dunno', ret
        print 'Set to', str(currentStep), '  Reads',str(ret)
        
        
    def gotoWN(self, wn):
        #Will move the SPEX to the specified wavenumber
        notMoving = self.waitForMove()
        
        #Break because something went wrong and we weren't able to wait
        if not notMoving:
            return
        desiredWNSteps = int(self.wavenumberToSteps(wn))
        print 'Desired wnsteps:',desiredWNSteps
        currentSteps = self.curStep()
        print 'Currently:', currentSteps
        
        if desiredWNSteps == currentSteps:
            #Already where you wanted us to be
            return
        
        #Considerations must be done for backlash correction
        #Note, the converstion to steps is 31000-wn, which means larger wavenumber
        # is smaller steps
        toMove = desiredWNSteps - currentSteps
        if desiredWNSteps < currentSteps:
            #overstep it by the backlash amount
            self.relMove(toMove - self.backlash)
            toMove = self.backlash
            self.waitForMove()
        self.relMove(toMove)
        self.waitForMove()
            
        
        newPos = self.curStep()
        print 'Wanted,', desiredWNSteps
        print 'Got,', newPos
        
        self.currentPositionSteps = newPos
        self.currentPositionWN = self.stepsToWN(newPos)
        
    def curStep(self):
        #Return the current position, in steps
        ret = self.ask('H0')[:-1] #Ask, and remove the trailing /r
        if ret[0] == 'o':
            return int(ret[1:])
        else:
            return int(ret)
        
    def relMove(self, moveAmount):
        ''' Takes a relative amount of steps to move'''
        self.write('F0,'+str(moveAmount))
        
    def waitForMove(self):
        #This function runs until it sees that the motor is no longer moving
        busy = 'oq'
        notBusy = 'oz'
        i = 0 #Counter to not get stuck forever if things aren't working right
        ret = False
        while True:
            val = self.ask('E')
            if not val:
                print 'bad return from waiting'
                i = i+1
                if i == 10:
                    print 'Tried too many times'
                    break
            elif val == notBusy:
                #Done
                ret = True
                break
            elif val==busy:
                pass
            time.sleep(0.05)
        return ret
            
        
        
    def wavenumberToSteps(self, wn):
        return (self.maxWavenumber - wn) * self.stepsPerWavenumber
        
    def stepsToWN(self, step):
        return self.maxWavenumber - (float(step)/400.)
        
        



class SR830Instr(BaseInstr):
    def __init__(self, GPIB_Number = None, timeout = 3000):
        super(SR830Instr, self).__init__(GPIB_Number, timeout)
        self.write('OUTX 1')
                
    def setRefFreq(self, freq):
        '''Set the reference frequency  '''
        if type(freq) not in (float, int):
            print 'Error. Given frequency is not a number'
            return
        self.write('FREQ '+str(freq))
            
    def setRefVolt(self, volts):
        if type(volts) not in (float, int):
            print 'Error. Given voltage is not a number'
            return
        self.write('SLVL '+str(volts))
        
    def getRefVolt(self):
        return float(self.ask('SLVL?'))
        
    def getChannel(self, ch=1):
        if ch not in (1, 2, 3, 4, 'X', 'x', 'Y', 'y', 'R', 'r', 't', 'T', 'theta', 'Theta', 'th'):
            print 'Error. Must give valid channel number'
            return
        #if a letter is given instead of  anumber, must convert it
        if type(ch) is str:
            d = dict(x=1, y=2, r=3, t=4)
            ch = d[ch.lower()[0]]
        return float(self.ask('OUTP? '+str(ch)))
    def getMultiple(self, *args):
        '''Use the SNAP? command to read the values instantanously and avoid
            timing issues'''
        toRead = ''
        for (i, ch) in enumerate(args):
            if ch not in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                          'X', 'x', 'Y', 'y', 'R', 'r', 't', 'T', 'theta', 'Theta', 'th'):
                print 'Error. Must give valid channel number'
                return
            #if a letter is given instead of  anumber, must convert it
            if type(ch) is str:
                d = dict(x=1, y=2, r=3, t=4)
                ch = d[ch.lower()[0]]
            toRead = toRead + str(ch) +','
        toRead = toRead[:-1]
        ret = self.ask('SNAP?'+toRead)
        return [float(i) for i in ret.split(',')]
            
        
        

        

        

class Keithley236Instr(BaseInstr):
    def __init__(self, GPIB_Number=None, timeout = 3000):
        super(Keithley236Instr, self).__init__(GPIB_Number, timeout)
        
    def setBias(self, BiasLevel):
        #Set to the desired bias level, auto ranging and waiting 10ms
        if type(BiasLevel) not in (float, int):
            print 'Error. Invalid bias level'
            return 
        self.write('B'+str(BiasLevel)+',0,10X')
        
    def askCurrent(self):
        ret = self.ask('G5,2,0X')
        return float(ret.encode('ascii')[:-2].split(',')[1])
        
    def turnOff(self):
        self.write('N0X')
    
    def turnOn(self):
        self.write('N1X')
        
        
        
class Keithley2400Instr(BaseInstr):
    def __init__(self ,GPIB_Number=None, timeout = 3000, stopCurrent=1e-4, compliance=1e-3):
        super(Keithley2400Instr, self).__init__(GPIB_Number)

        #Reset the instrument, clear flags and errors
        self.write("*rst; status:preset; *cls")
        
        self.setSourceMode('volt')
        self.setSenseMode('curr')
        
        #set sensing ranging
        self.setSenseRange(5e-3)
        self.setCompliance(compliance)
        self.set4Probe(False) #set to 2point measurement?
        
    def setSourceMode(self, mode):
        newMode = 'volt'
        if mode.lower() in ('c', 'current', 'curr'):
            newMode = 'curr'
        st = 'sour:func:mode '+newMode
        self.write(st)
        self.sourcing = newMode
    
    def setSenseMode(self, mode):
        newMode = "'volt'"
        if mode.lower() in ('c', 'current', 'curr'):
            newMode = "'curr'"
        st = 'sens:func  '+newMode
        self.write(st)
        #cut off the leading/tailing quote marks        
        self.sensing = newMode[1:-1]
        
    def setSenseRange(self, level):
        if level>0:
            #turn off autorange
            lev = 'auto off'
            self.write('sens:'+self.sensing+':rang:'+lev)
            #set the range
            lev = 'upp '+str(level)
            self.write('sens:'+self.sensing+':rang:'+lev)
        else:
            #Turn on autorange if negative number is given
            lev = 'auto on'
            self.write('sens:'+self.sensing+':rang:'+lev)
            
    def setSourceRange(self, level):
        if level>0:
            #turn off autorange
            lev = 'auto off'
            self.write('sour:'+self.sourcing+':rang:'+str(lev))
            #set the range
            lev = 'upp '+level
            self.write('sour:'+self.sourcing+':rang:'+str(lev))
        else:
            #Turn on autorange if negative number is given
            lev = 'auto on'
            self.write('sour:'+self.sourcing+':rang:'+str(lev))
        
    def setCompliance(self, level):
        st = 'sens:'+self.sensing+':prot:lev '+str(level)
        self.write(st)
    
    def set4Probe(self, flag):
        '''Set whether to use 4 probe measurement (True) or not (False)'''
        doIt = 'OFF'
        if flag:
            doIt = 'ON'
        st = 'syst:rsen '+doIt
        self.write(st)
    
    def getValue(self):
        ret = self.ask("read?").encode('ascii')
        #comes back as a unicode, comma separated list of values
        return float(ret.encode('ascii')[:-1].split(',')[1])    
    def setCurrent(self,current):
        self.write("sour:curr:lev " + str(current))
        
    def setVoltage(self, voltage):
        self.write('sour:volt:lev ' + str(voltage))
        
    def turnOn(self):
        self.write('OUTP ON')
    
    def turnOff(self):
        self.write('OUTP OFF')
            
                
        







