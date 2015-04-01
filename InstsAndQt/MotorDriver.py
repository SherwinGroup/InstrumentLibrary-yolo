# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 11:24:38 2015

@author: dvalovcin
"""

import numpy as np
import matplotlib.pylab as plt
from matplotlib import rcParams
from ctypes import *


class FT_HANDLE(Structure):
    """ Class for retrieving the available parameters of the camera
        http://forge.abcd.harvard.edu/gf/project/storm_control/scmgit/?p=storm_control;a=blob_plain;f=hal4000/andor/andorcontroller.py;hb=ec7d862398760cf292dfc53fc5add8ebc39eeb74

    """
    _fields_ = [("ulSize", c_ulong),
                ("ulAcqModes", c_ulong),
                ("ulReadModes", c_ulong),
                ("ulTriggerModes", c_ulong),
                ("ulCameraType", c_ulong),
                ("ulPixelMode", c_ulong),
                ("ulSetFunctions", c_ulong),
                ("ulGetFunctions", c_ulong),
                ("ulFeatures", c_ulong),
                ("ulPCICard", c_ulong),
                ("ulEMGainCapability", c_ulong),
                ("ulFTReadModes", c_ulong)]

class TIMS0201(object):
    def __init__(self):
        self.dll = None
        self.registerFunctions()
        
    def registerFunctions(self):
        self.dll = CDLL("ftd2xx")
        
        self.dllFT_Open = self.dll.FT_Open
        self.dllFT_Open.argtypes = [c_int, POINTER(c_ulong)]
        self.dllFT_Open.restype = c_int
        
        self.dllFT_Close = self.dll.FT_Close
        self.dllFT_Open.argtypes = [c_int, POINTER(c_ulong)]
        self.dllFT_Open.restype = c_int
        
        self.dllFT_GetStatus = self.dll.FT_GetStatus
        self.dllFT_GetStatus.argtypes = [
                c_ulong, POINTER(c_ulong), POINTER(c_ulong),
                POINTER(c_ulong)]
        self.dllFT_GetStatus.restype = c_int
        
        
        
    def constructPacket(self, ctrl = 0x2000):
        to = c_uint8(0xD0)
        frm = c_uint8(0x01)
        control = c_uint16(0xD0)
        status = c_uint16(0xD0)
        ref = c_uint8(0xD0)
        length = c_uint8(0xD0)
        
        

A = TIMS0201()
























