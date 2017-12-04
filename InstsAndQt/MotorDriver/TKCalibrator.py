
from PyQt5 import QtCore, QtGui, QtWidgets
from InstsAndQt.customQt import TempThread
from InstsAndQt.TKOscope.TKWid import TKWid
from InstsAndQt.MotorDriver.motorMain import MotorWindow
import time
import numpy as np
import glob
import os
from scipy.interpolate import interp1d as i1d
from scipy.optimize import curve_fit as cf
import pyqtgraph as pg

try:
    from .wiregridcal_ui import Ui_MainWindow
except ModuleNotFoundError:
    from wiregridcal_ui import Ui_MainWindow
# from .scopeCollect import Win as ScopeViewWidget



tkTrans = np.array(
    [
    [000, 1.0],
    [100, 0.975],
    [200, 0.95],
    [300, 0.91],
    [400, 0.9],
    [500, 0.88],
    [600, 0.86],
    [700, 0.84],
    [800, 0.81],
    [900, 0.78],
    [1000, 0.75],
    [1100, 0.73],
    [1200, 0.7],
    [1300, 0.68],
    [1400, 0.66],
    [1500, 0.64],
    [1600, 0.63],
    [1700, 0.6],
    [1800, 0.59],
    [1900, 0.58],
    [2000, 0.56],
    [2100, 0.55],
    [2200, 0.54],
    [2300, 0.53],
    [2400, 0.528],
    [2500, 0.53],
    [2600, 0.529],
    [2700, 0.534],
    [2800, 0.535],
    [2900, 0.537],
    [3000, 0.534],
    [3100, 0.531],
    [3200, 0.519],
    [3300, 0.516],
    [3400, 0.514],
    [3500, 0.512],
    [3600, 0.507],
    [3700, 0.503],
    [3800, 0.498],
    [3900, 0.491],
    [4000, 0.478],
    [4100, 0.461],
    [4200, 0.444],
    [4300, 0.434],
    [4400, 0.437],
    [4500, 0.444],
    [4600, 0.447],
    [4700, 0.449],
    [4800, 0.45],
    [4900, 0.452],
    [5000, 0.452],
    [5100, 0.45],
    [5200, 0.444],
    [5300, 0.435],
    [5400, 0.424],
    [5500, 0.412],
    [5600, 0.399],
    [5700, 0.386],
    [5800, 0.371],
    [5900, 0.352],
    [6000, 0.328],
    [6100, 0.311],
    [6200, 0.293],
    [6300, 0.275],
    [6400, 0.255],
    [6500, 0.236],
    [6600, 0.215],
    [6700, 0.195],
    [6800, 0.179],
    [6900, 0.167],
    [7000, 0.16],
    [7100, 0.157],
    [7200, 0.155],
    [7300, 0.153],
    [7400, 0.149],
    [7500, 0.146],
    [7600, 0.146],
    [7700, 0.152],
    [7800, 0.155],
    [7900, 0.154],
    [8000, 0.152],
    [8100, 0.151],
    [8200, 0.147],
    [8300, 0.139],
    [8400, 0.13],
    [8500, 0.121],
    [8600, 0.108],
    [8700, 0.096],
    [8800, 0.091],
    [8900, 0.089],
    [9000, 0.095],
    [9100, 0.111],
    [9200, 0.127],
    [9300, 0.144],
    [9400, 0.157],
    [9500, 0.159],
    [9600, 0.168],
    [9700, 0.168],
    [9800, 0.175],
    [9900, 0.17],
    [10000, 0.174]]
)
tkTrans = i1d(tkTrans[:,0], tkTrans[:,1])


def minir(x, *p):
    A, mu, c = p
    return A*np.cos(np.deg2rad(x+mu))**4+c

tkCalFactor = 0.00502



