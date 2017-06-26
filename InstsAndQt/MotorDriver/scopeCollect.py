# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 15:36:27 2014

@author: Darren
"""

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import threading
from mainWindow_ui import Ui_MainWindow
from scopeView import ScopeViewWidget
from InstsAndQt.Instruments import Agilent6000
from InstsAndQt.customQt import *
import os
import visa

class Win(QtGui.QMainWindow):
    sigDataUpdate = QtCore.pyqtSignal()
    sigSetStatusBar = QtCore.pyqtSignal(object)

    def __init__(self):
        super(Win,self).__init__()
        self.initSettings()
        self.initUI()
        self.openAgilent()
        # self.sigSetStatusBar[str].connect(self.statusBar().showMessage)
        # self.sigSetStatusBar[str, int].connect(self.statusBar().showMessage)
        self.sigSetStatusBar.connect(self.updateStatusBar)
        self.poppedPlotWindow = None
        self.oldpOsc = None

    def initSettings(self):
        s = dict()
        #########################
        #
        # Get the GPIB list and open up the scope
        #
        #########################
        try:
            rm = visa.ResourceManager()
            ar = [i.encode('ascii') for i in rm.list_resources()]
            ar.append('Fake')
            s['GPIBlist'] = ar
        except:
            print 'Error loading GPIB list'
            ar = ['a', 'b', 'c', 'Fake']
            s['GPIBlist'] = ar
        try:
            # Pretty sure we can safely say it's
            # ASRL1
            idx = s['GPIBlist'].index("USB0::0x0957::0x1798::MY54410143::INSTR")
            s["oGPIBidx"] = idx
        except ValueError:
            # otherwise, just set it to the fake index
            s["oGPIBidx"] = s['GPIBlist'].index('Fake')

        s["isScopePaused"] = True # Default to paused
        s["aveScope"] = False
        s["aveScopeNum"] = 1

        s["saveDir"] = ''

        s["boxcarData"] = np.empty((0, 2))
        s["boxcarPair"] = np.array([0., 0.])
        s["boxcarPairFlag"] = [False, False]

        self.settings = s
        
    def initUI(self):
        #Import ui file from designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ######################################################
        #
        # Create the scope widgets, connect signals
        #
        ######################################################
        self.ch1View = ScopeViewWidget('CH1')
        self.ch2View = ScopeViewWidget('CH2')
        self.ch3View = ScopeViewWidget('CH3')
        self.ch4View = ScopeViewWidget('CH4')
        self.chWidList = [self.ch1View,
                          self.ch2View,
                          self.ch3View,
                          self.ch4View]

        self.chBoxList = [self.ui.cbSettingsCH1,
                           self.ui.cbSettingsCH2,
                           self.ui.cbSettingsCH3,
                           self.ui.cbSettingsCH4]
        for i in self.chBoxList:
            i.toggled.connect(self.updateChannelWidgets)

        self.chNameList = [self.ui.tSettingsCH1,
                           self.ui.tSettingsCH2,
                           self.ui.tSettingsCH3,
                           self.ui.tSettingsCH4]
        for i in self.chNameList:
            i.editingFinished.connect(self.chNameChanged)


        self.ui.hlChannels.insertWidget(0, self.ch1View)
        self.ui.hlChannels.insertWidget(1, self.ch2View)
        self.ch2View.hide()
        self.ui.hlChannels.insertWidget(2, self.ch3View)
        self.ch3View.hide()
        self.ui.hlChannels.insertWidget(3, self.ch4View)
        self.ch4View.hide()

        ######################################################
        #
        # Initialize status bar
        #
        ######################################################
        self.sbTextList = [QTimedText(), # CH1 saved
                           QTimedText(), # CH2 saved
                           QTimedText(), # CH3 saved
                           QTimedText(), # CH4 saved
                           QTimedText()] # General

        for i in self.sbTextList:
            self.statusBar().addPermanentWidget(i, 1) # 1 for weighting

        # Removes the weird lines that show up when you have a bunch of permanent widgest
        #http://stackoverflow.com/questions/16218232/qprogressbar-on-qstatusbar-how-to-remove-the-2-little-vertical-lines-on-either

        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")


        ######################################################
        #
        # Initialize settings
        #
        ######################################################

        self.ui.cSettingsGPIB.addItems(self.settings['GPIBlist'])
        self.ui.cSettingsGPIB.setCurrentIndex(self.settings["oGPIBidx"])
        self.ui.cSettingsGPIB.currentIndexChanged.connect(self.openAgilent)
        self.ui.bSettingsChooseDir.clicked.connect(self.chooseSaveDir)
        self.ui.cbSettingsAve.toggled[bool].connect(self.changeAveragingState)
        self.ui.tSettingsAve.textAccepted.connect(self.changeAveragingNumber)

        ######################################################
        #
        # Initialize waveforms tab
        #
        ######################################################
        self.ui.bCHPause.toggled[bool].connect(self.toggleScopePause)
        self.ui.bCHSave.sigSingleClicked.connect(self.saveAllChannels)

        ######################################################
        #
        # Initialize boxcar tab
        #
        ######################################################

        # Connect buttons
        self.ui.bBoxcarPopout.clicked.connect(self.popoutBoxcar)
        self.ui.bBoxcarSave.clicked.connect(self.saveBoxcar)
        self.ui.bBoxcarReset.clicked.connect(self.resetBoxcarPlot)

        # add initial value
        self.ui.cBoxcarCHX.addItem(str(self.ch1View))
        self.ui.cBoxcarCHY.addItem(str(self.ch1View))
        self.ui.cBoxcarCHX.currentIndexChanged.connect(self.updateWantedBoxcars)
        self.ui.cBoxcarCHY.currentIndexChanged.connect(self.updateWantedBoxcars)

        # set up the graph
        self.pBoxcar = self.ui.gBoxcar.plot(pen='k')
        plotitem = self.ui.gBoxcar.getPlotItem()
        plotitem.setTitle("Boxcar Values")
        plotitem.setLabel('bottom',text='CH1')
        plotitem.setLabel('left',text='CH1')

        # variables for the boxcar emits that we're interested in
        self.wantedBoxcarWidX = self.ch1View
        self.wantedBoxcarWidY = self.ch1View

        # Connect the emits of the channels
        for i in self.chWidList:
            i.sigBoxcarValue[object].connect(self.acceptSingleBoxcar)


        self.show()

    def updateStatusBar(self, obj):
        # If just a string is passed, set the general status bar text
        if type(obj) is str:
            self.sbTextList[-1].setMessage(obj)
        # Else it must be a list, if not, dunno what you want
        elif type(obj) is list:
            if len(obj)==2:
                # This is a string and a timeout, assume you want general
                if type(obj[1]) is int:
                    self.sbTextList[-1].setMessage(obj[0], obj[1])
                # Or did you pass the object you want updated?
                elif type(obj[1]) is type(self.sbTextList[-1]):
                    obj[1].setMessage(obj[0])
            # Or you passed the object to be updated and the time
            elif len(obj) == 3 and type(obj[1]) is type(self.sbTextList[-1]):
                obj[1].setMessage(obj[0], obj[2])
            else:
                print "UPDATE STATUSBAR: UNKONWN COMMANDA: {}, {}".format(type(obj[1]), type(self.sbTextList[-1]))
        else:
            print "UPDATE STATUSBAR: UNKONWN COMMANDB: {}".format(obj)


    @staticmethod
    def _____CHANNEL_SETTINGS():
        pass

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    #
    #
    # All functions related to changes that occur when changing which
    # channels to read or channel names
    #
    #
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    def updateChannelWidgets(self, b):
        sent = self.sender()
        idx = self.chBoxList.index(sent) + 1
        if b:
            self.chWidList[idx-1].show()
            self.ui.cBoxcarCHX.insertItem(idx-1, str(self.chWidList[idx-1]) )
            self.ui.cBoxcarCHY.insertItem(idx-1, str(self.chWidList[idx-1]) )
        else:
            self.chWidList[idx-1].hide()
            self.ui.cBoxcarCHX.removeItem(self.ui.cBoxcarCHX.findText(str(self.chWidList[idx-1]) ))
            self.ui.cBoxcarCHY.removeItem(self.ui.cBoxcarCHX.findText(str(self.chWidList[idx-1]) ))

    def chNameChanged(self):
        sent = self.sender()
        idx = self.chNameList.index(sent)
        oldName = str(self.chWidList[idx])
        newName = str(self.chNameList[idx].text())
        curidxX = self.ui.cBoxcarCHX.currentIndex()
        curidxY = self.ui.cBoxcarCHY.currentIndex()

        self.ui.cBoxcarCHX.removeItem(self.ui.cBoxcarCHX.findText(oldName))
        self.ui.cBoxcarCHY.removeItem(self.ui.cBoxcarCHY.findText(oldName))
        self.ui.cBoxcarCHX.insertItem(idx, newName )
        self.ui.cBoxcarCHY.insertItem(idx, newName )

        self.ui.cBoxcarCHX.setCurrentIndex(curidxX)
        self.ui.cBoxcarCHY.setCurrentIndex(curidxY)

        self.chWidList[idx].changeName(newName)

    def updateData(self):
        pass

    @staticmethod
    def _____SCOPE():
        pass

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    #
    #
    # All functions related to opening the scope or interfacing
    # with it
    #
    #
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    def openAgilent(self, idx = None):
        self.settings["shouldScopeLoop"] = False
        isPaused = self.settings["isScopePaused"] # For intelligently restarting scope afterwards
        if isPaused:
            self.toggleScopePause(False)
        try:
            self.scopeCollectionThread.wait()
        except:
            pass
        try:
            self.Agilent.close()
        except Exception as e:
            print "__main__.openAgilent:\nError closing Agilent,",e
        try:
            self.Agilent = Agilent6000(
                self.settings["GPIBlist"][int(self.ui.cSettingsGPIB.currentIndex())]
            )
            print 'Agilent opened'
        except Exception as e:
            print "__main__.openAgilent:\nError opening Agilent,",e
            self.Agilent = Agilent6000("Fake")
            # If you change the index programatically,
            # it signals again. But that calls this thread again
            # which really fucks up with the threading stuff
            # Cheap way is to just disconnect it and then reconnect it
            self.ui.cSettingsGPIB.currentIndexChanged.disconnect()
            self.ui.cSettingsGPIB.setCurrentIndex(
                self.settings["GPIBlist"].index("Fake")
            )
            self.ui.cSettingsGPIB.currentIndexChanged.connect(self.openAgilent)

        self.Agilent.setTrigger(source = 4)
        self.settings['shouldScopeLoop'] = True
        if isPaused:
            self.toggleScopePause(True)

        self.scopeCollectionThread = TempThread(target = self.collectScopeLoop)
        self.scopeCollectionThread.start()

    def toggleScopePause(self, val):
        print "Toggle scope. val={}".format(val)
        self.settings["isScopePaused"] = val
        if not val: # We want to stop any pausing thread if neceesary
            try:
                self.scopePausingLoop.exit()
            except:
                pass

    def collectScopeLoop(self):
        while self.settings['shouldScopeLoop']:
            if self.settings['isScopePaused']:
                #Have the scope updating remotely so it can be changed if needed
                self.Agilent.write(':RUN')
                #If we want to pause, make a fake event loop and terminate it from outside forces
                self.scopePausingLoop = QtCore.QEventLoop()
                self.scopePausingLoop.exec_()
                continue

            # Figure out which channels to read
            checked = [True if i.isChecked() else False for i in self.chBoxList]
            channelNums = [i+1 for i in range(len(checked)) if checked[i]]
            retData = self.Agilent.getMultipleChannels(*channelNums)
            if not self.settings['isScopePaused']:
                for (idx, wid) in enumerate([self.chWidList[i] for i in range(len(checked)) if checked[i]]):
                    wid.updateData(retData[idx])
                self.sigDataUpdate.emit()
                if self.ui.bCHSave.isChecked():
                    self.saveAllChannels()

    def changeAveragingState(self, b):
        if b:
            self.Agilent.setMode("AVER")
        else:
            self.Agilent.setMode("NORM")

    def changeAveragingNumber(self):
        num = self.ui.tSettingsAve.value()
        self.Agilent.setAverages(num)



    @staticmethod
    def _____BOXCAR():
        pass
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    #
    #
    # Functions related to handling the boxcar
    #
    #
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    def updateWantedBoxcars(self):
        sent = self.sender()
        wantedWid = [
            i for i in self.chWidList if i.name == str(sent.currentText())
        ][0]
        if sent == self.ui.cBoxcarCHX:
            axis = "bottom"
            self.wantedBoxcarWidX = wantedWid
        else:
            axis = "left"
            self.wantedBoxcarWidY = wantedWid
        if self.poppedPlotWindow is not None:
            plotitem = self.poppedPlotWindow.pw.getPlotItem()
        else:
            plotitem = self.ui.gBoxcar.getPlotItem()
        plotitem.setLabel(axis,text=sent.currentText())

    def acceptSingleBoxcar(self, bcVal):
        sent = self.sender()
        if sent == self.wantedBoxcarWidX:
            self.settings["boxcarPair"][0] = bcVal
            self.settings["boxcarPairFlag"][0] = True
        if sent == self.wantedBoxcarWidY:
            self.settings["boxcarPair"][1] = bcVal
            self.settings["boxcarPairFlag"][1] = True
        if False not in self.settings["boxcarPairFlag"]:
            self.updateBoxcars()

    def updateBoxcars(self):
        if self.ui.bBoxcarCollect.isChecked():
            self.settings["boxcarData"] = np.append(
                self.settings["boxcarData"], [self.settings["boxcarPair"]], axis=0
            )
            self.pBoxcar.setData(
                self.settings["boxcarData"][:,0], self.settings["boxcarData"][:,1])
        self.settings["boxcarPairFlag"] = [False, False]

    def resetBoxcarPlot(self):
        self.settings["boxcarData"] = np.empty((0, 2))
        self.pBoxcar.setData([], [])

    def popoutBoxcar(self):
        if self.poppedPlotWindow is None:
            self.poppedPlotWindow = pgPlot()
            self.oldpBoxcar = self.pBoxcar
            self.pBoxcar = self.poppedPlotWindow.pw.plot(pen='k')
            plotitem = self.poppedPlotWindow.pw.getPlotItem()
            plotitem.setTitle("Boxcar Values")
            plotitem.setLabel('bottom',text=self.wantedBoxcarWidX.name)
            plotitem.setLabel('left',text=self.wantedBoxcarWidY.name)
            self.poppedPlotWindow.closedSig.connect(self.cleanupCloseBoxcar)
        else:
            self.poppedPlotWindow.raise_()

    def cleanupCloseBoxcar(self):
        self.poppedPlotWindow = None
        self.pBoxcar = self.oldpBoxcar

    @staticmethod
    def _____SAVING():
        pass
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    #
    #
    # Functions related to saving
    #
    #
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    def chooseSaveDir(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                     caption="Choose Save Directory",
                                                     directory=self.settings["saveDir"])
        if directory == "":
            return
        self.settings["saveDir"] = str(directory)
        self.ui.tSettingsSaveDir.setText(directory)

    def saveFile(self, data = None, filename = "", header = "", statusbar = None):
        """
        All files will be saved in the form of:
        self.ui.tSettingsSaveName_base_number
        where filename = base, and number is how many files already exist
        statusbar is the widget which should be updated
        :param data:
        :param filename:
        :param header:
        :return:
        """
        try:
            filelist = os.listdir(self.settings["saveDir"])
        except:
            print "__main__saveFile:Error, path doesn't exist"
            self.sigSetStatusBar.emit("Please choose a save dir")
            return
        basename = str(self.ui.tSettingsSaveName.text())
        filelist = [i for i in filelist if basename+"_"+filename in i]
        num = len(filelist)

        try:
            np.savetxt(os.path.join(self.settings["saveDir"],
                                    basename+"_"+filename+"_"+str(num)+".txt" ),
                       data, header=header)
        except Exception as e:
            print "__main__saveFile:Error file cannae be saved,",e
            self.sigSetStatusBar.emit("File could not be saved")
        else:
            if statusbar is not None:
                self.sigSetStatusBar.emit(["Saved file {}".format(basename+"_"+filename+"_"+str(num)), statusbar])
            else:
                self.sigSetStatusBar.emit("Saved file {}".format(basename+"_"+filename+"_"+str(num)))

    def saveAllChannels(self):
        # Which channels are checked to be shown?
        toSaveShowing = [True if i.isChecked() else False for i in self.chBoxList]
        # Which channels are checked to be saved?
        toSaveChecked = [i.ui.cSave.isChecked() for i in self.chWidList]
        # Which fits both?
        toSave = [x&y for (x, y) in zip(toSaveShowing, toSaveChecked)]
        for i in range(len(toSave)):
            if toSave[i]:
                self.saveFile(self.chWidList[i].data,
                              filename = str(self.chWidList[i]),
                              header = self.genHeader(),
                              statusbar=self.sbTextList[i])

    def saveBoxcar(self):
        self.saveFile(self.settings["boxcarData"],
                      filename = "boxcar",
                      header = self.genHeader(False))

    def genHeader(self, isChannel = True):
        st = ""
        st += str(self.ui.tSaveComments.toPlainText()) + "\n"
        if isChannel:
            st += "Time(s), Voltage(V)\n"
        else:
            st += "{} Boxcars:\n".format(self.wantedBoxcarWidX)
            st += "\tBG: {:10.5g} -> {:10.5g}\n".format(
                *self.wantedBoxcarWidX.boxcarRegions[0].getRegion())
            st += "\tBG: {:10.5g} -> {:10.5g}\n".format(
                *self.wantedBoxcarWidX.boxcarRegions[1].getRegion())

            st += "{} Boxcars:\n".format(self.wantedBoxcarWidY)
            st += "\tBG: {:10.5g} -> {:10.5g}\n".format(
                *self.wantedBoxcarWidY.boxcarRegions[0].getRegion())
            st += "\tBG: {:10.5g} -> {:10.5g}\n".format(
                *self.wantedBoxcarWidY.boxcarRegions[1].getRegion())

            st += "{}, {}\n".format(self.wantedBoxcarWidX, self.wantedBoxcarWidY)
        return st


    def closeEvent(self,event):
        self.settings['isScopePaused'] = False
        self.settings['shouldScopeLoop'] = False
        try:
            self.scopePausingLoop.exit()
        except:
            pass
        try:
            self.scopeCollectionThread.wait()
        except:
            pass
        self.Agilent.write(':RUN')
        self.Agilent.close()
        self.close()

        

def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    ex = Win()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()