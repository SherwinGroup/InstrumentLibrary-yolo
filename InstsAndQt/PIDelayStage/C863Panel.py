from PyQt5 import QtCore, QtGui, QtWidgets
try:
    from UIs.piPanel_ui import Ui_PIPanel
except ModuleNotFoundError:
    from .UIs.piPanel_ui import Ui_PIPanel

try:
    from ..Instruments import C863
except ValueError:
    from InstsAndQt.Instruments import C863
from InstsAndQt.customQt import *
import numpy as np
import pyqtgraph
import logging
log = logging.getLogger("Instruments")


class C863Panel(QtWidgets.QWidget):
    thWaitForMotor = TempThread()
    sigCreateGuiElement = QtCore.pyqtSignal(object, object)
    # Emits a signal of error messages when encountered.
    sigErrorsEncountered = QtCore.pyqtSignal(object)

    def __init__(self, parent = None):
        super(C863Panel, self).__init__()

        self.instrument = None
        self.initUI()


        self.thWaitForMotor.finished.connect(self.cleanupMotorMove)
        self.sigCreateGuiElement.connect(self.createGuiElement)

    def initUI(self):
        self.ui = Ui_PIPanel()
        self.ui.setupUi(self)

        # self.ui.sbPosition.setOpts(step=1)
        self.ui.sbPosition.sigValueChanged.connect(lambda: self.startChangePosition(self.moveMotor))
        self.ui.sbPosition.setDecimals(6)
        self.ui.sbPosition.setMaximum(100000)
        self.ui.bGoHome.clicked.connect(lambda: self.startChangePosition(target=self.goHome))
        self.ui.cGPIB.setInstrumentClass(C863)
        self.ui.cGPIB.sigInstrumentOpened.connect(self.openMotor)
        self.ui.cGPIB.setAddress("ASRL3::INSTR")


    def toggleMotor(self, val):
        if val:
            self.openMotor()
        else:
            self.closeMotor()

    def openMotor(self, inst=None):

        if inst is not None:
            self.instrument = inst
        # inst = C863()

        inst.motorOn()

        self.ui.labelMoving.setText("Ready")
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(self.getPosition())
        self.ui.sbPosition.blockSignals(False)

    def getPosition(self):
        if self.instrument is None: return
        pos = self.instrument.getPosition()
        # convert the mm of the instrument to fs
        pos = C863Panel.mmtofs(pos)
        return pos

    # def closeMotor(self):
    #     log.debug("Closing motor")
    #     self.motor.close()
    #     for ii in self.disableElements: ii.setEnabled(False)
    #     self.ui.labelMoving.setText("Closed")
    #     self.ui.bOpen.setChecked(False)

    def setCurrentPosition(self):
        ### Not yet implemented for the C863
        raise NotImplementedError()
        val, ok = QtWidgets.QInputDialog.getDouble(self,"Current Position", "Current Angle:", 0)
        if ok:
            self.ui.sbPosition.blockSignals(True)
            self.motor.setPosition(val)
            self.ui.sbPosition.setValue(self.motor.getPosition())
            self.ui.sbPosition.blockSignals(False)

    def setHomeOffset(self):
        ### Not yet implemented for the C863
        raise NotImplementedError()
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
            ret = self.instrument.gotoNegativeReference(
                callback = lambda p: self.sigCreateGuiElement.emit(self._updatePosition, p),
                timeout = None
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
        # convert fs to mm
        value=C863Panel.fstomm(value)

        try:
            ret = self.instrument.move(
                value,
                callback = lambda p: self.sigCreateGuiElement.emit(self._updatePosition, p)
            )
            if not ret:
                self.setStatusWidget("Error", {"background-color": "red"})
        except Exception as e:
            log.exception("Error moving axis")
            self.setStatusWidget("Timeout", {"background-color" : "red"})
            return
        self.sigCreateGuiElement.emit(self._updatePosition, self.instrument.getPosition())

    def cleanupMotorMove(self, *args):
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(self.getPosition())
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
        # assume it's coming from the update from the motor directly,
        # which comes in mm
        val = C863Panel.mmtofs(val)
        self.ui.sbPosition.blockSignals(True)
        self.ui.sbPosition.setValue(val)
        self.ui.sbPosition.blockSignals(False)

    def createGuiElement(self, function, *args):
        function(*args)


    @staticmethod
    def fstomm(fs):
        mm = fs * 1e-15 * 2.9979e8 * 1e3/2
        print("{} fs -> {} mm".format(fs, mm))
        return mm

    @staticmethod
    def mmtofs(mm):
        fs = mm*2*1e-3/2.9979e8 * 1e15
        print("{} mm -> {} fs".format(mm, fs))
        return fs

    # def close(self):
    #     print("i got closed")
    #     self.closeMotor()

    # def closeEvent(self, ev):
    #     self.close()
    #     super(K10CR1Panel, self).closeEvent(ev)












if __name__ == "__main__":
    import sys


    e = QtWidgets.QApplication(sys.argv)
    win = C863Panel()
    win.show()
    sys.exit(e.exec_())
