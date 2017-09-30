from ctypes import *
from ctypes.wintypes import *
"""
This file is for the FTD2xx driver used by the
"""

FT_OK = 0
FT_INVALID_HANDLE = 1
FT_DEVICE_NOT_FOUND = 2
FT_DEVICE_NOT_OPENED = 3
FT_IO_ERROR = 4
FT_INSUFFICIENT_RESOURCES = 5
FT_INVALID_PARAMETER = 6
FT_INVALID_BAUD_RATE = 7
FT_DEVICE_NOT_OPENED_FOR_ERASE = 8
FT_DEVICE_NOT_OPENED_FOR_WRITE = 9
FT_FAILED_TO_WRITE_DEVICE = 10
FT_EEPROM_READ_FAILED = 11
FT_EEPROM_WRITE_FAILED = 12
FT_EEPROM_ERASE_FAILED = 13
FT_EEPROM_NOT_PRESENT = 14
FT_EEPROM_NOT_PROGRAMMED = 15
FT_INVALID_ARGS = 16
FT_OTHER_ERROR = 17

FT_OPEN_BY_SERIAL_NUMBER = 1
FT_OPEN_BY_DESCRIPTION = 2

FT_LIST_NUMBER_ONLY = 0x80000000
FT_LIST_BY_INDEX = 0x40000000
FT_LIST_ALL = 0x20000000

FT_DEVICE_232BM = 0
FT_DEVICE_232AM = 1
FT_DEVICE_100AX = 2
FT_DEVICE_UNKNOWN = 3


FT_BITS_8 = 8
FT_BITS_7 = 7

FT_STOP_BITS_1 = 0
FT_STOP_BITS_2 = 2

FT_PARITY_NONE = 0
FT_PARITY_ODD = 1
FT_PARITY_EVEN = 2
FT_PARITY_MARK = 3
FT_PARITY_SPACE = 4

FT_FLOW_NONE = 0x0000
FT_FLOW_RTS_CTS = 0x0100
FT_FLOW_DTR_DSR = 0x0200
FT_FLOW_XON_XOFF = 0x0400

FT_PURGE_RX = 1
FT_PURGE_TX = 2

FT_EVENT_RXCHAR = 1
FT_EVENT_MODEM_STATUS = 2

inverseErrors = {
    "FT_OK": 0,
    "FT_INVALID_HANDLE": 1,
    "FT_DEVICE_NOT_FOUND": 2,
    "FT_DEVICE_NOT_OPENED": 3,
    "FT_IO_ERROR": 4,
    "FT_INSUFFICIENT_RESOURCES": 5,
    "FT_INVALID_PARAMETER": 6,
    "FT_INVALID_BAUD_RATE": 7,
    "FT_DEVICE_NOT_OPENED_FOR_ERASE": 8,
    "FT_DEVICE_NOT_OPENED_FOR_WRITE": 9,
    "FT_FAILED_TO_WRITE_DEVICE": 10,
    "FT_EEPROM_READ_FAILED": 11,
    "FT_EEPROM_WRITE_FAILED": 12,
    "FT_EEPROM_ERASE_FAILED": 13,
    "FT_EEPROM_NOT_PRESENT": 14,
    "FT_EEPROM_NOT_PROGRAMMED": 15,
    "FT_INVALID_ARGS": 16,
    "FT_OTHER_ERROR": 17
}

errors = {v:k for k,v in inverseErrors.items()}


