# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 11:24:38 2015

@author: dvalovcin
"""

import numpy as np
import matplotlib.pylab as plt
from matplotlib import rcParams
from ctypes import *
from struct import *
import time

# cyclical left bitshift for calulating LRC
rol = lambda val, r_bits=1, max_bits=8: \
    (val << r_bits%max_bits) & (2**max_bits-1) | \
    ((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits)))
    
# Longitudinal redundancy check calculation. See manual
def calcLRC(byteArr):
    a = bytearray(byteArr)
    lrc = 0xaa
    for i in a[:-1]:
        lrc = (lrc + i)
        lrc = rol(lrc)
    return lrc

def printByteArray(byteArr):
    for i in byteArr:
        print "{:02x}".format(i).upper(),
    print ""

    
CTRL_GETSTATUS  = [0x02, 0x00]
CTRL_STOP       = [0x02, 0x10]

CTRL_SINGLESTEP = [0x02, 0x12]
CTRL_CONTSTEP   = [0x02, 0x13]

CTRL_MVABS      = [0x02, 0x16]
CTRL_MVREL      = [0x02, 0x17]

CTRL_STEPSGET   = [0x02, 0x20]
CTRL_STEPSSET   = [0x02, 0x21]

CTRL_CURLIMGET  = [0x02, 0x30]
CTRL_CURLIMSET  = [0x02, 0x31]
CTRL_MOTPOWREAD = [0x02, 0x32]

CTRL_STEPRATEGET= [0x02, 0x40]
CTRL_STEPRATESET= [0x02, 0x41]
CTRL_STEPRATESAV= [0x02, 0x42]

CTRL_SEEKRATEGET= [0x02, 0x44]
CTRL_SEEKRATESET= [0x02, 0x45]
CTRL_SEEKRATESAV= [0x02, 0x46]




class TIMS0201(object):
    readTimeout = 20 #ms
    def __init__(self):
        self.dll = None
        self.registerFunctions()
        
        
    @staticmethod
    def makeMotorStatusPacket():
        return TIMS0201.makePacket(CTRL_GETSTATUS)
        
    @staticmethod
    def makePacket(control, data = [0x00]):
        packet = (c_ubyte * (9+len(data)))(0)
        packet[0] = 0xd0 # To
        packet[1] = 0x01 # from
        packet[2] = control[0]
        packet[3] = control[1]
        packet[4] = 0x00 # status[0]
        packet[5] = 0x00 # status[1]
        packet[6] = 0xCC # ref, easier for debugging parsing
        packet[7] = len(data)-1 # length
        packet[8:-1] = data
        packet[-1] = calcLRC(packet)
        return packet
        
        
    def getStatus(self, verbose = False):
        rx = c_ulong(1)
        tx = c_ulong(1)
        status = c_ulong(1)
        ret = self.dllGetStatus(self.handle, rx, tx, status)
        if not verbose:
            print "Status: {}\n\trx: {}, tx: {}, status: {}".format(
                ret,
                rx.value, tx.value, status.value)
        return rx.value, tx.value
    
    def open_(self):
        self.handle = c_uint(0)
        print "opened: {}".format(self.dllOpen(0, self.handle))
        
        # Need toset up other things to talk to the device properly
        # I don't think it should be done ever again, so they're not
        # extra functions. Looked at Jova's VI's for values
        print self.dll.FT_SetLatencyTimer(self.handle, c_ubyte(1))
        
        print self.dll.FT_SetBaudRate(self.handle, c_ulong(230000))
        
        print self.dll.FT_SetDataCharacteristics(self.handle,
                    c_ubyte(8), c_ubyte(0), c_ubyte(0))
        
    def close_(self):
        try:
            print "closed: {}".format(self.dllClose(self.handle))
        except:
            print "already closed"
        
    def purge(self):
        self.dll.FT_Purge(A.handle, c_ulong(3))
        
    def write(self, packet):
        written = c_ulong()
        self.dllWrite(self.handle, packet, len(packet), written)
        # print "\tWanted: {}, Wrote: {}".format(len(packet), written.value)
        
    def read(self, expectedbytes = 9, verbose = False):
        toRead, dump = self.getStatus(verbose=True)
        count = 0
        while toRead < expectedbytes: # a minimum of 9 bytes will be read
                                      # but sometimes it isknown there will be more
            time.sleep(5./1000.)
            toRead, dump = self.getStatus(verbose=True)
            count += 1
            if count >= self.readTimeout:
                print "Nothing to read, ", toRead
                return
        readPacket = (c_ubyte * toRead)()
        read = c_ulong()
        self.dllRead(self.handle, readPacket, toRead, read)

        if not verbose:
            print "Read {} bytes.\n\t".format(read),
            for i in readPacket:
                print "{:02x}".format(i).upper(),
            print ""
        return readPacket
        
    def stopMotor(self):
        packet = TIMS0201.makePacket(CTRL_STOP)
        self.write(packet)
        # ignore the response packet
        self.read(verbose = True)
        
    def singleStep(self, fwd = True):
        direction = 0 # reverse
        if fwd:
            direction = 1
        packet = TIMS0201.makePacket(CTRL_SINGLESTEP, [direction])
        self.write(packet)
        self.read()
        
    def continousMove(self, fwd = True):
        direction = 0 # reverse
        if fwd:
            direction = 1
        packet = TIMS0201.makePacket(CTRL_CONTSTEP, [direction])
        self.write(packet)
        self.read()
        
    def moveAbsolute(self, move):
        print "NOT IMPLEMENTED: moveAbsolute"
        
    def moveRelative(self, move):
        data = int(move)
        data = (c_ubyte * 4).from_buffer_copy(pack(">i", data))
        packet = TIMS0201.makePacket(CTRL_MVREL, data)
        self.write(packet)
        self.read(13, verbose=True)
        
    def getSteps(self):
        packet = TIMS0201.makePacket(CTRL_STEPSGET)
        self.write(packet)
        ret = self.read(13, verbose = True)
        if ret is not None:
            return unpack(">i", str(bytearray(ret[8:-1])))[0]
        else:
            print "ERROR GETTING STEPS"
            return 0
            
            
    
    def setSteps(self, steps):
        data = int(steps)
        data = (c_ubyte * 4).from_buffer_copy(pack(">i", data))
        packet = TIMS0201.makePacket(CTRL_STEPSSET, data)
        self.write(packet)
        self.read(verbose=True)
        
    def getCurrentLimit(self):
        packet = TIMS0201.makePacket(CTRL_CURLIMGET)
        self.write(packet)
        read = self.read(verbose=True)
        if read is not None:
            return read[8:-1][0]
        
    def setCurrentLimit(self, limit=1):
        limit = int(limit)
        if limit > 20:
            print "ERROR: DO NOT EXCEED 20\%"
            limit = 20
        packet = TIMS0201.makePacket(CTRL_CURLIMSET, [limit])
        self.write(packet)
        self.read(verbose=True)
    
    def getMotorPowers(self):
        packet= TIMS0201.makePacket(CTRL_MOTPOWREAD)
        self.write(packet)
        ret = self.read(20, verbose=True) # 12 bytes of data
        if ret is not None:
            # (Motor Voltage, Winding A current, Winding B current)
            # (     V,               A,                  A        )
            return unpack(">fff", str(bytearray(ret[8:-1])))
        else:
            print "error getting motor power"
            print self.read()


    def setStepRate(self, rate):
        rate = int(rate)
        data = (c_ubyte * 2).from_buffer_copy(pack(">H", rate))
        packet = TIMS0201.makePacket(CTRL_STEPRATESET, data)
#        print data[:]
#        for i in packet:
#            print "{:02x}".format(i).upper(),
#        return
        self.write(packet)
        self.read(10, verbose = True)

    def getStepRate(self):
        packet = TIMS0201.makePacket(CTRL_STEPRATEGET)
        self.write(packet)
        ret = self.read(11, verbose=True)
        if ret is not None:
            try:
                return unpack(">H", bytearray(ret[8:-1]))[0]
            except:
                print "ERROR GETTING STEPRATE\n"
                printByteArray(bytearray(ret))
                printByteArray(bytearray(ret[8:-1]))
        else:
            print "ERROR GETTING STEPRATE, NONE READ"
            return 100
            
    def getDeviceStatus(self):
        packet = TIMS0201.makePacket(CTRL_GETSTATUS)
        self.write(packet)
        ret = self.read(10, verbose = True)
        if ret is not None:
            return unpack(">h", bytearray(ret[8:-1]))[0]
        else:
            print "ERROR GETTING DEVICE STATUS"
            return -1
            
    def isBusy(self):
        status = self.getDeviceStatus()
        if status == -1:
            return True
        busy = 0b01
        move = 0b10
        
        if status&busy or status&move:
            return True
        return False
        

        
        
        
    def registerFunctions(self):
        self.dll = CDLL("ftd2xx")
        
        self.dllOpen = self.dll.FT_Open
        self.dllOpen.argtypes = [c_int, POINTER(c_ulong)]
        self.dllOpen.restype = c_int
        
        self.dllClose = self.dll.FT_Close
        self.dllClose.argtypes = [c_ulong]
        self.dllClose.restype = c_int
        
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
        
        
        

        
        
try:
    A.close_()
except:
    pass
        
A = TIMS0201()
    
    





















