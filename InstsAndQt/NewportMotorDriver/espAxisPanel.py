from PyQt4 import QtCore, QtGui
from .UIs.axisPanel_ui import Ui_ESPAxisPanel
# from esp300 import ESP300
try:
    from ..Instruments import ESP300
except ValueError:
    from InstsAndQt.Instruments import ESP300
from InstsAndQt.customQt import *
import numpy as np
import pyqtgraph


import logging
log = logging.getLogger("Instruments")


class ESPAxisPanel(QtGui.QWidget):
    thWaitForMotor = TempThread()
    sigCreateGuiElement = QtCore.pyqtSignal(object, object)
    # Emits a signal of error messages when encountered.
    sigErrorsEncountered = QtCore.pyqtSignal(object)

    def __init__(self, parent = None, GPIB="Fake", axis=1):
        super(ESPAxisPanel, self).__init__(parent)
        self.ESPAxis = None
        self.initUI()
        # self.ESPAxis = ESP300()
        self.GPIB = GPIB
        self.openESPAxis(axis)

        self.sigCreateGuiElement.connect(self.createGuiElement)


    def initUI(self):
        self.ui = Ui_ESPAxisPanel()
        self.ui.setupUi(self)

        # self.ui.sbPosition.valueChanged.connect(self.startChangePosition)
        self.ui.sbPosition.setOpts(step=1)
        self.ui.sbPosition.sigValueChanged.connect(lambda: self.startChangePosition(self.moveMotor))
        self.ui.cbOn.toggled.connect(self.toggleMotor)
        self.ui.bSetPosition.clicked.connect(self.setCurrentPosition)
        self.ui.bGoHome.clicked.connect(self.goHome)

    def setCurrentPosition(self):
        val, ok = QtGui.QInputDialog.getDouble(self,"Current Position", "Current Angle:", 0)
        if ok:
            self.ui.sbPosition.blockSignals(True)
            self.ESPAxis.home = val
            self.ui.sbPosition.setValue(self.ESPAxis.position)
            self.ui.sbPosition.blockSignals(False)

    def goHome(self):
        self.startChangePosition(target=self.ESPAxis.goHome)

    def toggleMotor(self):
        try:
            self.ESPAxis.motor_on = bool(self.ui.cbOn.isChecked())
        except Exception as e:
            print("Error turning motor on", e)

    def openESPAxis(self, axis):
        self.ESPAxis = ESP300(self.GPIB, current_axis=axis)

        self.ui.sbAxis.setValue(axis)
        self.ui.sbPosition.setValue(self.ESPAxis.position)
        self.ui.labelMoving.setStyleSheet("QLabel { background-color : green; color : black; }")

        self.ui.cbOn.setChecked(bool(self.ESPAxis.motor_on))

    def startChangePosition(self, target=None ):
        """
        Start the thread for waiting for the motor to move
        :param target: Fucntion to thread
        :return:
        """
        if target is None:
            target = self.moveMotor
        self.thWaitForMotor.target = target
        # self.thWaitForMotor.finished.connect(self.cleanupMotorMove)
        self.thWaitForMotor.start()

    def moveMotor(self):

        self.setStatusWidget("Moving", "QLabel { background-color : yellow; color : black; }")
        expectedTime = np.abs(self.ESPAxis.position - float(self.ui.sbPosition.value()))/self.ESPAxis.velocity
        # force minimum of 10s
        expectedTime = max(expectedTime, 10)
        # Update the timeout time so it won't break when you want long moves
        # Have about ~10% more than expected, just for safety.
        self.ESPAxis.instrument.timeout = expectedTime * 1.1 * 1000 + self.ESPAxis.delay

        try:
            self.ESPAxis.position = float(self.ui.sbPosition.value())
        except Exception as e:
            log.exception("Error moving axis\n\tTimeout set to: {}".format(self.ESPAxis.instrument.timeout))
            self.setStatusWidget("Timeout", "QLabel { background-color : red; color : black; }")
            return
        self.sigCreateGuiElement.emit(self.cleanupMotorMove, [])

    def cleanupMotorMove(self, *args):
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(self.ESPAxis.position)
        self.ui.sbPosition.blockSignals(False)

        self.setStatusWidget("Ready", "QLabel { background-color : green; color : black; }")
        self.checkErrors()

    def checkErrors(self):
        errors = self.ESPAxis.error_message
        if "0" in errors.split(',')[0]: return
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
    e = QtGui.QApplication(sys.argv)
    win = MotorWindow(device = TIMS0201(), parent = None)
    sys.exit(e.exec_())