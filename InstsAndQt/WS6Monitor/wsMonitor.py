from InstsAndQt.Instruments import WS6
from PyQt5 import QtCore, QtWidgets, QtGui
from pyqtgraph import SpinBox
import time
import os
from InstsAndQt.SettingsDict import Settings
import numpy as np

import interactivePG as pg
from InstsAndQt.cQt.DateAxis import DateAxis
import logging
log = logging.getLogger("Instruments")

class LaserState(object):
    """
    helper class for keeping track of the the laser state
    changing, allowing easier comparison of time and what not.

    """
    def __init__(self, time=0, wavelength=0, power=0):
        if isinstance(time, LaserState):
            self.time=time.time
            self.wavelength = time.wavelength
            self.power = time.power
            self.thresholdPower = time.thresholdPower
            self.thresholdWavelength = time.thresholdWavelength
            self.thresholdTime = time.thresholdTime
        else:
            self.time = time
            self.wavelength = wavelength
            self.power = power

            self.thresholdPower = 10
            self.thresholdWavelength = 50
            self.thresholdTime = 10

    def __eq__(self, other):
        # Returns True if all parameters are within the
        # threshold values
        # thT = abs(self.time - other.time) < self.thresholdTime
        # thW = abs(self.wavelenegth - other.wavelenegth) < self.thresholdWavelength
        thP = abs(self.power - other.power) < self.thresholdPower
        thW = self.wavelength == other.wavelength
        # thP = self.power == other.power
        return all([thW, thP])

    def __sub__(self, other):
        """
        return the time difference between the two states
        useful for finding time difference in saving
        :param other:
        :return:
        """
        return self.time-other.time

    def setThresholdPower(self, val):
        self.thresholdPower = val

    def setThresholdWavelength(self, val):
        self.thresholdWavelength = val

    def setThresholdTime(self, val):
        self.thresholdTime = val

    def saveStr(self):
        if self.wavelength == 0: return ""
        return f"{self.time},{self.wavelength:.4f},{self.power:.1f}\n"


