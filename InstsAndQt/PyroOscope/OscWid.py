import scipy.integrate as spi
from ..Instruments import *
import visa
from Oscilloscope_ui import Ui_Oscilloscope
from image_spec_for_gui import *
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

import logging
log = logging.getLogger("EMCCD")

setPrintOutput(False)

class OscWid(QtGui.QWidget):

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

    sigPulseCounted = QtCore.pyqtSignal()


    def __init__(self, *args, **kwargs):
        super(OscWid, self).__init__()

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
            idx = self.settings['GPIBlist'].index('GPIB0::5::INSTR')
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

        # How many pulses are there?
        self.settings["FELPulses"] = 0
        # list of the field intensities for each pulse in a scan
        self.settings["fieldStrength"] = []
        self.settings["fieldInt"] = []
        # Either the FP time (cavity dumping)
        # or the pulse time (hole coupler)
        self.settings["felTime"] = []
        # max voltage (pk-pk)
        self.settings["pyroVoltage"] = []
        # CD ratio when necessary
        self.settings["cdRatios"] = []

        self.settings["fel_power"] = kwargs.get("fel_power", 0)
        self.settings["fel_lambda"] = kwargs.get("fel_lambda", 0)
        self.settings["fel_reprate"] = kwargs.get("fel_reprate", 1.07)
        self.settings["sample_spot_size"] = kwargs.get("sample_spot_size", 0.05)
        self.settings["window_trans"] = kwargs.get("window_trans", 1.0)
        self.settings["eff_field"] = kwargs.get("eff_field", 1.0)
        self.settings["fel_pol"] = kwargs.get("fel_pol", 'H')
        self.settings["exposing"] = False

        # lists for holding the boundaries of the linear regions
        self.settings['bcpyBG'] = kwargs.get('bcpyBG', [0,0])
        self.settings['bcpyFP'] = kwargs.get('bcpyFP', [0,0])
        self.settings['bcpyCD'] = kwargs.get('bcpyCD', [0,0])
        self.settings['pyData'] = None

        self.settings["pyBG"] = 0
        self.settings["pyFP"] = 0
        self.settings["pyCD"] = 0
        self.settings["CDtoFPRatio"] = 0

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

        ###################
        # Setting up oscilloscope values
        ##################
        self.ui.cOGPIB.addItems(self.settings['GPIBlist'])
        self.ui.cOGPIB.setCurrentIndex(self.settings["agilGPIBidx"])
        self.ui.bOPause.clicked[bool].connect(self.toggleScopePause)
        self.ui.cOGPIB.currentIndexChanged.connect(self.openAgilent)
        self.ui.bOscInit.clicked.connect(self.initOscRegions)
        self.ui.bOPop.clicked.connect(self.popoutOscilloscope)

        ###################
        # Setting plot labels
        ##################
        import sys
        self.pOsc = self.ui.gOsc.plot(pen='k')
        self.ui.gOsc.sigRangeChanged.connect(self.updatePkTextPos)

        plotitem = self.ui.gOsc.getPlotItem()

        self.plotItem = plotitem
        plotitem.setTitle('Reference Detector')
        plotitem.setLabel('bottom',text='time scale',units='us')
        plotitem.setLabel('left',text='Voltage', units='V')
        # add a textbox for pk-pk value
        self.pkText = pg.TextItem('', color=(0,0,0))
        self.pkText.setPos(0,0)
        self.pkText.setFont(QtGui.QFont("", 15))
        self.ui.gOsc.addItem(self.pkText)

        #Now we make an array of all the textboxes for the linear regions to make it
        #easier to iterate through them. Set it up in memory identical to how it
        #appears on the panel for sanity, in a row-major fashion
        lrtb = [[self.ui.tBgSt, self.ui.tBgEn],
                [self.ui.tFpSt, self.ui.tFpEn],
                [self.ui.tCdSt, self.ui.tCdEn]]
        # Connect the changes to update the Linear Regions
        for i in lrtb:
            for j in i:
                j.textAccepted.connect(self.updateLinearRegionsFromText)

        self.linearRegionTextBoxes = lrtb
        self.initLinearRegions()

        self.ui.cFELCoupler.currentIndexChanged.connect(self.updateFELCoupler)

        self.ui.tFELP.setText(str(self.settings["fel_power"]))
        self.ui.tFELFreq.setText(str(self.settings["fel_lambda"]))
        self.ui.tFELRR.setText(str(self.settings["fel_reprate"]))
        self.ui.tSpotSize.setText(str(self.settings["sample_spot_size"]))
        self.ui.tWindowTransmission.setText(str(self.settings["window_trans"]))
        self.ui.tEffectiveField.setText(str(self.settings["eff_field"]))
        self.ui.tFELPol.setText(self.settings["fel_pol"])

        self.show()

    @staticmethod
    def __ALL_THINGS_LINEARREGIONS(): pass

    def initLinearRegions(self, item = None):
        #initialize array for all 3 boxcar regions
        self.boxcarRegions = [None]*3

        bgCol = pg.mkBrush(QtGui.QColor(255, 0, 0, 50))
        fpCol = pg.mkBrush(QtGui.QColor(0, 0, 255, 50))
        sgCol = pg.mkBrush(QtGui.QColor(0, 255, 0, 50))

        #Background region for the pyro plot
        self.boxcarRegions[0] = pg.LinearRegionItem(self.settings['bcpyBG'], brush = bgCol)
        self.boxcarRegions[1] = pg.LinearRegionItem(self.settings['bcpyFP'], brush = fpCol)
        self.boxcarRegions[2] = pg.LinearRegionItem(self.settings['bcpyCD'], brush = sgCol)

        #Connect it all to something that will update values when these all change
        for i in self.boxcarRegions:
            i.sigRegionChangeFinished.connect(self.updateLinearRegionValues)

        if item is None:
            item = self.ui.gOsc
        item.addItem(self.boxcarRegions[0])
        item.addItem(self.boxcarRegions[1])
        item.addItem(self.boxcarRegions[2])

        if str(self.ui.cFELCoupler.currentText()) == 'Hole':
            self.boxcarRegions[1].hide()

    def initOscRegions(self):
        try:
            length = len(self.settings['pyData'])
            point = self.settings['pyData'][length/2,0]
        except Exception as e:
            log.warning("Error initializing scope regions {}".format(e))
            return

        # Update the dicionary values so that the bounds are proper when
        d = {0: "bcpyBG",
             1: "bcpyFP",
             2: "bcpyCD"
        }
        for i in range(len(self.boxcarRegions)):
            self.boxcarRegions[i].setRegion(tuple((point, point)))
            self.settings[d[i]] = list((point, point))

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
             1: "bcpyFP",
             2: "bcpyCD"
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
             1: "bcpyFP",
             2: "bcpyCD"
        }
        self.settings[d[i]] = list(curVals)

    def updateFELCoupler(self):
        """
        Called when felcoupler combobox changes so the
        FP thigns can be added/removed as necessary
        :return:
        """
        nowFP = str(self.ui.cFELCoupler.currentText()) == "Cavity Dump"
        if nowFP:
            # self.plotItem.addItem(self.boxcarRegions[1])
            self.boxcarRegions[1].show()
        else:
            # self.plotItem.removeItem(self.boxcarRegions[1])
            self.boxcarRegions[1].hide()
        self.ui.tFpSt.setEnabled(nowFP)
        self.ui.tFpEn.setEnabled(nowFP)

    @staticmethod
    def __POPPING_OUT_CONTROLS(): pass

    def popoutOscilloscope(self):
        if self.poppedPlotWindow is None:
            self.poppedPlotWindow = BorderlessPgPlot()
            self.oldpOsc = self.pOsc
            for i in self.boxcarRegions:
                self.ui.gOsc.removeItem(i)
            self.ui.gOsc.removeItem(self.pkText)
            self.ui.gOsc.sigRangeChanged.disconnect(self.updatePkTextPos)
            self.poppedPlotWindow.pw.addItem(self.pkText)
            self.pOsc = self.poppedPlotWindow.pw.plot(pen='k')
            self.poppedPlotWindow.pw.sigRangeChanged.connect(self.updatePkTextPos)
            plotitem = self.poppedPlotWindow.pw.getPlotItem()

            self.plotItem = plotitem
            # plotitem.setLabel('bottom',text='time scale',units='s')
            plotitem.setLabel('left',text='Voltage', units='V')

            # self.poppedPlotWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            self.poppedPlotWindow.show()
            # self.poppedPlotWindow.setWindowFlags(QtCore.Qt.WindowSystemMenuHint)
            self.poppedPlotWindow.closedSig.connect(self.cleanupCloseOsc)
            self.initLinearRegions(self.poppedPlotWindow.pw)
        else:
            self.poppedPlotWindow.raise_()

    def cleanupCloseOsc(self):
        self.poppedPlotWindow.pw.sigRangeChanged.disconnect(self.updatePkTextPos)
        self.poppedPlotWindow = None
        self.pOsc = self.oldpOsc
        self.plotItem = self.ui.gOsc.plotItem
        self.initLinearRegions()
        self.ui.gOsc.addItem(self.pkText)
        self.ui.gOsc.sigRangeChanged.connect(self.updatePkTextPos)

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

        self.Agilent.setTrigger()
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
                self.settings['pyData'] = pyData
                self.sigOscDataCollected.emit()

    def processPulse(self):
        """
        Called to integrate data to find the values of the linear
        regions, calculate the fields, calculate the timing constraints
        and decide whether to add them all to the running tally
        :return:
        """

        pyBG, pyFP, pyCD, time, pkpk, ratio = self.integrateData()
        self.settings["pyBG"] = pyBG
        self.settings["pyFP"] = pyFP
        self.settings["pyCD"] = pyCD

        self.doFieldCalculation()

        if True:
            self.sigPulseCounted.emit()

    def doPhotonCountingLoop(self):
        while self.settings["doPhotonCounting"]:
            self.photonWaitingLoop = QtCore.QEventLoop()
            self.sigOscDataCollected.connect(self.photonWaitingLoop.exit)
            self.photonWaitingLoop.exec_()
            # if self.papa.curExp.runSettings["exposing"]:
            if self.settings["exposing"]:
                pyBG = self.settings["pyBG"]
                pyFP = self.settings["pyFP"]
                pyCD = self.settings["pyCD"]

                # count pulse if CD signal - BG signal is greater than
                # some user-specified value.
                if (
                    (pyCD-pyBG > self.ui.tOscCDRatio.value())
                ):
                    self.settings["FELPulses"] += 1
                    # self.papa.updateElementSig.emit(self.ui.tOscPulses, self.settings["FELPulses"])
                    # self.papa.updateElementSig.emit(self.papa.curExp.ui.tCCDFELPulses, self.settings["FELPulses"])
                    # self.doFieldCalcuation(pyBG, pyFP, pyCD)
                    self.sigDoneCounting.emit()
                else:
                    print "PULSE NOT COUNTED!"

    def startExposure(self):
        self.settings["exposing"] = True

        # reset all pulse counting metrics
        self.settings["FELPulses"] = 0
        # list of the field intensities for each pulse in a scan
        self.settings["fieldStrength"] = []
        self.settings["fieldInt"] = []
        # Either the FP time (cavity dumping)
        # or the pulse time (hole coupler)
        self.settings["felTime"] = []
        # max voltage (pk-pk)
        self.settings["pyroVoltage"] = []
        # CD ratio when necessary
        self.settings["cdRatios"] = []



    @staticmethod
    def __INTEGRATING(): pass


    def integrateData(self):
        #Neater and maybe solve issues if the data happens to update
        #while trying to do analysis?
        pyD = self.settings['pyData']

        pyBGbounds = self.boxcarRegions[0].getRegion()
        pyBGidx = self.findIndices(pyBGbounds, pyD[:,0])

        pyFPbounds = self.boxcarRegions[1].getRegion()
        pyFPidx = self.findIndices(pyFPbounds, pyD[:,0])

        pyCDbounds = self.boxcarRegions[2].getRegion()
        pyCDidx = self.findIndices(pyCDbounds, pyD[:,0])

        pyBG = spi.simps(pyD[pyBGidx[0]:pyBGidx[1],1], pyD[pyBGidx[0]:pyBGidx[1], 0])
        pyBG /= np.diff(pyBGidx)[0]

        pyBG = np.mean(pyD[pyBGidx[0]:pyBGidx[1], 1])

        if str(self.ui.cFELCoupler.currentText()) == "Cavity Dump":
            if str(self.ui.cPyroMode.currentText()) == "Instant":
                # if the pyro is in instantaneous ("fast" mode), integrate the data
                # ourselves
                pyFP = spi.simps(pyD[pyFPidx[0]:pyFPidx[1],1], pyD[pyFPidx[0]:pyFPidx[1], 0])
                pyFP /= np.diff(pyFPidx)[0]
                pyCD = spi.simps(pyD[pyCDidx[0]:pyCDidx[1],1], pyD[pyCDidx[0]:pyCDidx[1], 0])
                pyCD /= np.diff(pyCDidx)[0]
                ratio = (pyCD-pyBG)/(pyCD + pyFP - 2*pyBG)
                # set the FP time by the region of the boxcar
                tau = pyFPbounds[1] - pyFPbounds[0]
                pkpk = np.max(pyD[pyCDidx[0]:pyCDidx[1],1]) - pyBG
            else:
                # otherwise, assume it's in integrating mode, we just
                # want to pick out the points at the end of the FP
                # and the start of the CD

                # fit the FP to a line in the region selected by the user
                #
                linearCoeff = np.polyfit(*pyD[pyFPidx,:].T, deg=1)
                pyFP = np.polyval(x = pyD[pyFPidx[-1], 0], p = linearCoeff)

                # for the CD, grab the average
                pyCD = np.mean(pyD[pyCDidx[0]:pyCDidx[1], 1])
                ratio = (pyCD-pyFP)/(pyCD - pyBG)

                # for the FP time, grab the end of the linear region, and the point where the line
                # fitting it would intersect with the background
                t2 = pyFPbounds[1]
                t1 = (pyBG - linearCoeff[1])/linearCoeff[0]
                tau = t2-t1

                pkpk = pyCD - pyBG


        else:
            # Now we assume that it's the hole coupler,
            # need to ignore the FP regions
            #
            # Force all calculations for "ratio" to be 1, since
            # all the energy is now in the "cavity dump",
            # which I'll take to mean the region of interest.
            pyFP = 0
            ratio = 1
            # just calculate the average for both, right?
            pyCD = np.mean(pyD[pyCDidx[0]:pyCDidx[1], 1])
            if str(self.ui.cPyroMode.currentText()) == "Instant":

                tau = pyCDbounds[1] - pyCDbounds[0]

                pkpk = np.max(pyD[pyCDidx[0]:pyCDidx[1], 1]) - pyBG
            else:
                pkpk = pyCD - pyBG

                # We've found the FWHM of an instant signal
                # corresponds to rouhgly the 10-90 values
                # on an integrated value. use that for the time
                tau = self.calcPulseWidth(pyD, lowHeight=pyBG, highHeight=pyCD)


        return pyBG, pyFP, pyCD, tau, pkpk, ratio

    @staticmethod
    def calcPulseWidth(data, lowRange = (.095, .105), highRange=(.895, .905), lowHeight=None, highHeight=None, debug=False):
        # low/highRange are either an interable of boudns of min/max
        # for the start/end heights of pulse,
        # or a single value with bounds taken +-0.5%
        # (i.e. lowRange=0.1 will cause it to look
        # for a starting point at 0.095 to .105)
        #
        # Debug = True causes debug print statements
        # debug = None prevents it from returning nan (to prevent recursive
        #         calls when recalling for larger bounds)

        # parse inputs
        try:
            lowRange[0]
            lowRange[1]
        except TypeError:
            lowRange = tuple(lowRange + np.array([-0.005, 0.005]))
        except IndexError:
            # print "How the fuck did you do this?"
            raise
        try:
            highRange[0]
            highRange[1]
        except TypeError:
            highRange = tuple(highRange + np.array([-0.005, 0.005]))
        except IndexError:
            # print "How the fuck did you do this?"
            raise

        if data.ndim == 2:
            time = data[:,0]
            data = data[:,1]
        else:
            raise ValueError("Need a 2d array to calculate widths")


        if None in [lowHeight, highHeight]:
            # define the min/max of the data as the
            # first/last 5% of the data if not
            # passed
            N = len(data)
            # if debug or debug is None:
            #     print data.shape
            N05 = int(N*0.05)
            # if debug or debug is None:
            #     print N, N05
            lowHeight, highHeight = data[:N05].mean(), data[-N05:].mean()
        # if debug or debug is None:
        #     print low, high

        data -= lowHeight

        pkpk = highHeight-lowHeight
        # if debug or debug is None:
        #     print "lowRanges", lowRange
        #     print "looking lowRanges between:", pkpk*np.array(lowRange)
        #     plt.plot(time[[0,-1]], [pkpk*lowRange[0]]*2)
        #     plt.plot(time[[0,-1]], [pkpk*lowRange[1]]*2)
        lowIdx = list(set(np.where(data>lowRange[0]*pkpk)[0]) & set(np.where(data<lowRange[1]*pkpk)[0]))
        # if debug or debug is None:
        #     print "lowtimes:", time[lowIdx].mean()
        #     print

        # if debug or debug is None:
        #     print "high height", highRange
        #     print "looking highRanges between: {}".format(pkpk*np.array(highRange))
        #     plt.plot(time[[0,-1]], [pkpk*highRange[0]]*2)
        #     plt.plot(time[[0,-1]], [pkpk*highRange[1]]*2)
        highIdx = list(set(np.where(data>highRange[0]*pkpk)[0]) & set(np.where(data<highRange[1]*pkpk)[0]))
        # if debug or debug is None:
        #     print "data>high[0]", time[np.where(data>highRange[0])[0]][:10]
        #     print "data<high[1]", time[np.where(data<highRange[1])[0]][-10:]
        # if debug or debug is None:
        #     print "hightimes:", time[highIdx].mean()
        #     plt.plot(time, data)
            # plt.show()
        ret = time[highIdx].mean() - time[lowIdx].mean()
        if np.isnan(ret) and debug is not None:
            # print "Error, couldn't find values. Poor digitization?"
            ret = OscWid.calcPulseWidth(np.column_stack((time, data)),
                                 lowRange=(lowRange[0]+0.05, lowRange[1]+0.15),
                                 highRange=(highRange[0]-0.15, highRange[1]-0.05),
                                 highHeight = highHeight, lowHeight = lowHeight,
                                 debug=None)

        return ret

    @staticmethod
    def findIndices(values, dataset):
        """Given an ordered dataset and a pair of values, returns the indices which
           correspond to these bounds  """
        indx = list((dataset>values[0]) & (dataset<values[1]))
        #convert to string for easy finding
        st = ''.join([str(int(i)) for i in indx])
        start = st.find('1')
        if start == -1:
            start = 0
        end = start + st[start:].find('0')
        if end<=0:
            end = 1
        return start, end

    @staticmethod
    def __FIELD_CALCULATIONS():pass
    def doFieldCalculation(self):
        """
        :param BG: integrated background value
        :param FP: integrated front porch value
        :param CD: integrated cav   ity dump region
        :return:
        """
        try:
            energy = self.ui.tFELP.value()
            windowTrans = self.ui.tWindowTransmission.value()
            effField = self.ui.tEffectiveField.value()
            radius = self.ui.tSpotSize.value()
            # if str(self.papa.oscWidget.ui.cPyroMode.currentText()) == "Instant":
            #     ratio = CD/(FP + CD)
            # else:
            #     ratio = CD/FP
            ratio = self.settings['CDtoFPRatio']
            intensity = calc_THz_intensity(energy, windowTrans, effField, radius=radius,
                                           ratio = ratio)
            field = calc_THz_field(intensity)

            intensity = round(intensity/1000., 3)
            field = round(field/1000., 3)

            self.papa.updateElementSig.emit(
                self.ui.tIntensity, "{:.3f}".format(intensity))
            self.papa.updateElementSig.emit(
                self.ui.tEField, "{:.3f}".format(field))

            self.settings["fieldInt"].append(intensity)
            self.settings["fieldStrength"].append(field)

        except Exception as e:
            log.warning("Could not calculate electric field, {}".format(e))

    def updateOscilloscopeGraph(self):
        data = self.settings['pyData']
        self.pOsc.setData(data[:,0], data[:,1])
        self.plotItem.vb.update()
        # [i['item'].update() for i in self.plotItem.axes.values()

    def updatePkTextPos(self, null, range):
        self.pkText.setPos(range[0][0], range[1][1])

    def updatePkText(self, *args):
        pass


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
    ex = OscWid()
    sys.exit(app.exec_())
