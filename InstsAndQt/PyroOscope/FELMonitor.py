from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import os
import glob
import time
import pyqtgraph as pg
from io import StringIO, BytesIO
# import InstsAndQt # get the __init__ to rehook exceptions to stop crashign
from InstsAndQt.cQt.DateAxis import DateAxis
from InstsAndQt.customQt import BorderlessPgPlot


pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')




class FELMonitor(BorderlessPgPlot):
    updateTimer = QtCore.QTimer()

    def __init__(self, *args, **kwargs):
        super(FELMonitor, self).__init__(*args, **kwargs)

        # reference to the file handle used for loading data
        self.fh = None

        # change the string format on the plot to
        # show the wall time instead of epoch time
        pi = self.pw.plotItem
        pi.layout.removeItem(pi.getAxis('bottom'))
        caxis = DateAxis(orientation='bottom', parent=pi)
        caxis.linkToView(pi.vb)
        pi.axes["bottom"]["item"] = caxis
        pi.layout.addItem(caxis, 3, 1)

        auto = QtWidgets.QMenu("Autoscroll", self)
        self.cbAutoEnabled = QtWidgets.QCheckBox("Enabled")
        self.cbAutoEnabled.setChecked(True)
        self.sbAutoTime = pg.SpinBox(value=10, step=1, int=True, bounds=(0, 600))
        self.cbAutoEnabled.stateChanged.connect(
            lambda x: self.sbAutoTime.setEnabled(x)
        )
        wid = QtWidgets.QWidget(None)
        layout = QtWidgets.QHBoxLayout(wid)
        layout.addWidget(self.cbAutoEnabled)
        layout.addWidget(self.sbAutoTime)
        wid.setLayout(layout)
        self.acAutoTime = QtWidgets.QWidgetAction(None)
        self.acAutoTime.setDefaultWidget(wid)
        auto.addAction(self.acAutoTime)

        # Insert the autoscroll menu before the Close button
        pi.vb.menu.insertMenu(pi.vb.menu.actions()[-1], auto)

        loadAct = QtWidgets.QAction("Load File...", self)
        loadAct.triggered.connect(self.openFile)
        pi.vb.menu.insertAction(pi.vb.menu.actions()[-1], loadAct)

        self.logFile = r'Z:\~HSG\Data\2018'

        self.updateTimer.timeout.connect(self.updatePlot)
        self.updateTimer.setInterval(750)
        self.updateTimer.start()

        self.data = np.empty((0, 4))
        self.pData = self.pw.plotItem.plot(self.data[:, 0], self.data[:, 1], pen='k')

        # self.setLayout(mainlayout)

        self.show()

    def openFile(self):
        loc = QtWidgets.QFileDialog.getOpenFileName(self, "Pick logging file",
                                                    self.logFile,
                                                    "Text File (*.txt)")[0]

        loc = str(loc)
        if not loc: return
        self.data = np.empty((0, 4))
        self.setWindowTitle("\\".join(loc.split("/")[-2:]))
        self.logFile = loc
        self.fh = open(self.logFile, 'rt')

    def updatePlot(self):
        if self.fh is None: return
        newData = self.fh.read()
        if not newData: return
        newData = np.genfromtxt(BytesIO(newData.encode()), delimiter=',')
        if 0 in newData.shape: return
        # remove nan's
        try:
            newData = newData[np.isfinite(newData[:, 0])]
        except IndexError:
            # newData = newData[np.isfinite(newData[:,0])]
            if not np.isfinite(newData[0]):
                return

        self.data = np.row_stack((self.data, newData))
        self.pData.setData(self.data[:, 0], self.data[:, 1])

        if self.cbAutoEnabled.isChecked(): self.updateAutoscale()

    def updateAutoscale(self):
        dt = self.sbAutoTime.value() * 60
        x1 = self.data[-1, 0] - dt
        x2 = self.data[-1, 0]
        self.pw.setXRange(x1, x2)
        try:
            y1idx = np.where(self.data[:, 0] > x1)[0][0]
        except IndexError:
            y1idx = 0
        y1 = self.data[y1idx:, 1].min()
        y2 = self.data[y1idx:, 1].max()
        if y1 < y2:
            y11 = y1 - 0.1 * np.abs(y2 - y1)
            y22 = y2 + 0.1 * np.abs(y2 - y1)
        elif y1 == y2:
            y11 = y1 - 3
            y22 = y2 + 3
        else:
            y11 = y2 + 0.05 * np.abs(y2 - y1)
            y22 = y1 - 0.05 * np.abs(y2 - y1)
        self.pw.setYRange(y11, y22, padding=0)



if __name__ == '__main__':
    import sys


    app = QtWidgets.QApplication(sys.argv)
    ex = FELMonitor()
    sys.exit(app.exec_())
