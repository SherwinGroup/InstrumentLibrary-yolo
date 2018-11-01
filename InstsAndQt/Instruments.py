# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 16:38:33 2015

@author: dvalovcin
"""


import numpy as np
import visa
import pyvisa.errors
import time
import logging
from ctypes import *

# from customQt import *
# import fakeInstruments.setPrintOutput



log = logging.getLogger("Instruments")
# log.setLevel(logging.DEBUG)
# handler = logging.FileHandler("TheInstrumentLog.log")
# handler.setLevel(logging.DEBUG)
# handler1 = logging.StreamHandler()
# handler1.setLevel(logging.WARN)
# formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)s()] - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# handler1.setFormatter(formatter)
# log.addHandler(handler)
# log.addHandler(handler1)


# The instrument launcher should only display the UIs, nothing more. If a widget is
# called in the UI file of another, this causes it to instantiate the whole widget,
# potentially opening devices and other issues that shouldn't arise. So widgets should
# check to make sure they are only supposed to display, do no connections
import sys
try:
    __displayonly__ = "Launcher" in sys.argv[0]
except Exception as e:
    __displayonly__ = False

class FakeResourceManager(object):
    """
    If you try to instantiate visa.resourceManager() without installing the NIVISA
    backend, it'll just error out. But if I'm debugging or something where I don't have
    or need that backend, I stil want to be able to run.
    """
    @staticmethod
    def list_resources():
        return ["a", "b", "c"]

    @staticmethod
    def open_resource(*args):
        # just error out so the code will make a fake 
        # resource on it's own
        raise visa.VisaIOError(2)

class BaseInstr(object):
    """Base class which handles opening the GPIB and safely reading/writing to the instrument"""
    def __init__(self, GPIB_Number = None, timeout = 3000):
        if GPIB_Number is None or GPIB_Number == 'Fake' or GPIB_Number == 'None':
            log.debug('Error. No GPIB assigned {}'.format(self.__class__.__name__))
            # self.instrument = FakeInstr()
            self._instrument = getCls(self)()
        else:
            try:
                rm = visa.ResourceManager()
            except ValueError:
                rm=FakeResourceManager()
            try:
                self._instrument = rm.open_resource(GPIB_Number)
                log.debug( "GOT INSTRUMENT AT {}".format(GPIB_Number))
                self._instrument.timeout = timeout
            except visa.VisaIOError:
                log.exception("Unable to open GPIB {}".format(GPIB_Number))
                self._instrument = getCls(self)()
            except Exception as e:
                log.exception('Error opening GPIB {}'.format(GPIB_Number))
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
            self._instrument.write(command)
        except pyvisa.errors.VisaIOError:
            log.warning("Error: timeout while writing {}".format(command))
        except Exception as e:
            log.exception("Error writitng command: {}".format(command))
            return False
        return True
    
    def ask(self, command, strip=1, timeout = None):
        """A function to catch reading errors. 
        strip = 1 will strip tailing \n and encode from unicode
        strip = 0 will simply encode from unicode
        strip < 0 will do nothing"""
        if timeout is not None:
            self._instrument.timeout = timeout
        ret = False
        try:
            ret = self._instrument.ask(command)
            if strip>=0:
                # python 3 changed encoding features.
                # Need to test this with various intsruments to see how to chance
                # note: "".encode("ascii") which was previously used,
                # returns a byte string.
                pass
            if strip>=1:
                ret = ret[:-1]
        except pyvisa.errors.VisaIOError:
            log.warning("Error: timeout while asking {}".format(command))
        except Exception as e:
            log.exception("Erorr asking instrument: {}".format(command))
        return ret

    def read(self):
        ret = False
        try:
            ret = self._instrument.read()
        except pyvisa.errors.VisaIOError:
            log.warning("Error: timeout while reading")
        except Exception as e:
            log.exception("Error reading")
        return ret
        
    def query(self, command, strip=1):
        """A function to catch reading errors. 
        strip = 1 will strip tailing \n and encode from unicode
        strip = 0 will simply encode from unicode
        strip < 0 will do nothing"""
        ret = None
        try:
            ret = self._instrument.query(command)
            if strip>=0:
                ... # issue with python 3 cchanginb byte strings
                # ret = ret.encode('ascii')
            if strip>=1:
                ret = ret[:-1]
        except:
            log.exception("Error querying {}".format(command))
        return ret
        
    def query_binary_values(self, command):
        ret = False
        try:
            ret = self._instrument.query_binary_values(command, datatype='b')
        except pyvisa.errors.VisaIOError:
            log.warning("Timeout occured in querying binary command {}".format(command))
            return visa.constants.VI_ERROR_TMO
        except Exception as e:
            log.exception("Error querying binary {}".format(command))
        return ret

    def query_ascii_values(self, *arg, **kwargs):
        ret = False
        try:
            ret = self._instrument.query_ascii_values(*arg, **kwargs)
        except Exception as e:
            log.exception("Error querying ascii {}".format(arg))
        return ret
        
    def close(self):
        self._instrument.close()
        try:
            self._instrument.unlock()
        except:
            pass

    def open(self):
        self._instrument.open()

class ActonSP(BaseInstr):
    backlashCorr = -6
    doCal = None
    def __init__(self, GPIB_Number=None, timeout=3000):
        super(ActonSP, self).__init__(GPIB_Number, timeout)
        try:
            time.sleep(0.5) # maybe asking too soon after communication has been established?
            self.grating = self.getGrating() # Need for calibration
            self.wavelength = self.getWavelength()
        except Exception as e:
            print("ERROR INIT:", e)
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
            print("ERROR GETTING SPECTROMETER WAVELENGTH")
            return
        return float(ret[3:-8])

    def setGrating(self, grating):
        if grating not in (1, 2, 3):
            print('Not a valid grating')
            return
        print(self.ask(str(grating)+' grating', timeout=25000))

    def getGrating(self):
        ret = self.ask('?grating')
        if not ret:
            print("ERROR GETTING SPECTROMETER GRATING\nENSURE COMMUNICATION")
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
            self._instrument.setIntegrating(val)
        except:
            #for debugging things with fake instruments. I'm sorry
            pass

    def setCD(self, val):
        try:
            self._instrument.setCD(val)
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
            print("Error, invalid channel for reading, {}".format(channel))
            return
        st = ":DIG CHAN"+str(channel)
        self.write(st)
        self.waitForComplete()

        raw = self.readChannel(channel)
        if raw is visa.constants.VI_ERROR_TMO:
            return visa.constants.VI_ERROR_TMO
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

        origTO = self._instrument.timeout
        if timeout is not None:
            self._instrument.timeout = timeout
        #Ask for operations complete
        self.ask('*OPC?')
        self._instrument.timeout = origTO

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
        self._instrument.timeout = num / 0.75 * 1.5 * 1000

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

class ArduinoWavemeter(BaseInstr):
    def __init__(self, GPIB_Number=None, timeout = 3000):
        super(ArduinoWavemeter, self).__init__(GPIB_Number, timeout)
        self._instrument.parent = self
        self._instrument.open()
        self._instrument._write_termination = '\n'
        self._instrument._read_termination = '\r\n'
        self._instrument.baud_rate = 115200
        self.exposureTime = 100 # ms

    def ask(self, command, strip=-1, timeout = None):
        return super(ArduinoWavemeter, self).ask(command, strip, timeout)

    def read_values(self, exposureTime = None):
        if exposureTime is None:
            exposureTime = self.exposureTime
        exposureTime = int(exposureTime)
        print("querying to expose for,", exposureTime)

        retVal = self.ask(str(exposureTime))
        print("arduino response:", retVal)

        time.sleep(float(exposureTime)/1000)

        # values = self.ask(str(exposureTime))
        values = self.read()

        if not values:
            return False
        try:
            return list(map(int, values.split(';')))
        except ValueError:
            # for some reason, sometimes pyvisa will not remove a
            # \n, which map tries to parse to an int, which throws
            # the value error. Just remove the problem non-numbert
            return list(map(int, values.split(';')[:-1]))

class C863(BaseInstr):
    """
    Physik Instrumente motor controller
    """
    def __init__(self, *args, **kwargs):
        super(C863, self).__init__(*args, **kwargs)
        self._instrument.baud_rate = 38400
        self._instrument._write_termination = '\n'
        self.address = 1

    def errorCheck(self):
        errcode = {}
        errcode[0]="PI_CNTR_NO_ERROR No error"
        errcode[1]="PI_CNTR_PARAM_SYNTAX Parameter syntax error"
        errcode[2]="PI_CNTR_UNKNOWN_COMMAND Unknown command"
        errcode[3]="PI_CNTR_COMMAND_TOO_LONG Command length out of imits or command buffer verrun"
        errcode[4]="PI_CNTR_SCAN_ERROR Error while scanning"
        errcode[5]="PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO Unallowable move ttempted on nreferenced axis, or ove attempted with ervo off"
        errcode[6]="PI_CNTR_INVALID_SGA_PARAM Parameter for SGA not alid"
        errcode[7]="PI_CNTR_POS_OUT_OF_LIMITS Position out of limits"
        errcode[8]="PI_CNTR_VEL_OUT_OF_LIMITS Velocity out of limits"
        errcode[9]="PI_CNTR_SET_PIVOT_NOT_POSSIBLE Attempt to set pivot point hile U,V and W not all 0"
        errcode[10]="PI_CNTR_STOP Controller was stopped y command"
        errcode[11]="PI_CNTR_SST_OR_SCAN_RANGE Parameter for SST or for ne of the embedded can algorithms out of ange"
        errcode[12]="PI_CNTR_INVALID_SCAN_AXES Invalid axis combination or fast scan"
        errcode[13]="PI_CNTR_INVALID_NAV_PARAM Parameter for NAV out of ange"
        errcode[14]="PI_CNTR_INVALID_ANALOG_INPUT Invalid analog channel"
        errcode[15]="PI_CNTR_INVALID_AXIS_IDENTIFIER Invalid axis identifier"
        errcode[16]="PI_CNTR_INVALID_STAGE_NAME Unknown stage name"
        errcode[17]="PI_CNTR_PARAM_OUT_OF_RANGE Parameter out of range"
        errcode[18]="PI_CNTR_INVALID_MACRO_NAME Invalid macro name ww.pi.ws C-663 MS208E Release 1.0.0 Page 162GCS Commands"
        errcode[19]="PI_CNTR_MACRO_RECORD Error while recording acro"
        errcode[20]="PI_CNTR_MACRO_NOT_FOUND Macro not found"
        errcode[21]="PI_CNTR_AXIS_HAS_NO_BRAKE Axis has no brake"
        errcode[22]="PI_CNTR_DOUBLE_AXIS Axis identifier specified ore than once"
        errcode[23]="PI_CNTR_ILLEGAL_AXIS Illegal axis"
        errcode[24]="PI_CNTR_PARAM_NR Incorrect number of arameters"
        errcode[25]="PI_CNTR_INVALID_REAL_NR Invalid floating point umber"
        errcode[26]="PI_CNTR_MISSING_PARAM Parameter missing"
        errcode[27]="PI_CNTR_SOFT_LIMIT_OUT_OF_RANGE Soft limit out of range"
        errcode[28]="PI_CNTR_NO_MANUAL_PAD No manual pad found"
        errcode[29]="PI_CNTR_NO_JUMP No more step-response alues"
        errcode[30]="PI_CNTR_INVALID_JUMP No step-response values ecorded"
        errcode[31]="PI_CNTR_AXIS_HAS_NO_REFERENCE Axis has no reference ensor"
        errcode[32]="PI_CNTR_STAGE_HAS_NO_LIM_SWITCH Axis has no limit switch"
        errcode[33]="PI_CNTR_NO_RELAY_CARD No relay card installed"
        errcode[34]="PI_CNTR_CMD_NOT_ALLOWED_FOR_STAGE Command not allowed or selected stage(s)"
        errcode[35]="PI_CNTR_NO_DIGITAL_INPUT No digital input installed"
        errcode[36]="PI_CNTR_NO_DIGITAL_OUTPUT No digital output onfigured"
        errcode[37]="PI_CNTR_NO_MCM No more MCM esponses"
        errcode[38]="PI_CNTR_INVALID_MCM No MCM values ecorded"
        errcode[39]="PI_CNTR_INVALID_CNTR_NUMBER Controller number invalid"
        errcode[40]="PI_CNTR_NO_JOYSTICK_CONNECTED No joystick configured"
        errcode[41]="PI_CNTR_INVALID_EGE_AXIS Invalid axis for electronic earing, axis can not be lave"
        errcode[42]="PI_CNTR_SLAVE_POSITION_OUT_OF_RANGE Position of slave axis is ut of range"
        errcode[43]="PI_CNTR_COMMAND_EGE_SLAVE Slave axis cannot be ommanded directly hen electronic gearing s enabled ww.pi.ws C-663 MS208E Release 1.0.0 Page 163GCS Commands"
        errcode[44]="PI_CNTR_JOYSTICK_CALIBRATION_FAILED Calibration of joystick ailed"
        errcode[45]="PI_CNTR_REFERENCING_FAILED Referencing failed"
        errcode[46]="PI_CNTR_OPM_MISSING OPM (Optical Power eter) missing"
        errcode[47]="PI_CNTR_OPM_NOT_INITIALIZED OPM (Optical Power eter) not initialized or annot be initialized"
        errcode[48]="PI_CNTR_OPM_COM_ERROR OPM (Optical Power eter) Communication rror"
        errcode[49]="PI_CNTR_MOVE_TO_LIMIT_SWITCH_FAILED Move to limit switch ailed"
        errcode[50]="PI_CNTR_REF_WITH_REF_DISABLED Attempt to reference axis ith referencing disabled"
        errcode[51]="PI_CNTR_AXIS_UNDER_JOYSTICK_CONTROL Selected axis is ontrolled by joystick"
        errcode[52]="PI_CNTR_COMMUNICATION_ERROR Controller detected ommunication error"
        errcode[53]="PI_CNTR_DYNAMIC_MOVE_IN_PROCESS MOV! motion still in rogress"
        errcode[54]="PI_CNTR_UNKNOWN_PARAMETER Unknown parameter"
        errcode[55]="PI_CNTR_NO_REP_RECORDED No commands were ecorded with REP"
        errcode[56]="PI_CNTR_INVALID_PASSWORD Password invalid"
        errcode[57]="PI_CNTR_INVALID_RECORDER_CHAN Data Record Table does ot exist"
        errcode[58]="PI_CNTR_INVALID_RECORDER_SRC_OPT Source does not exist; umber too low or too igh"
        errcode[59]="PI_CNTR_INVALID_RECORDER_SRC_CHAN Source Record Table umber too low or too igh"
        errcode[60]="PI_CNTR_PARAM_PROTECTION Protected Param: current ommand Level (CCL) oo low"
        errcode[61]="PI_CNTR_AUTOZERO_RUNNING Command execution not ossible while Autozero s running"
        errcode[62]="PI_CNTR_NO_LINEAR_AXIS Autozero requires at east one linear axis"
        errcode[63]="PI_CNTR_INIT_RUNNING Initialization still in rogress"
        errcode[64]="PI_CNTR_READ_ONLY_PARAMETER Parameter is read-only ww.pi.ws C-663 MS208E Release 1.0.0 Page 164GCS Commands"
        errcode[65]="PI_CNTR_PAM_NOT_FOUND Parameter not found in on-volatile memory"
        errcode[66]="PI_CNTR_VOL_OUT_OF_LIMITS Voltage out of limits"
        errcode[67]="PI_CNTR_WAVE_TOO_LARGE Not enough memory vailable for requested ave curve"
        errcode[68]="PI_CNTR_NOT_ENOUGH_DDL_MEMORY Not enough memory vailable for DDL table; DL can not be started"
        errcode[69]="PI_CNTR_DDL_TIME_DELAY_TOO_LARGE Time delay larger than DL table; DDL can not e started"
        errcode[70]="PI_CNTR_DIFFERENT_ARRAY_LENGTH The requested arrays ave different lengths; uery them separately"
        errcode[71]="PI_CNTR_GEN_SINGLE_MODE_RESTART Attempt to restart the enerator while it is unning in single step ode"
        errcode[72]="PI_CNTR_ANALOG_TARGET_ACTIVE Motion commands and ave generator ctivation are not allowed hen analog target is ctive"
        errcode[73]="PI_CNTR_WAVE_GENERATOR_ACTIVE Motion commands are ot allowed when wave enerator output is ctive; use WGO to isable generator output"
        errcode[74]="PI_CNTR_AUTOZERO_DISABLED No sensor channel or no iezo channel connected o selected axis (sensor nd piezo matrix)"
        errcode[75]="PI_CNTR_NO_WAVE_SELECTED Generator started (WGO) ithout having selected a ave table (WSL)."
        errcode[76]="PI_CNTR_IF_BUFFER_OVERRUN Interface buffer did verrun and command ouldn't be received orrectly"
        errcode[77]="PI_CNTR_NOT_ENOUGH_RECORDED_DATA Data Record Table does ot hold enough ecorded data"
        errcode[78]="PI_CNTR_TABLE_DEACTIVATED Data Record Table is not onfigured for recording ww.pi.ws C-663 MS208E Release 1.0.0 Page 165GCS Commands"
        errcode[79]="PI_CNTR_OPENLOOP_VALUE_SET_WHEN_SERVO_ON Open-loop commands SVA, SVR) are not llowed when servo is on"
        errcode[80]="PI_CNTR_RAM_ERROR Hardware error affecting AM"
        errcode[81]="PI_CNTR_MACRO_UNKNOWN_COMMAND Not macro command"
        errcode[82]="PI_CNTR_MACRO_PC_ERROR Macro counter out of ange"
        errcode[83]="PI_CNTR_JOYSTICK_ACTIVE Joystick is active"
        errcode[84]="PI_CNTR_MOTOR_IS_OFF Motor is off"
        errcode[85]="PI_CNTR_ONLY_IN_MACRO Macro-only command"
        errcode[86]="PI_CNTR_JOYSTICK_UNKNOWN_AXIS Invalid joystick axis"
        errcode[87]="PI_CNTR_JOYSTICK_UNKNOWN_ID Joystick unknown"
        errcode[88]="PI_CNTR_REF_MODE_IS_ON Move without referenced tage"
        errcode[89]="PI_CNTR_NOT_ALLOWED_IN_CURRENT_MOTION_MODE Command not allowed in urrent motion mode"
        errcode[90]="PI_CNTR_DIO_AND_TRACING_NOT_POSSIBLE No tracing possible while igital IOs are used on his HW revision. econnect to switch peration mode."
        errcode[91]="PI_CNTR_COLLISION Move not possible, would ause collision"
        errcode[92]="PI_CNTR_SLAVE_NOT_FAST_ENOUGH Stage is not capable of ollowing the master. heck the gear atio(SRA)."
        errcode[93]="PI_CNTR_CMD_NOT_ALLOWED_WHILE_AXIS_IN_MOTION This command is not llowed while the ffected axis or its aster is in motion."
        errcode[100]="PI_LABVIEW_ERROR PI LabVIEW driver eports error. See source ontrol for details."
        errcode[200]="PI_CNTR_NO_AXIS No stage connected to xis"
        errcode[201]="PI_CNTR_NO_AXIS_PARAM_FILE File with axis parameters ot found"
        errcode[202]="PI_CNTR_INVALID_AXIS_PARAM_FILE Invalid axis parameter ile"
        errcode[203]="PI_CNTR_NO_AXIS_PARAM_BACKUP Backup file with axis arameters not found"
        errcode[204]="PI_CNTR_RESERVED_204 PI internal error code 204 ww.pi.ws C-663 MS208E Release 1.0.0 Page 166GCS Commands"
        errcode[205]="PI_CNTR_SMO_WITH_SERVO_ON SMO with servo on"
        errcode[206]="PI_CNTR_UUDECODE_INCOMPLETE_HEADER uudecode: incomplete eader"
        errcode[207]="PI_CNTR_UUDECODE_NOTHING_TO_DECODE uudecode: nothing to ecode"
        errcode[208]="PI_CNTR_UUDECODE_ILLEGAL_FORMAT uudecode: illegal UUE ormat"
        errcode[209]="PI_CNTR_CRC32_ERROR CRC32 error"
        errcode[210]="PI_CNTR_ILLEGAL_FILENAME Illegal file name (must be errcode[8-0]=format"
        errcode[211]="PI_CNTR_FILE_NOT_FOUND File not found on ontroller"
        errcode[212]="PI_CNTR_FILE_WRITE_ERROR Error writing file on ontroller"
        errcode[213]="PI_CNTR_DTR_HINDERS_VELOCITY_CHANGE VEL command not llowed in DTR ommand Mode"
        errcode[214]="PI_CNTR_POSITION_UNKNOWN Position calculations ailed"
        errcode[215]="PI_CNTR_CONN_POSSIBLY_BROKEN The connection between ontroller and stage may e broken"
        errcode[216]="PI_CNTR_ON_LIMIT_SWITCH The connected stage has riven into a limit switch, ome controllers need LR to resume operation"
        errcode[217]="PI_CNTR_UNEXPECTED_STRUT_STOP Strut test command ailed because of an nexpected strut stop"
        errcode[218]="PI_CNTR_POSITION_BASED_ON_ESTIMATION While MOV! is running osition can only be stimated!"
        errcode[219]="PI_CNTR_POSITION_BASED_ON_INTERPOLATION Position was calculated uring MOV motion"
        errcode[230]="PI_CNTR_INVALID_HANDLE Invalid handle"
        errcode[231]="PI_CNTR_NO_BIOS_FOUND No bios found"
        errcode[232]="PI_CNTR_SAVE_SYS_CFG_FAILED Save system onfiguration failed"
        errcode[233]="PI_CNTR_LOAD_SYS_CFG_FAILED Load system onfiguration failed"
        errcode[301]="PI_CNTR_SEND_BUFFER_OVERFLOW Send buffer overflow"
        errcode[302]="PI_CNTR_VOLTAGE_OUT_OF_LIMITS Voltage out of limits ww.pi.ws C-663 MS208E Release 1.0.0 Page 167GCS Commands"
        errcode[303]="PI_CNTR_OPEN_LOOP_MOTION_SET_WHEN_SERVO_ON Open-loop motion ttempted when servo N"
        errcode[304]="PI_CNTR_RECEIVING_BUFFER_OVERFLOW Received command is oo long"
        errcode[305]="PI_CNTR_EEPROM_ERROR Error while eading/writing EEPROM"
        errcode[306]="PI_CNTR_I2C_ERROR Error on I2C bus"
        errcode[307]="PI_CNTR_RECEIVING_TIMEOUT Timeout while receiving ommand"
        errcode[308]="PI_CNTR_TIMEOUT A lengthy operation has ot finished in the xpected time"
        errcode[309]="PI_CNTR_MACRO_OUT_OF_SPACE Insufficient space to tore macro"
        errcode[310]="PI_CNTR_EUI_OLDVERSION_CFGDATA Configuration data has ld version number"
        errcode[311]="PI_CNTR_EUI_INVALID_CFGDATA Invalid configuration data"
        errcode[333]="PI_CNTR_HARDWARE_ERROR Internal hardware error"
        errcode[400]="PI_CNTR_WAV_INDEX_ERROR Wave generator index rror"
        errcode[401]="PI_CNTR_WAV_NOT_DEFINED Wave table not defined"
        errcode[402]="PI_CNTR_WAV_TYPE_NOT_SUPPORTED Wave type not supported"
        errcode[403]="PI_CNTR_WAV_LENGTH_EXCEEDS_LIMIT Wave length exceeds imit"
        errcode[404]="PI_CNTR_WAV_PARAMETER_NR Wave parameter number rror"
        errcode[405]="PI_CNTR_WAV_PARAMETER_OUT_OF_LIMIT Wave parameter out of ange"
        errcode[406]="PI_CNTR_WGO_BIT_NOT_SUPPORTED WGO command bit not upported"
        errcode[500]="PI_CNTR_EMERGENCY_STOP_BUTTON_ACTIVATED The \"red knob\" is still et and disables system"
        errcode[501]="PI_CNTR_EMERGENCY_STOP_BUTTON_WAS_ACTIVATED The \"red knob\" was ctivated and still isables system - eanimation required"
        errcode[502]="PI_CNTR_REDUNDANCY_LIMIT_EXCEEDED Position consistency heck failed"
        errcode[503]="PI_CNTR_COLLISION_SWITCH_ACTIVATED Hardware collision ensor(s) are activated ww.pi.ws C-663 MS208E Release 1.0.0 Page 168GCS Commands"
        errcode[504]="PI_CNTR_FOLLOWING_ERROR Strut following error ccurred, e.g. caused by verload or encoder ailure"
        errcode[555]="PI_CNTR_UNKNOWN_ERROR BasMac: unknown ontroller error"
        errcode[601]="PI_CNTR_NOT_ENOUGH_MEMORY Not enough memory"
        errcode[602]="PI_CNTR_HW_VOLTAGE_ERROR Hardware voltage error"
        errcode[603]="PI_CNTR_HW_TEMPERATURE_ERROR Hardware temperature ut of range"
        errcode[1000]="PI_CNTR_TOO_MANY_NESTED_MACROS Too many nested macros"
        errcode[1001]="PI_CNTR_MACRO_ALREADY_DEFINED Macro already defined"
        errcode[1002]="PI_CNTR_NO_MACRO_RECORDING Macro recording not ctivated"
        errcode[1003]="PI_CNTR_INVALID_MAC_PARAM Invalid parameter for AC"
        errcode[1004]="PI_CNTR_MACRO_DELETE_ERROR Deleting macro failed"
        errcode[1005]="PI_CNTR_CONTROLLER_BUSY Controller is busy with ome lengthy operation e.g. reference move, ast scan algorithm)"
        errcode[1006]="PI_CNTR_INVALID_IDENTIFIER Invalid identifier (invalid pecial characters, ...)"
        errcode[1007]="PI_CNTR_UNKNOWN_VARIABLE_OR_ARGUMENT Variable or argument not efined"
        errcode[1008]="PI_CNTR_RUNNING_MACRO Controller is (already) unning a macro"
        errcode[1009]="PI_CNTR_MACRO_INVALID_OPERATOR Invalid or missing perator for condition. heck necessary spaces round operator."
        errcode[1063]="PI_CNTR_EXT_PROFILE_UNALLOWED_CMD User Profile Mode: ommand is not allowed, heck for required reparatory commands"
        errcode[1064]="PI_CNTR_EXT_PROFILE_EXPECTING_MOTION_ERROR User Profile Mode: First arget position in User rofile is too far from urrent position"
        errcode[1065]="PI_CNTR_PROFILE_ACTIVE Controller is (already) in ser Profile Mode"
        errcode[1066]="PI_CNTR_PROFILE_INDEX_OUT_OF_RANGE User Profile Mode: Block r Data Set index out of llowed range ww.pi.ws C-663 MS208E Release 1.0.0 Page 169GCS Commands"
        errcode[1071]="PI_CNTR_PROFILE_OUT_OF_MEMORY User Profile Mode: Out of emory"
        errcode[1072]="PI_CNTR_PROFILE_WRONG_CLUSTER User Profile Mode: luster is not assigned to his axis"
        errcode[1073]="PI_CNTR_PROFILE_UNKNOWN_CLUSTER_IDENTIFIER Unknown cluster dentifier"
        errcode[2000]="PI_CNTR_ALREADY_HAS_SERIAL_NUMBER Controller already has a erial number"
        errcode[4000]="PI_CNTR_SECTOR_ERASE_FAILED Sector erase failed"
        errcode[4001]="PI_CNTR_FLASH_PROGRAM_FAILED Flash program failed"
        errcode[4002]="PI_CNTR_FLASH_READ_FAILED Flash read failed"
        errcode[4003]="PI_CNTR_HW_MATCHCODE_ERROR HW match code issing/invalid"
        errcode[4004]="PI_CNTR_FW_MATCHCODE_ERROR FW match code issing/invalid"
        errcode[4005]="PI_CNTR_HW_VERSION_ERROR HW version issing/invalid"
        errcode[4006]="PI_CNTR_FW_VERSION_ERROR FW version issing/invalid"
        errcode[4007]="PI_CNTR_FW_UPDATE_ERROR FW update failed"
        errcode[4008]="PI_CNTR_FW_CRC_PAR_ERROR FW Parameter CRC rong"
        errcode[4009]="PI_CNTR_FW_CRC_FW_ERROR FW CRC wrong"
        errcode[5000]="PI_CNTR_INVALID_PCC_SCAN_DATA PicoCompensation scan ata is not valid"
        errcode[5001]="PI_CNTR_PCC_SCAN_RUNNING PicoCompensation is unning, some actions an not be executed uring canning/recording"
        errcode[5002]="PI_CNTR_INVALID_PCC_AXIS Given axis can not be efined as PPC axis"
        errcode[5003]="PI_CNTR_PCC_SCAN_OUT_OF_RANGE Defined scan area is arger than the travel ange"
        errcode[5004]="PI_CNTR_PCC_TYPE_NOT_EXISTING Given PicoCompensation ype is not defined"
        errcode[5005]="PI_CNTR_PCC_PAM_ERROR PicoCompensation arameter error"
        errcode[5006]="PI_CNTR_PCC_TABLE_ARRAY_TOO_LARGE PicoCompensation table s larger than maximum able length ww.pi.ws C-663 MS208E Release 1.0.0 Page 170GCS Commands"
        errcode[5100]="PI_CNTR_NEXLINE_ERROR Common error in Nexline irmware module"
        errcode[5101]="PI_CNTR_CHANNEL_ALREADY_USED Output channel for exline can not be edefined for other usage"
        errcode[5102]="PI_CNTR_NEXLINE_TABLE_TOO_SMALL Memory for Nexline ignals is too small"
        errcode[5103]="PI_CNTR_RNP_WITH_SERVO_ON RNP can not be xecuted if axis is in losed loop"
        errcode[5104]="PI_CNTR_RNP_NEEDED Relax procedure (RNP) eeded"
        errcode[5200]="PI_CNTR_AXIS_NOT_CONFIGURED Axis must be configured or this action nterface Errors"
        errcode[0]="COM_NO_ERROR No error occurred during unction call"
        errcode[-1]="COM_ERROR Error during com peration (could not be pecified)"
        errcode[-2]="SEND_ERROR Error while sending data"
        errcode[-3]="REC_ERROR Error while receiving data"
        errcode[-4]="NOT_CONNECTED_ERROR Not connected (no port ith given ID open)"
        errcode[-5]="COM_BUFFER_OVERFLOW Buffer overflow"
        errcode[-6]="CONNECTION_FAILED Error while opening port"
        errcode[-7]="COM_TIMEOUT Timeout error"
        errcode[-8]="COM_MULTILINE_RESPONSE There are more lines aiting in buffer"
        errcode[-9]="COM_INVALID_ID There is no interface or LL handle with the iven ID"
        errcode[-10]="COM_NOTIFY_EVENT_ERROR Event/message for otification could not be pened"
        errcode[-11]="COM_NOT_IMPLEMENTED Function not supported y this interface type"
        errcode[-12]="COM_ECHO_ERROR Error while sending echoed data"
        errcode[-13]="COM_GPIB_EDVR IEEE488: System error ww.pi.ws C-663 MS208E Release 1.0.0 Page 171GCS Commands"
        errcode[-14]="COM_GPIB_ECIC IEEE488: Function equires GPIB board to e CIC"
        errcode[-15]="COM_GPIB_ENOL IEEE488: Write function etected no listeners"
        errcode[-16]="COM_GPIB_EADR IEEE488: Interface board ot addressed correctly"
        errcode[-17]="COM_GPIB_EARG IEEE488: Invalid rgument to function call"
        errcode[-18]="COM_GPIB_ESAC IEEE488: Function equires GPIB board to e SAC"
        errcode[-19]="COM_GPIB_EABO IEEE488: I/O operation borted"
        errcode[-20]="COM_GPIB_ENEB IEEE488: Interface board ot found"
        errcode[-21]="COM_GPIB_EDMA IEEE488: Error erforming DMA"
        errcode[-22]="COM_GPIB_EOIP IEEE488: I/O operation tarted before previous peration completed"
        errcode[-23]="COM_GPIB_ECAP IEEE488: No capability or intended operation"
        errcode[-24]="COM_GPIB_EFSO IEEE488: File system peration error"
        errcode[-25]="COM_GPIB_EBUS IEEE488: Command rror during device call"
        errcode[-26]="COM_GPIB_ESTB IEEE488: Serial pollstatus byte lost"
        errcode[-27]="COM_GPIB_ESRQ IEEE488: SRQ remains sserted"
        errcode[-28]="COM_GPIB_ETAB IEEE488: Return buffer ull"
        errcode[-29]="COM_GPIB_ELCK IEEE488: Address or oard locked"
        errcode[-30]="COM_RS_INVALID_DATA_BITS RS-232: 5 data bits with 2 stop bits is an invalid ombination, as is 6, 7, or 8 data bits with 1.5 stop its"
        errcode[-31]="COM_ERROR_RS_SETTINGS RS-232: Error configuring he COM port"
        errcode[-32]="COM_INTERNAL_RESOURCES_ERROR Error dealing with internal ystem resources events, threads, ...) ww.pi.ws C-663 MS208E Release 1.0.0 Page 172GCS Commands"
        errcode[-33]="COM_DLL_FUNC_ERROR A DLL or one of the equired functions could ot be loaded"
        errcode[-34]="COM_FTDIUSB_INVALID_HANDLE FTDIUSB: invalid handle"
        errcode[-35]="COM_FTDIUSB_DEVICE_NOT_FOUND FTDIUSB: device not ound"
        errcode[-36]="COM_FTDIUSB_DEVICE_NOT_OPENED FTDIUSB: device not pened"
        errcode[-37]="COM_FTDIUSB_IO_ERROR FTDIUSB: IO error"
        errcode[-38]="COM_FTDIUSB_INSUFFICIENT_RESOURCES FTDIUSB: insufficient esources"
        errcode[-39]="COM_FTDIUSB_INVALID_PARAMETER FTDIUSB: invalid arameter"
        errcode[-40]="COM_FTDIUSB_INVALID_BAUD_RATE FTDIUSB: invalid baud ate"
        errcode[-41]="COM_FTDIUSB_DEVICE_NOT_OPENED_FOR_ERASE FTDIUSB: device not pened for erase"
        errcode[-42]="COM_FTDIUSB_DEVICE_NOT_OPENED_FOR_WRITE FTDIUSB: device not pened for write"
        errcode[-43]="COM_FTDIUSB_FAILED_TO_WRITE_DEVICE FTDIUSB: failed to write evice"
        errcode[-44]="COM_FTDIUSB_EEPROM_READ_FAILED FTDIUSB: EEPROM ead failed"
        errcode[-45]="COM_FTDIUSB_EEPROM_WRITE_FAILED FTDIUSB: EEPROM rite failed"
        errcode[-46]="COM_FTDIUSB_EEPROM_ERASE_FAILED FTDIUSB: EEPROM rase failed"
        errcode[-47]="COM_FTDIUSB_EEPROM_NOT_PRESENT FTDIUSB: EEPROM not resent"
        errcode[-48]="COM_FTDIUSB_EEPROM_NOT_PROGRAMMED FTDIUSB: EEPROM not rogrammed"
        errcode[-49]="COM_FTDIUSB_INVALID_ARGS FTDIUSB: invalid rguments"
        errcode[-50]="COM_FTDIUSB_NOT_SUPPORTED FTDIUSB: not supported"
        errcode[-51]="COM_FTDIUSB_OTHER_ERROR FTDIUSB: other error"
        errcode[-52]="COM_PORT_ALREADY_OPEN Error while opening the OM port: was already pen"
        errcode[-53]="COM_PORT_CHECKSUM_ERROR Checksum error in eceived data from COM ort ww.pi.ws C-663 MS208E Release 1.0.0 Page 173GCS Commands"
        errcode[-54]="COM_SOCKET_NOT_READY Socket not ready, you hould call the function gain"
        errcode[-55]="COM_SOCKET_PORT_IN_USE Port is used by another ocket"
        errcode[-56]="COM_SOCKET_NOT_CONNECTED Socket not connected (or ot valid)"
        errcode[-57]="COM_SOCKET_TERMINATED Connection terminated by peer)"
        errcode[-58]="COM_SOCKET_NO_RESPONSE Can't connect to peer"
        errcode[-59]="COM_SOCKET_INTERRUPTED Operation was nterrupted by a onblocked signal"
        errcode[-60]="COM_PCI_INVALID_ID No Device with this ID is resent"
        errcode[-61]="COM_PCI_ACCESS_DENIED Driver could not be pened (on Vista: run as dministrator!) LL Errors"
        errcode[-1001]="PI_UNKNOWN_AXIS_IDENTIFIER Unknown axis identifier"
        errcode[-1002]="PI_NR_NAV_OUT_OF_RANGE Number for NAV out of ange--must be in 1,10000]"
        errcode[-1003]="PI_INVALID_SGA Invalid value for SGA-- ust be one of {1, 10,100, 1000}"
        errcode[-1004]="PI_UNEXPECTED_RESPONSE Controller sent nexpected response"
        errcode[-1005]="PI_NO_MANUAL_PAD No manual control pad nstalled, calls to SMA nd related commands re not allowed"
        errcode[-1006]="PI_INVALID_MANUAL_PAD_KNOB Invalid number for anual control pad knob"
        errcode[-1007]="PI_INVALID_MANUAL_PAD_AXIS Axis not currently ontrolled by a manual ontrol pad"
        errcode[-1008]="PI_CONTROLLER_BUSY Controller is busy with ome lengthy operation e.g. reference move, fast can algorithm) ww.pi.ws C-663 MS208E Release 1.0.0 Page 174GCS Commands"
        errcode[-1009]="PI_THREAD_ERROR Internal error--could not tart thread"
        errcode[-1010]="PI_IN_MACRO_MODE Controller is (already) in acro mode--command ot valid in macro mode"
        errcode[-1011]="PI_NOT_IN_MACRO_MODE Controller not in macro ode--command not alid unless macro mode ctive"
        errcode[-1012]="PI_MACRO_FILE_ERROR Could not open file to rite or read macro"
        errcode[-1013]="PI_NO_MACRO_OR_EMPTY No macro with given ame on controller, or acro is empty"
        errcode[-1014]="PI_MACRO_EDITOR_ERROR Internal error in macro ditor"
        errcode[-1015]="PI_INVALID_ARGUMENT One or more arguments iven to function is invalid empty string, index out f range, ...)"
        errcode[-1016]="PI_AXIS_ALREADY_EXISTS Axis identifier is already n use by a connected tage"
        errcode[-1017]="PI_INVALID_AXIS_IDENTIFIER Invalid axis identifier"
        errcode[-1018]="PI_COM_ARRAY_ERROR Could not access array ata in COM server"
        errcode[-1019]="PI_COM_ARRAY_RANGE_ERROR Range of array does not it the number of arameters"
        errcode[-1020]="PI_INVALID_SPA_CMD_ID Invalid parameter ID iven to SPA or SPA?"
        errcode[-1021]="PI_NR_AVG_OUT_OF_RANGE Number for AVG out of ange--must be >0"
        errcode[-1022]="PI_WAV_SAMPLES_OUT_OF_RANGE Incorrect number of amples given to WAV"
        errcode[-1023]="PI_WAV_FAILED Generation of wave failed"
        errcode[-1024]="PI_MOTION_ERROR Motion error: position rror too large, servo is witched off automatically"
        errcode[-1025]="PI_RUNNING_MACRO Controller is (already) unning a macro"
        errcode[-1026]="PI_PZT_CONFIG_FAILED Configuration of PZT tage or amplifier failed ww.pi.ws C-663 MS208E Release 1.0.0 Page 175GCS Commands"
        errcode[-1027]="PI_PZT_CONFIG_INVALID_PARAMS Current settings are not alid for desired onfiguration"
        errcode[-1028]="PI_UNKNOWN_CHANNEL_IDENTIFIER Unknown channel dentifier"
        errcode[-1029]="PI_WAVE_PARAM_FILE_ERROR Error while eading/writing wave enerator parameter file"
        errcode[-1030]="PI_UNKNOWN_WAVE_SET Could not find description f wave form. Maybe G.INI is missing?"
        errcode[-1031]="PI_WAVE_EDITOR_FUNC_NOT_LOADED The WGWaveEditor DLL unction was not found at tartup"
        errcode[-1032]="PI_USER_CANCELLED The user cancelled a ialog"
        errcode[-1033]="PI_C844_ERROR Error from C-844 ontroller"
        errcode[-1034]="PI_DLL_NOT_LOADED DLL necessary to call unction not loaded, or unction not found in DLL"
        errcode[-1035]="PI_PARAMETER_FILE_PROTECTED The open parameter file s protected and cannot e edited"
        errcode[-1036]="PI_NO_PARAMETER_FILE_OPENED There is no parameter file pen"
        errcode[-1037]="PI_STAGE_DOES_NOT_EXIST Selected stage does not xist"
        errcode[-1038]="PI_PARAMETER_FILE_ALREADY_OPENED There is already a arameter file open. lose it before opening a ew file"
        errcode[-1039]="PI_PARAMETER_FILE_OPEN_ERROR Could not open arameter file"
        errcode[-1040]="PI_INVALID_CONTROLLER_VERSION The version of the onnected controller is nvalid"
        errcode[-1041]="PI_PARAM_SET_ERROR Parameter could not be et with SPA--parameter ot defined for this ontroller!"
        errcode[-1042]="PI_NUMBER_OF_POSSIBLE_WAVES_EXCEEDED The maximum number of ave definitions has een exceeded ww.pi.ws C-663 MS208E Release 1.0.0 Page 176GCS Commands"
        errcode[-1043]="PI_NUMBER_OF_POSSIBLE_GENERATORS_EXCEEDED The maximum number of ave generators has een exceeded"
        errcode[-1044]="PI_NO_WAVE_FOR_AXIS_DEFINED No wave defined for pecified axis"
        errcode[-1045]="PI_CANT_STOP_OR_START_WAV Wave output to axis lready stopped/started"
        errcode[-1046]="PI_REFERENCE_ERROR Not all axes could be eferenced"
        errcode[-1047]="PI_REQUIRED_WAVE_NOT_FOUND Could not find parameter et required by frequency elation"
        errcode[-1048]="PI_INVALID_SPP_CMD_ID Command ID given to PP or SPP? is not valid"
        errcode[-1049]="PI_STAGE_NAME_ISNT_UNIQUE A stage name given to ST is not unique"
        errcode[-1050]="PI_FILE_TRANSFER_BEGIN_MISSING A uuencoded file ransfered did not start ith \"begin\" followed by he proper filename"
        errcode[-1051]="PI_FILE_TRANSFER_ERROR_TEMP_FILE Could not create/read file n host PC"
        errcode[-1052]="PI_FILE_TRANSFER_CRC_ERROR Checksum error when ransfering a file to/from he controller"
        errcode[-1053]="PI_COULDNT_FIND_PISTAGES_DAT The PiStages.dat atabase could not be ound. This file is equired to connect a tage with the CST ommand"
        errcode[-1054]="PI_NO_WAVE_RUNNING No wave being output to pecified axis"
        errcode[-1055]="PI_INVALID_PASSWORD Invalid password"
        errcode[-1056]="PI_OPM_COM_ERROR Error during ommunication with OPM Optical Power Meter), aybe no OPM onnected"
        errcode[-1057]="PI_WAVE_EDITOR_WRONG_PARAMNUM WaveEditor: Error during ave creation, incorrect umber of parameters"
        errcode[-1058]="PI_WAVE_EDITOR_FREQUENCY_OUT_OF_RANGE WaveEditor: Frequency ut of range ww.pi.ws C-663 MS208E Release 1.0.0 Page 177GCS Commands"
        errcode[-1059]="PI_WAVE_EDITOR_WRONG_IP_VALUE WaveEditor: Error during ave creation, incorrect ndex for integer arameter"
        errcode[-1060]="PI_WAVE_EDITOR_WRONG_DP_VALUE WaveEditor: Error during ave creation, incorrect ndex for floating point arameter"
        errcode[-1061]="PI_WAVE_EDITOR_WRONG_ITEM_VALUE WaveEditor: Error during ave creation, could not alculate value"
        errcode[-1062]="PI_WAVE_EDITOR_MISSING_GRAPH_COMPONENT WaveEditor: Graph isplay component not nstalled"
        errcode[-1063]="PI_EXT_PROFILE_UNALLOWED_CMD User Profile Mode: ommand is not allowed, heck for required reparatory commands"
        errcode[-1064]="PI_EXT_PROFILE_EXPECTING_MOTION_ERROR User Profile Mode: First arget position in User rofile is too far from urrent position"
        errcode[-1065]="PI_EXT_PROFILE_ACTIVE Controller is (already) in ser Profile Mode"
        errcode[-1066]="PI_EXT_PROFILE_INDEX_OUT_OF_RANGE User Profile Mode: Block r Data Set index out of llowed range"
        errcode[-1067]="PI_PROFILE_GENERATOR_NO_PROFILE ProfileGenerator: No rofile has been created et"
        errcode[-1068]="PI_PROFILE_GENERATOR_OUT_OF_LIMITS ProfileGenerator: enerated profile xceeds limits of one or oth axes"
        errcode[-1069]="PI_PROFILE_GENERATOR_UNKNOWN_PARAMETER ProfileGenerator: nknown parameter ID in et/Get Parameter ommand"
        errcode[-1070]="PI_PROFILE_GENERATOR_PAR_OUT_OF_RANGE ProfileGenerator: arameter out of allowed ange"
        errcode[-1071]="PI_EXT_PROFILE_OUT_OF_MEMORY User Profile Mode: Out of emory"
        errcode[-1072]="PI_EXT_PROFILE_WRONG_CLUSTER User Profile Mode: luster is not assigned to his axis ww.pi.ws C-663 MS208E Release 1.0.0 Page 178GCS Commands ww.pi.ws C-663 MS208E Release 1.0.0 Page 179"
        errcode[-1073]="PI_EXT_PROFILE_UNKNOWN_CLUSTER_IDENTIFIER Unknown cluster dentifier"
        errcode[-1074]="PI_INVALID_DEVICE_DRIVER_VERSION The installed device river doesn't match the equired version. Please ee the documentation to etermine the required evice driver version."
        errcode[-1075]="PI_INVALID_LIBRARY_VERSION The library used doesn't atch the required ersion. Please see the ocumentation to etermine the required ibrary version."
        errcode[-1076]="PI_INTERFACE_LOCKED The interface is currently ocked by another unction. Please try again ater."
        errcode[-1077]="PI_PARAM_DAT_FILE_INVALID_VERSION Version of parameter AT file does not match he required version. urrent files are available t www.pi.ws."
        errcode[-1078]="PI_CANNOT_WRITE_TO_PARAM_DAT_FILE Cannot write to arameter DAT file to tore user defined stage ype."
        errcode[-1079]="PI_CANNOT_CREATE_PARAM_DAT_FILE Cannot create parameter AT file to store user efined stage type."
        errcode[-1080]="PI_PARAM_DAT_FILE_INVALID_REVISION Parameter DAT file does ot have correct revision."
        errcode[-1081]="PI_USERSTAGES_DAT_FILE_INVALID_REVISION User stages DAT file oes not have correct evisio"

        retcode = int(self.query("ERR?"))
        return retcode, errcode.get(retcode, "Unknown Code")

    def move(self, pos, waitForStop = True, *args, **kwargs):
        self.write("MOV {} {}".format(self.address, pos))
        code, desc = self.errorCheck()
        if code:
            log.warning("Error moving referencing C863 stage {}: {}".format(code, desc))
        if waitForStop:
            self.waitForMove(*args, **kwargs)
        # self.write("MOV {}".format(pos))

    def getPosition(self):
        return float(self.query("MOV?").split("=")[1])

    def home(self):
        self.write("GOH {}".format(self.address))

    def setMotorState(self, state):
        """ True for on, False for off"""
        print("sending command",
              "SVO {} {}".format(self.address, int(bool(state))))
        self.write("SVO {} {}".format(self.address, int(bool(state))))

    def motorOn(self):
        self.setMotorState(1)

    def motorOff(self):
        self.setMotorState(0)

    def getMotorState(self):
        return int(self.query("SVO?").split("=")[1])

    def gotoNegativeReference(self, waitForStop = True, *args, **kwargs):
        self.write("FNL {}".format(self.address))
        code, desc = self.errorCheck()
        if code:
            log.warning("Error negative referencing C863 stage {}: {}".format(code, desc))
            return False
        if waitForStop:
            self.waitForMove(*args, **kwargs)

    def checkMoving(self):
        ### I was having too much trouble gettnig the \x05 commands to be
        ##  sent and parsed properly, but using the the SRG? and checking
        ##  the status buffer is more reliable.
        # check to see if the motor is still moving
        # stupid ascii stuff made this annoying
        # self._instrument.write('\x05\10', termination=False)
        # ret = self.read()
        # print("checkmove is ", ret)
        # return int(ret)
        return self.checkStatus() & 0b0010000000000000

    def checkStatus(self):
        # self._instrument.write('\x04\10', termination=False)
        # time.sleep(0.3)
        # ret = self._instrument.read('\n')
        ret = self.query("SRG? {} {}".format(self.address, 1)).split('=')[1]
        print("Check status return", ret)
        return int(ret, 0)

    def waitForMove(self, timeout=10, callback=None):
        # Timeout in seconds
        stTime = time.time()
        endTime = stTime
        endTime += np.inf if timeout is None else timeout

        # callback for update that can be called while waiting
        if not hasattr(callback, "__call__"):
            callback = lambda x: None

        while self.checkMoving():
            # print(self.checkMoving())
            time.sleep(0.25)
            callback(self.getPosition())
            # print(self.checkStatus())
            if time.time()>endTime: break







class DG535(BaseInstr):

    outputMap = {
        "T": 1,
        "A": 2,
        "B": 3,
        "AB": 4,
        "C": 5,
        "D": 6,
        "CD": 7
    }

    outputUnMap = {v:k for k, v in list(outputMap.items())}

    def checkError(self):
        """
        Return an array of ints where each index corresponds to a bit in the
        error signal, 1 indicating an error.

        7 Always zero
        6 Recalled data was corrupt
        5 Delay range error
        4 Delay linkage error
        3 Wrong mode for the command
        2 Value is outside allowed range
        1 Wrong number of parameters
        0 Unrecognized command
        """
        return list(map(int, "{:08b}".format(int(self.ask("ES")))))

    def checkStatus(self):
        """
        Return an array of ints where each index corresponds to a bit in the
        error signal, 1 indicating an error.

        7 Memory contents corrupted
        6 Service request
        5 Always zero
        4 Trigger rate too high
        3 80MHz PLL is unlocked
        2 Trigger has occurred
        1 Busy with timing cycle
        0 Command error detected
        """
        return list(map(int, "{:08b}".format(int(self.ask("IS")))))

    def setDelay(self, source, rel="T", t=0):
        chS = DG535.outputMap[source]
        chR = DG535.outputMap[rel]
        self.write("DT {},{},{}".format(chS, chR, float(t)))

    def getDelay(self, source):
        ret = self.ask("DT {}".format(DG535.outputMap[source]))
        if not ret:
            #timeout or something else occured
            log.warning("Error getting delay values for channel {}".format(source))
            return -1, -1
        ch, t = ret.split(',')
        return DG535.outputUnMap[int(ch)], float(t)

    def getTriggerMode(self):
        """
        0 - Internal
        1 - External
        2 - SS
        3 - Burst
        :return:
        """
        return int(self.ask("TM"))

    def setTriggerMode(self, val=1):
        if val not in list(range(4)):
            log.warning("Invalid value for trigger mode! {}".format(val))
            return
        self.write("TM {:d}".format(val))

    def getTriggerRate(self, forBurst=False):
        return float(self.ask("TR {:d}".format(forBurst)))

    def setTriggerRate(self, val=1, forBurst=False):
        self.write("TR {:d},{:f}".format(forBurst, val))

    def getTriggerLevel(self):
        return float(self.ask("TL"))

    def setTriggerLevel(self, val=3):
        self.write("TL {:f}".format(val))

    def getTriggerSlope(self):
        return float(self.ask("TS"))

    def setTriggerSlope(self, isRising=False):
        self.write("TS {:d}".format(isRising))

    def getTriggerLoad(self):
        return float(self.ask("TZ 0"))

    def setTriggerLoad(self, isHigh=False):
        self.write("TZ 0,{:d}".format(isHigh))


class ESP300(BaseInstr):
    """
    Newport Universal Motion Controller/Driver Model ESP300

    all axis control commands are sent to the number axis given by the
    local variable self.current_axis. so here is an example usage

    esp= ESP300()
    esp.current_axis=1
    esp.units= 'millimeter'
    esp.position = 10
    print esp.position
    """
    UNIT_DICT = {
        'enoder count':0,
        'motor step':1,
        'millimeter':2,
        'micrometer':3,
        'inches':4,
        'milli inches':5,
        'micro inches':6,
        'degree':7,
        'gradient':8,
        'radian':9,
        'milliradian':10,
        'microradian':11,
        }

    def __init__(self, address, current_axis=2,
        always_wait_for_stop=True,delay=500,**kwargs):
        """
        takes:
            address:    Gpib address, int [1]
            current_axis:   number of current axis, int [1]
            always_wait_for_stop:   wait for stage to stop before
                returning control to calling program, boolean [True]
            **kwargs:   passed to GpibInstrument initializer
        """

        # GpibInstrument.__init__(self,address,**kwargs)
        super(ESP300, self).__init__(address)
        # self.instrument = rm().open_resource(address)
        self._instrument.timeout = 10000
        self.current_axis = current_axis
        self.always_wait_for_stop = always_wait_for_stop
        self.delay=delay
    @property
    def current_axis(self):
        """
        current axis used in all subsequent commands
        """
        return self._current_axis
    @current_axis.setter
    def current_axis(self, input):
        """
        takes:
            input:  desired current axis number, int []
        """
        self._current_axis = input

    @property
    def velocity(self):
        """
        the velocity of current axis
        """
        command_string = 'VA'
        return (float(self.ask('%i%s?'%(self.current_axis,command_string))))
    @velocity.setter
    def velocity(self,input):
        command_string = 'VA'
        self.write('%i%s%f'%(self.current_axis,command_string,input))

    @property
    def acceleration(self):
        command_string = 'AC'
        return (self.ask('%i%s?'%(self.current_axis,command_string)))
    @acceleration.setter
    def acceleration(self,input):
        command_string = 'AC'
        self.write('%i%s%f'%(self.current_axis,command_string,input))

    @property
    def deceleration(self):
        command_string = 'AG'
        return (self.ask('%i%s?'%(self.current_axis,command_string)))
    @deceleration.setter
    def deceleration(self,input):
        command_string = 'AG'
        self.write('%i%s%f'%(self.current_axis,command_string,input))

    @property
    def position_relative(self):
        raise NotImplementedError('See position property for reading position')
    @position_relative.setter
    def position_relative(self,input):
        command_string = 'PR'
        self.write('%i%s%f'%(self.current_axis,command_string,input))
        if self.always_wait_for_stop:
            self.wait_for_stop()

    @property
    def position(self):
        command_string = 'TP'
        return float(self.ask('%i%s'%(self.current_axis,command_string)))
    @position.setter
    def position(self,input):
        """
        set the position of current axis to input
        """
        command_string = 'PA'
        self.write('%i%s%f'%(self.current_axis,command_string,input))
        if self.always_wait_for_stop:
            self.wait_for_stop()

    @property
    def home(self):
        command_string = 'OR'
        self.write('%i%s'%(self.current_axis,command_string))
        if self.always_wait_for_stop:
            self.wait_for_stop()

    def goHome(self):
        # Want to overload so this is a callable.
        self.home
    @home.setter
    def home(self, input):
        command_string = 'DH'
        self.write('%i%s%f'%(self.current_axis,command_string,input))

    @property
    def units(self):
        raise NotImplementedError('I dont know how to read units')
    @units.setter
    def units(self, input):
        """
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
        """
        command_string = 'SN'
        self.write('%i%s%i'%(self.current_axis,command_string, self.UNIT_DICT[input]))

    @property
    def error_message(self):
        return (self.ask('TB?'))

    @property
    def motor_on(self):
        command_string = 'MO'
        return (self.ask('%i%s?'%(self.current_axis,command_string)))
    @motor_on.setter
    def motor_on(self,input):
        if input:
            command_string = 'MO'
            self.write('%i%s'%(self.current_axis,command_string))
        if not input:
            command_string = 'MF'
            self.write('%i%s'%(self.current_axis,command_string))

    def send_stop(self):
        command_string = 'ST'
        self.write('%i%s'%(self.current_axis,command_string))

    def wait_for_stop(self):
        # Tell the device to wait for a stop, then send a SRQ when it's
        # done. Then tell the local instrument to wait until it recieves that.
        command_string = 'WS'
        self.write('%i%s%i;RQ3'%(self.current_axis,command_string, self.delay))
        self._instrument.wait_for_srq()
        # print("Status: ", self._instrument.stb)
        # tmp = self.position

class Keithley236Instr(BaseInstr):
    def __init__(self, GPIB_Number=None, timeout = 3000):
        super(Keithley236Instr, self).__init__(GPIB_Number, timeout)

    def setBias(self, BiasLevel):
        #Set to the desired bias level, auto ranging and waiting 10ms
        if type(BiasLevel) not in (float, int):
            print('Error. Invalid bias level')
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
    # breakLoop = LockableBool(False)
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
                print("Error calling intermediate function!", e)
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

class LakeShore325(BaseInstr):
    """
    Temperature Controller for LED
    """
    def __init__(self, GPIB_Number=None, timeout=3000):
        super(LakeShore325, self).__init__(GPIB_Number,timeout)

    def askTemp(self, channel="A"):
        #returns temp in C from input A/B in float
        temp=self.ask("CRDG? "+channel)
        return float(temp)

    def getSampleTemp(self, channel="A"):
        return self.askTemp(channel)


    def askSetpoint(self, loop="1"):
        #returns set point in loop 1/2 in float
        sp=self.ask("SETP? "+loop)
        return float(sp)

    def askOutput(self, loop="1"):
        #returns heater output of loop 1 or 2 in float
        output=self.ask("HTR? "+loop)
        return float(output)

class LakeShore330(BaseInstr):
    """
    Temperature Controller for Sample
    There's some distinction between "sample" and control
    channels. I'm not quite sure the difference. At thee
    time of writing, we operate with both being the same
    (channel b)
    """
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

class SPEX(BaseInstr):
    def __init__(self, GPIB_Number=None, timeout=3000):
        super(SPEX, self).__init__(GPIB_Number, timeout)

        # try:
        #     self.ask(" ")
        # except visa.VisaIOError:
        #     log.warning("SPEX write terminator has been chagned")
        #     self._instrument._write_termination = ""
        #     self.ask(" ")

        self._instrument._write_termination = ""
        
        self.maxWavenumber = 31000
        self.stepsPerWavenumber = 400
        self.backlash = 8000
        try:
            self.currentPositionSteps = self.curStep()
            self.currentPositionWN = self.stepsToWN(self.currentPositionSteps)
        except Exception as e:
            if self.whereAmI().lower()=="b":
                log.warning("Error! SPEX not initialized!")
            else:
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
        return val
        
    def initBoot(self, wavenumber = None):
        """This function should be called if the SPEX isn't in the proper boot mode
        (e.g. if after being power cycled)

        Pass the wavenumber that is currently read on the SPEX
        __DO NOT__ add 4 wavenumber. That's done internally
        since I always forget whether it's + or -.
        """
        
        if wavenumber is not None:
            self.currentPositionWN = wavenumber
        # correct for SPEX offset.
        self.currentPositionWN-=4
        print('Checking position')
        pos = self.whereAmI()
        #First make sure the query didn't return FALSE if it timed out
        if not pos:
            print('Error finding position. SPEX hung?')
            return
        elif pos.lower() == 'f':
            print('SPEX already in operating mode. I\'ll keep going, but I\'m not sure I should...')
        elif not pos.lower() == 'b':
            print('This shouldn\'t have happened', pos)
            return
        #start main program
        print('Starting main SPEX software')
        ret = self.ask('O2000\r', timeout = 5)
        if not ret:
            print('Error starting SPEX main program. Retry init suggested')
            return
        elif not ret == '*':
            print("This also shouldn't have happened. ret =", ret)
        print('Initializing motors')
        
        #Needs to wait for 100 seconds, according to p37        
        ret = self.ask('A', timeout=100)
        if not ret:
            print('Error initalizing motors')
            return
        elif not ret.lower()=='o':
            print("Bad motor initialization", ret)
            return
        
        #These settings are coming from the SPEX init.vi
        #Come from appendix 1
        #
        #speed type 0, 1000Hz min, 18000Hz max, 2000ms ramp time
        print('setting motor speed')
        speedStr = '1000,18000,2000'
        ret = self.ask('B0,'+speedStr + "\r")
        if not ret:
            print('Error initalizing motor speed')
            return
        elif not ret.lower()[0]=='o':
            print("Bad motor speed set", ret)
            return
        ret = self.ask('C0' + "\r")
        if not ret:
            print('Error confirming motor speed')
            return
        elif not ret == 'o'+speedStr:
            print("Motor speed not correctly set?", ret)
            
        print('Setting internal position...')
        #This is what the dial reads on the SPEX.
        #Either enter manually or read from a file        
        currentPosition = self.currentPositionWN
        currentStep = self.wavenumberToSteps(currentPosition)
        ret = self.ask('G0,'+str(currentStep) + "\r")
        if not ret:
            print('Error setting position')
            return
        elif not ret == 'o':
            print("Motor position not correctly set?", ret)
        
        #verify position
        ret = self.ask('H0\r')
        if not ret:
            print('Error quering current position')
            return
        elif not ret[0]=='o':
            print('I dunno', ret)
        print('Set to', str(currentStep), '  Reads',str(ret))
        
    def gotoWN(self, wn):
        #Will move the SPEX to the specified wavenumber
        if wn>15000:
            print("NO. BAD. DON'T GO THERE.\n\tDesired SPEX wavenumber too large")
            return
        notMoving = self.waitForMove()
        
        #Break because something went wrong and we weren't able to wait
        if not notMoving:
            return
        desiredWNSteps = int(self.wavenumberToSteps(wn))
        print('Desired wnsteps:',desiredWNSteps)
        currentSteps = self.curStep()
        print('Currently:', currentSteps)
        
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
        print('Wanted,', desiredWNSteps)
        print('Got,', newPos)
        
        self.currentPositionSteps = newPos
        self.currentPositionWN = self.stepsToWN(newPos)
        
    def curStep(self):
        #Return the current position, in steps
        ret = self.ask('H0\r')[:-1] #Ask, and remove the trailing /r
        if ret[0] == 'o':
            return int(ret[1:])
        else:
            return int(ret)
        
    def relMove(self, moveAmount):
        """ Takes a relative amount of steps to move"""
        self.write('F0,'+str(moveAmount) + "\r")
        
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
                print('bad return from waiting')
                i = i+1
                if i >= 10:
                    print('Tried too many times')
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

class SR760(BaseInstr):
    """
    class for controlling the FFT spectrum analyzer
    """
    def __init__(self, *args, **kwargs):
        super(SR760, self).__init__(*args, **kwargs)
        # SR760 really dislikes being ended with \r
        self._instrument._write_termination = '\n'

    def getBinValue(self, i=0):
        return float(self.ask("BVAL?-1,{:d}".format(i)))

    def getFrequencies(self):
        return np.array(list(map(self.getBinValue, list(range(400)))))

    def getSpan(self):
        sp = [0.191, 0.382, 0.763, 1.500, 3.100, 6.100, 12.200, 24.400,
              48.750, 97.500, 195.000, 390.000, 780.000, 1560.000, 3125.000,
              6250.000, 12500.000, 25000.000, 50000.000, 100000.000]

        i = int(self.ask('SPAN?'))
        return sp[i]

    def getStartFrequency(self):
        return float(self.ask("STRF?"))

    def getSTB(self):
        """serial poll byte"""
        return list(map(int, "{:08b}".format(int(self.ask("*STB?")))))

    def getESR(self):
        """Standard status byte"""
        return list(map(int, "{:08b}".format(int(self.ask("*ESR?")))))

    def getERRS(self):
        """Error status byte"""
        return list(map(int, "{:08b}".format(int(self.ask("ERRS?")))))

    def getFFTE(self):
        return list(map(int, "{:08b}".format(int(self.ask("FFTE?")))))

    def waitForComplete(self):
        timeout = self._instrument.timeout
        maxCount = int(timeout/250)+1
        bit = self.getSTB()
        for ii in range(maxCount):
            if bit[-1]: break
            time.sleep(0.25)
            bit = self.getSTB()
        else:
            log.warning("Timeout occured in waiting for completion?")
            return False
        log.debug("Successfully completed")
        return True

    def setSpan(self, span=0):
        self._instrument.write("SPAN {:d}".format(span))

    def setStartFrequency(self, st=0):
        self._instrument.write("STRF {:f}".format(st))

class SR830Instr(BaseInstr):
    def __init__(self, GPIB_Number = None, timeout = 3000):
        super(SR830Instr, self).__init__(GPIB_Number, timeout)
        self.write('OUTX 1')
                
    def setRefFreq(self, freq):
        """Set the reference frequency  """
        if type(freq) not in (float, int):
            print('Error. Given frequency is not a number')
            return
        self.write('FREQ '+str(freq))
            
    def setRefVolt(self, volts):
        if type(volts) not in (float, int):
            print('Error. Given voltage is not a number')
            return
        self.write('SLVL '+str(volts))
        
    def getRefVolt(self):
        return float(self.ask('SLVL?'))
        
    def getChannel(self, ch=1):
        if ch not in (1, 2, 3, 4, 'X', 'x', 'Y', 'y', 'R', 'r', 't', 'T', 'theta', 'Theta', 'th'):
            print('Error. Must give valid channel number')
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
                print('Error. Must give valid channel number')
                return
            #if a letter is given instead of  anumber, must convert it
            if type(ch) is str:
                d = dict(x=1, y=2, r=3, t=4)
                ch = d[ch.lower()[0]]
            toRead = toRead + str(ch) +','
        toRead = toRead[:-1]
        ret = self.ask('SNAP?'+toRead)
        return [float(i) for i in ret.split(',')]

class WS6flags(object):
    """
    Flags for the WS6 object. All taken from the documentation/.h file
    in the program file.
    """

    cInstCheckForWLM = -1
    cInstResetCalc = 0
    cInstReturnMode = cInstResetCalc
    cInstNotification = 1
    cInstCopyPattern = 2
    cInstCopyAnalysis = cInstCopyPattern
    cInstControlWLM = 3
    cInstControlDelay = 4
    cInstControlPriority = 5

# Notification Constants for 'Mode' parameter
    cNotifyInstallCallback = 0
    cNotifyRemoveCallback = 1
    cNotifyInstallWaitEvent = 2
    cNotifyRemoveWaitEvent = 3
    cNotifyInstallCallbackEx = 4
    cNotifyInstallWaitEventEx = 5

# ResultError Constants of Set...-functions
    ResERR_NoErr = 0
    ResERR_WlmMissing = -1
    ResERR_CouldNotSet = -2
    ResERR_ParmOutOfRange = -3
    ResERR_WlmOutOfResources = -4
    ResERR_WlmInternalError = -5
    ResERR_NotAvailable = -6
    ResERR_WlmBusy = -7
    ResERR_NotInMeasurementMode = -8
    ResERR_OnlyInMeasurementMode = -9
    ResERR_ChannelNotAvailable = -10
    ResERR_ChannelTemporarilyNotAvailable = -11
    ResERR_CalOptionNotAvailable = -12
    ResERR_CalWavelengthOutOfRange = -13
    ResERR_BadCalibrationSignal = -14
    ResERR_UnitNotAvailable = -15
    ResERR_FileNotFound = -16
    ResERR_FileCreation = -17
    ResERR_TriggerPending = -18
    ResERR_TriggerWaiting = -19
    ResERR_NoLegitimation = -20

# Mode Constants for Callback-Export and WaitForWLMEvent-function
    cmiResultMode = 1
    cmiRange = 2
    cmiPulse = 3
    cmiPulseMode = cmiPulse
    cmiWideLine = 4
    cmiWideMode = cmiWideLine
    cmiFast = 5
    cmiFastMode = cmiFast
    cmiExposureMode = 6
    cmiExposureValue1 = 7
    cmiExposureValue2 = 8
    cmiDelay = 9
    cmiShift = 10
    cmiShift2 = 11
    cmiReduce = 12
    cmiReduced = cmiReduce
    cmiScale = 13
    cmiTemperature = 14
    cmiLink = 15
    cmiOperation = 16
    cmiDisplayMode = 17
    cmiPattern1a = 18
    cmiPattern1b = 19
    cmiPattern2a = 20
    cmiPattern2b = 21
    cmiMin1 = 22
    cmiMax1 = 23
    cmiMin2 = 24
    cmiMax2 = 25
    cmiNowTick = 26
    cmiCallback = 27
    cmiFrequency1 = 28
    cmiFrequency2 = 29
    cmiDLLDetach = 30
    cmiVersion = 31
    cmiAnalysisMode = 32
    cmiDeviationMode = 33
    cmiDeviationReference = 34
    cmiDeviationSensitivity = 35
    cmiAppearance = 36
    cmiAutoCalMode = 37
    cmiWavelength1 = 42
    cmiWavelength2 = 43
    cmiLinewidth = 44
    cmiLinewidthMode = 45
    cmiLinkDlg = 56
    cmiAnalysis = 57
    cmiAnalogIn = 66
    cmiAnalogOut = 67
    cmiDistance = 69
    cmiWavelength3 = 90
    cmiWavelength4 = 91
    cmiWavelength5 = 92
    cmiWavelength6 = 93
    cmiWavelength7 = 94
    cmiWavelength8 = 95
    cmiVersion0 = cmiVersion
    cmiVersion1 = 96
    cmiDLLAttach = 121
    cmiSwitcherSignal = 123
    cmiSwitcherMode = 124
    cmiExposureValue11 = cmiExposureValue1
    cmiExposureValue12 = 125
    cmiExposureValue13 = 126
    cmiExposureValue14 = 127
    cmiExposureValue15 = 128
    cmiExposureValue16 = 129
    cmiExposureValue17 = 130
    cmiExposureValue18 = 131
    cmiExposureValue21 = cmiExposureValue2
    cmiExposureValue22 = 132
    cmiExposureValue23 = 133
    cmiExposureValue24 = 134
    cmiExposureValue25 = 135
    cmiExposureValue26 = 136
    cmiExposureValue27 = 137
    cmiExposureValue28 = 138
    cmiPatternAverage = 139
    cmiPatternAvg1 = 140
    cmiPatternAvg2 = 141
    cmiAnalogOut1 = cmiAnalogOut
    cmiAnalogOut2 = 142
    cmiMin11 = cmiMin1
    cmiMin12 = 146
    cmiMin13 = 147
    cmiMin14 = 148
    cmiMin15 = 149
    cmiMin16 = 150
    cmiMin17 = 151
    cmiMin18 = 152
    cmiMin21 = cmiMin2
    cmiMin22 = 153
    cmiMin23 = 154
    cmiMin24 = 155
    cmiMin25 = 156
    cmiMin26 = 157
    cmiMin27 = 158
    cmiMin28 = 159
    cmiMax11 = cmiMax1
    cmiMax12 = 160
    cmiMax13 = 161
    cmiMax14 = 162
    cmiMax15 = 163
    cmiMax16 = 164
    cmiMax17 = 165
    cmiMax18 = 166
    cmiMax21 = cmiMax2
    cmiMax22 = 167
    cmiMax23 = 168
    cmiMax24 = 169
    cmiMax25 = 170
    cmiMax26 = 171
    cmiMax27 = 172
    cmiMax28 = 173
    cmiAvg11 = cmiPatternAvg1
    cmiAvg12 = 174
    cmiAvg13 = 175
    cmiAvg14 = 176
    cmiAvg15 = 177
    cmiAvg16 = 178
    cmiAvg17 = 179
    cmiAvg18 = 180
    cmiAvg21 = cmiPatternAvg2
    cmiAvg22 = 181
    cmiAvg23 = 182
    cmiAvg24 = 183
    cmiAvg25 = 184
    cmiAvg26 = 185
    cmiAvg27 = 186
    cmiAvg28 = 187
    cmiPatternAnalysisWritten = 202
    cmiSwitcherChannel = 203
    cmiStartCalibration = 235
    cmiEndCalibration = 236
    cmiAnalogOut3 = 237
    cmiAnalogOut4 = 238
    cmiAnalogOut5 = 239
    cmiAnalogOut6 = 240
    cmiAnalogOut7 = 241
    cmiAnalogOut8 = 242
    cmiIntensity = 251
    cmiPower = 267
    cmiActiveChannel = 300
    cmiPIDCourse = 1030
    cmiPIDUseTa = 1031
    cmiPIDUseT = cmiPIDUseTa
    cmiPID_T = 1033
    cmiPID_P = 1034
    cmiPID_I = 1035
    cmiPID_D = 1036
    cmiDeviationSensitivityDim = 1040
    cmiDeviationSensitivityFactor = 1037
    cmiDeviationPolarity = 1038
    cmiDeviationSensitivityEx = 1039
    cmiDeviationUnit = 1041
    cmiDeviationBoundsMin = 1042
    cmiDeviationBoundsMax = 1043
    cmiDeviationRefMid = 1044
    cmiDeviationRefAt = 1045
    cmiPIDConstdt = 1059
    cmiPID_dt = 1060
    cmiPID_AutoClearHistory = 1061
    cmiDeviationChannel = 1063
    cmiPID_ClearHistoryOnRangeExceed = 1069
    cmiAutoCalPeriod = 1120
    cmiAutoCalUnit = 1121
    cmiAutoCalChannel = 1122
    cmiServerInitialized = 1124
    cmiWavelength9 = 1130
    cmiExposureValue19 = 1155
    cmiExposureValue29 = 1180
    cmiMin19 = 1205
    cmiMin29 = 1230
    cmiMax19 = 1255
    cmiMax29 = 1280
    cmiAvg19 = 1305
    cmiAvg29 = 1330
    cmiWavelength10 = 1355
    cmiWavelength11 = 1356
    cmiWavelength12 = 1357
    cmiWavelength13 = 1358
    cmiWavelength14 = 1359
    cmiWavelength15 = 1360
    cmiWavelength16 = 1361
    cmiWavelength17 = 1362
    cmiExternalInput = 1400
    cmiPressure = 1465
    cmiBackground = 1475
    cmiDistanceMode = 1476
    cmiInterval = 1477
    cmiIntervalMode = 1478
    cmiCalibrationEffect = 1480
    cmiLinewidth1 = cmiLinewidth
    cmiLinewidth2 = 1481
    cmiLinewidth3 = 1482
    cmiLinewidth4 = 1483
    cmiLinewidth5 = 1484
    cmiLinewidth6 = 1485
    cmiLinewidth7 = 1486
    cmiLinewidth8 = 1487
    cmiLinewidth9 = 1488
    cmiLinewidth10 = 1489
    cmiLinewidth11 = 1490
    cmiLinewidth12 = 1491
    cmiLinewidth13 = 1492
    cmiLinewidth14 = 1493
    cmiLinewidth15 = 1494
    cmiLinewidth16 = 1495
    cmiLinewidth17 = 1496
    cmiTriggerState = 1497
    cmiDeviceAttach = 1501
    cmiDeviceDetach = 1502
    cmiTimePerMeasurement = 1514
    cmiAutoExpoMin = 1517
    cmiAutoExpoMax = 1518
    cmiAutoExpoStepUp = 1519
    cmiAutoExpoStepDown = 1520
    cmiAutoExpoAtSaturation = 1521
    cmiAutoExpoAtLowSignal = 1522
    cmiAutoExpoFeedback = 1523
    cmiAveragingCount = 1524
    cmiAveragingMode = 1525
    cmiAveragingType = 1526

# Index constants for Get- and SetExtraSetting
    cesCalculateLive = 4501

# WLM Control Mode Constants
    cCtrlWLMShow = 1
    cCtrlWLMHide = 2
    cCtrlWLMExit = 3
    cCtrlWLMStore = 4
    cCtrlWLMCompare = 5
    cCtrlWLMWait        = 0x0010
    cCtrlWLMStartSilent = 0x0020
    cCtrlWLMSilent      = 0x0040
    cCtrlWLMStartDelay  = 0x0080

# Operation Mode Constants (for "Operation" and "GetOperationState" functions)
    cStop = 0
    cAdjustment = 1
    cMeasurement = 2

# Base Operation Constants (To be used exclusively, only one of this list at a time,
# but still can be combined with "Measurement Action Addition Constants". See below.)
    cCtrlStopAll = cStop
    cCtrlStartAdjustment = cAdjustment
    cCtrlStartMeasurement = cMeasurement
    cCtrlStartRecord = 0x0004
    cCtrlStartReplay = 0x0008
    cCtrlStoreArray  = 0x0010
    cCtrlLoadArray   = 0x0020

# Additional Operation Flag Constants (combine with "Base Operation Constants" above.)
    cCtrlDontOverwrite = 0x0000
    cCtrlOverwrite     = 0x1000 # don't combine with cCtrlFileDialo
    cCtrlFileGiven     = 0x0000
    cCtrlFileDialog    = 0x2000 # don't combine with cCtrlOverwrite and cCtrlFileASCI
    cCtrlFileBinary    = 0x0000 # *.smr, *.lt
    cCtrlFileASCII     = 0x4000 # *.smx, *.ltx, don't combine with cCtrlFileDialo

# Measurement Control Mode Constants
    cCtrlMeasDelayRemove = 0
    cCtrlMeasDelayGenerally = 1
    cCtrlMeasDelayOnce = 2
    cCtrlMeasDelayDenyUntil = 3
    cCtrlMeasDelayIdleOnce = 4
    cCtrlMeasDelayIdleEach = 5
    cCtrlMeasDelayDefault = 6

# Measurement Triggering Action Constants
    cCtrlMeasurementContinue = 0
    cCtrlMeasurementInterrupt = 1
    cCtrlMeasurementTriggerPoll = 2
    cCtrlMeasurementTriggerSuccess = 3
    cCtrlMeasurementEx = 0x0100

# ExposureRange Constants
    cExpoMin = 0
    cExpoMax = 1
    cExpo2Min = 2
    cExpo2Max = 3

# Amplitude Constants
    cMin1 = 0
    cMin2 = 1
    cMax1 = 2
    cMax2 = 3
    cAvg1 = 4
    cAvg2 = 5

# Measurement Range Constants
    cRange_250_410 = 4
    cRange_250_425 = 0
    cRange_300_410 = 3
    cRange_350_500 = 5
    cRange_400_725 = 1
    cRange_700_1100 = 2
    cRange_800_1300 = 6
    cRange_900_1500 = cRange_800_1300
    cRange_1100_1700 = 7
    cRange_1100_1800 = cRange_1100_1700

# Measurement Range Model Constants
    cRangeModelOld = 65535
    cRangeModelByOrder = 65534
    cRangeModelByWavelength = 65533

# Unit Constants for Get-/SetResultMode, GetLinewidth, Convert... and Calibration
    cReturnWavelengthVac = 0
    cReturnWavelengthAir = 1
    cReturnFrequency = 2
    cReturnWavenumber = 3
    cReturnPhotonEnergy = 4

# Power Unit Constants
    cPower_muW = 0
    cPower_dBm = 1

# Source Type Constants for Calibration
    cHeNe633 = 0
    cHeNe1152 = 0
    cNeL = 1
    cOther = 2
    cFreeHeNe = 3

# Unit Constants for Autocalibration
    cACOnceOnStart = 0
    cACMeasurements = 1
    cACDays = 2
    cACHours = 3
    cACMinutes = 4

# ExposureRange Constants
    cGetSync = 1
    cSetSync = 2

# Pattern- and Analysis Constants
    cPatternDisable = 0
    cPatternEnable = 1
    cAnalysisDisable = cPatternDisable
    cAnalysisEnable = cPatternEnable

    cSignal1Interferometers = 0
    cSignal1WideInterferometer = 1
    cSignal1Grating = 1
    cSignal2Interferometers = 2
    cSignal2WideInterferometer = 3
    cSignalAnalysis = 4
    cSignalAnalysisX = cSignalAnalysis
    cSignalAnalysisY = cSignalAnalysis + 1

# State constants used with AutoExposureSetting functions
    cJustStepDown = 0
    cRestartAtMinimum = 1
    cJustStepUp = 0
    cDriveToLevel = 1
    cConsiderFeedback = 1
    cDontConsiderFeedback = 0

# State constants used with AveragingSetting functions
    cAvrgFloating = 1
    cAvrgSucceeding = 2
    cAvrgSimple = 0
    cAvrgPattern = 1

# Return errorvalues of GetFrequency, GetWavelength and GetWLMVersion
    ErrNoValue = 0
    ErrNoSignal = -1
    ErrBadSignal = -2
    ErrLowSignal = -3
    ErrBigSignal = -4
    ErrWlmMissing = -5
    ErrNotAvailable = -6
    InfNothingChanged = -7
    ErrNoPulse = -8
    ErrChannelNotAvailable = -10
    ErrDiv0 = -13
    ErrOutOfRange = -14
    ErrUnitNotAvailable = -15
    ErrMaxErr = ErrUnitNotAvailable

# Return errorvalues of GetTemperature and GetPressure
    ErrTemperature = -1000
    ErrTempNotMeasured = ErrTemperature + ErrNoValue
    ErrTempNotAvailable = ErrTemperature + ErrNotAvailable
    ErrTempWlmMissing = ErrTemperature + ErrWlmMissing

# Return errorvalues of GetDistance
    # real errorvalues are ErrDistance combined with those of GetWavelength
    ErrDistance = -1000000000
    ErrDistanceNotAvailable = ErrDistance + ErrNotAvailable
    ErrDistanceWlmMissing = ErrDistance + ErrWlmMissing

# Return flags of ControlWLMEx in combination with Show or Hide, Wait and Res = 1
    flServerStarted           = 0x00000001
    flErrDeviceNotFound       = 0x00000002
    flErrDriverError          = 0x00000004
    flErrUSBError             = 0x00000008
    flErrUnknownDeviceError   = 0x00000010
    flErrWrongSN              = 0x00000020
    flErrUnknownSN            = 0x00000040
    flErrTemperatureError     = 0x00000080
    flErrPressureError        = 0x00000100
    flErrCancelledManually    = 0x00000200
    flErrWLMBusy              = 0x00000400
    flErrUnknownError         = 0x00001000
    flNoInstalledVersionFound = 0x00002000
    flDesiredVersionNotFound  = 0x00004000
    flErrFileNotFound         = 0x00008000
    flErrParmOutOfRange       = 0x00010000
    flErrCouldNotSet          = 0x00020000
    flErrEEPROMFailed         = 0x00040000
    flErrFileFailed           = 0x00080000
    flDeviceDataNewer         = 0x00100000
    flFileDataNewer           = 0x00200000
    flErrDeviceVersionOld     = 0x00400000
    flErrFileVersionOld       = 0x00800000
    flDeviceStampNewer        = 0x01000000
    flFileStampNewer          = 0x02000000

# Return file info flags of SetOperationFile
    flFileInfoDoesntExist = 0x0000
    flFileInfoExists      = 0x0001
    flFileInfoCantWrite   = 0x0002
    flFileInfoCantRead    = 0x0004
    flFileInfoInvalidName = 0x0008
    cFileParameterError = -1

    @staticmethod
    def callbackParse(k):
        return {1: "cmiResultMode",
        2: "cmiRange",
        3: "cmiPulse",
        # cmiPulse: "cmiPulseMode",
        4: "cmiWideLine",
        # cmiWideLine: "cmiWideMode",
        5: "cmiFast",
        # cmiFast: "cmiFastMode",
        6: "cmiExposureMode",
        7: "cmiExposureValue1",
        8: "cmiExposureValue2",
        9: "cmiDelay",
        10: "cmiShift",
        11: "cmiShift2",
        12: "cmiReduce",
        # cmiReduce: "cmiReduced",
        13: "cmiScale",
        14: "cmiTemperature",
        15: "cmiLink",
        16: "cmiOperation",
        17: "cmiDisplayMode",
        18: "cmiPattern1a",
        19: "cmiPattern1b",
        20: "cmiPattern2a",
        21: "cmiPattern2b",
        22: "cmiMin1",
        23: "cmiMax1",
        24: "cmiMin2",
        25: "cmiMax2",
        26: "cmiNowTick",
        27: "cmiCallback",
        28: "cmiFrequency1",
        29: "cmiFrequency2",
        30: "cmiDLLDetach",
        31: "cmiVersion",
        32: "cmiAnalysisMode",
        33: "cmiDeviationMode",
        34: "cmiDeviationReference",
        35: "cmiDeviationSensitivity",
        36: "cmiAppearance",
        37: "cmiAutoCalMode",
        42: "cmiWavelength1",
        43: "cmiWavelength2",
        44: "cmiLinewidth",
        45: "cmiLinewidthMode",
        56: "cmiLinkDlg",
        57: "cmiAnalysis",
        66: "cmiAnalogIn",
        67: "cmiAnalogOut",
        69: "cmiDistance",
        90: "cmiWavelength3",
        91: "cmiWavelength4",
        92: "cmiWavelength5",
        93: "cmiWavelength6",
        94: "cmiWavelength7",
        95: "cmiWavelength8",
        # cmiVersion: "cmiVersion0",
        96: "cmiVersion1",
        121: "cmiDLLAttach",
        123: "cmiSwitcherSignal",
        124: "cmiSwitcherMode",
        # cmiExposureValue1: "cmiExposureValue11",
        125: "cmiExposureValue12",
        126: "cmiExposureValue13",
        127: "cmiExposureValue14",
        128: "cmiExposureValue15",
        129: "cmiExposureValue16",
        130: "cmiExposureValue17",
        131: "cmiExposureValue18",
        # cmiExposureValue2: "cmiExposureValue21",
        132: "cmiExposureValue22",
        133: "cmiExposureValue23",
        134: "cmiExposureValue24",
        135: "cmiExposureValue25",
        136: "cmiExposureValue26",
        137: "cmiExposureValue27",
        138: "cmiExposureValue28",
        139: "cmiPatternAverage",
        140: "cmiPatternAvg1",
        141: "cmiPatternAvg2",
        # cmiAnalogOut: "cmiAnalogOut1",
        142: "cmiAnalogOut2",
        # cmiMin1: "cmiMin11",
        146: "cmiMin12",
        147: "cmiMin13",
        148: "cmiMin14",
        149: "cmiMin15",
        150: "cmiMin16",
        151: "cmiMin17",
        152: "cmiMin18",
        # cmiMin2: "cmiMin21",
        153: "cmiMin22",
        154: "cmiMin23",
        155: "cmiMin24",
        156: "cmiMin25",
        157: "cmiMin26",
        158: "cmiMin27",
        159: "cmiMin28",
        # cmiMax1: "cmiMax11",
        160: "cmiMax12",
        161: "cmiMax13",
        162: "cmiMax14",
        163: "cmiMax15",
        164: "cmiMax16",
        165: "cmiMax17",
        166: "cmiMax18",
        # cmiMax2: "cmiMax21",
        167: "cmiMax22",
        168: "cmiMax23",
        169: "cmiMax24",
        170: "cmiMax25",
        171: "cmiMax26",
        172: "cmiMax27",
        173: "cmiMax28",
        # cmiPatternAvg1: "cmiAvg11",
        174: "cmiAvg12",
        175: "cmiAvg13",
        176: "cmiAvg14",
        177: "cmiAvg15",
        178: "cmiAvg16",
        179: "cmiAvg17",
        180: "cmiAvg18",
        # cmiPatternAvg2: "cmiAvg21",
        181: "cmiAvg22",
        182: "cmiAvg23",
        183: "cmiAvg24",
        184: "cmiAvg25",
        185: "cmiAvg26",
        186: "cmiAvg27",
        187: "cmiAvg28",
        202: "cmiPatternAnalysisWritten",
        203: "cmiSwitcherChannel",
        235: "cmiStartCalibration",
        236: "cmiEndCalibration",
        237: "cmiAnalogOut3",
        238: "cmiAnalogOut4",
        239: "cmiAnalogOut5",
        240: "cmiAnalogOut6",
        241: "cmiAnalogOut7",
        242: "cmiAnalogOut8",
        251: "cmiIntensity",
        267: "cmiPower",
        300: "cmiActiveChannel",
        1030: "cmiPIDCourse",
        1031: "cmiPIDUseTa",
        # cmiPIDUseTa: "cmiPIDUseT",
        1033: "cmiPID_T",
        1034: "cmiPID_P",
        1035: "cmiPID_I",
        1036: "cmiPID_D",
        1040: "cmiDeviationSensitivityDim",
        1037: "cmiDeviationSensitivityFactor",
        1038: "cmiDeviationPolarity",
        1039: "cmiDeviationSensitivityEx",
        1041: "cmiDeviationUnit",
        1042: "cmiDeviationBoundsMin",
        # 1043: "cmiDeviationBoundsMax ,
        1044: "cmiDeviationRefMid",
        1045: "cmiDeviationRefAt",
        1059: "cmiPIDConstdt",
        1060: "cmiPID_dt",
        1061: "cmiPID_AutoClearHistory",
        1063: "cmiDeviationChannel",
        1069: "cmiPID_ClearHistoryOnRangeExceed",
        1120: "cmiAutoCalPeriod",
        1121: "cmiAutoCalUnit",
        1122: "cmiAutoCalChannel",
        1124: "cmiServerInitialized",
        1130: "cmiWavelength9",
        1155: "cmiExposureValue19",
        1180: "cmiExposureValue29",
        1205: "cmiMin19",
        1230: "cmiMin29",
        1255: "cmiMax19",
        1280: "cmiMax29",
        1305: "cmiAvg19",
        1330: "cmiAvg29",
        1355: "cmiWavelength10",
        1356: "cmiWavelength11",
        1357: "cmiWavelength12",
        1358: "cmiWavelength13",
        1359: "cmiWavelength14",
        1360: "cmiWavelength15",
        1361: "cmiWavelength16",
        1362: "cmiWavelength17",
        1400: "cmiExternalInput",
        1465: "cmiPressure",
        1475: "cmiBackground",
        1476: "cmiDistanceMode",
        1477: "cmiInterval",
        1478: "cmiIntervalMode",
        1480: "cmiCalibrationEffect",
        # cmiLinewidth: "cmiLinewidth1",
        1481: "cmiLinewidth2",
        1482: "cmiLinewidth3",
        1483: "cmiLinewidth4",
        1484: "cmiLinewidth5",
        1485: "cmiLinewidth6",
        1486: "cmiLinewidth7",
        1487: "cmiLinewidth8",
        1488: "cmiLinewidth9",
        1489: "cmiLinewidth10",
        1490: "cmiLinewidth11",
        1491: "cmiLinewidth12",
        1492: "cmiLinewidth13",
        1493: "cmiLinewidth14",
        1494: "cmiLinewidth15",
        1495: "cmiLinewidth16",
        1496: "cmiLinewidth17",
        1497: "cmiTriggerState",
        1501: "cmiDeviceAttach",
        1502: "cmiDeviceDetach",
        1514: "cmiTimePerMeasurement",
        1517: "cmiAutoExpoMin",
        1518: "cmiAutoExpoMax",
        1519: "cmiAutoExpoStepUp",
        1520: "cmiAutoExpoStepDown",
        1521: "cmiAutoExpoAtSaturation",
        1522: "cmiAutoExpoAtLowSignal",
        1523: "cmiAutoExpoFeedback",
        1524: "cmiAveragingCount",
        1525: "cmiAveragingMode",
        1526: "cmiAveragingType"}.get(k, "Not found: {}".format(k))

class WS6(object):
    """
    This instrument is controlled by a dll, not the pyvisa
    library, so it doesn't inherit BaseInstr
    """
    c = WS6flags()
    callbackFuncs = [] # Need to keep references to the callback functions
                       # to prevent crashing
    def __init__(self):
        self.dll = self.registerFunctions()
        if self.dll is None: return

    def __del__(self):
        print("I got called to be deleted")
        try:
            print(self.dllInstantiate(WS6.c.cInstNotification,
                                      WS6.c.cNotifyRemoveCallback,
                                      0, 0))
        except:
            log.exception("Couldn't close out functions")

    def attachCallback(self, func):
        """
        attach a function to be called when the wavemeter is updated
        See the WS6 manual. Function needs to take two ints and a float
        :param func:
        :return:
        """
        if not callable(func):
            log.warning("Function needs to be callable!")
            return

        CALLFUNC = CFUNCTYPE(None, c_int, c_int, c_double)
        cfunc = CALLFUNC(func)
        WS6.callbackFuncs.append(cfunc)
        self.dllInstantiate(WS6.c.cInstNotification,
                               WS6.c.cNotifyInstallCallback,
                               cfunc, 0)


    def registerFunctions(self):
        try:
            dll = CDLL("wlmData.dll")
        except:
            log.exception("Couldn't instantiate dll object")
            dll = None
            return dll

        self.dllInstantiate = dll.Instantiate
        self.dllInstantiate.restype = c_uint
        # self.dllInstantiate.argtypes = [c_uint, c_uint, c_uint, c_uint]

        self.dllGetFrequency = dll.GetFrequency
        self.dllGetFrequency.restype = c_uint
        self.dllGetFrequency.argtypes = [c_uint, c_uint, c_uint, c_uint]

        self.dllGetPowerNum = dll.GetPowerNum
        self.dllGetPowerNum.restype = c_uint
        self.dllGetPowerNum.argtypes = [c_uint, c_uint, c_uint, c_uint]

        self.dllGetResultMode = dll.GetResultMode
        self.dllGetResultMode.restype = c_uint
        self.dllGetResultMode.argtypes = [c_uint, c_uint, c_uint, c_uint]

        self.dllSetResultMode = dll.SetResultMode
        self.dllSetResultMode.restype = c_uint
        self.dllSetResultMode.argtypes = [c_uint, c_uint, c_uint, c_uint]

        self.dllGetExposureMode = dll.GetExposureMode
        self.dllGetExposureMode.restype = c_uint
        self.dllGetExposureMode.argtypes = [c_uint, c_uint, c_uint, c_uint]





        return dll


# Needs to be at the bottom to prevent
# cyclical definitions. This makes me think
# I'm doing things wrong, but I dunno what else.
try:
    from .fakeInstruments import setPrintOutput, getCls
except ImportError:
    print("got the import error")



if __name__ == '__main__':
    import interactivePG as pg
    a = ESP300("GPIB0::2::INSTR")
    print(a.position)
    a.position-=20
    print(a.position)







