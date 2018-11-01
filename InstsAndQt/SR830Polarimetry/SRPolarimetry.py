from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np
from hsganalysis import makeCurve, curve_fit
from InstsAndQt.ThorlabsCageRotator.K10CR1Panel import K10CR1Panel
from InstsAndQt.Instruments import SR830Instr
from InstsAndQt.SR830Polarimetry.SR830Polar_ui import Ui_SR830PolMeasure
from InstsAndQt.customQt import TempThread
import time
import pyqtgraph as pg

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")
import serial


class SerialSR830(object):
    def __init__(self, address=None):
        self.instrument = serial.Serial()
        self.instrument.baudrate = 19200
        self.instrument.timeout = 5
        if address is not None:
            self.openInstrument(address)

    def openInstrument(self, address=None):
        if address is None: return
        if address == "None" or address == "Fake":
            print("I don't know...")
            return

        self.instrument.port = address

        self.instrument.open()

    def closeInstrument(self):
        self.instrument.close()

    def write(self, command=''):
        if not command: return False
        if command[-1] != '\n':
            command += "\n"
        try:
            command = command.encode()  # need bytearray
        except AttributeError:
            pass  # already bytearray

        self.instrument.write(command)

    def read(self):
        response = ''
        char = self.instrument.read(1).decode()
        while char != '\r' and char != '':
            response += char
            char = self.instrument.read(1).decode()
        if char == '':
            print("Timeout error occurred")
        return response

    def ask(self, command=''):
        self.write(command)
        return self.read()

    def setRefFreq(self, freq):
        """Set the reference frequency  """
        if type(freq) not in (float, int):
            print('Error. Given frequency is not a number')
            return
        self.write('FREQ ' + str(freq))

    def setRefVolt(self, volts):
        if type(volts) not in (float, int):
            print('Error. Given voltage is not a number')
            return
        self.write('SLVL ' + str(volts))

    def getRefVolt(self):
        return float(self.ask('SLVL?'))

    def getChannel(self, ch=1):
        if ch not in (1, 2, 3, 4, 'X', 'x', 'Y', 'y', 'R', 'r', 't', 'T', 'theta', 'Theta', 'th'):
            print('Error. Must give valid channel number')
            return
        # if a letter is given instead of  anumber, must convert it
        if type(ch) is str:
            d = dict(x=1, y=2, r=3, t=4)
            ch = d[ch.lower()[0]]
        return float(self.ask('OUTP? ' + str(ch)))

    def getMultiple(self, *args):
        """Use the SNAP? command to read the values instantanously and avoid
            timing issues"""
        toRead = ''
        for (i, ch) in enumerate(args):
            if ch not in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                          'X', 'x', 'Y', 'y', 'R', 'r', 't', 'T', 'theta', 'Theta', 'th'):
                print('Error. Must give valid channel number')
                return
            # if a letter is given instead of  anumber, must convert it
            if type(ch) is str:
                d = dict(x=1, y=2, r=3, t=4)
                ch = d[ch.lower()[0]]
            toRead = toRead + str(ch) + ','
        toRead = toRead[:-1]
        ret = self.ask('SNAP?' + toRead)
        return [float(i) for i in ret.split(',')]


