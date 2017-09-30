from PyQt5 import QtCore, QtGui, QtWidgets
import time


import numpy as np


from InstsAndQt.Instruments import DG535


import pyqtgraph as pg


pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

# Support for running as a standalone object,
# or imported into another.
#
#
try:
    from .delayGenerator_ui import Ui_MainWindow
except ModuleNotFoundError:
    from delayGenerator_ui import Ui_MainWindow




class DG535Monitor(QtWidgets.QMainWindow):

    # emit as <str 'Changed Channel'>,
    #         <tup (old ref, new ref)>,
    #         <
    sigDelayChanged = QtCore.pyqtSignal(object, object, object)
    sigClosed = QtCore.pyqtSignal()
    def __init__(self):
        super(DG535Monitor, self).__init__()
        self.instrument = None
        self.initUI()

        self.channelMap = {
            "A": (self.ui.cbARef, self.ui.dATime),
            "B": (self.ui.cbBRef, self.ui.dBTime),
            "C": (self.ui.cbCRef, self.ui.dCTime),
            "D": (self.ui.cbDRef, self.ui.dDTime)
        }


        self.ui.cbARef.currentIndexChanged.connect(
            lambda: self.updateDelay("A"))
        self.ui.dATime.editor.sigNewValue.connect(
            lambda: self.updateDelay("A"))

        self.ui.cbBRef.currentIndexChanged.connect(
            lambda: self.updateDelay("B"))
        self.ui.dBTime.editor.sigNewValue.connect(
            lambda: self.updateDelay("B"))

        self.ui.cbCRef.currentIndexChanged.connect(
            lambda: self.updateDelay("C"))
        self.ui.dCTime.editor.sigNewValue.connect(
            lambda: self.updateDelay("C"))

        self.ui.cbDRef.currentIndexChanged.connect(
            lambda: self.updateDelay("D"))
        self.ui.dDTime.editor.sigNewValue.connect(
            lambda: self.updateDelay("D"))

        if "GPIB0::15::INSTR" in self.ui.cbGPIB:
            self.ui.cbGPIB.setAddress("GPIB0::15::INSTR")





    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.cbGPIB.setInstrumentClass(DG535)
        self.ui.cbGPIB.sigInstrumentOpened.connect(self.refreshValues)

        self.ui.cbGPIB.setFixedWidth(130)

        self.ui.tTriggerRate.setValidator(QtGui.QDoubleValidator())
        self.ui.tTriggerBCount.setValidator(QtGui.QIntValidator())
        self.ui.tTriggerBPeriod.setValidator(QtGui.QIntValidator())
        self.ui.tTriggerLevel.setValidator(QtGui.QDoubleValidator())

        self.show()

        # fix width/height to be minimized when window is created. QtDesigner was messing
        # this up.
        self.setGeometry(QtCore.QRect(
            self.geometry().x(),
            self.geometry().y(),
            246,339
            )
        )

    def refreshValues(self, inst=None):
        """
        Query the device to update all of the display panels
        :return:
        """
        if inst is not None:
            self.instrument = inst

        for ch, (cbRef, dTime) in list(self.channelMap.items()):
            ref, tim = self.instrument.getDelay(ch)
            # if timeout errors occured, the
            if ref == tim == -1:
                ref = "D"
                tim = -1

            cbRef.blockSignals(True)
            dTime.blockSignals(True)

            cbRef.setCurrentIndex(cbRef.findText(ref))
            dTime.editor.setValue(tim)

            cbRef.blockSignals(False)
            dTime.blockSignals(False)

        self.updateTriggerPanel()

    def updateTriggerPanel(self):
        trig = self.instrument.getTriggerMode()

        if trig == 0:
            self.ui.rateLabel.setVisible(True)
            self.ui.tTriggerRate.setVisible(True)

            self.ui.levelVLabel.setVisible(False)
            self.ui.tTriggerLevel.setVisible(False)

            self.ui.slopeLabel.setVisible(False)
            self.ui.cbTriggerSlope.setVisible(False)

            self.ui.inputLoadLabel.setVisible(False)
            self.ui.cbTriggerLoad.setVisible(False)

            self.ui.burstCountLabel.setVisible(False)
            self.ui.tTriggerBCount.setVisible(False)

            self.ui.burstPeriodLabel.setVisible(False)
            self.ui.tTriggerBPeriod.setVisible(False)

            self.ui.bTriggerSingleShot.setVisible(False)
        elif trig == 1:
            self.ui.rateLabel.setVisible(False)
            self.ui.tTriggerRate.setVisible(False)

            self.ui.levelVLabel.setVisible(True)
            self.ui.tTriggerLevel.setVisible(True)

            self.ui.slopeLabel.setVisible(True)
            self.ui.cbTriggerSlope.setVisible(True)

            self.ui.inputLoadLabel.setVisible(True)
            self.ui.cbTriggerLoad.setVisible(True)

            self.ui.burstCountLabel.setVisible(False)
            self.ui.tTriggerBCount.setVisible(False)

            self.ui.burstPeriodLabel.setVisible(False)
            self.ui.tTriggerBPeriod.setVisible(False)

            self.ui.bTriggerSingleShot.setVisible(False)

        self.ui.cbTriggerMode.blockSignals(True)
        self.ui.cbTriggerMode.setCurrentIndex(trig)
        self.ui.cbTriggerMode.blockSignals(False)

        rate = self.instrument.getTriggerRate(trig==3)

        self.ui.tTriggerRate.blockSignals(True)
        self.ui.tTriggerRate.setText("{:f}".format(rate))
        self.ui.tTriggerRate.blockSignals(False)

        self.ui.tTriggerLevel.blockSignals(True)
        self.ui.tTriggerLevel.setText("{:f}".format(self.instrument.getTriggerLevel()))
        self.ui.tTriggerLevel.blockSignals(False)

        self.ui.cbTriggerSlope.blockSignals(True)
        self.ui.cbTriggerSlope.setCurrentIndex(self.instrument.getTriggerSlope())
        self.ui.cbTriggerSlope.blockSignals(False)

        self.ui.cbTriggerLoad.blockSignals(True)
        self.ui.cbTriggerLoad.setCurrentIndex(self.instrument.getTriggerLoad())
        self.ui.cbTriggerLoad.blockSignals(False)

        #Todo implement burst stuff

    def updateDelay(self, ch):
        ref, tim = self.channelMap[ch]
        print("updating trigger", tim.editor.value())
        oldRef, oldTim = self.instrument.getDelay(ch)
        self.instrument.setDelay(ch, str(ref.currentText()), tim.editor.value())

        self.sigDelayChanged.emit(
            ch, (oldRef, ref.currentText()), (oldTim, tim.editor.value())
        )

    def closeEvent(self, *args, **kwargs):
        self.sigClosed.emit()






if __name__ == '__main__':
    import sys


    print(sys.argv)
    ap = QtWidgets.QApplication([])
    if "slave" in sys.argv:
        win = DG535Monitor()
        print("made a slave delay window")
        ap.exec_()
        print("exited slave delay window")
    else:
        win = DG535Monitor()
        print("made a delay window")
        sys.exit(ap.exec_())

