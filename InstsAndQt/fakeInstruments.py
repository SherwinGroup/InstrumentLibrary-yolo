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

import Instruments


PRINT_OUTPUT = True


def setPrintOutput(enabled = True):
    global PRINT_OUTPUT
    PRINT_OUTPUT = enabled




class FakeInstr(object):
    timeout = 3000
    def __init__(self):
        self._locked = False
        # print "fkae instr class", self.__class__.__name__
    def lock(self):
        if self._locked:
            raise IOError("instrument locked")
        else:
            self._locked = Truea

    def unlock(self):
        if not self._locked:
            raise IOError("Instrument isn't locked")
        else:
            self._locked = False
    def lock_excl(self):
        self.lock()

    def write(self, string):
        if PRINT_OUTPUT:
            print ' '*15 + string
    def ask(self, string):
        if PRINT_OUTPUT:
            print ' '*12 + string
        if '*OPC?'==string:
            time.sleep(0.5)
            return u'1\r'
        
    def close(self):
        print self.__class__.__name__ + 'closed'

    def open(self):
        print self.__class__.__name__ + 'opened'

class ArduinoWavemeter(FakeInstr):
    def ask(self, string):
        ret = super(ArduinoWavemeter, self).ask(string)
        if ret is not None:
            return ret
        try:
            t = float(string)
            time.sleep(t/1000)
            return 'd{}'.format(int(t))
        except Exception as e:
            print "it's not you", string, type(string), e

    def read(self):
        # so far, only the arduino calls the reads
        # directly
        if hasattr(self, 'parent'):
            if isinstance(self.parent, ArduinoWavemeter):
                return ";".join([str(ii) for ii in np.random.randint(300, 3000, (401,))])

    def query_ascii_values(self, str=''):
        """
        ArduinoWavemeter calls this
        :param str:
        :return:
        """
        return ";".join(np.random.randint(300, 3000, (401,)))

class Agilent6000(FakeInstr):
    integrating = True # for simulating pyro behavior for oscopes
    CD = True
    def setIntegrating(self, val):
        self.integrating = val
    def setCD(self, val):
        self.CD = val
    def write(self, string):
        super(Agilent6000, self).write(string)
        if ':DIG' in string: #Agilent telling it to start data collection
            time.sleep(1/25)
    def ask(self, string):
        ret = super(Agilent6000, self).ask(string)
        if ret is not None:
            return ret
        if ':WAV:PRE?' == string:#agilent oscilloscope, waveform preamble
            # a = np.random.random((10,))
            a = np.ones((10,))
             #Forcing some numbers for reasonable consistancy
            a[4] = 5e-9 # x inc
            a[5] = 1.659e-2 # x origin
            a[6] = 0. # x reference?
            a[7] = 1.5625e-3 # y increment
            a[8] = -4e-2 # y origin
            a[9] = 0. # y ref?
            st = ''
            for i in a:
                st+=str(i)+','
            return st
        elif ':WAV:DATA?' == string: #agilent querying data
            a = 10.*np.random.random((1000,)) + 100
            b = 10.*np.random.random((1000,)) + 200
            arr = np.concatenate((a,b))
            if self.integrating:
                arr = np.cumsum(arr) * 1e-3
            return arr

    def query_binary_values(self, string, datatype):
        np.random.seed()
        if ':WAV:DATA?' == string: #agilent querying data
            if self.CD:
                # Simulate a missed pulse 1/10
                noise = np.random.normal(scale=0.5, size=(2500,))
                if np.random.randint(0,10)==0:
                    return noise
                a = np.zeros((1000,)) # start
                b = np.random.randint(50,70) * np.ones((1000,)) # FP
                c = np.random.randint(1200,1300) * np.ones((20,)) #CD
                d = np.zeros((480,))
                arr = np.concatenate((a,b, c, d))
                if self.integrating:
                    arr = np.cumsum(arr) *1e-3
                else:
                    arr *= 5e-2
                arr += noise
                arr += np.random.randint(-40, 40)
                return arr
            else:
                # Simulate a missed pulse 1/10
                noise = np.random.normal(scale=0.5, size=(2500,))
                if np.random.randint(0,10)==0:
                    return noise
                a = np.zeros((1000,)) # start
                x = np.arange(750)
                b = np.random.randint(150,175) * (1. - np.exp(-x/400))
                x = np.arange(250)
                c = b[-1]*(np.exp(-x/55))
                d = np.zeros((500,))
                arr = np.concatenate((a, b, c, d))
                if self.integrating:
                    arr = np.cumsum(arr) *1e-3
                else:
                    arr *= 5e-2
                arr += noise
                arr += np.random.randint(-10, 10)
                return arr

