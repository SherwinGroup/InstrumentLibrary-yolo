

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from singleChannel_ui import Ui_Form
import scipy.integrate as spi
import re
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class ScopeViewWidget(QtGui.QWidget):
    sigBoxcarValue = QtCore.pyqtSignal(object)
    sigUpdateData = QtCore.pyqtSignal()

    def __init__(self, name=None):
        super(ScopeViewWidget,self).__init__()
        self.name = name
        self.initSettings()
        self.initUI()
        self.sigUpdateData.connect(self.updatePlots)
        self.data = np.array([])

    def __str__(self):
        return self.name

    def initSettings(self):
        s = dict()
        s['bcpyBG'] = [0, 0]
        s['bcpySG'] = [0, 0]

        self.settings = s

    def initUI(self):
        #Import ui file from designer
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.pPlot = self.ui.gPlot.plot(pen='k')
        plotitem = self.ui.gPlot.getPlotItem()
        plotitem.setTitle(self.name)
        plotitem.setLabel('bottom',text='Time',units='s')
        plotitem.setLabel('left',text='Voltage', units='V')

        #Make an array of all the textboxes for the linear regions to make it
        #easier to iterate through them. Set it up in memory identical to how it
        #appears on the panel for sanity, in a row-major fashion
        lrtb = [[self.ui.tBGStart, self.ui.tBGEnd],
                [self.ui.tSGStart, self.ui.tSGEnd]]
        # Connect the changes to update the Linear Regions
        for i in lrtb:
            for j in i:
                j.textAccepted.connect(self.updateLinearRegionsFromText)

        self.linearRegionTextBoxes = lrtb
        self.initLinearRegions()

        self.ui.bInit.clicked.connect(self.setLinearRegions)

    def initLinearRegions(self, item = None):
        #initialize array for all 5 boxcar regions
        self.boxcarRegions = [None]*2

        bgCol = pg.mkBrush(QtGui.QColor(255, 0, 0, 50))
        sgCol = pg.mkBrush(QtGui.QColor(0, 255, 0, 50))

        #Background region for the plot
        self.boxcarRegions[0] = pg.LinearRegionItem(self.settings['bcpyBG'], brush = bgCol)
        self.boxcarRegions[1] = pg.LinearRegionItem(self.settings['bcpySG'], brush = sgCol)

        #Connect it all to something that will update values when these all change
        for i in self.boxcarRegions:
            i.sigRegionChangeFinished.connect(self.updateLinearRegionValues)

        if item is None:
            item = self.ui.gPlot
        item.addItem(self.boxcarRegions[0])
        item.addItem(self.boxcarRegions[1])


    def updateLinearRegionValues(self):
        sender = self.sender()
        sendidx = -1
        for (i, v) in enumerate(self.boxcarRegions):
            #I was debugging something. I tried to use id(), which is effectively the memory
            #location to try and fix it. Found out it was anohter issue, but
            #id() seems a little safer(?) than just equating them in the sense that
            #it's explicitly asking if they're the same object, isntead of potentially
            #calling some weird __eq__() pyqt/graph may have set up
            if id(sender) == id(v):
                sendidx = i
        i = sendidx
        #Just being paranoid, no reason to think it wouldn't find the proper thing
        if sendidx<0:
            return
        self.linearRegionTextBoxes[i][0].setText('{:.9g}'.format(sender.getRegion()[0]))
        self.linearRegionTextBoxes[i][1].setText('{:.9g}'.format(sender.getRegion()[1]))

        # Update the dicionary values so that the bounds are proper when
        d = {0: "bcpyBG",
             1: "bcpySG"
        }
        self.settings[d[i]] = list(sender.getRegion())

    def updateLinearRegionsFromText(self):
        sender = self.sender()
        #figure out where this was sent
        sendi, sendj = -1, -1
        for (i, v)in enumerate(self.linearRegionTextBoxes):
            for (j, w) in enumerate(v):
                if id(w) == id(sender):
                    sendi = i
                    sendj = j

        i = sendi
        j = sendj
        curVals = list(self.boxcarRegions[i].getRegion())
        curVals[j] = float(sender.text())
        self.boxcarRegions[i].setRegion(tuple(curVals))
        # Update the dicionary values so that the bounds are proper when
        d = {0: "bcpyBG",
             1: "bcpySG",
        }
        self.settings[d[i]] = list(curVals)

    def setLinearRegions(self):
        try:
            length = self.data.shape[0]
        except:
            return
        newVal = self.data[int(length/2), 0]
        for i in self.boxcarRegions:
            i.setRegion((newVal, newVal))

    def updateData(self, data):
        self.data = data
        self.sigUpdateData.emit()

    def updatePlots(self):
        self.pPlot.setData(self.data)
        bg, sg = self.integrateData()
        self.ui.tBGBoxcar.setText("{:.5g}".format(bg))
        self.ui.tSGBoxcar.setText("{:.5g}".format(sg))
        self.sigBoxcarValue.emit(sg-bg)

    def changeName(self, name):
        self.name = name
        plotitem = self.ui.gPlot.getPlotItem()
        plotitem.setTitle(self.name)

    @staticmethod
    def findIndices(values, dataset):
        """Given an ordered dataset and a pair of values, returns the indices which
           correspond to these bounds  """
        indx = list((dataset>values[0]) & (dataset<values[1]))
        # convert to string for easy finding
        st = ''.join([str(int(i)) for i in indx])
        start = st.find('1')
        if start == -1:
            start = 0
        end = (start + st[start:].find('0') if st[start:].find('0')!=-1 else len(indx))
        if end<=0:
            end = 1 + start
        return start, end

    def integrateData(self):
        #Neater and maybe solve issues if the data happens to update
        #while trying to do analysis?
        pyD = self.data

        pyBGbounds = self.boxcarRegions[0].getRegion()
        pyBGidx = self.findIndices(pyBGbounds, pyD[:,0])

        pySGbounds = self.boxcarRegions[1].getRegion()
        pySGidx = self.findIndices(pySGbounds, pyD[:,0])
        try:
            pyBG = spi.simps(pyD[pyBGidx[0]:pyBGidx[1],1], pyD[pyBGidx[0]:pyBGidx[1], 0])
        except:
            pyBG = 0
        try:
            pySG = spi.simps(pyD[pySGidx[0]:pySGidx[1],1], pyD[pySGidx[0]:pySGidx[1], 0])
        except:
            pySG = 0

        return pyBG, pySG
        
