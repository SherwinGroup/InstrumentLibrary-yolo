from PyQt4 import QtGui, QtCore
import numpy as np
import time
import scipy.optimize as spo
import pyqtgraph as pg
import os

from calibrator_ui import Ui_PyroCalibration
    
class PyroCalibrator(QtGui.QMainWindow):
    def __init__(self):
        super(PyroCalibrator, self).__init__()
        self.initUI()
        self.calData = []
        self.calFactor = 0
        self.clearCalData()

        self.intermediateData = [None, None]

        # A timer to make sure the signals from the TK and
        # pyro come at the same time, to prevent mixing
        # results from different pulses
        self.synchronizer = QtCore.QTimer()
        self.synchronizer.setSingleShot(True)
        # Set it to 150ms interval, so the two signals have to be
        # that close together. I don't think the FEL will ever run
        # at 7 Hz, so we don't need to worry about this allowing
        # different pulses.
        self.synchronizer.setInterval(150)

        # Set the pyro widget to always try to count
        # pulses
        self.ui.pyroWid.settings["exposing"] = True

        self.saveDir = r'Z:\Hunter Banks\Data\2016'

    def initUI(self):
        self.ui = Ui_PyroCalibration()
        self.ui.setupUi(self)

        self.ui.pyroWid.sigPulseCounted.connect(self.appendData)
        self.ui.TKWid.sigPulseEnergy.connect(self.appendData)
        self.ui.TKWid.ui.gbAveraging.setChecked(False)


        # add a textbox for pk-pk value
        self.calText = pg.TextItem('', color=(0, 0, 0))
        self.calText.setPos(0, 0)
        self.calText.setFont(QtGui.QFont("", 15))
        self.ui.gRatio.sigRangeChanged.connect(self.updateCalTextPos)

        self.ui.gRatio.addItem(self.calText)
        self.pCalPoints = self.ui.gRatio.plotItem.plot(pen=None, symbol='o')
        self.pCalLine = self.ui.gRatio.plotItem.plot(pen='k')
        pi = self.ui.gRatio.plotItem
        pi.setLabel("bottom", "Pyro Signal", "V")
        pi.setLabel("left", "Pulse Energy", "mJ")

        save = pi.vb.menu.addAction("Save Points...")
        save.triggered.connect(self.saveData)

        self.ui.bDoublePause.clicked.connect(self.toggleBothScopes)
        self.ui.pyroWid.ui.bOPause.clicked.connect(self.toggleBothScopes)
        self.ui.TKWid.ui.bOPause.clicked.connect(self.toggleBothScopes)
        self.ui.bClear.clicked.connect(self.clearCalData)



        self.show()

    def toggleBothScopes(self, newVal):
        if self.sender() == self.ui.bDoublePause:
            for wid in [self.ui.pyroWid.ui.bOPause, self.ui.TKWid.ui.bOPause]:
                # wid.blockSignals(True)
                wid.clicked.disconnect(self.toggleBothScopes)
                wid.setChecked(newVal)
                wid.clicked.emit(newVal)
                wid.clicked.connect(self.toggleBothScopes)
                # wid.blockSignals(False)
            # self.ui.pyroWid.ui.bOPause.setChecked(newVal)
            # self.ui.TKWid.ui.bOPause.setChecked(newVal)
        else:
            tp = self.ui.TKWid.ui.bOPause.isChecked()
            pp = self.ui.pyroWid.ui.bOPause.isChecked()

            if (tp and pp):
                self.ui.bDoublePause.setChecked(True)
            else:
                self.ui.bDoublePause.setChecked(False)

    def updateCalTextPos(self, null, range):
        self.calText.setPos(range[0][0], range[1][1])

    def clearCalData(self):
        self.ui.pyroWid.settings["FELPulses"] = 0
        self.calData = np.empty((0,2))

    def appendData(self, data):
        if not self.ui.bCal.isChecked(): return
        if self.sender() is self.ui.pyroWid:
            idx = 0
            # skip a bad pulse
            if data<0: return
            data = self.ui.pyroWid.settings["pyroVoltage"][-1]
        elif self.sender() is self.ui.TKWid:
            idx = 1
        else:
            raise RuntimeError("Who sent this data? {}, {}".format(self.sender(), data))

        self.intermediateData[idx] = data
        if self.synchronizer.isActive():
            if None in self.intermediateData:
                raise RuntimeError("How is the timer active with not-full data? {}".format(self.intermediateData))
            self.calData = np.row_stack((self.calData, self.intermediateData))
            self.intermediateData = [None]*2
            self.updateCalibration()
        else:
            self.synchronizer.start()

    def saveData(self):
        loc = QtGui.QFileDialog.getSaveFileName(
            self, "Choose save file", self.saveDir
        )
        loc = str(loc)
        if not loc: return
        self.saveDir = os.path.dirname(loc)


        oh = "#{"+"\n#\t'Freq': {}\n#\t'Cal Factor': {}\n#".format(
            self.ui.TKWid.ui.tFELFreq.value()*29.9979,
            self.calFactor*1e-3
        )+"}\n"
        oh += "Pyro Voltage,TK Energy\n"
        oh += "mV,mJ\n"
        oh += "Pyro Voltage,TK Energy"

        saveData = self.calData.copy()
        saveData[:,0]*=1e3

        np.savetxt(loc, saveData, fmt='%f', delimiter=',',
                   comments='', header=oh)



    def updateCalibration(self):
        self.pCalPoints.setData(self.calData)
        cal, _ = spo.curve_fit(lambda x,m: m*x, *self.calData.T)
        mn, mx = self.calData[:,0].min(), self.calData[:,0].max()

        self.calFactor = cal[0]
        pts = np.array([mn-(mx-mn)*.05, mx+(mx-mn)*.05 ])
        self.calText.setText("{:.3f} mJ/mV".format(self.calFactor*1e-3), color=(0,0,0))
        self.pCalLine.setData(pts, pts*self.calFactor)

    def closeEvent(self, *args, **kwargs):
        self.ui.pyroWid.close()
        self.ui.TKWid.close()
        super(PyroCalibrator, self).closeEvent(*args, **kwargs)



if __name__ == '__main__':
	import sys
	ap = QtGui.QApplication(sys.argv)
	wid = PyroCalibrator()
	wid.show()
	sys.exit(ap.exec_())
