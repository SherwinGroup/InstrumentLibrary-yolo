from ctypes import *
from struct import *
from .MotorDriver import (CTRL_GETSTATUS  ,
    CTRL_STOP       ,
    CTRL_SINGLESTEP ,
    CTRL_CONTSTEP   ,
    CTRL_MVABS      ,
    CTRL_MVREL      ,
    CTRL_STEPSGET   ,
    CTRL_STEPSSET   ,
    CTRL_STEPMODE   ,
    CTRL_CURLIMGET  ,
    CTRL_CURLIMSET  ,
    CTRL_MOTPOWREAD ,
    CTRL_STEPRATEGET,
    CTRL_STEPRATESET,
    CTRL_STEPRATESAV,
    CTRL_SEEKRATEGET,
    CTRL_SEEKRATESET,
    CTRL_SEEKRATESAV,
    calcLRC, printByteArray
)


class myCallable(object):
    ''' Need a class which is callable, but also
        need it to have the argtypes and restype
        parameters to match the calls made setting up the CCD. '''

    def __init__(self, func=None, retWeights=()):
        self.argtypes = []
        self.restype = None
        self.func = func
        # ((retchance1, retchance2, retchance3... ),
        #  (retval1,    retval2,    retval3))
        self.retWeights = retWeights

    def __call__(self, *args):
        self.func(*args)
        ret = 0
        # if not np.random.randint(5):
        #     ret = 20004
        if self.retWeights:
            ranges = np.cumsum(self.retWeights[0])
            rando = np.random.randint(ranges[-1])
            return self.retWeights[1][
                # Grab the first one where
                # it crosses over
                np.argwhere(rando < ranges)[0]
            ]

        return ret

class FakeDLL(object):
    readQueue = ''
    writeQueue = ''
    steps = 20
    currentLimit = 35
    def __init__(self):
        self.FT_Open = myCallable(self.__voidReturn)
        self.FT_Close = myCallable(self.__voidReturn)
        self.FT_SetLatencyTimer = myCallable(self.__voidReturn)
        self.FT_SetBaudRate = myCallable(self.__voidReturn)
        self.FT_SetDataCharacteristics = myCallable(self.__voidReturn)
        self.FT_GetStatus = myCallable(self.__getStatus)
        self.FT_Write = myCallable(self.__write)
        self.FT_Read = myCallable(self.__read)
        self.FT_Purge = myCallable(self.__purge)

    def __voidReturn(self, *args):
        pass

    def __getStatus(self, *args):
        args[1].value = len(self.readQueue)
        args[2].value = len(self.writeQueue)
        args[3].value = 0

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

    def __write(self, handle, packet, length, leng):
        to = packet[0]
        frm = packet[1]
        ctrl = [packet[2], packet[3]]
        length = packet[7]
        data = packet[8:-1]
        lrc = packet[-1]

        if ctrl==CTRL_STEPSGET:
            rpacket = self.makePacket(ctrl,
                            (c_ubyte * 4).from_buffer_copy(pack(">i", self.steps))
                            )
            self.readQueue = rpacket
        elif ctrl == CTRL_STEPSSET:
            stps = unpack(">i", str(bytearray(data)))[0]
            self.steps = stps
            self.readQueue = packet
        elif ctrl == CTRL_MVREL:
            mv = unpack(">i", str(bytearray(data)))[0]
            self.steps += mv
            self.readQueue = packet
        elif ctrl == CTRL_STEPMODE:
            self.readQueue = packet
        elif ctrl == CTRL_CURLIMGET:
            rpacket = self.makePacket(ctrl,
                            [self.currentLimit]
                            )
            self.readQueue = rpacket
        elif ctrl == CTRL_CURLIMSET:
            self.currentLimit = data[0]
            self.readQueue = packet
        elif ctrl == CTRL_GETSTATUS:
            rpacket = self.makePacket(ctrl,
                            [0, 0]
                            )
            self.readQueue = rpacket




    def __read(self, handle, packet, toread, read):
        packet[:] = self.readQueue
        read.value = len(packet)
        self.readQueue = ''

    def __purge(self, *args):
        self.readQueue = ''
        self.writeQueue = ''