class SR830Polarimeter(QtWidgets.QMainWindow):
    anaDir = "V"

    thSweeper = TempThread()

    sigNewData = QtCore.pyqtSignal(object)  # emit the new data pair

    def __init__(self, *args, **kwargs):
        super(SR830Polarimeter, self).__init__(*args, **kwargs)
        self.initUI()

        self.instrument = SerialSR830("COM1")

        self.dataCurve = self.ui.gPolaragram.scatterPlot(pen='r')
        self.fitCurve = self.ui.gPolaragram.plot(pen=pg.mkPen("k", width=3))
        self.sweepPoints = []

        self.thSweeper.target = self.doMeasurement
        self.thSweeper.finished.connect(lambda: self.ui.bStart.setChecked(False))
        self.sigNewData.connect(self.addPoint)

        eta = lambda x: 1.734e-8 * x ** 2 - 1.2586e-4 * x + 0.33996
        self.fitFunction = makeCurve(eta(808), self.anaDir == "V")

    def initUI(self):
        self.ui = Ui_SR830PolMeasure()
        self.ui.setupUi(self)

        # self.ui.cbGPIB.setInstrumentClass(SerialSR830)
        # self.ui.cbGPIB.sigInstrumentOpened.connect(self.setInstrument)

        self.ui.bStart.clicked.connect(self.startMeasurement)

        self.polText = pg.TextItem("", color=(0, 0, 0))
        self.polText.setPos(0, 0)
        self.polText.setFont(QtGui.QFont("", 15))
        self.ui.gPolaragram.addItem(self.polText, ignoreItemBoundary=True)
        pg.PlotItem

        self.show()

    def setInstrument(self, inst):
        self.instrument = inst

    def startMeasurement(self, val):
        if not val: return  # unchecking
        self.data = np.array([]).reshape(-1, 2)
        self.dataCurve.setData(self.data)
        self.fitCurve.setData([], [])

        start, ok = QtWidgets.QInputDialog.getDouble(self, "Starting val", "Start", 0)
        if not ok:
            self.ui.mFileDoHWPSweep.setChecked(False)
            return

        stop, ok = QtWidgets.QInputDialog.getDouble(self, "Stopping val", "Stop", 360)
        if not ok:
            self.ui.mFileDoHWPSweep.setChecked(False)
            return

        step, ok = QtWidgets.QInputDialog.getDouble(self, "Stepping val", "Step", 360 / 64)
        if not ok:
            self.ui.mFileDoHWPSweep.setChecked(False)
            return

        self.sweepPoints = np.arange(start, stop, step)

        self.thSweeper.start()

    def doMeasurement(self):
        for angle in self.sweepPoints:
            if not self.ui.bStart.isChecked(): return
            self.ui.wK10CR1.startChangePosition(target=False)
            # print("Startmove", angle)
            self.ui.wK10CR1.moveMotor(value=angle)
            # print("\tendmove")
            self.ui.wK10CR1.cleanupMotorMove()
            if not self.ui.bStart.isChecked(): return
            time.sleep(0.1)  # Wait for the lock-in time constant?

            data = self.instrument.getChannel("r")
            # print("\temittting", [angle, data])
            self.sigNewData.emit([angle, data])

    def addPoint(self, point):
        self.data = np.row_stack((self.data, point))

        self.dataCurve.setData(*self.data.T)
        s0 = [1, 1, 1, 1]
        try:
            p, pcov = curve_fit(self.fitFunction, self.data[:, 0], self.data[:, 1], p0=s0)
        except TypeError:
            ## when too few points
            return
        fineAngles = np.linspace(0, self.data[:, 0].max(), 100)

        self.fitCurve.setData(fineAngles,
                              self.fitFunction(fineAngles, *p))

        d = np.sqrt(np.diag(pcov))
        d0, d1, d2, d3 = d
        S0, S1, S2, S3 = p

        # append alpha value
        alpha = np.arctan2(S2, S1) / 2 * 180. / np.pi
        # append alpha error
        dalpha = (d2 ** 2 * S1 ** 2 + d1 ** 2 * S2 ** 2) / (S1 ** 2 + S2 ** 2) ** 2

        # append gamma value
        gamma = np.arctan2(S3, np.sqrt(S1 ** 2 + S2 ** 2)) / 2 * 180. / np.pi
        # append gamma error
        dgamma = (d3 ** 2 * (S1 ** 2 + S2 ** 2) ** 2 + (d1 ** 2 * S1 ** 2 + d2 ** 2 * S2 ** 2) * S3 ** 2) / (
                (S1 ** 2 + S2 ** 2) * (S1 ** 2 + S2 ** 2 + S3 ** 2) ** 2)

        # append degree of polarization
        dop = np.sqrt(S1 ** 2 + S2 ** 2 + S3 ** 2) / S0
        ddop = ((d1 ** 2 * S0 ** 2 * S1 ** 2 + d0 ** 2 * (S1 ** 2 + S2 ** 2 + S3 ** 2) ** 2 + S0 ** 2 * (
                d2 ** 2 * S2 ** 2 + d3 ** 2 * S3 ** 2)) / (S0 ** 4 * (S1 ** 2 + S2 ** 2 + S3 ** 2)))

        msg = "State: a={:.3f}+-{:.3f}, g={:.3f}+-{:.3f}, DOP={:.3f}+-{:.3f}".format(alpha, dalpha,
                                                                                     gamma, dgamma,
                                                                                     dop, ddop)

        print(msg)
        self.polText.setText(msg)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = SR830Polarimeter()

    app.exec_()

