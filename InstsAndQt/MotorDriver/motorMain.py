from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

from InstsAndQt.TIMSMotorDriver import *
from InstsAndQt.customQt import *
from InstsAndQt.Instruments import __displayonly__
from InstsAndQt.MotorDriver.Control import SettingsWindow
from InstsAndQt.MotorDriver.movementWindow_ui import Ui_MainWindow
import time







class MotorWindow(QtWidgets.QMainWindow):
    # emit a list of values to update the voltages/currents of the coils
    thMoveMotor = None
    sigUpdateDegrees = QtCore.pyqtSignal(object)


    def __init__(self, device = None, parent = None):
        super(MotorWindow, self).__init__(parent)
        self.stepsPerDeg = 11.85556
        self.initUI()
        if __displayonly__: return
        self.device = None
        self.openDevice()


        self.ui.tFitA.editingFinished.connect(self.calcTransmission)
        self.ui.tFitMu.editingFinished.connect(self.calcTransmission)
        self.ui.tFitC.editingFinished.connect(self.calcTransmission)

    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        if __displayonly__: return

        self.buttons = [
            self.ui.bm01,
            self.ui.bm05,
            self.ui.bm10,
            self.ui.bp01,
            self.ui.bp05,
            self.ui.bp10,
            self.ui.bGo,
        ]
        for button in self.buttons:
            button.clicked.connect(self.moveMotorDeg)

        self.ui.sbAngle.setOpts(bounds = (-360, 360), decimals = 5, step = 0.1)
        #self.ui.bStop.clicked.connect(self.stopMove)

        self.ui.mMoreSettings.triggered.connect(self.launchSettings)
        self.ui.mMoreZero.triggered.connect(self.zeroDegrees)

        self.ui.bQuit.clicked.connect(self.close)

        self.ui.bCloseDevice.clicked.connect(self.toggleDeviceOpen)

        self.show()

    def openDevice(self):
        try:
            self.device = TIMSArduino()
            self.device.open_()
            # try:
            #     self.currentAngle = self.device.getSteps()/self.stepsPerDeg
            # except:
            #     self.currentAngle = 0
            self.currentLimit = self.device.getCurrentLimit()
            if self.currentLimit == 0:
                self.currentLimit = 25
            self.device.setCurrentLimit(0)
            self.device.setSteppingMode(toHalf=True)
            self.settingsWindow = None
            self.sigUpdateDegrees.connect(self.setDegrees)

            self.finishedMove()
        except Exception as e:
            log.critical("Cannot open motor driver (No driver?)")
            self.closeDevice()
        else:
            self.toggleUIEnabled(True)
            self.ui.bCloseDevice.blockSignals(True)
            self.ui.bCloseDevice.setChecked(True)
            self.ui.bCloseDevice.blockSignals(False)

    def closeDevice(self):
        try:
            if self.device is not None:
                self.device.close_()
        except Exception as e:
            print("error closing", e)
        self.device = None
        self.toggleUIEnabled(False)
        self.ui.bCloseDevice.blockSignals(True)
        self.ui.bCloseDevice.setChecked(False)
        self.ui.bCloseDevice.blockSignals(False)

    def toggleDeviceOpen(self):
        if self.device is None:
            self.openDevice()
        else:
            self.closeDevice()

    def toggleUIEnabled(self, state=True):
        [i.setEnabled(state) for i in self.buttons]
        self.ui.sbAngle.setEnabled(state)
        self.ui.bStop.setEnabled(state)

    def moveMotorDeg(self, moveTo=False):
        if isinstance(moveTo, float):
            moveBy = moveTo - self.currentAngle
        else:
            sent = self.sender()
            if sent in self.buttons[:-1]:
                moveBy = int(sent.text()[:-1])
            else:
                moveBy = self.ui.sbAngle.interpret() - self.currentAngle


        for button in self.buttons:
            button.setEnabled(False)

        if self.settingsWindow is not None:
            self.currentLimit = self.settingsWindow.ui.sbCurrent.interpret()

        self.device.setCurrentLimit(self.currentLimit)
        self.device.moveRelative(moveBy * self.stepsPerDeg)
        
        self.thMoveMotor = TempThread(target = self.waitForMotor)
        # self.thMoveMotor.terminated.connect(self.finishedMove)
        self.thMoveMotor.start()

    def stopMove(self):
        self.thMoveMotor.terminate()
        try:
            self.device.stopMotor()
        except Exception as e:
            print("Error stopping motor", e)

    def launchSettings(self):
        self.device.setCurrentLimit(self.currentLimit)
        self.settingsWindow = SettingsWindow(device = self.device, parent = self)

    def zeroDegrees(self):
        val = self.ui.sbAngle.interpret()
        self.device.setSteps(0)
        time.sleep(0.1)
        self.finishedMove()

    def waitForMotor(self):
        # Needed because the arduino seems to drop the first
        # query. Not sure why, though.
        time.sleep(0.1)
        flg = self.device.isBusy()        
        while flg:
            curSteps = self.device.getSteps()
            self.sigUpdateDegrees.emit(curSteps/self.stepsPerDeg)
            time.sleep(0.1)
            flg = self.device.isBusy()
        print("done move")
        self.finishedMove()

    def finishedMove(self):
        for button in self.buttons:
            button.setEnabled(True)
        # Stop it from whining when not moving
        self.device.setCurrentLimit(0)

        curSteps = self.device.getSteps()
        try:
            self.sigUpdateDegrees.emit(curSteps/self.stepsPerDeg)
        except:
            pass

    def setDegrees(self, val):
        self.ui.sbAngle.setValue(val)
        self.currentAngle = val
        self.calcTransmission()

    def calcTransmission(self):
        val = self.currentAngle
        A, mu, c = self.ui.tFitA.value(), self.ui.tFitMu.value(), self.ui.tFitC.value()

        cos = A*np.cos(np.deg2rad(val+mu))**4 + c
        self.ui.tCosCalc.setText("{:0.4f}".format(cos))


    def closeEvent(self, QCloseEvent):
        if self.settingsWindow is not None:
            self.settingsWindow.close()
        # if self.parent() is None:
        #     self.device.close_()
        # 12/4/17 previously had the above if statement
        # not sure why it was there...
        self.close()
        QCloseEvent.accept()
    def close(self):
        self.device.close_()











if __name__ == "__main__":
    import sys


    e = QtWidgets.QApplication(sys.argv)
    win = MotorWindow(parent = None)
    sys.exit(e.exec_())
