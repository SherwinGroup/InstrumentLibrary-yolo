from PyQt4 import QtGui, QtCore
import numpy as np
import os
import glob
import time
import pyqtgraph as pg
from io import StringIO

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class UI(object): pass
class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        for x in values:
            try:
                strns.append(time.strftime("%X", time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        return strns

class FELMonitor(QtGui.QWidget):
    updateTimer = QtCore.QTimer()
    def __init__(self, *args, **kwargs):
        super(FELMonitor, self).__init__(*args, **kwargs)
        self.ui = UI()
        self.fh = None
        self.ui.gPlotter = pg.PlotWidget()
        # change the string format on the plot to
        # show the time
        pi = self.ui.gPlotter.plotItem
        pi.layout.removeItem(pi.getAxis('bottom'))
        caxis = DateAxis(orientation='bottom', parent=pi)
        caxis.linkToView(pi.vb)
        pi.axes["bottom"]["item"] = caxis
        pi.layout.addItem(caxis, 3, 1)

        auto = QtGui.QMenu("Autoscroll", self)
        self.ui.cbAutoEnabled = QtGui.QCheckBox("Enabled")
        self.ui.cbAutoEnabled.setChecked(True)
        self.ui.sbAutoTime = pg.SpinBox(value=10, step=1, decimals=1, bounds=(0, 600))
        self.ui.cbAutoEnabled.stateChanged.connect(
            lambda x: self.ui.sbAutoTime.setEnabled(x)
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

        self.ui.bChooseDir = QtGui.QPushButton("Choose File")
        self.ui.bChooseDir.clicked.connect(self.openFile)
        mainlayout = QtGui.QVBoxLayout()
        button1 = QtGui.QHBoxLayout()
        button1.setMargin(0)
        button1.addStretch(10)
        button1.addWidget(self.ui.bChooseDir)
        mainlayout.addWidget(self.ui.gPlotter)
        mainlayout.addLayout(button1)
        mainlayout.setMargin(0)

        self.logFile = r'Z:\~Hunter Banks\Data\2017'


        self.updateTimer.timeout.connect(self.updatePlot)
        self.updateTimer.setInterval(750)
        self.updateTimer.start()

        self.data = np.empty((0,4))
        self.pData = self.ui.gPlotter.plotItem.plot(self.data[:,0], self.data[:,1], pen='k')

        self.setLayout(mainlayout)

        self.show()
    def openFile(self):
        loc = QtGui.QFileDialog.getOpenFileName(self, "Pick logging file",
                                                self.logFile,
                                                "Text File (*.txt)")
        loc = str(loc)
        if not loc: return
        self.logFile = loc
        self.fh = open(self.logFile, 'rt')

    def updatePlot(self):
        # print "checking new file"
        # print self.fh.read()
        if self.fh is None: return
        newData = self.fh.read()
        if not newData: return
        newData = np.genfromtxt(StringIO(newData), delimiter=',')
        # print newData
        # print "new data:", newData
        # print '\n'*3
        if 0 in newData.shape: return

        self.data = np.row_stack((self.data, newData))
        self.pData.setData(self.data[:,0], self.data[:,1])

        if self.ui.cbAutoEnabled.isChecked(): self.updateAutoscale()

    def updateAutoscale(self):
        dt = self.ui.sbAutoTime.value()*60
        x1 = self.data[-1,0]-dt
        x2 = self.data[-1,0]
        self.ui.gPlotter.setXRange(x1, x2)
        try:
            y1idx = np.where(self.data[:,0]>x1)[0][0]
        except IndexError:
            y1idx = 0
        y1 = self.data[y1idx:, 1].min()
        y2 = self.data[y1idx:, 1].max()
        if y1<y2:
            y11 = y1 - 0.1*np.abs(y2-y1)
            y22 = y2 + 0.1*np.abs(y2-y1)
        elif y1==y2:
            y11 = y1 - 3
            y22 = y2 + 3
        else:
            y11 = y2 + 0.05*np.abs(y2-y1)
            y22 = y1 - 0.05*np.abs(y2-y1)
        self.ui.gPlotter.setYRange(y11, y22, padding=0)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    ex = FELMonitor()
    sys.exit(app.exec_())
