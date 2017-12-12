import logging
import time
log = logging.getLogger("Instruments")
logging._handlerList[2]().setLevel(logging.DEBUG)
from ctypes import *
from ctypes import wintypes
from enum import Enum
from ctypes import POINTER, Structure
import os

if os.name == 'nt':

    kernel32 = WinDLL('kernel32', use_last_error=True)

    def check_bool(result, func, args):
        if not result:
            raise WinError(get_last_error())
        return args

    kernel32.LoadLibraryExW.errcheck = check_bool
    kernel32.LoadLibraryExW.restype = wintypes.HMODULE
    kernel32.LoadLibraryExW.argtypes = (wintypes.LPCWSTR,
                                        wintypes.HANDLE,
                                        wintypes.DWORD)

class CDLLEx(CDLL):
    DONT_RESOLVE_DLL_REFERENCES = 0x00000001
    LOAD_LIBRARY_AS_DATAFILE = 0x00000002
    LOAD_WITH_ALTERED_SEARCH_PATH = 0x00000008
    LOAD_IGNORE_CODE_AUTHZ_LEVEL = 0x00000010  # NT 6.1
    LOAD_LIBRARY_AS_IMAGE_RESOURCE = 0x00000020  # NT 6.0
    LOAD_LIBRARY_AS_DATAFILE_EXCLUSIVE = 0x00000040  # NT 6.0

    # These cannot be combined with LOAD_WITH_ALTERED_SEARCH_PATH.
    # Install update KB2533623 for NT 6.0 & 6.1.
    LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR = 0x00000100
    LOAD_LIBRARY_SEARCH_APPLICATION_DIR = 0x00000200
    LOAD_LIBRARY_SEARCH_USER_DIRS = 0x00000400
    LOAD_LIBRARY_SEARCH_SYSTEM32 = 0x00000800
    LOAD_LIBRARY_SEARCH_DEFAULT_DIRS = 0x00001000
    def __init__(self, name, mode=0, handle=None,
                 use_errno=True, use_last_error=False):
        if os.name == 'nt' and handle is None:
            handle = kernel32.LoadLibraryExW(name, None, mode)
        super(CDLLEx, self).__init__(name, mode, handle,
                                     use_errno, use_last_error)

class WinDLLEx(WinDLL):
    def __init__(self, name, mode=0, handle=None,
                 use_errno=False, use_last_error=True):
        if os.name == 'nt' and handle is None:
            handle = kernel32.LoadLibraryExW(name, None, mode)
        super(WinDLLEx, self).__init__(name, mode, handle,
                                       use_errno, use_last_error)

"""
The structures for getting information from the device
"""
class TLI_DeviceInfo(Structure):
    _fields_ = [
        ("typeID", wintypes.DWORD),
        ("description", c_char * 65),
        ("serialNo", c_char*9),
        ("PID", wintypes.DWORD),
        ("isKnownType", c_bool),
        ("motorType", c_int),
        ("isPiezeo", c_bool),
        ("isLaser", c_bool),
        ("isCustomType", c_bool),
        ("isRack", c_bool),
        ("maxChannels", c_short)
    ]
    def __str__(self):
        st = f"""        "typeID": {self.typeID}
        "description": {self.description}
        "serialNo": {self.serialNo}
        "PID": {self.PID}
        "isKnownType": {self.isKnownType}
        "motorType": {self.motorType}
        "isPiezeo": {self.isPiezeo}
        "isLaser": {self.isLaser}
        "isCustomType": {self.isCustomType}
        "isRack": {self.isRack}
        "maxChannels": {self.maxChannels}"""
        return st

class MOT_JogModes(object):
    MOT_JogModeUndefined = 0x00 # < Undefined
    MOT_Continuous = 0x01 # < Continuousjogging
    MOT_SingleStep = 0x02 # < Jog 1 step at a time

class MOT_StopModes(object):
    MOT_StopModeUndefined = 0x00 # < Undefined
    MOT_Immediate = 0x01 # < Stops immediate
    MOT_Profiled = 0x02 # < Stops using a velocity profile

class MOT_VelocityParameters(Structure):
    _fields_ = [
        ("minVelocity", c_int),
        ("maxVelocity", c_int),
        ("acceleration", c_int)
    ]

