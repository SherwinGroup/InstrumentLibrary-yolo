from PyQt4 import QtCore, QtGui
from UIs.axisPanel_ui import Ui_ESPAxisPanel
# from esp300 import ESP300
from ..Instruments import ESP300
from InstsAndQt.customQt import *
import numpy as np
import pyqtgraph


class ESPAxisPanel(QtGui.QWidget):
    thWaitForMotor = TempThread()
    sigCreateGuiElement = QtCore.pyqtSignal(object, object)

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
        self.ui.sbPosition.sigValueChanged.connect(self.startChangePosition)
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
        self.ESPAxis.instrument.write("{}OR".format(self.ESPAxis.current_axis))
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(self.ESPAxis.position)
        self.ui.sbPosition.blockSignals(False)



    def toggleMotor(self):
        try:
            self.ESPAxis.motor_on = bool(self.ui.cbOn.isChecked())
        except Exception as e:
            print "Error turning motor on", e


    def openESPAxis(self, axis):
        self.ESPAxis = ESP300(self.GPIB, current_axis=axis)

        self.ui.sbAxis.setValue(axis)
        self.ui.sbPosition.setValue(self.ESPAxis.position)
        self.ui.labelMoving.setStyleSheet("QLabel { background-color : green; color : black; }")

        self.ui.cbOn.setChecked(bool(self.ESPAxis.motor_on))

    def startChangePosition(self):
        self.ui.labelMoving.setStyleSheet("QLabel { background-color : yellow; color : black; }")
        self.ui.labelMoving.setText("Moving")

        self.thWaitForMotor.target = self.moveMotor
        self.thWaitForMotor.start()

    def moveMotor(self):

        expectedTime = np.abs(self.ESPAxis.position - float(self.ui.sbPosition.value()))/self.ESPAxis.velocity


        # force minimum of 10s
        expectedTime = max(expectedTime, 10)
        # Update the timeout time so it won't break when you want long moves
        # Have about ~10% more than expected, just for safety.
        self.ESPAxis.instrument.timeout = expectedTime * 1.1 * 1000 + self.ESPAxis.delay

        try:
            self.ESPAxis.position = float(self.ui.sbPosition.value())
        except Exception as e:
            print "ERROR",e
            print "timeout was", self.ESPAxis.instrument.timeout


            self.sigCreateGuiElement.emit(self.ui.labelMoving.setText, ("Timeout", ))

            self.sigCreateGuiElement.emit(
                    self.ui.labelMoving.setStyleSheet,
                    ("QLabel { background-color : red; color : black; }", ))
            return

        self.sigCreateGuiElement.emit(self.ui.sbPosition.blockSignals, (True,))
        self.sigCreateGuiElement.emit(
            self.ui.sbPosition.setValue, (self.ESPAxis.position, True, False)
        )
        self.sigCreateGuiElement.emit(self.ui.sbPosition.blockSignals, (False,))

        self.sigCreateGuiElement.emit(self.ui.labelMoving.setText, ("Ready", ))

        self.sigCreateGuiElement.emit(
                self.ui.labelMoving.setStyleSheet,
                ("QLabel { background-color : green; color : black; }", ))

    def createGuiElement(self, function, args):
        function(*args)













if __name__ == "__main__":
    import sys
    e = QtGui.QApplication(sys.argv)
    win = MotorWindow(device = TIMS0201(), parent = None)
    sys.exit(e.exec_())