class TKCalibrator(QtWidgets.QMainWindow):
    thWaitForScope = None
    thDoTKSweep = TempThread()
    sigDoGui = QtCore.pyqtSignal(object, object)
    def __init__(self):
        super(TKCalibrator, self).__init__()
        self.initUI()

        self.thDoTKSweep.target = self.doTKSweep
        self.sigDoGui.connect(self.makeGuiThings)


        self.settings = {
            "saveDir": r'Z:\~HSG\Data\2017',
            "thzSweepPoints": [0,15,25,32,35,39,44,50,54,58,60,63,68],
            "thzSweepPointsIter": iter([]),
            "saveData": [],
        }

        self.show()

    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.motorWid = self.ui.wMotor
        self.scopeWid = self.ui.wTK

        self.ui.fitWid = pg.PlotWidget()
        self.curveData = self.ui.fitWid.plotItem.plot(pen=None, symbol='o', brush='k')
        self.curveFit = self.ui.fitWid.plotItem.plot(pen='k')
        self.textFit = pg.TextItem()
        self.textFit.setFont(QtGui.QFont("", 15))
        self.ui.fitWid.plotItem.addItem(self.textFit, ignoreBounds=True)
        self.scopeWid.ui.tabWidget.addTab(self.ui.fitWid, "Cos Fit")
        # only emit signal when completed.
        self.scopeWid.settings["emit_mid_average"] = False

        self.ui.bSaveDir.clicked.connect(self.pickSaveDir)
        self.ui.bStartSweep.clicked.connect(self.startSweep)


    def pickSaveDir(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self,
                                                 "Save File",
                                                 self.settings["saveDir"],
                                                 "Text files (*.txt)")[0]
        if not path:
            return
        self.settings["saveDir"] = str(path)

    def startSweep(self, val):
        if not val:
            return
        st, ok = QtWidgets.QInputDialog.getText(self,
                    "Desired Angles",
                    "Enter angles in deg separated by commas",
                    text=",".join(map(str, self.settings["thzSweepPoints"])))
        if not ok:
            return
        self.settings["thzSweepPoints"] = [float(i) for i in st.split(',')]
        self.settings["thzSweepPointsIter"] = iter(self.settings["thzSweepPoints"])
        self.settings["saveData"] = []
        self.motorWid.moveMotorDeg(next(self.settings["thzSweepPointsIter"]))
        # for it to restart counting
        self.scopeWid.updateAveSize()
        # self.thDoTKSweep.start()
        self.scopeWid.sigPulseEnergy.connect(self.addSweepPoint)

    def doTKSweep(self):
        for angle in self.settings["thzSweepPoints"]:
            if not self.ui.bStartSweep.isChecked(): break
            print("at angle", angle)
            self.sigDoGui.emit(
                self.motorWid.ui.sbAngle.setValue, angle
            )
            self.motorWid.ui.bGo.clicked.emit(False)
            time.sleep(0.1)
            self.motorWid.thMoveMotor.wait()
            angleData = []
            for i in range(self.settings["numAve"]):
                print("\t num", i)
                waiter = QtCore.QEventLoop()
                self.scopeWid.ch1View.sigUpdateData.connect(waiter.exit)
                waiter.exec_()
                waveformData = self.scopeWid.ch1View.data.copy()
                try:
                    angleData = np.column_stack((angleData, waveformData[:,1]))
                except:
                    angleData = waveformData[:, 1]

            tkVal = self.processTKWaveform(angleData.mean(axis=1))
            print("\n\tmeasured {}\n\n".format(tkVal))


            self.settings["saveData"].append([angle, tkVal])

        self.sigDoGui.emit(
            self.ui.bStartSweep.setChecked, False
        )
        self.saveData()

    def addSweepPoint(self, energy):
        self.scopeWid.sigPulseEnergy.disconnect(self.addSweepPoint)
        self.settings["saveData"].append([self.motorWid.currentAngle, energy])
        self.statusBar().showMessage("At {:.2f}, measured {:.3f}".format(*self.settings["saveData"][-1]), 3000)
        print("At {:.2f}, measured {:.3f}".format(*self.settings["saveData"][-1]))
        self.updateFit()
        try:
            # Move the motor. Force an exit if the button was unchecked
            if not self.ui.bStartSweep.isChecked(): raise StopIteration
            self.motorWid.moveMotorDeg(next(self.settings["thzSweepPointsIter"]))
            self.motorWid.thMoveMotor.wait()
            if not self.ui.bStartSweep.isChecked(): raise StopIteration
        except StopIteration:
            self.ui.bStartSweep.setChecked(False)
            self.saveData()
            return
        # reset averaging so it's all taken after the motor moved
        self.scopeWid.updateAveSize()
        self.scopeWid.sigPulseEnergy.connect(self.addSweepPoint)

    def saveData(self):
        data = np.array(self.settings["saveData"])

        f = self.settings["saveDir"].split('.txt')[0]
        num = len([ii for ii in glob.glob(f+"*") if os.path.isfile(ii)])
        print("found {} files".format(num))
        f += "{}.txt".format(num)

        oh = "#Freq: {}\nAngle,TK\ndeg,mJ\nAngle,TK".format(
            self.scopeWid.ui.tFELFreq.value()*29.9792)
        np.savetxt(f, data, fmt="%f", delimiter=',', header=oh, comments='')

    def updateFit(self):
        data = np.array(self.settings["saveData"])
        fitX = data[:,0]
        fitY = data[:,1]
        fitY = fitY/fitY.max()

        self.curveData.setData(fitX, fitY)
        try:
            p, pcov = cf(minir, fitX, fitY, p0=[22, 5, 0.1])
        except TypeError:
            return

        angles = np.linspace(0, 90, 500)
        fit = minir(angles, *p)
        self.curveFit.setData(angles, fit)

        self.textFit.setText(
            "A={:.3f}, mu=\n {:.3f}, c={:.3f}".format(*p), color=(0,0,0)
        )


    def makeGuiThings(self, func, args):
        if args is None:
            func()
        else:
            func(args)

    def closeEvent(self, ev):
        self.scopeWid.close()
        super(TKCalibrator, self).closeEvent(ev)







if __name__ == '__main__':
    ex = QtWidgets.QApplication([])
    win = TKCalibrator()
    import sys


    sys.exit(ex.exec_())