class MOT_JogParameters(Structure):
    _fields_ = [
        ("mode", c_short),
        ("stepSize", c_uint),
        ("velParams", MOT_VelocityParameters),
        ("stopMode", c_short),
    ]

class MOT_MotorTypes(Enum):
    MOT_NotMotor = 0
    MOT_DCMotor = 1
    MOT_StepperMotor = 2
    MOT_BrushlessMotor = 3
    MOT_CustomMotor = 100

class MOT_LimitSwitchParameters(Structure):
    _fields_ = [
        ("clockwiseHardwareLimit", wintypes.WORD),
        ("anticlockwiseHardwareLimit", wintypes.WORD),
        ("clockwisePosition", wintypes.DWORD),
        ("anticlockwisePosition", wintypes.DWORD),
        ("softLimitMode", wintypes.WORD),
    ]

class MOT_HomingParameters(Structure):
    _fields_ = [
        ("direction", c_short), # 0, undef; 1 forward; 2 rev
        ("limitSwitch", c_short), #0 undef; 1 rev; 4 forward
        ("velocity", c_uint),
        ("offsetDistance", c_uint)
    ]

class ThorlabsIntegratedStepper(object):
    serialNo = None
    def __init__(self):
        self.dll = self.registerFunctions()
        # keep track of whether we're open or not
        # 0 is closed, -1 is open with no polling time, >0 is the polling time
        # (so I can know to automatically close the polling time on close)
        self._opened = False
        try:
            ret = self.dll.TLI_BuildDeviceList()
        except Exception:
            log.exception("Error building device list!")
        if ret:
            log.warning("Bad return from building device list: {}".format(ret))

    def getDeviceInfo(self):
        if self.serialNo is None:
            raise RuntimeError("Need a serial number")
        info = TLI_DeviceInfo()
        self.dll.TLI_GetDeviceInfo(self.serialNo, info)
        return info

    def waitForStop(self, waitOn = "move", timeout=45e3, callback = None):
        """
        Wait for the motor to stop moving. Copied from manual.
        Queries to make sure the device isn't moving

        The motor doesn't have a generic way to tell if it's moving, i.e. homing and
        moving to a position are different flags. Need to pass which one you're
        waiting on here "move", or "home", as the waitOn param

        timeout is in ms. Pass 0 to not enable a timeout.
        callback is a function to call at each step, so you can
           sill-ily updated a spinbox or something to show it moving
        Returns True if successful, 0 if timeout.
        """
        if not hasattr(callback, "__call__"):
            callback = lambda x: None

        if waitOn.lower() not in ["move", "home"]:
            raise RuntimeError("Must wait on a 'home'ing, or 'move'ing, not", waitOn)

        msgIdCheck = ["home", "move"].index(waitOn.lower())

        messageType, messageId, messageData = self._waitForMessage()
        startTime = time.time()
        if timeout:
            while (time.time() - startTime)*1e3 < timeout and \
                    (messageType != 2 or messageId != msgIdCheck):
                messageType, messageId, messageData = self._waitForMessage()
                callback(self.getPosition())
            if messageType != 2 or messageId != msgIdCheck:
                log.warning("Timeout occurred in waiting loop!")
                return False
            return True
        while messageType != 2 or messageId != msgIdCheck:
            messageType, messageId, messageData = self._waitForMessage()
            callback(self.getPosition())

        return True

    def _waitForMessage(self):
        messageType, messageId, messageData = wintypes.WORD(0), wintypes.WORD(0), wintypes.DWORD(0)
        self.dll.ISC_WaitForMessage(self.serialNo, messageType, messageId, messageData)
        return messageType.value, messageId.value, messageData.value

    def open(self, startPolling = 200):
        """
        Open the device. If startPolling isn't False, start the internal polling
        of the device

        Note: I think this is so that the DLL will internally poll the motor to get
        the latest parameters, preventing you from needing to request them?
        :param startPolling: Time to poll. Docs use 200ms
        :return:
        """
        if self._opened:
            log.debug("Device is already opened")
            return True
        ret = self.dll.ISC_Open(self.serialNo)
        if ret:
            log.warning("Error opening the device: {}".format(ret))
            return False
        self._opened = -1

        ## Don't know what's going on with this function. Sometimes throws a windows error,
        ## sometimes doesn't work at all.
        # if not self.dll.ISC_LoadSettings(self.serialNo):
        #     log.warning("Error loading settings")

        ## Instead, I ripped a bunch of values from looking at the Kinesis software
        ## logs and did all the same calls here. presumably, these are all default
        ## values.
        self.dll.ISC_SetPotentiometerParams(self.serialNo, 0, 20,  1466016)
        self.dll.ISC_SetPotentiometerParams(self.serialNo, 1, 50,  2199023)
        self.dll.ISC_SetPotentiometerParams(self.serialNo, 2, 80,  2932031)
        self.dll.ISC_SetPotentiometerParams(self.serialNo, 3, 100, 3665039)

        jogParams = MOT_JogParameters()
        jogParams.mode = 2
        jogParams.stepSize = 682667
        jogParams.stopMode = 2
        jogParams.velParams.acceleration = 22530
        jogParams.velParams.maxVelocity = 109951163
        jogParams.velParams.minVelocity = 0
        self.dll.ISC_SetJogParamsBlock(self.serialNo, byref(jogParams))

        limitSwitchParams = MOT_LimitSwitchParameters()
        limitSwitchParams.clockwiseHardwareLimit = 136533
        limitSwitchParams.anticlockwiseHardwareLimit = 136533
        limitSwitchParams.clockwisePosition = 4
        limitSwitchParams.anticlockwisePosition = 1
        limitSwitchParams.softLimitMode = 1
        self.dll.ISC_SetLimitSwitchParamsBlock(self.serialNo, byref(limitSwitchParams))
        self.dll.ISC_SetTriggerSwitches(self.serialNo, c_byte(0))

        self.dll.ISC_SetMotorParamsExt(self.serialNo, 200, 120, 360)

        if startPolling:
            if self.dll.ISC_StartPolling(self.serialNo, startPolling):
                self._opened = startPolling
                time.sleep(startPolling/1000.)
            else:
                log.warning("Error starting the dll polling!")

        return True

    def close(self):
        if not self._opened:
            log.debug("Device isn't open")
            return False
        # I've opened it with polling
        if self._opened > 0:
            self.dll.ISC_StopPolling(self.serialNo)
        self.dll.ISC_Close(self.serialNo)
        self._opened = False

    def home(self, waitForStop = True, *args, **kwargs):
        """
        home the motor
        :param waitForStop: wait for the motor to stop in this thread
        :return:
        """
        ret = self.dll.ISC_Home(self.serialNo)
        if ret:
            log.warning("Error homing device, {}".format(ret))
            return False
        if waitForStop:
            ret = self.waitForStop(waitOn = "home", *args, **kwargs)
            if self._opened > 1:
                # for some reason, the wait loop for homing isn't quite
                # synchronous with the dll's polling loop, so wait the
                # polling time to make sure it's updated
                time.sleep(self._opened/1000.)
            return ret
        return True

    def setHomeOffset(self, offset = 0):
        """
        After the motor homes, it can be told to move to some offset.
        Set that offset here.
        :param offset:
        :return:
        """
        offset = self._realToDevice(offset, "pos")
        params = MOT_HomingParameters()
        self.dll.ISC_GetHomingParamsBlock(self.serialNo, params)
        params.offsetDistance = offset
        self.dll.ISC_SetHomingParamsBlock(self.serialNo, params)

    def getHomeOffset(self):
        """
        After the motor homes, it can be told to move to some offset.
        Get that offset here.
        :param offset:
        :return:
        """
        params = MOT_HomingParameters()
        self.dll.ISC_GetHomingParamsBlock(self.serialNo, params)
        return self._deviceToReal(params.offsetDistance)

    def moveAbsolute(self, position = None, waitForStop = True, *args, **kwargs):
        """
        move the motor to an absolute position (deg)
        :param waitForStop: wait for the motor to stop in this thread
        :return:
        """
        if position is None:
            raise RuntimeError("Need to pass a position argument")
        position = self._realToDevice(position, "pos")
        ret = self.dll.ISC_MoveToPosition(self.serialNo, position)
        if ret:
            log.warning("Error moving device, {}".format(ret))
            return False
        if waitForStop:
            return self.waitForStop(waitOn = "move", *args, **kwargs)
        return True

    def getPosition(self):
        pos = self.dll.ISC_GetPosition(self.serialNo)
        pos = self._deviceToReal(pos, "pos")
        return pos

    def setPosition(self, pos = 0):
        pos = self._realToDevice(pos, "pos")
        ret = self.dll.ISC_SetPositionCounter(self.serialNo, pos)
        if ret:
            log.warning(f"Error setting position counter: {ret}")

    def getVelocity(self):
        _, vel = self._getVelParams()
        vel = self._deviceToReal(vel, "vel")
        return vel

    def getAcceleration(self):
        acc, _ = self._getVelParams()
        acc = self._deviceToReal(acc, "acc")
        return acc

    def _getVelParams(self):
        """
        get the velocity and acceleration.
        Note: this is a protected function to separate it from the
        getVelocity/getAcceleration, because this returns
        _device_ units, while the former two return _real_ units. There needs to be the
        distinction of where units get converted, and I figured I'd do it in the public
        members, so this function can work with the _setVelParams without doing several
        calls, potentially accumulating precision errors.
        :return:
        """
        acc, vel = c_int(0), c_int(0)
        ret = self.dll.ISC_GetVelParams(self.serialNo, acc, vel)
        if ret:
            log.warning(f"Error geting velocity parameters {ret}")
            return -1, -1
        return acc.value, vel.value

    def setVelocity(self, vel):
        vel = self._realToDevice(vel, "vel")
        return self._setVelParams(vel=vel)

    def setAcceleration(self, acc):
        acc = self._realToDevice(acc, "acc")
        return self._setVelParams(acc = acc)

    def _setVelParams(self, acc = None, vel = None):
        """
        Set the velocity and acceleration.
        Note: this is a protected function to separate it from the
        setVelocity/setAcceleration, because this expects acc/vel to be in
        _device_ units, while the former two expect _real_ units, and it's not
        immediately clear how to tell which it is, without silly boilerplate
        stuff.
        :param acc:
        :param vel:
        :return:
        """
        oldAcc, oldVel = self._getVelParams()
        if acc is None: acc = oldAcc
        if vel is None: vel = oldVel

        # acc, vel = c_int(acc), c_int(vel)
        ret = self.dll.ISC_SetVelParams(self.serialNo, acc, vel)
        if ret:
            log.warning(f"Error seting velocity parameters {ret}")
            return False
        return True

    def _realToDevice(self, val, mode = "pos"):
        """
        convert a real world unit to a device unit
        :param val: the value to convert
        :param mode: "pos", "vel", "acc", or 0, 1, 2, mapped accordingly
        :return: the value in device units
        """
        if isinstance(mode, str):
            if "pos" in mode:
                mode = 0
            elif "vel" in mode:
                mode = 1
            elif "acc" in mode:
                mode = 2
            else:
                raise RuntimeError(f"Invalid string passed: {mode}")

        if mode not in [0, 1, 2]:
            raise RuntimeError(f"Invalid mode flag passed: {mode}")

        # The dll function returns error code 20. Tech from thorlabs hasn't been able
        # to help me. I found these card-coded values from messing around with the
        # Kinesis software. The position number is steps/rev * gear ratio * uSteps.
        # I don't know where the acc/vel come from
        if mode == 0:
            return int(136533 * val)
        elif mode == 1:
            return int(7330077.5 * val)
        else:
            return int(1502 * val)

        # device = c_long(0)
        # ret = self.dll.ISC_GetDeviceUnitFromRealValue(self.serialNo, val, device, mode)
        # if ret:
        #     log.warning(f"Error converting real unit to device unit: {ret}")
        #     log.warning(f"\tWanted to convert {val} of {mode}")
        #
        # return device.value

    def _deviceToReal(self, val, mode = "pos"):
        """
        convert a device unit to a real world unit
        :param val: the value to convert
        :param mode: "pos", "vel", "acc", or 0, 1, 2, mapped accordingly
        :return: the value in real world units
        """
        if isinstance(mode, str):
            if "pos" in mode:
                mode = 0
            elif "vel" in mode:
                mode = 1
            elif "acc" in mode:
                mode = 2
            else:
                raise RuntimeError(f"Invalid string passed: {mode}")

        if mode not in [0, 1, 2]:
            raise RuntimeError(f"Invalid mode flag passed: {mode}")

        # The dll function returns error code 20. Tech from thorlabs hasn't been able
        # to help me. I found these card-coded values from messing around with the
        # Kinesis software. The position number is steps/rev * gear ratio * uSteps.
        # I don't know where the acc/vel come from
        if mode == 0:
            return val/136533
        elif mode == 1:
            return val/7330077.5
        else:
            return val/1502

        # real = c_double(0)
        # ret = self.dll.ISC_GetRealValueFromDeviceUnit(self.serialNo, val, real, mode)
        # if ret:
        #     log.warning(f"Error converting device unit to real unit: {ret}")
        #
        # return real.value

    def registerFunctions(self):
        try:
            dll = CDLL("Thorlabs.MotionControl.IntegratedStepperMotors.dll")
        except OSError:
            dll = CDLLEx(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.IntegratedStepperMotors.dll",
                         CDLLEx.LOAD_WITH_ALTERED_SEARCH_PATH)

        """
        TLI_BuildDeviceList
        Build the DeviceList. 

        This function builds an internal collection of all devices found on the USB that are not currently open. 
        NOTE, if a device is open, it will not appear in the list until the device has been closed. 
                
        Returns
            The error code (see Error Codes) or zero if successful. 
        """
        dll.TLI_BuildDeviceList.argtypes = None
        dll.TLI_BuildDeviceList.restypes = c_short

        """
        TLI_GetDeviceInfo 
        Get the device information from the USB port. 

        The Device Info is read from the USB port not from the device itself.
        Parameters
            serialNo The serial number of the device.  
            info The TLI_DeviceInfo device information.  
        Returns
            1 if successful, 0 if not. 
        """
        dll.TLI_GetDeviceInfo.argtypes = [c_char_p, POINTER(TLI_DeviceInfo)]
        dll.TLI_GetDeviceInfo.restypes = c_short

        """
        TLI_GetDeviceListSize
            Gets the device list size. 
        Returns
            Number of devices in device list.  
        """
        dll.TLI_GetDeviceListSize.argtypes = None
        dll.TLI_GetDeviceListSize.restypes = c_short

        """
        ISC_Open 
            Open the device for communications.
        Parameters
            serialNo The serial no of the device to be connected.  
        Returns
            The error code (see Error Codes) or zero if successful. 
        """
        dll.ISC_Open.argtypes = [c_char_p]
        dll.ISC_Open.restypes = c_short

        """
        ISC_Close 
            Disconnect and close the device. 
        Parameters
            serialNo The serial no of the device to be disconnected.  
        Returns
        """
        dll.ISC_Close.argtypes = [c_char_p]
        dll.ISC_Close.restypes = None

        """
        ISC_WaitForMessage 
            Wait for next MessageQueue item. 
        Parameters
            serialNo The device serial no.  
            messageType The address of the parameter to receive the message Type.  
            messageID The address of the parameter to receive the message id.  
            messageData The address of the parameter to receive the message data.  

        Returns
            true if successful, false if not. 
        """
        dll.ISC_WaitForMessage.argtypes = [c_char_p, POINTER(wintypes.WORD), POINTER(wintypes.WORD), POINTER(wintypes.DWORD)]
        dll.ISC_WaitForMessage.restypes = c_bool

        """
        ISC_StartPolling 
            Starts the internal polling loop which continuously requests position and status.  
        Parameters
            serialNo The device serial no.  
            milliseconds The milliseconds polling rate.  
        Returns
            true if successful, false if not. 
        """
        dll.ISC_StartPolling.argtypes = [c_char_p, c_int]
        dll.ISC_StartPolling.restypes = c_bool

        """
        ISC_StopPolling 
            Stops the internal polling loop. 
        Parameters
            serialNo The device serial no.  
        Returns
            None
        """
        dll.ISC_StopPolling.argtypes = [c_char_p]
        dll.ISC_StopPolling.restypes = None

        """
        ISC_LoadSettings  
            Update device with stored settings. 
        Parameters
            serialNo The device serial no.  
        Returns
            true if successful, false if not. 
        """
        dll.ISC_LoadSettings.argtypes = [c_char_p]
        dll.ISC_LoadSettings.restypes = c_bool

        """
        ISC_SetMotorParamsExt  
            Sets the motor stage parameters. These parameters, when combined define the
            stage motion in terms of Real World Units. (mm or degrees) The real world
            unit is defined from stepsPerRev * gearBoxRatio / pitch.

        Parameters
            serialNo The device serial no.  
            stepsPerRev The steps per revolution.  
            gearBoxRatio The gear box ratio.  
            pitch The pitch.  
 
        Returns
            true if successful, false if not. 
        """
        dll.ISC_SetMotorParamsExt.argtypes = [c_char_p, c_double, c_double, c_double]
        dll.ISC_SetMotorParamsExt.restypes = c_short

        """
        ISC_SetMotorParams  
            Sets the motor stage parameters. These parameters, when combined define the
            stage motion in terms of Real World Units. (mm or degrees) The real world
            unit is defined from stepsPerRev * gearBoxRatio / pitch.

        Parameters
            serialNo The device serial no.  
            stepsPerRev The steps per revolution.  
            gearBoxRatio The gear box ratio.  
            pitch The pitch.  
 
        Returns
            true if successful, false if not. 
        """
        dll.ISC_SetMotorParams.argtypes = [c_char_p, c_long, c_long, c_double]
        dll.ISC_SetMotorParams.restypes = c_short

        """
        ISC_GetMotorParamsExt  
            Gets the motor stage parameters. These parameters, when combined define the
            stage motion in terms of Real World Units. (mm or degrees) The real world
            unit is defined from stepsPerRev * gearBoxRatio / pitch.

        Parameters
            serialNo The device serial no.  
            stepsPerRev The steps per revolution.  
            gearBoxRatio The gear box ratio.  
            pitch The pitch.  
 
        Returns
            true if successful, false if not. 
        """
        dll.ISC_GetMotorParamsExt.argtypes = [c_char_p, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
        dll.ISC_GetMotorParamsExt.restypes = c_short

        """
        ISC_GetMotorParams  
            Gets the motor stage parameters. These parameters, when combined define the
            stage motion in terms of Real World Units. (mm or degrees) The real world
            unit is defined from stepsPerRev * gearBoxRatio / pitch.

        Parameters
            serialNo The device serial no.  
            stepsPerRev The steps per revolution.  
            gearBoxRatio The gear box ratio.  
            pitch The pitch.  
 
        Returns
            true if successful, false if not. 
        """
        dll.ISC_GetMotorParams.argtypes = [c_char_p, POINTER(c_long), POINTER(c_long), POINTER(c_double)]
        dll.ISC_GetMotorParams.restypes = c_short

        """
        ISC_GetPosition 
            Get the current position. The current position is the last recorded position.
            The current position is updated either by the polling mechanism or by 
            calling RequestPosition or RequestStatus.

        Parameters
            serialNo The device serial no.  
        Returns
            The current position in Device Units. 
        """
        dll.ISC_GetPosition.argtypes = [c_char_p]
        dll.ISC_GetPosition.restypes = c_int

        """
        ISC_MoveToPosition 
            Move the device to the specified position (index). The motor may need to be
            Homed before a position can be set. 

        Parameters
            serialNo The device serial no.  
            index The position in Device Units.  
        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_MoveToPosition.argtypes = [c_char_p, c_int]
        dll.ISC_MoveToPosition.restypes = c_short

        """
        ISC_StopImmediate 
            Stop the current move immediately (with risk of losing track of position). 

        Parameters
            serialNo The device serial no.  
        Returns
            The error code (see Error Codes) or zero if successful.  
        """
        dll.ISC_StopImmediate.argtypes = [c_char_p]
        dll.ISC_StopImmediate.restypes = c_short

        """
        ISC_StopProfiled 
            Stop the current move using the current velocity profile.  

        Parameters
            serialNo The device serial no.  
        Returns
            The error code (see Error Codes) or zero if successful.  
        """
        dll.ISC_StopProfiled.argtypes = [c_char_p]
        dll.ISC_StopProfiled.restypes = c_short

        """
        ISC_GetVelParams 
            Gets the move velocity parameters. 

        Parameters
            serialNo The device serial no.  
            acceleration Address of the parameter to receive the acceleration value in Device Units.  
            maxVelocity Address of the parameter to receive the maximum velocity value in Device Units.  

        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_GetVelParams.argtypes = [c_char_p, POINTER(c_int), POINTER(c_int)]
        dll.ISC_GetVelParams.restypes = c_short

        """
        ISC_SetVelParams 
            Sets the move velocity parameters. 

        Parameters
            serialNo The device serial no.  
            acceleration The new acceleration value in Device Units.  
            maxVelocity The new maximum velocity value in Device Units.  

        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_SetVelParams.argtypes = [c_char_p, c_int, c_int]
        dll.ISC_SetVelParams.restypes = c_short

        """
        ISC_Home 
            Home the device. Homing the device will set the device to a known state 
            and determine the home position,

        Parameters
            serialNo The device serial no.  

        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_Home.argtypes = [c_char_p]
        dll.ISC_Home.restypes = c_short

        """
        ISC_SetHomingParamsBlock 
            Set the homing parameters. 

        Parameters
            serialNo The device serial no.  
            homingParams Address of the new homing parameters.  

        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_SetHomingParamsBlock.argtypes = [c_char_p, POINTER(MOT_HomingParameters)]
        dll.ISC_SetHomingParamsBlock.restypes = c_short

        """
        ISC_GetHomingParamsBlock 
            Get the homing parameters. 

        Parameters
            serialNo The device serial no.  
            homingParams Address of the new homing parameters.  

        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_GetHomingParamsBlock.argtypes = [c_char_p, POINTER(MOT_HomingParameters)]
        dll.ISC_GetHomingParamsBlock.restypes = c_short

        """
        ISC_SetPositionCounter 
            Set the Position Counter. 
            Setting the position counter will locate the current position. 
            Setting the position counter will effectively define the home position of a motor. 

        Parameters
            serialNo The device serial no.  
            count Position count in Device Units.    

        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_SetPositionCounter.argtypes = [c_char_p, c_long]
        dll.ISC_SetPositionCounter.restypes = c_short

        """
        ISC_GetRealValueFromDeviceUnit 
            Converts a devic unit to a real worl unit. 

        Parameters
            serialNo The serial no.  
            device_unit The device unit.  
            real_unit The real unit.  
            unitType Type of the unit.
                Distance 0  
                Velocity 1  
                Acceleration 2  

        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_GetRealValueFromDeviceUnit.argtypes = [c_char_p, c_int, POINTER(c_double), c_int]
        dll.ISC_GetRealValueFromDeviceUnit.restypes = c_short

        """
        ISC_GetDeviceUnitFromRealValue  
            Converts a devic unit to a real worl unit. [sic]

        Parameters
            serialNo The serial no.  
            real_unit  The real unit.  
            real_unit The device unit.  
            unitType Type of the unit.
                Distance 0  
                Velocity 1  
                Acceleration 2  

        Returns
            The error code (see Error Codes) or zero if move successfully started.  
        """
        dll.ISC_GetDeviceUnitFromRealValue.argtypes = [c_char_p, c_double, POINTER(c_int), c_int]
        dll.ISC_GetDeviceUnitFromRealValue.restypes = c_short

        """
        ISC_TimeSinceLastMsgReceived  
            Gets the time in milliseconds since tha last message was received from the device. 
            This can be used to determine whether communications with the device is still good


        Parameters
            serialNo The device serial no.  
            lastUpdateTimeMS The time since the last message was received in milliseconds.  


        Returns
            True if monitoring is enabled otherwize False.   
        """
        dll.ISC_TimeSinceLastMsgReceived.argtypes = [c_char_p, POINTER(c_int)]
        dll.ISC_TimeSinceLastMsgReceived.restypes = c_bool

        """
        ISC_EnableLastMsgTimer  
            Enables the last message monitoring timer. 
            This can be used to determine whether communications with the device is still good

        Parameters
            serialNo The device serial no.  
            enable True to enable monitoring otherwise False to disable.  
            lastMsgTimeout The last message error timeout in ms. 0 to disable.  

        Returns
            None   
        """
        dll.ISC_EnableLastMsgTimer.argtypes = [c_char_p, c_bool, c_long]
        dll.ISC_EnableLastMsgTimer.restypes = None

        return dll


class K10CR1(ThorlabsIntegratedStepper):
    serialNo = b"55000760"


if __name__ == '__main__':
    k = K10CR1()
    # print(k.dll.TLI_BuildDeviceList())
    print(k.getDeviceInfo())
    print(k.dll.TLI_GetDeviceListSize())

    print("Open", k.open())

    print("acc/vel", k.getVelocity(), k.getAcceleration())

    # k.setHomeOffset(-3)
    print("home")
    k.home()
    print("pos", k.getPosition())
    time.sleep(.2)
    print("pos", k.getPosition())




    print("closing", k.close())
































