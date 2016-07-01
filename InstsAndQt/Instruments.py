# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 16:38:33 2015

@author: dvalovcin
"""

from __future__ import division
import numpy as np
import visa
import pyvisa.errors
import time
import logging

from customQt import *
# import fakeInstruments.setPrintOutput



log = logging.getLogger("Instruments")
log.setLevel(logging.DEBUG)
handler = logging.FileHandler("TheInstrumentLog.log")
handler.setLevel(logging.DEBUG)
handler1 = logging.StreamHandler()
handler1.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)s()] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler1.setFormatter(formatter)
log.addHandler(handler)
log.addHandler(handler1)


class BaseInstr(object):
    """Base class which handles opening the GPIB and safely reading/writing to the instrument"""
    def __init__(self, GPIB_Number = None, timeout = 3000):
        if GPIB_Number is None or GPIB_Number == 'Fake':
            log.debug('Error. No GPIB assigned {}'.format(self.__class__.__name__))
            # self.instrument = FakeInstr()
            self.instrument = getCls(self)()
        else:
            rm = visa.ResourceManager()
            try:
                self.instrument = rm.open_resource(GPIB_Number)
                log.debug( "GOT INSTRUMENT AT {}".format(GPIB_Number))
                self.instrument.timeout = timeout
            except Exception as e:
                log.warning('Error opening GPIB {}'.format(e))
                raise

        # try:
        #     # key = self.instrument.lock()
        #     self.instrument.lock_excl()
        # except:
        #     log.warning("Instrument is already open in anothe program")
        #     raise RuntimeError("Instrument is already open, don't open it again")

    def write(self, command, strip=True):
        """A safer function to catch errors in writing commands. Also ensures
        proper ending to command. """
        try:
            self.instrument.write(command)
        except Exception as e:
            print 'Error writting command, {}. {}'.format(command, e)
            return False
        return True
    
    def ask(self, command, strip=1, timeout = None):
        """A function to catch reading errors. 
        strip = 1 will strip tailing \n and encode from unicode
        strip = 0 will simply encode from unicode
        strip < 0 will do nothing"""
        if timeout is not None:
            self.instrument.timeout = timeout
        ret = False
        try:
            ret = self.instrument.ask(command)
            if strip>=0:
                ret = ret.encode('ascii')
            if strip>=1:
                ret = ret[:-1]
        except pyvisa.errors.VisaIOError:
            print "error: timeout while asking", command
        except Exception as e:
            print 'Error asking,', command, e
        return ret

    def read(self):
        ret = False
        try:
            ret = self.instrument.read()
        except pyvisa.errors.VisaIOError:
            print "timeout while reading"
        return ret
        
    def query(self, command, strip=1):
        """A function to catch reading errors. 
        strip = 1 will strip tailing \n and encode from unicode
        strip = 0 will simply encode from unicode
        strip < 0 will do nothing"""
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

    def query_ascii_values(self, *arg, **kwargs):
        ret = False
        try:
            ret = self.instrument.query_ascii_values(*arg, **kwargs)
        except Exception as e:
            print "Error querying ascii values", arg, kwargs
            print "Error is", e
        return ret
        
    def close(self):
        self.instrument.close()
        try:
            self.instrument.unlock()
        except:
            pass

    def open(self):
        self.instrument.open()

class ArduinoWavemeter(BaseInstr):
    def __init__(self, GPIB_Number=None, timeout = 3000):
        super(ArduinoWavemeter, self).__init__(GPIB_Number, timeout)
        self.instrument.parent = self
        self.instrument.open()
        self.instrument._write_termination = '\n'
        self.instrument._read_termination = '\r\n'
        self.instrument.baud_rate = 115200
        self.exposureTime = 100 # ms

    def ask(self, command, strip=-1, timeout = None):
        return super(ArduinoWavemeter, self).ask(command, strip, timeout)

    def read_values(self, exposureTime = None):
        if exposureTime is None:
            exposureTime = self.exposureTime
        exposureTime = int(exposureTime)
        print "querying to expose for,", exposureTime

        retVal = self.ask(str(exposureTime))
        print "arduino response:", retVal

        time.sleep(float(exposureTime)/1000)

        # values = self.ask(str(exposureTime))
        values = self.read()

        if not values:
            return False
        try:
            return map(int, values.split(';'))
        except ValueError:
            # for some reason, sometimes pyvisa will not remove a
            # \n, which map tries to parse to an int, which throws
            # the value error. Just remove the problem non-numbert
            return map(int, values.split(';')[:-1])

class Agilent6000(BaseInstr):
    # We need a static 16.6ms offset for instrument triggering purposes,
    # but often look at timescales of us's, which causes long and ugly
    # time-bases. This number will subtract a static number so save files
    # can be smaller and generally less obnoxious
    EXTERNAL_OFFSET = 16.59e-3

    # Will convert the time base to this value. Default is us
    TIME_BASE = 1e6
    def __init__(self, GPIB_Number=None, timeout = 3000):
        super(Agilent6000, self).__init__(GPIB_Number, timeout)

        #Keep in memory which channel it is        
        self.channel = 1
        self.setSource(self.channel)

    def setIntegrating(self, val):
        try:
            self.instrument.setIntegrating(val)
        except:
            #for debugging things with fake instruments. I'm sorry
            pass

    def setCD(self, val):
        try:
            self.instrument.setCD(val)
        except:
            #for debugging things with fake instruments. I'm sorry
            pass
        
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
        if channel is None:
            channel = self.channel
        elif channel != self.channel:
            self.setSource(channel)
        values = self.query_binary_values(':WAV:DATA?')
        return values
        
    def scaleData(self, data=None):
        #See page 638
        #get the preamble
        # Assumes you're scaling the data that is
        # currently active

        time = np.arange(len(data))
        volt = data

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
        time -= self.EXTERNAL_OFFSET
        time *= self.TIME_BASE

        
        return np.vstack((time, volt)).T

    def getSingleChannel(self, channel):
        if channel not in (1, 2, 3, 4):
            print "Error, invalid channel for reading, {}".format(channel)
            return
        st = ":DIG CHAN"+str(channel)
        self.write(st)
        self.waitForComplete()

        raw = self.readChannel(channel)
        return self.scaleData(raw)

    def getMultipleChannels(self, *channels):
        #pass the channels that should be read
        if len(channels) == 1:
            self.setSource(channels[0])
            return (self.getSingleChannel(channels[0]),)
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
        
        
    def waitForComplete(self, timeout=None):

        origTO = self.instrument.timeout
        if timeout is not None:
            self.instrument.timeout = timeout
        #Ask for operations complete        
        self.ask('*OPC?')
        self.instrument.timeout = origTO
        
    def setTrigger(self, isNormal = True, mode = 'EDGE', level=2.5, slope = 'POS', source = 4):
        """Set up the triggering of the oscilloscope. See the doucmentation for details.
        isNormal switches between normal (as expected) or auto, where it internally triggers if no external trigger
        level is the voltage at which it triggers
        slope = [POS | NEG | EITHER | ALTERNATE]
        source is the channel source, EXT for external
        """
        
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
            self.write(':TRIG:EDGE:SOUR ' + ch)

    def setMode(self, mode):
        if mode.lower() not in ["normal", "average", "hresolution", "peak",
                                "norm", "aver", "hres"]:
            mode = "NORM"
        self.write(":ACQ:TYPE {}".format(mode))
    def setAverages(self, num):
        try:
            num = int(num)
        except:
            num = 1

        # Set it so it hopefully doesn't timeout
        # 0.75 = ~FEL RR
        # 1.5 is factor in case maybe 1/3 pulses is missed
        self.instrument.timeout = num/0.75 * 1.5*1000

        self.write(":ACQ:COUN {}".format(num))

    @staticmethod
    def integrateData(data, bounds):
        """
        So often, I find myself having to integrate osc data
        for boxcar purposes. I'm tired of doing it by hand. Henceforth,
        call this function.

        Data = 2D array. Data[:,0] = x, data[:,1] = y
        bounds = tuple of x points overwhich to integrate
        """
        st = bounds[0]
        en = bounds[1]

        x = data[:,0]
        y = data[:,1]

        gt = set(np.where(x>st)[0])
        lt = set(np.where(x<en)[0])

        # find the intersection of the sets
        vals = list(gt&lt)

        # Calculate the average
        tot = np.sum(y[vals])

        # Multiply by sampling
        tot *= (x[1]-x[0])

        # Normalize by total width
        tot /= (en-st)
        return tot

class SPEX(BaseInstr):
    
    def __init__(self, GPIB_Number=None, timeout=3000):
        super(SPEX, self).__init__(GPIB_Number, timeout)
        
        self.maxWavenumber = 31000
        self.stepsPerWavenumber = 400
        self.backlash = 8000
        try:
            self.currentPositionSteps = self.curStep()
            self.currentPositionWN = self.stepsToWN(self.currentPositionSteps)
        except Exception as e:
            log.warning("Error! Could not initialize settings.\n Instrument not initialized after boot? {}".format(e))
    def ask(self, command, timeout=None):
        #Call the parent asking function, but only encode
        return super(SPEX, self).ask(command, strip=0, timeout=timeout)
        
    def query(self, command):
        ret = super(SPEX, self).query(command, strip=-1)
        return ret.encode('ascii')

    
    def whereAmI(self):
        """ Should return 'B' if in boot sequence or 'F' in main sequence"""
        val = self.ask(' ')
        print val
        return val
        
    def initBoot(self, wavenumber = None):
        """This function should be called if the SPEX isn't in the proper boot mode
        (e.g. if after being power cycled)"""
        
        if wavenumber is not None:
            self.currentPositionWN = wavenumber
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
        ret = self.ask('O2000', timeout = 5)
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
        elif not ret.lower()[0]=='o':
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
        if wn>15000:
            print "NO. BAD. DON'T GO THERE.\n\tDesired SPEX wavenumber too large"
            return
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
        """ Takes a relative amount of steps to move"""
        self.write('F0,'+str(moveAmount))
        
    def waitForMove(self):
        #This function runs until it sees that the motor is no longer moving
        busy = 'oq'
        notBusy = 'oz'
        i = 0 #Counter to not get stuck forever if things aren't working right
        ret = False
        while True:
            if i >= 800: # did something go terribly wrong?
                break
            val = self.ask('E')
            if not val:
                print 'bad return from waiting'
                i = i+1
                if i >= 10:
                    print 'Tried too many times'
                    break
            elif val == notBusy:
                #Done
                ret = True
                break
            elif val==busy:
                pass
            time.sleep(0.05)
            i += 1
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
        """Set the reference frequency  """
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
        """Use the SNAP? command to read the values instantanously and avoid
            timing issues"""
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
    # Custom bool which can be locked
    # to prevent changing
    breakLoop = LockableBool(False)
    def __init__(self ,GPIB_Number=None, timeout = 3000, stopCurrent=1e-4, compliance=1e-3):
        super(Keithley2400Instr, self).__init__(GPIB_Number)

        self.sleepTime = 0.05 # s
        self.breakLoop = False # flag for when to stop ramping/measuring
        self.voltage = 0.0

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
        """Set whether to use 4 probe measurement (True) or not (False)"""
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
        self.voltage = voltage
        
    def turnOn(self):
        self.write('OUTP ON')
    
    def turnOff(self):
        self.write('OUTP OFF')

    def rampVoltage(self, vrange, toCall=lambda x: None, sleep = None):
        """
        Ramp through the given voltages in range. Sleep the time given,
        and then call the callable function. Will NOT turn on the voltage
        and will NOT turn it off
        """
        if sleep is None:
            sleep = self.sleepTime
        for voltage in vrange:
            if self.breakLoop:
                return voltage # Let caller know where we were stopped
            self.setVoltage(voltage)
            try:
                toCall(voltage)
            except TypeError:
                toCall()
            except Exception as e:
                print "Error calling intermediate function!", e
            time.sleep(sleep)
        return vrange[-1]

    def doLoop(self, start, stop, step=0.1, sleep = None, toCall = lambda x: None, measureHyst = False):

        # Do some tests to make sure the start/stop parameters are correct
        if start * stop < 0:
            # If on opposite sides of zero, should always be stepping
            # away from the starting point
            assert np.sign(step) == -np.sign(start)
        else:
            # Otherwise, on the same side, but need to make sure you're properly stepping
            assert np.sign(step) == np.sign(stop - start)

        if sleep is None:
            sleep = self.sleepTime
        self.breakLoop = False
        self.turnOn()
        stoppedAt = 0.0

        # Make sure we start off ramping where we want to be.
        if not start == 0:
            voltages = np.arange(0, start, np.sign(start) * np.abs(step))
            voltages = np.append(voltages, start)
            # start ramping to the start voltage. Get the value
            # where we're supposed to stop
            # (in case it was stopped prematurely)
            stoppedAt = self.rampVoltage(voltages, sleep=sleep)

        # make sure we haven't been told to stop. Turn off
        # after ramping and return if we have been.
        if self.shouldStopLoop(stoppedAt, step, sleep):
            self.turnOff()
            return

        # do the real loop
        voltages = np.arange(start, stop, step)
        voltages = np.append(voltages, stop)
        stoppedAt = self.rampVoltage(voltages, toCall, sleep)

        if measureHyst:
            if self.shouldStopLoop(stoppedAt, step, sleep):
                self.turnOff()
                return
            voltages = np.arange(stop, start, -step)
            voltages = np.append(voltages, start)
            stoppedAt = self.rampVoltage(voltages, toCall, sleep)
            
        # Cheap hack to make it ramp down
        self.breakLoop = True

        self.shouldStopLoop(stoppedAt, step, sleep)
        self.turnOff()



    def shouldStopLoop(self, voltage, step, sleep):
        """ Convenience function to check whether
         we should stop doing a loop. If true, will automatically
         step down
        """
        if not self.breakLoop: return False

        self.breakLoop = False
        self.breakLoop.lock()

        voltages = np.arange(voltage, 0, -np.sign(voltage) * np.abs(step))
        voltages = np.append(voltages, 0)

        self.rampVoltage(voltages, sleep = sleep)
        self.breakLoop.unlock()
        self.breakLoop = True

class ActonSP(BaseInstr):
    backlashCorr = -6
    doCal = None
    def __init__(self, GPIB_Number=None, timeout=3000):
        super(ActonSP, self).__init__(GPIB_Number, timeout)
        try:
            time.sleep(0.5) # maybe asking too soon after communication has been established?
            self.grating = self.getGrating() # Need for calibration
            self.wavelength = self.getWavelength()
        except Exception, e:
            print "ERROR INIT:", e
    def gotoWavelength(self, wl, doCal=True):
        """ Will go to the sepcified wavelength, given in nm, up to 3 decimal places """
        """
        doCal is a parameter that was used when the spectrometer was not well aligned.
        A polynomial correction was used so lines would be centered properly. In summer '15,
        the spectrometer was opened and fully aligned so software corrections
        were deemed unnecessary. Parameter left for legacy reasons.
        """

        # Some weird hystersis in the spectrometer. 
        # Want to go past the desired amount and step back up.
        #
        # self.backlash < 0: always step down
        # self.backlash > 0: always step up

        if (self.wavelength - wl)*self.backlashCorr > 0:
            goto = "{:.3f} GOTO".format(float(wl) - self.backlashCorr)
            self.ask(goto, timeout = 10000)
        
        wl = "{:.3f} GOTO".format(float(wl)) # ensure that it's 3 decimal places, at most
        self.ask(wl, timeout = 10000) # ask so it waits for the response when finished
        self.wavelength = self.getWavelength()
        
    def getWavelength(self):
        ret = self.ask('?nm')
        # return is "?nm <wavelength> nm  ok\r\n. base class removes \n
        if not ret:
            print "ERROR GETTING SPECTROMETER WAVELENGTH"
            return
        return float(ret[3:-8])
        
    def setGrating(self, grating):
        if grating not in (1, 2, 3):
            print 'Not a valid grating'
            return
        print self.ask(str(grating)+' grating', timeout=25000)
        
    def getGrating(self):
        ret = self.ask('?grating')
        if not ret:
            print "ERROR GETTING SPECTROMETER GRATING\nENSURE COMMUNICATION"
            return
        return int(ret[8:-5])
        
    def goAndAsk(self, wl, doCal = True):
        self.gotoWavelength(wl, doCal)
        return self.getWavelength()
        
    def getSpeed(self):
        ret = self.ask("?nm/min")
        if not ret:
            pass
    def gotoSpeed(self, wl):
        wl = "{:.3f} nm".format(float(wl))
        self.ask(wl, timeout=None)

class ESP300(BaseInstr):
    '''
    Newport Universal Motion Controller/Driver Model ESP300

    all axis control commands are sent to the number axis given by the
    local variable self.current_axis. so here is an example usage

    esp= ESP300()
    esp.current_axis=1
    esp.units= 'millimeter'
    esp.position = 10
    print esp.position
    '''
    UNIT_DICT = {\
        'enoder count':0,\
        'motor step':1,\
        'millimeter':2,\
        'micrometer':3,\
        'inches':4,\
        'milli inches':5,\
        'micro inches':6,\
        'degree':7,\
        'gradient':8,\
        'radian':9,\
        'milliradian':10,\
        'microradian':11,\
        }

    def __init__(self, address, current_axis=1,\
        always_wait_for_stop=True,delay=500,**kwargs):
        '''
        takes:
            address:    Gpib address, int [1]
            current_axis:   number of current axis, int [1]
            always_wait_for_stop:   wait for stage to stop before
                returning control to calling program, boolean [True]
            **kwargs:   passed to GpibInstrument initializer
        '''

        # GpibInstrument.__init__(self,address,**kwargs)
        super(ESP300, self).__init__(address)
        # self.instrument = rm().open_resource(address)
        self.instrument.timeout = 10000L
        self.current_axis = current_axis
        self.always_wait_for_stop = always_wait_for_stop
        self.delay=delay
    @property
    def current_axis(self):
        '''
        current axis used in all subsequent commands
        '''
        return self._current_axis
    @current_axis.setter
    def current_axis(self, input):
        '''
        takes:
            input:  desired current axis number, int []
        '''
        self._current_axis = input


    @property
    def velocity(self):
        '''
        the velocity of current axis
        '''
        command_string = 'VA'
        return (float(self.instrument.ask('%i%s?'%(self.current_axis,command_string))))
    @velocity.setter
    def velocity(self,input):
        command_string = 'VA'
        self.instrument.write('%i%s%f'%(self.current_axis,command_string,input))

    @property
    def acceleration(self):
        command_string = 'AC'
        return (self.instrument.ask('%i%s?'%(self.current_axis,command_string)))
    @acceleration.setter
    def acceleration(self,input):
        command_string = 'AC'
        self.instrument.write('%i%s%f'%(self.current_axis,command_string,input))

    @property
    def deceleration(self):
        command_string = 'AG'
        return (self.instrument.ask('%i%s?'%(self.current_axis,command_string)))
    @deceleration.setter
    def deceleration(self,input):
        command_string = 'AG'
        self.instrument.write('%i%s%f'%(self.current_axis,command_string,input))

    @property
    def position_relative(self):
        raise NotImplementedError('See position property for reading position')
    @position_relative.setter
    def position_relative(self,input):
        command_string = 'PR'
        self.instrument.write('%i%s%f'%(self.current_axis,command_string,input))
        if self.always_wait_for_stop:
            self.wait_for_stop()

    @property
    def position(self):
        command_string = 'TP'
        return float(self.instrument.ask('%i%s'%(self.current_axis,command_string)))
    @position.setter
    def position(self,input):
        '''
        set the position of current axis to input
        '''
        command_string = 'PA'
        self.instrument.write('%i%s%f'%(self.current_axis,command_string,input))
        if self.always_wait_for_stop:
            self.wait_for_stop()
    @property
    def home(self):
        raise NotImplementedError
    @home.setter
    def home(self, input):
        command_string = 'DH'
        self.instrument.write('%i%s%f'%(self.current_axis,command_string,input))


    @property
    def units(self):
        raise NotImplementedError('I dont know how to read units')
    @units.setter
    def units(self, input):
        '''
         set axis units for all commands.
         takes:
            input: a string, describing the units here are a list of
                possibilities.
                 'enoder count'
                'motor step'
                'millimeter'
                'micrometer'
                'inches'
                'milli inches'
                'micro inches'
                'degree'
                'gradient'
                'radian'
                'milliradian'
                'microradian'
        '''
        command_string = 'SN'
        self.instrument.write('%i%s%i'%(self.current_axis,command_string, self.UNIT_DICT[input]))

    @property
    def error_message(self):
        return (self.instrument.ask('TB?'))

    @property
    def motor_on(self):
        command_string = 'MO'
        return (self.instrument.ask('%i%s?'%(self.current_axis,command_string)))
    @motor_on.setter
    def motor_on(self,input):
        if input:
            command_string = 'MO'
            self.instrument.write('%i%s'%(self.current_axis,command_string))
        if not input:
            command_string = 'MF'
            self.instrument.write('%i%s'%(self.current_axis,command_string))

    def send_stop(self):
        command_string = 'ST'
        self.instrument.write('%i%s'%(self.current_axis,command_string))

    def wait_for_stop(self):
        command_string = 'WS'
        self.instrument.write('%i%s%i'%(self.current_axis,command_string, self.delay))
        tmp = self.position

class LakeShore325(BaseInstr):
    ''' 
    Temperature Controller for LED
    '''
    def __init__(self, GPIB_Number=None, timeout=3000):
        super(LakeShore325, self).__init__(GPIB_Number,timeout)
    
    def askTemp(self, channel="A"):
        #returns temp in C from input A/B in float
        temp=self.ask("CRDG? "+channel)
        return float(temp)  


    def askSetpoint(self, loop="1"):
        #returns set point in loop 1/2 in float
        sp=self.ask("SETP? "+loop)
        return float(sp) 

    def askOutput(self, loop="1"):
        #returns heater output of loop 1 or 2 in float
        output=self.ask("HTR? "+loop)
        return float(output)

class LakeShore330(BaseInstr):
    ''' 
    Temperature Controller for Sample
    There's some distinction between "sample" and control
    channels. I'm not quite sure the difference. At thee
    time of writing, we operate with both being the same
    (channel b)
    '''
    def __init__(self, GPIB_Number=None, timeout=3000):
        super(LakeShore330, self).__init__(GPIB_Number,timeout)

    def setControlChannel(self, channel='B'):
        # set the control channel to the specified one
        # Default to 'A' if input is not 'B'
        channel = channel if channel=='B' else 'A'
        self.write("CCHN {}".format(channel))

    def getControlChannel(self):
        return self.ask("CCHN?")

    def setControlUnits(self, units = 'K'):
        self.write("CUNI {}".format(units))

    def getControlUnits(self):
        return self.ask("CUNI?")

    def getControlTemp(self, channel="A"):
        #returns temp in C from input A/B in float
        temp=self.ask("CDATA?")
        return float(temp)

    def setSampleChannel(self, channel='B'):
        # set the control channel to the specified one
        # Default to 'A' if input is not 'B'
        channel = channel if channel=='B' else 'A'
        self.write("SCHN {}".format(channel))

    def getSampleChannel(self):
        return self.ask("SCHN?")

    def setSampleUnits(self, units = 'K'):
        self.write("SUNI {}".format(units))

    def getSampleUnits(self):
        return self.ask("SUNI?")

    def getSampleTemp(self, channel="A"):
        #returns temp in C from input A/B in float
        temp=self.ask("SDATA?")
        return float(temp)

    def getSetpoint(self):
        #returns set point in loop 1/2 in float
        sp=self.ask("SETP?")
        return float(sp)

    def setSetpoint(self, sp=280):
        #returns set point in loop 1/2 in float
        self.write("SETP {:.2f}".format(sp))

    def getHeater(self):
        #returns heater output of loop 1 or 2 in float
        output=self.ask("HEAT?")
        return float(output)

    def setHeaterRange(self, range=0):
        self.write("RANG {}".format(range))

    def getHeaterRange(self):
        return int(self.ask("RANG?"))

    def getP(self):
        return int(self.ask("GAIN?"))

    def setP(self, P):
        self.write("GAIN {:d}".format(P))

    def getI(self):
        return int(self.ask("RSET?"))

    def setI(self, I):
        self.write("RSET {:d}".format(I))

    def getD(self):
        return int(self.ask("RATE?"))

    def setD(self, D):
        self.write("RATE {:d}".format(D))

    def getPID(self):
        return self.getP(), self.getI(), self.getD()

    def setPID(self, P=None, I=None, D=None):
        if P is None:
            P = self.getP()
        if I is None:
            I = self.getI()
        if D is None:
            D = self.getD()
        self.setP(P)
        self.setI(I)
        self.setD(D)



# Needs to be at the bottom to prevent
# cyclical definitions. This makes me think
# I'm doing things wrong, but I dunno what else.
try:
    from fakeInstruments import setPrintOutput, getCls
except ImportError:
    print "got the import error"



if __name__ == '__main__':
    a = LakeShore325("GPIB0::12::INSTR")
    print a.askOutput()


        