class WS6Monitor(QtWidgets.QLabel):
    """
    A class for monitoring the WS6.

    Barebones, showing no window or border or anything to
    be minimal. It logs to file, but only when the wavelength changes
    It pops up a dialog when the wavelength changes from the setpoint

    """
    # Emitted when the wavelength changes.
    # Emits as <previous value> <new value>
    # TODO: decide what units (or constant nm?)
    sigStateChanged = QtCore.pyqtSignal()

    # Sig for updating style sheet (see docstring on parsing callback)
    sigStyleSheet = QtCore.pyqtSignal(object)

    sigStartTimer = QtCore.pyqtSignal()
    _plot = None

    def __init__(self, *args, **kwargs):
        super(WS6Monitor, self).__init__()


        self.settings = Settings({
            "units": "nm",
            "logFile": r"Z:\~HSG\Data\2017",
            "setpoint": 764, #nm
            "setpointErr": 1, #pm
            "powerSetpoint": 10,  # uW
        })
        self.settings.filePath = os.path.join(os.path.dirname(__file__), "Settings.txt")

        # Keep a reference to the log file to prevent needs to open/close
        # all the time, hopefully saving a lot of time when the laser is
        # jumping and causing a lot of writes
        self._logFile = None

        try:
            self.ws = WS6()
        except:
            log.exception("Couldn't get WS6")
            raise RuntimeError("No WS6")

        self.setText("This is the text")

        # open the log file if there's a good settings file
        # (meaning you likely chose one and it was saved in the settings)
        if self.settings.loadSettings():
            self.openLogFile()
        self.defaultStyleSettings = {
            "background-color": "white",
            "color": "black",
            "font-size": 28
        }

        menu = self.getContextMenuTree()


        self.resetStyleSheet()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda x: menu.exec(self.mapToGlobal(x))
        )

        self.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )
        # self.setMinimumHeight(62)
        geo = self.geometry()
        geo.setHeight(62)
        geo.setWidth(165)
        self.setGeometry(geo)
        self.sigStateChanged.connect(self.handleWavelengthChange)

        self.sigStyleSheet.connect(self.resetStyleSheet)

        # Only allow the power change to cause updates once a
        # second to keep down on file sizes
        self.powerTimer = QtCore.QTimer(self)
        self.powerTimer.setSingleShot(True)
        self.powerTimer.setInterval(1000)
        self.sigStartTimer.connect(self.powerTimer.start)
        # I want to keep track of the last time the laser jumped. If it's a long
        # time, I want to have the file log the old and new wavelengths at the same
        # time, so that if I plot it later, it's not a giant jump. But if the
        # laser's jumping all over and noisy, I don't want to ad a shitton of points
        # and square pulses, because it'll look worse
        # self._lastWrite = time.time()

        # internal reference to the wavelength, in nm
        # Prevents precision issues if you use the value in
        # self.text() alone
        # self._value = 0

        self.currentState = LaserState(time=time.time())
        self.currentState.thresholdWavelength = self.settings["setpointErr"]
        self.currentState.thresholdPower = self.settings["powerSetpoint"]
        self.lastSavedState = LaserState()


        try:
            self.ws.attachCallback(self.parseWSCallback)
        except:
            log.exception("Couldn't attach callback")

    def closeEvent(self, ev):
        try:
            self._logFile.close()
        except AttributeError:
            pass
        print("closed event")
        self.ws.registerFunctions()
        super(WS6Monitor, self).closeEvent(ev)

    def changeEvent(self, ev):
        if ev.type() != QtCore.QEvent.ActivationChange:
            return super(WS6Monitor, self).changeEvent(ev)
        if self.isActiveWindow():
            self.resetStyleSheet()
        return super(WS6Monitor, self).changeEvent(ev)

    def resizeEvent(self, a0):
        try:
            picture = QtGui.QPicture()
            p = QtGui.QPainter(picture)
            newSize = None
            for size in np.array([-2, -1, 1, 2]) +self.defaultStyleSettings["font-size"]:
                p.setFont(QtGui.QFont("", pointSize=size))
                br = p.boundingRect(self.geometry(), QtCore.Qt.AlignLeft, self.text())
                if br.width()*.75 < self.geometry().width() and br.height()*.75:
                    newSize = int(size)
            if newSize is not None:
                self.defaultStyleSettings["font-size"] = newSize
                print(newSize)
                self.resetStyleSheet()
        finally:
            # Python crashes if you don't end the painter
            p.end()
        super(WS6Monitor, self).resizeEvent(a0)

    def resetStyleSheet(self, sheet=dict()):
        style = self.defaultStyleSettings.copy()
        style.update(sheet)
        self.setStyleSheet(f"QLabel {{ background-color: {style['background-color']};"
                           f"color: {style['color']};"
                           f"font-size: {style['font-size']}px}}")

    def mouseMoveEvent(self, evt):
        evt.accept()
        d = evt.screenPos() - self.moveOffset
        self.move(d.x(), d.y())

    def mousePressEvent(self, evt):
        evt.accept()
        # For some reason, the border of the window isn't being appropriately considered
        # with the base pos/screenpos functions. It seems if I get the border dimensions
        # and offset appropriately, it works better. Otherwise, the window jumps slightly
        # when you click and drag.
        dh = (self.frameGeometry().height() - self.geometry().height())/2
        dw = (self.frameGeometry().width() - self.geometry().width()) / 2

        self.moveOffset = evt.pos() + QtCore.QPoint(dw, dh)

    def mouseReleaseEvent(self, ev):
        ev.accept()

    def getContextMenuTree(self):
        # the overall menu
        menu = QtWidgets.QMenu()

        subMenu = menu.addMenu("Set watch point")

        sp = QtWidgets.QWidget(subMenu)
        layout = QtWidgets.QHBoxLayout(sp)

        self.sbSetPoint = SpinBox(subMenu, decimals = 7)
        self.sbSetPoint.setValue(self.settings["setpoint"])
        self.sbSetPoint.setMaximumWidth(70)
        self.sbSetPoint.sigValueChanged.connect(
            lambda x: self.settings.__setitem__("setpoint", x.value())
        )
        self.sbSetPointErr = SpinBox(subMenu, decimals=4, step=0.1)
        self.sbSetPointErr.sigValueChanged.connect(
            lambda x: self.settings.__setitem__("setpointErr", x.value())
        )
        self.sbSetPointErr.setValue(self.settings["setpointErr"])
        self.sbSetPointErr.setMaximumWidth(45)
        layout.addWidget(self.sbSetPoint, 1)
        layout.addWidget(QtWidgets.QLabel("nm +/-"), 0)
        layout.addWidget(self.sbSetPointErr, 1)
        layout.addWidget(QtWidgets.QLabel("pm"), 0)
        sp.setLayout(layout)
        action = QtWidgets.QWidgetAction(subMenu)
        action.setDefaultWidget(sp)
        subMenu.addAction(action)


        subMenu = menu.addMenu("Set Units")
        group = QtWidgets.QButtonGroup(subMenu)
        nm = QtWidgets.QRadioButton("nm")
        eV = QtWidgets.QRadioButton("eV")
        cm = QtWidgets.QRadioButton("cm-1")
        if self.settings["units"] == "nm":
            nm.setChecked(True)
        elif self.settings["units"] == "eV":
            eV.setChecked(True)
        else:
            cm.setChecked(True)
        wid = QtWidgets.QWidget(None)
        layout = QtWidgets.QVBoxLayout(wid)
        layout.addWidget(nm)
        layout.addWidget(eV)
        layout.addWidget(cm)
        group.buttonClicked.connect(
            lambda x: self.settings.__setitem__("units", str(x.text()))
        )
        wid.setLayout(layout)
        group.addButton(nm)
        group.addButton(eV)
        group.addButton(cm)
        group.buttonClicked.connect(self.updateUnits)
        action = QtWidgets.QWidgetAction(subMenu)
        action.setDefaultWidget(wid)
        subMenu.addAction(action)

        subMenu = menu.addMenu("Set power threshold")
        self.sbPowerSetPoint = SpinBox(subMenu, decimals=2)
        self.sbPowerSetPoint.setValue(self.settings["powerSetpoint"])
        self.sbPowerSetPoint.setMaximumWidth(70)
        self.sbPowerSetPoint.sigValueChanged.connect(
            lambda x: self.settings.__setitem__("powerSetpoint", x.value())
        )
        self.sbPowerSetPoint.sigValueChanged.connect(
            lambda x: self.currentState.setThresholdPower(x.value())
        )
        action = QtWidgets.QWidgetAction(subMenu)
        action.setDefaultWidget(self.sbPowerSetPoint)

        subMenu.addAction(action)

        save = menu.addAction("Select Save File...")
        save.triggered.connect(self.chooseLogFile)

        menu.addAction("Show Plot").triggered.connect(self.showPlot)

        return menu

    def handleWavelengthChange(self):
        # print(f"value changed from {oldVal} to {newVal}")
        self.saveWavelengthChange()
        self.updateValue(self.currentState)

        if abs(self.value() - self.sbSetPoint.value()) > self.sbSetPointErr.value()*1e-3:
            self.resetStyleSheet({"background-color":"red", "color":"yellow"})

    def saveWavelengthChange(self):
        if self.settings["logFile"] is None: return
        if self._logFile is None: return
        curTime = time.time()
        self.currentState.time = time.time()
        # Say, if it's more than 10 seconds?
        if self.currentState - self.lastSavedState > 10:
            # Update the last time to be the same as the current one.
            self.lastSavedState.time = self.currentState.time
            st = self.lastSavedState.saveStr() + self.currentState.saveStr()
        else:
            st = self.currentState.saveStr()
        self.lastSavedState = LaserState(self.currentState)

        try:
            self._logFile.write(st)
            self._logFile.flush()
            # self._lastWrite = curTime
        except:
            log.exception("Couldn't save wavelengths")

    def chooseLogFile(self):
        loc = QtWidgets.QFileDialog.getSaveFileName(self, "Pick logging file",
                                                self.settings["logFile"],
                                                "Text File (*.txt)")[0]
        loc = str(loc)
        if not loc: return
        self.settings["logFile"] = loc
        self.settings.saveSettings()
        self.openLogFile()

    def openLogFile(self):
        loc = self.settings["logFile"]
        # if not os.path.isfile(loc): return
        try:
            self._logFile.close()
        except AttributeError:
            pass
        oh = ''
        if not os.path.isfile(loc):
            oh += 'Time,wavelength,power\n'
            oh += 's,nm,uW\n'
            oh += ',,\n'

        # Save the current value. But don't do it if
        # this is called before everything's been initialized
        if self.value() != 1:
            # oh += "{},{:.4f}\n".format(time.time(), self._value)
            oh += self.currentState.saveStr()
        try:
            print("opening file", loc)
            self._logFile = open(loc, 'a+')
            self._logFile.write(oh)
            self._logFile.flush()
            print("I made a log handle,", self._logFile)
        except:
            log.exception("Couldn't open the log file")

    def updateUnits(self, button):
        oldUnits = self.settings["units"]
        self.settings["units"] = str(button.text())
        self.updateValue(self.value(), givenUnits=oldUnits)

    def value(self, units = 'nm'):
        """
        return the wavelength
        :return:
        """
        try:
            value = round(converter[self.settings["units"]][units](
                self.currentState.wavelength
            ), 4)
        except ZeroDivisionError:
            return 1 # Not sure when this one occurs
        except AttributeError:
            return 1 # called called before fully initialized
        except:
            log.exception("Error converting value!")
            return 1
        return value

    def parseWSCallback(self, mode, intVal, dval):
        """
        function called by the callback function of the WS6

        I don't think this is done in the main thread, as GUI changes
        from this function cause crashses. need the sigStyleChange to emit
        changes from here to call in the main thread.
        :param mode:
        :param intVal:
        :param dval:
        :return:
        """
        # Skip these modes, don't care about them
        if mode in [
            WS6.c.cmiMax1,
            WS6.c.cmiMin1,
            WS6.c.cmiPatternAvg1,
            WS6.c.cmiTemperature,
            WS6.c.cmiPressure
        ]: return
        if int(dval) in [WS6.c.ErrBigSignal, WS6.c.ErrLowSignal]:
            # self.resetStyleSheet(color="blue")
            self.sigStyleSheet.emit({"color":"blue"})
            return
        if mode == WS6.c.cmiWavelength1:
            # don't waste time updating if there's no change
            # if round(dval, 4) == self.value(): return
            self.currentState.wavelength = round(dval, 4)
            if self.currentState == self.lastSavedState: return
            self.sigStateChanged.emit()
            # self.updateValue(dval)
            # self._value = dval
        elif mode == WS6.c.cmiPower:
            if self.powerTimer.isActive(): return
            self.currentState.power = round(dval, 1)
            if self.currentState == self.lastSavedState:
                # print("states same", self.currentState.power, self.lastSavedState.power)
                return
            self.sigStartTimer.emit()
            self.sigStateChanged.emit()
        elif mode == WS6.c.cmiExposureValue1:
            # Warn me if the exposure is taking too long
            if intVal > 100:
                # self.resetStyleSheet(color="green")
                self.sigStyleSheet.emit({"color": "green"})

        else:
            print("Dunno mode", mode, intVal, dval)

    def showPlot(self):
        if not os.path.isfile(self.settings["logFile"]): return
        data = np.genfromtxt(self.settings["logFile"], delimiter=',')[3:]

        wid = pg.PlotContainerWindow()

        pi = wid.plotWidget.plotItem
        pi.layout.removeItem(pi.getAxis('bottom'))
        caxis = DateAxis(orientation='bottom', parent=pi)
        caxis.linkToView(pi.vb)
        pi.axes["bottom"]["item"] = caxis
        pi.layout.addItem(caxis, 3, 1)
        pi.layout.removeItem(pi.getAxis('top'))
        caxis = DateAxis(orientation='top', parent=pi)
        caxis.linkToView(pi.vb)
        pi.axes["top"]["item"] = caxis
        pi.layout.addItem(caxis, 0, 1)

        p2 = pg.pg.ViewBox()
        pi.getAxis("right").linkToView(p2)
        pi.scene().addItem(p2)
        p2.setXLink(pi.vb)
        p2.addItem(pg.pg.PlotDataItem(data[:,0], data[:,2], pen='r'))
        pi.vb.sigResized.connect(lambda: p2.setGeometry(pi.vb.sceneBoundingRect()))

        wid.plot(data[:,0], data[:,1])
        wid.show()

        self._plot = wid

    def updateValue(self, state, givenUnits="nm"):
        prec = {
            "nm": 4,
            "cm-1": 2,
            "eV": 6
        }
        value = state.wavelength
        power = state.power
        units = self.settings["units"]
        value = converter[givenUnits][units](value)

        txt = f"{value:.{prec[units]}f} {units}\n({power})"

        # txt = f"<font size={self._fontSize}>{txt}</font>"

        self.setText(str(txt))






h = 4.135667516e-15
c = 299792458



# converter[A][B](x):
#    convert x from A to B.
converter = {
    "nm":         {"nm": lambda x: x,           "eV": lambda x:h*c/(x*1e-9),            "cm-1": lambda x: 1e7/x},
    "eV":         {"nm": lambda x: h*c/(x*1e-9),   "eV": lambda x: x,                   "cm-1":lambda x: (x*1e-2)/(h*c)},
    "cm-1":       {"nm": lambda x: 1e7/x, "eV": lambda x: (x*1e-2)*(h*c),           "cm-1": lambda x: x}
}

if __name__ == '__main__':
    import sys
    ex = QtWidgets.QApplication(sys.argv)
    wid = WS6Monitor()
    wid.show()
    sys.exit(ex.exec_())
