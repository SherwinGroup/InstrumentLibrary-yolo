from PyQt4 import QtCore, QtGui
import scipy.integrate as spi
import scipy.stats as spt # for calculating FEL pulse information
import scipy.special as sps
import scipy.optimize as spo
import warnings
from ..Instruments import *
from ..Instruments import __displayonly__
from ..customQt import *
import pyqtgraph as pg
import visa
from scipy.interpolate import interp1d as i1d
from TK_ui import Ui_Oscilloscope
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

import logging
log = logging.getLogger("EMCCD")

setPrintOutput(False)

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

tkCalFactor = 0.00502



import glob, os
debugfiles = glob.glob(os.path.join(r"Z:\Darren\Data\2016\01-14 Wire Calibration", "wiregridcal_signalWaveform[0-9].txt"))
debugdata = [np.genfromtxt(ii, delimiter=',')[3:] for ii in debugfiles]


def sig(x, *p):
    # For fitting the hole-coupler integrated waveform
    a, mu, b, offset = p
    return a*sps.expit(b*(x-mu)) + offset


class TKWid(QtGui.QWidget):
    scopeCollectionThread = None # Thread which polls the scope
    scopePausingLoop = None # A QEventLoop which causes the scope collection
                            # thread to wait

    photonCountingThread = None # A thread whose only sad purpose
                                # in life is to wait for data to
                                # be emitted and to process
                                # and count it
    photonWaitingLoop = None # Loop while photon counting waits for more


    # Has the oscilloscope updated and data is now ready
    # for processing?
    sigOscDataCollected = QtCore.pyqtSignal()
    # emits the energy of the pulse
    sigPulseEnergy = QtCore.pyqtSignal(object)



    def __init__(self, *args, **kwargs):
        super(TKWid, self).__init__(*args)

        self.settings = dict()
        try:
            rm = visa.ResourceManager()
            ar = [i.encode('ascii') for i in rm.list_resources()]
            ar.append('Fake')
            self.settings['GPIBlist'] = ar
        except:
            log.warning("Error loading GPIB list")
            ar = ['a', 'b', 'c', 'Fake']
            self.settings['GPIBlist'] = ar
        try:
            # Pretty sure we can safely say it's
            # GPIB5
            idx = self.settings['GPIBlist'].index('USB0::0x0957::0x1798::MY54410143::INSTR')
            self.settings["agilGPIBidx"] = idx
        except ValueError:
            # otherwise, just set it to the fake index
            self.settings["agilGPIBidx"] = self.settings['GPIBlist'].index('Fake')

        # This will be used to toggle pausing on the scope
        self.settings["isScopePaused"] = True
        # This flag will be used for safely terminating the
        # oscilloscope thread
        self.settings["shouldScopeLoop"] = True
        self.settings["doPhotonCounting"] = True
        self.settings["exposing"] = False # For whether or not an exposure is happening

        self.settings['pyData'] = None

        # can we always assume 10k points? I don't know.
        self.settings["aveData"] = np.ones((10000, 4))*np.nan
        # self.settings["aveData"] = np.ones((9999, 4))*np.nan # WHY IS THIS 9999??

        self.settings["fel_lambda"] = 0

        # emit energy after every pulse, or only
        # after averaging is complete
        self.settings["emit_mid_average"] = True


        self.initUI()

        # self.pyDataSig.connect(self.updateOscilloscopeGraph)
        self.sigOscDataCollected.connect(self.updateOscilloscopeGraph)
        self.sigOscDataCollected.connect(self.processPulse)
        # self.photonCountingThread = TempThread(target = self.doPhotonCountingLoop)
        # self.photonCountingThread.start()

        self.poppedPlotWindow = None

        self.openAgilent()

    def initUI(self):
        self.ui = Ui_Oscilloscope()
        self.ui.setupUi(self)

        if __displayonly__:
            return

        ###################
        # Setting up oscilloscope values
        ##################
        self.ui.cOGPIB.addItems(self.settings['GPIBlist'])
        self.ui.cOGPIB.setCurrentIndex(self.settings["agilGPIBidx"])
        self.ui.bOPause.clicked[bool].connect(self.toggleScopePause)
        self.ui.cOGPIB.currentIndexChanged.connect(self.openAgilent)


        self.ui.sbAveNum.valueChanged.connect(self.updateAveSize)
        self.ui.cbAveMode.currentIndexChanged.connect(self.updateAveSize)
        self.ui.gbAveraging.clicked.connect(self.updateAveSize)
        ###################
        # Setting plot labels
        ##################
        self.ui.gOsc.sigRangeChanged.connect(self.updatePkTextPos)

        plotitem = self.ui.gOsc.getPlotItem()

        self.plotItem = plotitem
        plotitem.setTitle('TK')
        plotitem.setLabel('bottom',text='time scale',units='us')
        plotitem.setLabel('left',text='Voltage', units='V')
        # add a textbox for pk-pk value
        self.pkText = pg.TextItem('', color=(0,0,0))
        self.pkText.setPos(0,0)
        self.pkText.setFont(QtGui.QFont("", 15))
        self.ui.gOsc.addItem(self.pkText)

        # all of the curves to be used
        self.lines = {
            "brazil1": self.ui.gOsc.plot(pen=pg.mkPen('c', width=1)),
            "brazil2": self.ui.gOsc.plot(pen=pg.mkPen('c', width=1)),
            "data": self.ui.gOsc.plot(pen=pg.mkPen('k', width=3)),
            "ave": self.ui.gOsc.plot(pen=pg.mkPen('r', width=1.5)),
            "minData": self.ui.gOsc.plot(pen=pg.mkPen('g', width=3)),
            "maxData": self.ui.gOsc.plot(pen=pg.mkPen('g', width=3)),
            "minFit": self.ui.gOsc.plot(pen=pg.mkPen('b', width=3)),
            "maxFit": self.ui.gOsc.plot(pen=pg.mkPen('b', width=3))
        }
        brazilPlot = pg.FillBetweenItem(self.lines["brazil1"], self.lines["brazil2"],
                                        brush=pg.mkBrush('c'))
        self.ui.gOsc.addItem(brazilPlot)


        self.show()

    def loadSettings(self, **settings):
        self.settings.update(settings)
        self.ui.tFELFreq.setText(str(self.settings["fel_lambda"]))

    def setParentScope(self, scope):
        """
        Call this when this widget is being inserted into
        another widget which maintains control over the
        oscilloscope
        :param scope:
        :return:
        """
        # Pretty much just need to close the data collection thread
        # as this widget will default to a fake instrument,
        # don't need to worry about closing it.
        self.settings['shouldScopeLoop'] = False
        try:
            self.scopeCollectionThread.wait(1000)
        except:
            pass

        # hide the controls since they should be handled externally
        self.ui.oscControlsWidget.hide()

    def setData(self, data):
        """
        Need to be able to set the oscilloscope data
        when another wdiget is controlling it
        :param data:
        :return:
        """
        self.settings['pyData'] = data
        print '\n'*2, "Data shape", data.shape, "\n"*2

        # ii = np.random.randint(len(debugdata))
        # self.settings['pyData'] = debugdata[ii]


        self.sigOscDataCollected.emit()

    def getData(self):
        return self.settings.get('pyData', np.array([[],[]]).reshape(0, 2) )

    def updateAveSize(self):
        newAveSize = int(self.ui.sbAveNum.value())
        if str(self.ui.cbAveMode.currentText()) == "Waveform":
            self.settings["aveData"] = np.ones((10000, newAveSize))*np.nan
            # self.settings["aveData"] = np.ones((9999,  newAveSize))*np.nan
        else:
            self.settings["aveData"] = np.ones(newAveSize) * np.nan

        if not (self.ui.gbAveraging.isChecked() and str(self.ui.cbAveMode.currentText())=="Waveform"):
            self.lines["brazil1"].setData([], [])
            self.lines["brazil2"].setData([], [])
            self.lines["ave"].setData([], [])


    @staticmethod
    def __OPEN_CONTROLLER(): pass

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
            log.warning("Error closing Agilent")
        try:
            self.Agilent = Agilent6000(
                self.settings["GPIBlist"][int(self.ui.cOGPIB.currentIndex())]
            )
        except Exception as e:
            log.warning( "Error opening Agilent, {}".format(e))
            self.Agilent = Agilent6000("Fake")
            # If you change the index programatically,
            # it signals again. But that calls this thread again
            # which really fucks up with the threading stuff
            # Cheap way is to just disconnect it and then reconnect it
            self.ui.cOGPIB.currentIndexChanged.disconnect()
            self.ui.cOGPIB.setCurrentIndex(
                self.settings["GPIBlist"].index("Fake")
            )
            self.ui.cOGPIB.currentIndexChanged.connect(self.openAgilent)
        # THE SCOPE IS TRIGGERED BY THE BP, NOT THE AT
        self.Agilent.EXTERNAL_OFFSET=0
        self.Agilent.write(":WAV:POIN:MODE MAX")
        self.Agilent.write(":WAV:POIN 10000")
        # self.Agilent.setTrigger(level=1.5)
        self.settings['shouldScopeLoop'] = True
        if isPaused:
            self.toggleScopePause(True)

        self.scopeCollectionThread = TempThread(target = self.collectScopeLoop)
        self.scopeCollectionThread.start()


    @staticmethod
    def __CONTROLLING_LOOPING(): pass
    def toggleScopePause(self, val):
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
            pyData = self.Agilent.getSingleChannel(int(self.ui.cOChannel.currentIndex())+1)
            # if str(self.ui.cPyroMode.currentText()) == "Integrating":
            #     pyData[:,1] = np.cumsum(pyData[:,1])#*(pyData[1,0]-pyData[0,0])
            #     log.critical("THIS IS A DEBUG LINE, GET RID OF THIS")

            if not self.settings['isScopePaused']:
                # self.pyDataSig.emit(pyData)
                self.setData(pyData)

    def processPulse(self):
        """
        Called to integrate data to find the values of the linear
        regions, calculate the fields, calculate the timing constraints
        and decide whether to add them all to the running tally
        :return:
        """
        txtinfo = "{:.3f} mJ"
        if self.ui.gbAveraging.isChecked():
            if str(self.ui.cbAveMode.currentText()) == "Waveform":
                nextidx = np.argwhere(np.isnan(self.settings["aveData"][0, :]))[0][0]
                N = nextidx + 1
                self.settings["aveData"][:, nextidx] = self.settings["pyData"][:,1]

                fitData = np.column_stack((self.settings["pyData"][:,0],
                                           np.nanmean(self.settings["aveData"], axis=1)))
                std = np.nanstd(self.settings["aveData"], axis=1)

                self.lines["ave"].setData(fitData)
                self.lines["brazil1"].setData(fitData[:, 0], fitData[:,1]-std)
                self.lines["brazil2"].setData(fitData[:, 0], fitData[:,1] + std)
                E = self.getEnergy(fitData,
                    final = (self.settings["emit_mid_average"] or N==int(self.ui.sbAveNum.value())))
                txtinfo = txtinfo.format(E)
                if not self.ui.cbRolling.isChecked():
                    txtinfo += " ({})".format(N)
                if N == int(self.ui.sbAveNum.value()):
                    if self.ui.cbRolling.isChecked():
                        self.settings["aveData"][:,:N-1] = self.settings["aveData"][:,1:N]
                        self.settings["aveData"][:,-1] *= np.nan
                    else:
                        self.updateAveSize() # force reset to nans for reaveraging
            else:
                nextidx = np.argwhere(np.isnan(self.settings["aveData"]))[0][0]
                N = nextidx + 1

                E = self.getEnergy(self.settings["pyData"],
                    final = (self.settings["emit_mid_average"] or N==int(self.ui.sbAveNum.value())))
                self.settings["aveData"][nextidx] = E

                ave = np.nanmean(self.settings["aveData"])
                std = np.nanstd(self.settings["aveData"])

                txtinfo = "{:.3f} +- {:.3f} mJ".format(ave, std)
                if not self.ui.cbRolling.isChecked():
                    txtinfo += " ({})".format(N)
                if N == int(self.ui.sbAveNum.value()):
                    if self.ui.cbRolling.isChecked():
                        self.settings["aveData"][:N-1] = self.settings["aveData"][1:N]
                        self.settings["aveData"][-1] = np.nan
                    else:
                        self.updateAveSize() # force reset to nans for reaveraging
        else:
            E = self.getEnergy(self.settings["pyData"])
            txtinfo = txtinfo.format(E)

        self.pkText.setText(txtinfo, color=(0,0,0))

    def getSaveSettings(self):
        """
        returns a dict of the settings used for repopulating
        when restarting software
        :return:
        """
        s = {
            "fel_power": str(self.ui.tFELP.text()),
            "fel_lambda": str(self.ui.tFELFreq.text()),
            "fel_reprate": str(self.ui.tFELRR.text()),
            "sample_spot_size": str(self.ui.tSpotSize.text()),
            "window_trans": str(self.ui.tWindowTransmission.text()),
            "eff_field": str(self.ui.tEffectiveField.text()),
            "fel_pol": str(self.ui.tFELPol.text()),
            "pulseCountRatio": str(self.ui.tOscCDRatio.text()),
            "coupler": str(self.ui.cFELCoupler.currentText()),
            "integratingMode": str(self.ui.cPyroMode.currentText()),
            'bcpyBG': self.boxcarRegions[0].getRegion(),
            'bcpyFP': self.boxcarRegions[1].getRegion(),
            'bcpyCD': self.boxcarRegions[2].getRegion()
        }
        return s

    @staticmethod
    def __INTEGRATING(): pass

    def fitData(self, data):
        minSt, minEn = np.argmin(data[:, 1]) + np.array([-200, 350])
        self.lines["minData"].setData(data[minSt:minEn])


        maxSt, maxEn = np.argmax(data[minEn:, 1]) + minEn + np.array([-750, 750])
        self.lines["maxData"].setData(data[maxSt:maxEn])

        p1 = np.polyfit(data[minSt:minEn, 0], data[minSt:minEn, 1], 3)
        p2 = np.polyfit(data[maxSt:maxEn, 0], data[maxSt:maxEn, 1], 2)

        x1 = data[minSt:minEn, 0]
        x2 = data[maxSt:maxEn, 0]
        y1 = np.polyval(p1, x1)
        y2 = np.polyval(p2, x2)
        self.lines["minFit"].setData(x1, y1)
        self.lines["maxFit"].setData(x2, y2)

        return np.max(y2) - np.min(y1)

    def getEnergy(self, data, final=True):
        height = self.fitData(data)*1e3
        # print height
        T = tkTrans(float(self.ui.tFELFreq.value())*29.9792)
        E =  height / (0.49 * T) * tkCalFactor
        # print E

        if final:
            self.sigPulseEnergy.emit(E)
        return E


    @staticmethod
    def __FIELD_CALCULATIONS():pass

    def updateOscilloscopeGraph(self):
        data = self.settings['pyData']
        self.lines["data"].setData(data[:,0], data[:,1])
        self.plotItem.vb.update()
        # [i['item'].update() for i in self.plotItem.axes.values()

    def updatePkTextPos(self, null, range):
        self.pkText.setPos(range[0][0], range[1][1])

    def updatePkText(self, pkpk = 0, energy = 0):
        st = "pkpk: {:.1f}".format(pkpk*1e3)
        st += ", E: {:.2f} mJ".format(energy)
        self.pkText.setText(st, color=(0,0,0))

    def close(self):
        self.settings['shouldScopeLoop'] = False
        self.settings["doPhotonCounting"] = False
        #Stop pausing
        try:
            self.scopePausingLoop.exit()
        except:
            pass
        # Stop waiting for data
        try:
            self.photonWaitingLoop.exit()
        except:
            pass
        # Stop thread waiting for data
        try:
            self.waitingForDataLoop.exit()
        except:
            pass

        #Stop the runnign thread for collecting from scope
        try:
            self.scopeCollectionThread.wait()
        except:
            pass
        # Stop the thread which processing osc data
        try:
            self.photonCountingThread.wait()
        except:
            pass


        #Restart the scope to trigger as normal.
        try:
            self.Agilent.write(':RUN')
            self.Agilent.close()
        except AttributeError:
            pass
        if self.poppedPlotWindow is not None:
            self.poppedPlotWindow.close()


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    ex = TKWid()
    sys.exit(app.exec_())
