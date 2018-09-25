from PyQt5 import QtCore, QtGui, QtWidgets
try:
    from UIs.thorlabsPanel_ui import Ui_ThorlabsPanel
except ModuleNotFoundError:
    from .UIs.thorlabsPanel_ui import Ui_ThorlabsPanel

try:
    from ..ThorlabsRotationStage import K10CR1
except ValueError:
    from InstsAndQt.ThorlabsRotationStage import K10CR1
from InstsAndQt.customQt import *
import numpy as np
import pyqtgraph
import logging
log = logging.getLogger("Instruments")


class K10CR1Panel(QtWidgets.QWidget):
    thWaitForMotor = TempThread()
    sigCreateGuiElement = QtCore.pyqtSignal(object, object)
    # Emits a signal of error messages when encountered.
    sigErrorsEncountered = QtCore.pyqtSignal(object)

    def __init__(self, parent = None):
        super(K10CR1Panel, self).__init__()
        try:
            # If you don't have the dlls for the motor, don't let it
            # wrap it up, but still make the UI. Note: You shouldn't
            # interact with the widget...
            self.motor = K10CR1()
            self.openMotor()
        except OSError:
            pass
        finally:
            self.initUI()
            self.thWaitForMotor.finished.connect(self.cleanupMotorMove)
            self.sigCreateGuiElement.connect(self.createGuiElement)

    def initUI(self):
        self.ui = Ui_ThorlabsPanel()
        self.ui.setupUi(self)

        # Easy list for iterating to set enabled/disabled when the device
        # isn't opened
        self.disableElements = [
            self.ui.sbPosition,
            self.ui.bSettings,
            self.ui.bGoHome
        ]

        # self.ui.sbPosition.valueChanged.connect(self.startChangePosition)
        self.ui.sbPosition.setOpts(step=1)
        self.ui.sbPosition.sigValueChanged.connect(lambda: self.startChangePosition(self.moveMotor))
        self.ui.bOpen.clicked.connect(self.toggleMotor)
        # self.ui.bSetPosition.clicked.connect(self.setCurrentPosition)
        # self.ui.bGoHome.clicked.connect(self.goHome)
        self.ui.bGoHome.clicked.connect(lambda: self.startChangePosition(target=self.goHome))

        menu = QtWidgets.QMenu()
        menu.addAction("Set Position").triggered.connect(self.setCurrentPosition)
        menu.addAction("Set Home Offset").triggered.connect(self.setHomeOffset)
        self.ui.bSettings.setMenu(menu)

    def toggleMotor(self, val):
        if val:
            self.openMotor()
        else:
            self.closeMotor()

    def openMotor(self):
        mod = QtWidgets.QApplication.keyboardModifiers()
        if mod == QtCore.Qt.ShiftModifier:
            # add a way to re-instantiate the motor, causing it to restart everything.
            # Think it's necessary if you plug the device in after starting the software
            log.debug("Re-instantiating the motor")
            try:
                self.motor.close()
            except:
                pass
            self.motor = K10CR1()

        ret = self.motor.open()
        if not ret:
            # opening the motor failed, so disable everything
            log.debug("calling Closing motor")
            self.closeMotor()
            return
        for ii in self.disableElements: ii.setEnabled(True)
        self.ui.labelMoving.setText("Ready")
        self.ui.bOpen.setChecked(True)
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(self.motor.getPosition())
        self.ui.sbPosition.blockSignals(False)

    def closeMotor(self):
        log.debug("Closing motor")
        self.motor.close()
        for ii in self.disableElements: ii.setEnabled(False)
        self.ui.labelMoving.setText("Closed")
        self.ui.bOpen.setChecked(False)

    def setCurrentPosition(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self,"Current Position", "Current Angle:", 0)
        if ok:
            self.ui.sbPosition.blockSignals(True)
            self.motor.setPosition(val)
            self.ui.sbPosition.setValue(self.motor.getPosition())
            self.ui.sbPosition.blockSignals(False)

    def setHomeOffset(self):
        val, ok = QtWidgets.QInputDialog.getDouble(self,"Current Position",
                               "Current Angle:",
                               self.motor.getHomeOffset())
        if ok:
            self.ui.sbPosition.blockSignals(True)
            self.motor.setHomeOffset(val)
            self.ui.sbPosition.setValue(self.motor.getPosition())
            self.ui.sbPosition.blockSignals(False)

    def goHome(self):
        try:
            ret = self.motor.home(
                callback = lambda p: self.sigCreateGuiElement.emit(self._updatePosition, p),
                timeout = False
            )
            if not ret:
                self.setStatusWidget("Error", {"background-color": "red"})
        except Exception as e:
            log.exception("Error homing axis")
            self.setStatusWidget("Timeout", {"background-color" : "red"})
            return

    def startChangePosition(self, target=None ):
        """
        Start the thread for waiting for the motor to move
        :param target: Fucntion to thread. If none, defaults to self.moveMotor. If false, doesn't thread.
        :return:
        """
        if target is None:
            target = self.moveMotor

        self.setStatusWidget("Moving",
                             {"background-color" : "yellow"})


        if target:
            self.thWaitForMotor.target = target
            self.thWaitForMotor.start()

    def moveMotor(self, value = None):
        if value is None:
            value = self.ui.sbPosition.value()
        value = float(value)
        try:
            ret = self.motor.moveAbsolute(
                value,
                callback = lambda p: self.sigCreateGuiElement.emit(self._updatePosition, p)
            )
            if not ret:
                self.setStatusWidget("Error", {"background-color": "red"})
        except Exception as e:
            log.exception("Error moving axis")
            self.setStatusWidget("Timeout", {"background-color" : "red"})
            return

    def cleanupMotorMove(self, *args):
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(self.motor.getPosition())
        self.ui.sbPosition.blockSignals(False)

        self.setStatusWidget("Ready", {"background-color" : "green"})

    def setStatusWidget(self, text="", styleSheet=dict()):
        """
        convenience function to set the text and style of the "ready/moving/tiemout" status
        label. Thread-safe(?) in that it will emit a signal.
        :param text: What text
        :param styleSheet: Stylesheet for the label.
        :return:
        """
        style = {
            "background-color": "green",
            "color": "black"
        }
        style.update(styleSheet)
        styleSheetStr = "QLabel { " \
                        f"background-color : {style['background-color']};" \
                        f"color : {style['color']}; " \
                        "}"
        self.sigCreateGuiElement.emit(self.ui.labelMoving.setText, text)

        self.sigCreateGuiElement.emit(
                self.ui.labelMoving.setStyleSheet,
                styleSheetStr)

    def _updatePosition(self, val):
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(val)
        self.ui.sbPosition.blockSignals(False)

    def createGuiElement(self, function, *args):
        function(*args)

    def close(self):
        print("i got closed")
        self.closeMotor()

    def closeEvent(self, ev):
        self.close()
        super(K10CR1Panel, self).closeEvent(ev)












if __name__ == "__main__":
    import sys


    e = QtWidgets.QApplication(sys.argv)
    win = K10CR1Panel()
    win.show()
    sys.exit(e.exec_())