class SPEX(FakeInstr):
    curStep = 70000 #Making life interesting for SPEX instrument
    def write(self, string):
        super(SPEX, self).write(string)
        if 'F0' in string: #SPEX Relative move
            self.curStep += int(string[3:])
    def ask(self, string):
        ret = super(SPEX, self).ask(string)
        if ret is not None:
            return ret
        if 'H0' in string: #SPEX Relative move
            return str(self.curStep) + '\r'
        elif string == 'E': #SPEX, is it moving
            return 'oz'

class SR830Instr(FakeInstr):
    def ask(self, string):
        ret = super(SR830Instr, self).ask(string)
        if ret is not None:
            return ret
        #Test for some basic instrument questions and output the expected output
        if 'SLVL' in string or 'OUTP' in string:
            return str(np.random.random())
        elif 'SNAP?' in string:
            return str(np.random.random())+','+str(np.random.random())

class Keithley236Instr(FakeInstr):
    def __init__(self):
        raise NotImplementedError

class Keithley2400Instr(FakeInstr):
    def __init__(self):
        raise NotImplementedError

class ActonSP(FakeInstr):
    def ask(self, string):
        ret = super(ActonSP, self).ask(string)
        if ret is not None:
            return ret
        if '?nm'==string:
            val = np.random.randint(600, 700) + np.random.randint(1, 1000)/1000.
            return "?nm {} nm  ok\r".format(val)

        elif '?grating' == string:
            val = np.random.randint(1, 3)
            return "?grating {}  ok\r\n".format(val)
        elif 'GOTO' in string:
            return string[:4]
        elif 'grating' in string:
            return string[0]
        
class ESP300(FakeInstr):
    _vel = 10
    _acc = 10
    _dec = 10
    _pos = 0
    _on  = 0
    def write(self, string):
        super(ESP300, self).write(string)
        if "VA" in string:
            self._vel = float(string.split("VA")[1])
        elif "AC" in string:
            self._acc = float(string.split("AC")[1])
        elif "AG" in string:
            self._dec = float(string.split("AG")[1])
        elif "PA" in string:
            self._pos = float(string.split("PA")[1])
        elif "MO" in string:
            self._on = 1
        elif "MF" in string:
            self._on = 0
        elif "WS" in string:
            time.sleep(0.5)

    def ask(self, string):
        ret = super(ESP300, self).ask(string)
        if ret is not None:
            return ret
        if "VA" in string:
            return self._vel
        elif "AC" in string:
            return self._acc
        elif "AG" in string:
            return self._dec
        elif "TP" in string:
            return self._pos
        elif "MO" in string:
            return self._on

class LakeShore330(FakeInstr):
    def write(self, string):
        pass

    def ask(self, string):
        pass

clsDict = {
    Instruments.BaseInstr: FakeInstr,
    Instruments.ArduinoWavemeter: ArduinoWavemeter,
    Instruments.Agilent6000: Agilent6000,
    Instruments.SPEX: SPEX,
    Instruments.SR830Instr: SR830Instr,
    Instruments.Keithley236Instr: Keithley236Instr,
    Instruments.Keithley2400Instr: Keithley2400Instr,
    Instruments.ActonSP: ActonSP,
    Instruments.ESP300: ESP300,
    Instruments.LakeShore330: LakeShore330
}


def getCls(cls):
    return clsDict.get(cls.__class__, FakeInstr)


if __name__ == '__main__':

    a = Agilent6000("Fake")
    print a.__class__


        







