from PyQt4 import QtCore, QtGui
from ControlPanel_ui import Ui_Form
from InstsAndQt.MotorDriver import *
from InstsAndQt.customQt import *
import pyqtgraph



class SettingsWindow(QtGui.QWidget):
    # emit a list of values to update the voltages/currents of the coils
    sigUpdatePowers = QtCore.pyqtSignal(object)
    thMonitorVoltage = None
    doLoops = True

    mutex = QtCore.QMutex()

    def __init__(self, device = None, parent = None):
        super(SettingsWindow, self).__init__()
        if device is not None:
            self.device = device
        else:
            self.device = TIMS0201()
            self.device.open_()

        self.mainParentWindow = parent

        self.initUI()
        self.thMonitorVoltage = TempThread(target = self.monitorVoltageLoop)
        self.thMonitorVoltage.start()
        self.sigUpdatePowers.connect(self.updateVoltages)

    def initUI(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # self.ui.sbCurrent.setInputMask("09")
        # self.ui.sbCurrent.editingFinished.connect(self.updateCurrent)
        # self.ui.sbCurrent.setSuffix("%")
        self.ui.sbCurrent.setOpts(int = True, step=1, bounds = (0, 100))
        self.ui.sbCurrent.sigValueChanged.connect(self.updateCurrent)
        self.ui.slideCurrent.valueChanged.connect(self.updateCurrent)


        self.ui.sbStepRate.setOpts(int = True, step=1, bounds = (0, 700))
        self.ui.sbStepRate.sigValueChanged.connect(self.updateStepRate)
        self.ui.slideStepRate.valueChanged.connect(self.updateStepRate)

        current = self.device.getCurrentLimit()
        self.ui.sbCurrent.setValue(current)

        stepRate = self.device.getStepRate()
        self.ui.sbStepRate.setValue(stepRate)

        self.ui.bOK.clicked.connect(self.close)


        self.show()

    def updateCurrent(self):
        sent = self.sender()
        if sent == self.ui.sbCurrent:
            newVal = sent.interpret()
            if newVal > 35:
                newVal = 35
                sent.blockSignals(True)
                sent.setValue(newVal)
                sent.blockSignals(False)
            # prevent infinite recursions
            self.ui.slideCurrent.blockSignals(True)
            self.ui.slideCurrent.setValue(newVal)
            self.ui.slideCurrent.blockSignals(False)
        else:
            newVal = sent.value()
            if newVal > 35:
                newVal = 35
                sent.blockSignals(True)
                sent.setValue(newVal)
                sent.blockSignals(False)
            self.ui.sbCurrent.blockSignals(True)
            self.ui.sbCurrent.setValue(newVal)
            self.ui.sbCurrent.blockSignals(False)

        self.device.setCurrentLimit(newVal)


        # update them in case something went wrong and wasn't actually udpated
        newVal = self.device.getCurrentLimit()
        self.ui.slideCurrent.blockSignals(True)
        self.ui.slideCurrent.setValue(newVal)
        self.ui.slideCurrent.blockSignals(False)
        self.ui.sbCurrent.blockSignals(True)
        self.ui.sbCurrent.setValue(newVal)
        self.ui.sbCurrent.blockSignals(False)

    def updateStepRate(self):
        sent = self.sender()
        if sent == self.ui.sbStepRate:
            newVal = sent.interpret()
            # if newVal > 20:
            #     newVal = 20
            #     sent.blockSignals(True)
            #     sent.setValue(newVal)
            #     sent.blockSignals(False)
            # prevent infinite recursions
            self.ui.slideStepRate.blockSignals(True)
            self.ui.slideStepRate.setValue(newVal)
            self.ui.slideStepRate.blockSignals(False)
        else:
            newVal = sent.value()
            # if newVal > 20:
            #     newVal = 20
            #     sent.blockSignals(True)
            #     sent.setValue(newVal)
            #     sent.blockSignals(False)
            self.ui.sbStepRate.blockSignals(True)
            self.ui.sbStepRate.setValue(newVal)
            self.ui.sbStepRate.blockSignals(False)

        self.device.setStepRate(newVal)


        # update them in case something went wrong and wasn't actually udpated
        newVal = self.device.getStepRate()
        self.ui.slideStepRate.blockSignals(True)
        self.ui.slideStepRate.setValue(newVal)
        self.ui.slideStepRate.blockSignals(False)
        self.ui.sbStepRate.blockSignals(True)
        self.ui.sbStepRate.setValue(newVal)
        self.ui.sbStepRate.blockSignals(False)

    def monitorVoltageLoop(self):
        while self.doLoops:
            self.sigUpdatePowers.emit(self.device.getMotorPowers())
            time.sleep(100./1000.)

    def updateVoltages(self, values):
        # print "\tvalues = {}".format(values)
        if values is None:
            return
        self.ui.tVoltage.setText("{:.3f}".format(values[0]))
        self.ui.tWA.setText("{:.5f}".format(values[1]))
        self.ui.tWB.setText("{:.5f}".format(values[2]))





    def closeEvent(self, QCloseEvent):
        if self.mainParentWindow == None:
            print "closing device"
            self.device.close_()
        self.doLoops = False
        try:
            self.thMonitorVoltage.wait()
        except:
            pass
        QCloseEvent.accept()











if __name__ == "__main__":
    import sys
    e = QtGui.QApplication(sys.argv)
    win = SettingsWindow(device = TIMS0201(), parent = None)
    sys.exit(e.exec_())