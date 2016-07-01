from PyQt4 import QtGui, QtCore
import time
import numpy as np
from InstsAndQt.Instruments import LakeShore330
import pyqtgraph as pg
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

from lakeshore330Panel_ui import Ui_Form

class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        for x in values:
            try:
                strns.append(time.strftime("%X", time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        return strns

class LakeshoreMonitor(QtGui.QWidget):
    def __init__(self):
        super(LakeshoreMonitor, self).__init__()

        self.instrument = LakeShore330("GPIB0::12::INSTR")
        self.tempData=np.array([[time.time(), self.instrument.getSampleTemp(),
                                 self.instrument.getHeaterRange(), self.instrument.getHeater(),
                                 self.instrument.getSetpoint()]])
        self.initUI()
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.setInterval(1000)
        self.updateTimer.timeout.connect(self.updateDisplays)
        self.updateTimer.start()

        self.saveLoc = r'Z:\Hunter Banks\Data\2016\\'


    def initUI(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("Sample Temperature Monitor")
        self.ui.splitter.setStretchFactor(0, 100)
        self.ui.splitter.setStretchFactor(1,1)

        self.ui.sbSetpoint.setValue(
            self.instrument.getSetpoint()
        )

        self.ui.cbHeater.setCurrentIndex(
            self.instrument.getHeaterRange()
        )

        self.ui.sbSetpoint.valueChanged.connect(
            self.setSetpoint
        )

        self.ui.cbHeater.currentIndexChanged.connect(
            self.updateHeater
        )

        self.tempCurve = self.ui.gTemp.plot(pen='k')

        #change the string format on the plot to
        # show the time
        pi = self.ui.gTemp.plotItem
        pi.layout.removeItem(pi.getAxis('bottom'))
        caxis = DateAxis(orientation='bottom', parent=pi)
        caxis.linkToView(pi.vb)
        pi.axes["bottom"]["item"] = caxis
        pi.layout.addItem(caxis, 3,1)


        auto = QtGui.QMenu("Autoscroll", self)
        self.ui.cbAutoEnabled = QtGui.QCheckBox("Enabled")
        self.ui.cbAutoEnabled.setChecked(True)
        self.ui.sbAutoTime = pg.SpinBox(value=10, step=1, decimals=1, bounds=(0, 600))
        self.ui.cbAutoEnabled.stateChanged.connect(
            lambda x:self.ui.sbAutoTime.setEnabled(x)
        )
        wid = QtGui.QWidget(None)
        layout = QtGui.QHBoxLayout(wid)
        layout.addWidget(self.ui.cbAutoEnabled)
        layout.addWidget(self.ui.sbAutoTime)
        wid.setLayout(layout)
        self.ui.acAutoTime = QtGui.QWidgetAction(None)
        self.ui.acAutoTime.setDefaultWidget(wid)
        auto.addAction(self.ui.acAutoTime)

        pi.vb.menu.addMenu(auto)

        pid = pi.vb.menu.addAction("Change PID")
        pid.triggered.connect(self.changePID)
        save = pi.vb.menu.addAction("Save Trace...")
        save.triggered.connect(self.saveData)

        self.updateDisplays()
        self.show()

    def setSetpoint(self):
        self.instrument.setSetpoint(
            self.ui.sbSetpoint.value()
        )

    def updateHeater(self):
        self.instrument.setHeaterRange(
            int(self.ui.cbHeater.currentIndex())
        )

    def updateDisplays(self):
        temp = self.instrument.getSampleTemp()
        self.ui.tTemp.setText(str(temp))

        heat = self.instrument.getHeater()
        self.ui.pHeater.setValue(heat)

        self.tempData = np.row_stack((
            self.tempData, [[time.time(), temp,
                             self.instrument.getHeaterRange(), heat,
                             self.instrument.getSetpoint()]]
        ))

        self.tempCurve.setData(self.tempData[:,0], self.tempData[:,1])

        if self.ui.cbAutoEnabled.isChecked():
            self.updateAutoscale()

        self.addDropline()

    def changePID(self):
        PIDWid.changePIDValues(self, self.instrument)

    def saveData(self):
        loc = QtGui.QFileDialog.getSaveFileName(self, "Save File Name", self.saveLoc)
        if not loc: return
        # if not loc[-4:].lower() == ".txt": loc+=".txt"
        self.saveLoc = str(loc)

        oh = '#\n'*100
        oh += "Time,Temperature,Heater Setting,Heater Output,Setpoint\n"
        oh += "s,K,,%,K\n"
        oh += "Time,Temp,Heater,Output,SP"
        np.savetxt(self.saveLoc, self.tempData, fmt=["%.11e","%.2f", "%d", "%d", "%.2f"],
                   delimiter=',', header=oh, comments='')

    def addDropline(self):
        curtime = time.localtime(self.tempData[-1,0])
        # if curtime.tm_sec%3==0:
        if curtime.tm_min%15==0 and curtime.tm_sec==0:
            color = pg.mkColor("#0000003f")
            # if curtime.tm_sec%9==0:
            if curtime.tm_min==0:
                color = pg.mkColor("#000000FF")
            lin = pg.InfiniteLine(pen=pg.mkPen(color, width=2), movable=False,
                                  pos=int(self.tempData[-1,0]))
            self.ui.gTemp.plotItem.addItem(lin)

    def updateAutoscale(self):
        dt = self.ui.sbAutoTime.value()*60
        x1 = self.tempData[-1,0]-dt
        x2 = self.tempData[-1,0]
        self.ui.gTemp.setXRange(x1, x2)
        try:
            y1idx = np.where(self.tempData[:,0]>x1)[0][0]
        except IndexError:
            y1idx = 0
        y1 = self.tempData[y1idx:, 1].min()
        y2 = self.tempData[y1idx:, 1].max()
        if y1<y2:
            y11 = y1 - 0.1*np.abs(y2-y1)
            y22 = y2 + 0.1*np.abs(y2-y1)
        elif y1==y2:
            y11 = y1 - 3
            y22 = y2 + 3
        else:
            y11 = y2 + 0.05*np.abs(y2-y1)
            y22 = y1 - 0.05*np.abs(y2-y1)
        self.ui.gTemp.setYRange(y11, y22, padding=0)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.resize(269, 94)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setFlat(True)
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setContentsMargins(0, 10, 0, 0)
        self.tP = QtGui.QLineEdit(self.groupBox)
        self.horizontalLayout.addWidget(self.tP)
        self.horizontalLayout_4.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setFlat(True)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setContentsMargins(0, 10, 0, 0)
        self.tI = QtGui.QLineEdit(self.groupBox_2)
        self.horizontalLayout_2.addWidget(self.tI)
        self.horizontalLayout_4.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setFlat(True)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setContentsMargins(0, 10, 0, 0)
        self.tD = QtGui.QLineEdit(self.groupBox_3)
        self.horizontalLayout_3.addWidget(self.tD)
        self.horizontalLayout_4.addWidget(self.groupBox_3)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
        Dialog.setWindowTitle("PID Settings")
        self.groupBox.setTitle("P")
        self.groupBox_2.setTitle("I")
        self.groupBox_3.setTitle("D")

class PIDWid(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        self.instrument = kwargs.pop("inst", None)
        super(PIDWid, self).__init__(*args, **kwargs)

        self.initUI()

    def initUI(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        P, I, D = self.instrument.getPID()

        self.ui.tP.setText(str(P))
        self.ui.tI.setText(str(I))
        self.ui.tD.setText(str(D))

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.setPID)

    def setPID(self):
        P = int(self.ui.tP.text())
        I = int(self.ui.tI.text())
        D = int(self.ui.tD.text())
        self.instrument.setPID(P, I, D)

    @staticmethod
    def changePIDValues(parent, inst):
        wid = PIDWid(parent, inst=inst)
        result = wid.exec_()







if __name__ == '__main__':
    import sys
    ap = QtGui.QApplication([])
    win = LakeshoreMonitor()
    sys.exit(ap.exec_())

