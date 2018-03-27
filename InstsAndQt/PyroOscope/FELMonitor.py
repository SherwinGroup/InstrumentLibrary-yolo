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


# The map between parameter name from the osc widget saving
# and the index it correponds to
dataIdxs = {
    "energy": 1,
    "voltage": 2,
    "field strength": 4,
    "field intensity": 5
}

# Pens used to draw them, so you can tell at a glance what
# is being plotted
dataPens = {
    "energy": pg.mkPen('k', width=3),
    "voltage": pg.mkPen('l', width=3),
    "field strength": pg.mkPen('#008000', width=3),
    "field intensity": pg.mkPen('#808000', width=3)
}



class FELMonitor(BorderlessPgPlot):
    updateTimer = QtCore.QTimer()

    def __init__(self, *args, **kwargs):
        super(FELMonitor, self).__init__(*args, **kwargs)

        ## reference to the file handle used for loading data
        ## I keep a reference to the file (which stays open
        ## all the time) because I want it to keep
        ## track of where it was when it last read,
        ## so it's only reading in new data
        ##
        ## If you np.genfromtxt, it got expensive for
        ## long data sets
        ## I guess you could keep track internally of the
        ## buffer position and open/close it each time?
        ## But I didn't set it up that way and it works fine for now
        self.fh = None

        ## change the string format on the x axis to
        ## show the wall time instead of epoch time
        pi = self.pw.plotItem
        pi.layout.removeItem(pi.getAxis('bottom'))
        caxis = DateAxis(orientation='bottom', parent=pi)
        caxis.linkToView(pi.vb)
        pi.axes["bottom"]["item"] = caxis
        pi.layout.addItem(caxis, 3, 1)


        ## Append to the context menu to enable
        ## an autoscroll feature to only show the last
        ## few minutes
        ##
        ## Need to set it up as an action widget,
        ## because I want to have the scroll box for
        ## picking the time in the menu itself
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
        ## Insert the autoscroll menu before the Close button
        pi.vb.menu.insertMenu(pi.vb.menu.actions()[-1], auto)

        ## Append a list of values to plot
        plotMenu = QtWidgets.QMenu("Plot Data", self)
        ## set up an exlusive button group for the
        ## plot sets
        self.dataActionGroup = QtWidgets.QActionGroup(self)
        for label in sorted(dataIdxs.keys()):
            act = plotMenu.addAction(label.title())
            act.setCheckable(True)
            self.dataActionGroup.addAction(act)
            if "energy" == label.lower():
                act.setChecked(True)
            act.triggered.connect(self.updatePlot)
        pi.vb.menu.insertMenu(pi.vb.menu.actions()[-1], plotMenu)

        ## Loading the file is put in after
        loadAct = QtWidgets.QAction("Load File...", self)
        loadAct.triggered.connect(self.openFile)
        pi.vb.menu.insertAction(pi.vb.menu.actions()[-1], loadAct)

        self.logFile = r'Z:\~HSG\Data\2018'

        ## Sets up a loop to check every 750ms to see if the file
        ## has been updated.
        self.updateTimer.timeout.connect(self.updatePlot)
        self.updateTimer.setInterval(750)
        self.updateTimer.start()

        ## Set up the correct dimensions of the data array
        ## so we can append to it
        self.data = np.empty((0, 6))

        ## set the default pens for energy, the default
        ## value to be plotted
        self.pData = self.pw.plotItem.plot([], [],
                                           pen=dataPens["energy"])

        self.show()

    def openFile(self):
        loc = QtWidgets.QFileDialog.getOpenFileName(self, "Pick logging file",
                                                    self.logFile,
                                                    "Text File (*.txt)")[0]

        loc = str(loc)
        if not loc: return

        ## If you want to load various files to compare them,
        ## set the title name so you can quickly see which
        ## one is which
        self.setWindowTitle("\\".join(loc.split("/")[-2:]))
        self.logFile = loc

        ## keep a reference to the opened file.
        ## I feel like its maybe not the safest thing to have
        ## the reference kept open all the time,
        ## but it was being super slow when doing
        ## open/closes on each read
        self.fh = open(self.logFile, 'rt')

        ## Try to figure out how many columns there are,
        ## which is different from the old/new style of
        ## files
        ##
        ## Default add two because there's one more columns
        ## than there are commas
        num = self.fh.readline().count(',') + 1
        if num == 1: ## empty file
            num = 6 ## assume it'll end up being the new style

        self.data = np.empty((0, num))

        ## Go back to the beginning of the file as if it wasn't
        ## touched here
        self.fh.seek(0)

    def updatePlot(self):
        ## Skip if a file hasn't been chosen
        if self.fh is None: return
        newData = self.fh.read()
        ## Parse it if there's new data
        if newData:
            ## Need to uses bytesIO to keep everything in memory,
            ## instead of reading the file directly.
            newData = np.genfromtxt(BytesIO(newData.encode()), delimiter=',')
            # No real data was printed into the file, skip it
            if 0 in newData.shape: return
            # remove nan's
            try:
                newData = newData[np.isfinite(newData[:, 0])]
            except IndexError:
                if not np.isfinite(newData[0]):
                    return

            try:
                self.data = np.row_stack((self.data, newData))
            except ValueError:
                print("Value error occurred", self.data.shape, newData.shape)

        ## If the timer has triggered an update, but there's no
        ## data, then skip. Otherwise, if there's no new data
        ## but something else triggered, cause an update
        elif isinstance(self.sender(), QtCore.QTimer):
            return


        self.pData.setData(self.data[:, 0],
                           self.data[:, dataIdxs[
                                str(self.dataActionGroup.checkedAction().text()).lower()
                                        ]])
        self.pData.setPen(dataPens[
                str(self.dataActionGroup.checkedAction().text()).lower()
                                ])

        if self.cbAutoEnabled.isChecked(): self.updateAutoscale()

    def updateAutoscale(self):
        idx = dataIdxs[
            str(self.dataActionGroup.checkedAction().text()).lower()
        ]
        dt = self.sbAutoTime.value() * 60
        x1 = self.data[-1, 0] - dt
        x2 = self.data[-1, 0]
        self.pw.setXRange(x1, x2)
        try:
            y1idx = np.where(self.data[:, 0] > x1)[0][0]
        except IndexError:
            y1idx = 0
        y1 = self.data[y1idx:, idx].min()
        y2 = self.data[y1idx:, idx].max()
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