class FTD2XX(object):
    def __init__(self):
        self.registerFunctions()

    def getNumDevices(self):
        # numDevs = c_ulong(20)
        numDevs = c_void_p(3)
        ret = self.dllListDevices(numDevs, None, FT_LIST_NUMBER_ONLY)

        print("Return value: {} ({})".format(ret, errors[ret]))
        if ret == FT_OK:
            print("Number of devices: {}".format(numDevs.value))
            return numDevs.value


    def getInformationByIndex(self, idx=0, returnMode = FT_OPEN_BY_DESCRIPTION):
        p1 = c_void_p(idx)
        p2 = c_void_p(1)

        ret = self.dllListDevices(p1, p2, FT_LIST_BY_INDEX|returnMode)
        print("\nGetting Information")
        print(errors[ret])
        print(p1)
        print(p2)

    def getAllInformation(self):
        p1 = c_void_p(0)
        p2 = c_void_p(0)

        ret = self.dllListDevices(p1, p2, FT_LIST_ALL|FT_OPEN_BY_DESCRIPTION)
        print("\nGetting all information")
        print(errors[ret])
        print(p1)
        print(p2)


    def open_(self):
        # HEY! YOU!
        # Are the drivers installed and the software opens,
        # But you can't seem to get anything from the device?
        # (Won't read a goddamn thing?)
        # May be because the computer has multiple FTDI devices
        # connected, which changes the index needed to open
        # You can try to find out

        self.handle = c_ulong(0)
        print("opened: {}".format(self.dllOpen(0, self.handle)))
        print("Handle:", self.handle)

        # Need toset up other things to talk to the device properly
        # I don't think it should be done ever again, so they're not
        # extra functions. Looked at Jova's VI's for values
        print(errors[self.dll.FT_SetLatencyTimer(self.handle, c_ubyte(1))])

        print(errors[self.dll.FT_SetBaudRate(self.handle, c_ulong(230000))])

        print(errors[self.dll.FT_SetDataCharacteristics(self.handle,
                                                 c_ubyte(8), c_ubyte(0), c_ubyte(0))])


    def registerFunctions(self):
        try:
            self.dll = CDLL("ftd2XX64.dll")
        except OSError:
            self.dll = CDLL("ftd2XX.dll")

        self.dllOpen = self.dll.FT_Open
        self.dllOpen.argtypes = [c_ulong, POINTER(c_ulong)]
        self.dllOpen.restype = c_int

        self.dllClose = self.dll.FT_Close
        self.dllClose.argtypes = [c_ulong]
        self.dllClose.restype = c_int

        self.dllListDevices = self.dll.FT_ListDevices
        self.dllListDevices.argtypes = [POINTER(c_void_p), POINTER(c_void_p), c_ulong]
        self.dllListDevices.restype = c_int

        """
        FT_GetStatus
            Gets the device status including number of characters in the receive
            queue, number of characters in the transmit queue, and the current 
            event status.

            Parameters

            ftHandle
            Handle of the device to read.

            lpdwAmountInRxQueue
            Pointer to a variable of type DWORD which receives the number of 
            characters in the receive queue.

            lpdwAmountInTxQueue
            Pointer to a variable of type DWORD which receives the number of 
            characters in the transmit queue.

            lpdwEventStatus
            Pointer to a variable of type DWORD which receives the current state
            of the event status.
        """
        self.dllGetStatus = self.dll.FT_GetStatus
        self.dllGetStatus.argtypes = [
            c_ulong, POINTER(c_ulong), POINTER(c_ulong),
            POINTER(c_ulong)]
        self.dllGetStatus.restype = c_int

        """
        FT_Write
        Write data to the device.

        Parameters

        ftHandle
        Handle of the device to write.

        lpBuffer
        Pointer to the buffer that contains the data to be written to the device.

        dwBytesToWrite
        Number of bytes to write to the device.

        lpdwBytesWritten
        Pointer to a variable of type DWORD which receives the number of bytes 
        written to the device.

        Return Value
        FT_OK if successful, otherwise the return value is an FT error code.
        """
        self.dllWrite = self.dll.FT_Write
        self.dllWrite.argtypes = [
            c_ulong, POINTER(c_ubyte),
            c_ulong, POINTER(c_ulong)]
        self.dllWrite.restype = c_int

        """
        FT_Read
        Read data from the device.

        Parameters
        ftHandle
        Handle of the device to read.

        lpBuffer
        Pointer to the buffer that receives the data from the device.

        dwBytesToRead
        Number of bytes to be read from the device.
        packet[7] = 
        lpdwBytesReturned
        Pointer to a variable of type DWORD which receives the number of bytes 
        read from the device.

        Return Value
        FT_OK if successful, FT_IO_ERROR otherwise.
        """
        self.dllRead = self.dll.FT_Read
        self.dllRead.argtypes = [
            c_ulong, POINTER(c_ubyte),
            c_ulong, POINTER(c_ulong)]
        self.dllRead.restype = c_int




if __name__ == '__main__':
    ftd = FTD2XX()
    # ftd.getNumDevices()
    ftd.getInformationByIndex(0)
    # ftd.open_()
    ftd.getAllInformation()