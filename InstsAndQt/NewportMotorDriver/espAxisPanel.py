from PyQt5 import QtCore, QtGui, QtWidgets
from .UIs.axisPanel_ui import Ui_ESPAxisPanel
# from esp300 import ESP300
try:
    from ..Instruments import ESP300
except ValueError:
    from InstsAndQt.Instruments import ESP300
from InstsAndQt.customQt import *
import numpy as np
import pyqtgraph
import time
import logging


log = logging.getLogger("Instruments")
log.setLevel(logging.DEBUG)

class ESPAxisPanel(QtWidgets.QWidget):
    sigCreateGuiElement = QtCore.pyqtSignal(object, object)
    # Emits a signal of error messages when encountered.
    sigErrorsEncountered = QtCore.pyqtSignal(object)
    # Emit when moving is finished
    # (specifically called when the cleanup function is done)
    sigMoveFinished = QtCore.pyqtSignal()

    def __init__(self, parent = None, GPIB="Fake", axis=2):
        super(ESPAxisPanel, self).__init__(parent)
        self.ESPAxis = None
        self.thWaitForMotor = TempThread()
        self.initUI()
        # self.ESPAxis = ESP300()
        self.GPIB = GPIB
        self.openESPAxis(axis)

        self.sigCreateGuiElement.connect(self.createGuiElement)


    def initUI(self):
        self.ui = Ui_ESPAxisPanel()
        self.ui.setupUi(self)

        # self.ui.sbPosition.valueChanged.connect(self.startChangePosition)
        self.ui.sbPosition.setOpts(step=1, decimals=4)
        self.ui.sbPosition.sigValueChanged.connect(lambda: self.startChangePosition(self.moveMotor))
        self.ui.cbOn.toggled.connect(self.toggleMotor)
        self.ui.bSetPosition.clicked.connect(self.setCurrentPosition)
        # self.ui.bGoHome.clicked.connect(self.goHome)
        self.ui.bGoHome.clicked.connect(lambda: self.startChangePosition(target=self.ESPAxis.goHome))

    def setCurrentPosition(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self,"Current Position", "Current Angle:", 0)
        if ok:
            self.ESPAxis.home = val
            self.ui.sbPosition.blockSignals(True)
            self.ui.sbPosition.setValue(self.ESPAxis.position, delaySignal=True)
            self.ui.sbPosition.blockSignals(False)

    def goHome(self):
        pass
        # self.startChangePosition(target=self.ESPAxis.goHome)
        # self.ESPAxis.goHome()

    def toggleMotor(self):
        try:
            self.ESPAxis.motor_on = bool(self.ui.cbOn.isChecked())
        except Exception as e:
            print("Error turning motor on", e)

    def openESPAxis(self, axis):
        self.ESPAxis = ESP300(self.GPIB, current_axis=axis)
        self.ui.sbAxis.setValue(axis)
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(self.ESPAxis.position, delaySignal=True)
        self.ui.sbPosition.blockSignals(False)
        self.ui.labelMoving.setStyleSheet("QLabel { background-color : green; color : black; }")

        self.ui.cbOn.setChecked(bool(self.ESPAxis.motor_on))

    def startChangePosition(self, target = None ):
        """
        Start the thread for waiting for the motor to move
        :param target: Fucntion to thread. None defaults to moveMotor, false disables.
        :return:
        """
        if target is None:
            target = self.moveMotor



        self.setStatusWidget("Moving", "QLabel { background-color : yellow; color : black; }")

        # Do I really need to set these timeouts?
        # expectedTime = np.abs(self.ESPAxis.position - float(self.ui.sbPosition.value()))/self.ESPAxis.velocity
        # # force minimum of 10s
        # expectedTime = max(expectedTime, 10)
        # # Update the timeout time so it won't break when you want long moves
        # # Have about ~10% more than expected, just for safety.
        # self.ESPAxis._instrument.timeout = expectedTime * 1.1 * 1000 + self.ESPAxis.delay

        if target is not False:
            self.thWaitForMotor.target = target
            self.thWaitForMotor.finished.connect(self.cleanupMotorMove)
            self.thWaitForMotor.start()

        # self.thWaitForMotor.finished.connect(self.cleanupMotorMove)



    def moveMotor(self, value = None):

        # self.setStatusWidget("Moving", "QLabel { background-color : yellow; color : black; }")
        # expectedTime = np.abs(self.ESPAxis.position - float(self.ui.sbPosition.value()))/self.ESPAxis.velocity
        # # force minimum of 10s
        # expectedTime = max(expectedTime, 10)
        # # Update the timeout time so it won't break when you want long moves
        # # Have about ~10% more than expected, just for safety.
        # self.ESPAxis.instrument.timeout = expectedTime * 1.1 * 1000 + self.ESPAxis.delay
        if value is None:
            value = self.ui.sbPosition.value()
        value = float(value)

        try:
            print("Moving motor to {} in:".format(value), QtCore.QThread.currentThreadId())
            self.ESPAxis.position = float(value)
        except Exception as e:
            log.exception("Error moving axis\n\tTimeout set to: {}".format(self.ESPAxis._instrument.timeout))
            self.setStatusWidget("Timeout", "QLabel { background-color : red; color : black; }")
            return
        # self.sigCreateGuiElement.emit(self.cleanupMotorMove, [])

    def cleanupMotorMove(self, *args):
        print("Cleaning motor at {} in:".format(self.ui.sbPosition.value()), QtCore.QThread.currentThreadId())
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(self.ESPAxis.position, delaySignal=True)
        self.ui.sbPosition.blockSignals(False)

        try:
            self.thWaitForMotor.finished.disconnect(self.cleanupMotorMove)
        except TypeError:
            pass
        # if self.thWaitForMotor.isRunning():
        #     log.warning("The thread is still alive? This shoulnd't happen")
        # try:
        #     del self.thWaitForMotor
        # except:
        #     log.exception("Couldn't delete the thread")
        # self.thWaitForMotor = TempThread()

        self.setStatusWidget("Ready", "QLabel { background-color : green; color : black; }")
        self.checkErrors()
        self.sigMoveFinished.emit()

    def checkErrors(self):
        errors = self.ESPAxis.error_message
        if "0" in errors.split(',')[0]: return
        try:
            code, tickTime, message = errors.split(',')
        except:
            log.exception("Couldn't split the error")
        else:
            curTime = time.strftime('%H:%M:%S')
            errors = "{} - {}".format(curTime, message)

        log.debug("Error message from ESP is: {}".format(errors))
        self.sigErrorsEncountered.emit(errors)

    def setStatusWidget(self, text="", styleSheet=""):
        """
        convenience function to set the text and style of the "ready/moving/tiemout" status
        label. Thread-safe(?) in that it will emit a signal.
        :param text: What text
        :param styleSheet: Stylesheet for the label.
        :return:
        """
        self.sigCreateGuiElement.emit(self.ui.labelMoving.setText, text)

        self.sigCreateGuiElement.emit(
                self.ui.labelMoving.setStyleSheet,
                styleSheet)

    def createGuiElement(self, function, *args):
        function(*args)













if __name__ == "__main__":
    import sys


    e = QtWidgets.QApplication(sys.argv)
    win = MotorWindow(device = TIMS0201(), parent = None)
    sys.exit(e.exec_())
