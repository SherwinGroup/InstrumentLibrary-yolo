from InstsAndQt.Instruments import WS6
from PyQt5 import QtCore, QtWidgets
from pyqtgraph import SpinBox
import time
import os
from InstsAndQt.SettingsDict import Settings
import logging
log = logging.getLogger("Instruments")



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
    sigWavelengthChanged = QtCore.pyqtSignal(object, object)

    def __init__(self, *args, **kwargs):
        super(WS6Monitor, self).__init__()


        self.settings = Settings({
            "units": "nm",
            "logFile": r"Z:\~HSG\Data\2017",
            "setpoint": 764, #nm
            "setpointErr": 1, #pm
        })
        self.settings.filePath = os.path.join(os.path.dirname(__file__), "Settings.txt")


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
            "font-size": "28px"
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

        self.sigWavelengthChanged.connect(self.handleWavelengthChange)
        # I want to keep track of the last time the laser jumped. If it's a long
        # time, I want to have the file log the old and new wavelengths at the same
        # time, so that if I plot it later, it's not a giant jump. But if the
        # laser's jumping all over and noisy, I don't want to ad a shitton of points
        # and square pulses, because it'll look worse
        self._lastWrite = time.time()

        # Keep a reference to the log file to prevent needs to open/close
        # all the time, hopefully saving a lot of time when the laser is
        # jumping and causing a lot of writes

        self._logFile = None

        # internal reference to the wavelength, in nm
        # Prevents precision issues if you use the value in
        # self.text() alone
        self._value = 0

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
        super(WS6Monitor, self).closeEvent(ev)

    def changeEvent(self, ev):
        if ev.type() != QtCore.QEvent.ActivationChange:
            return super(WS6Monitor, self).changeEvent(ev)
        if self.isActiveWindow():
            self.resetStyleSheet()
        return super(WS6Monitor, self).changeEvent(ev)

    def resetStyleSheet(self, **sheet):
        style = self.defaultStyleSettings.copy()
        style.update(sheet)
        self.setStyleSheet(f"QLabel {{ background-color: {style['background-color']};"
                           f"color: {style['color']};"
                           f"font-size: {style['font-size']}}}")

    def mouseMoveEvent(self, evt):
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

        save = menu.addAction("Select Save File...")
        save.triggered.connect(self.chooseLogFile)

        return menu

    def handleWavelengthChange(self, oldVal, newVal):
        # print(f"value changed from {oldVal} to {newVal}")
        self.saveWavelengthChange(oldVal, newVal)

        if abs(newVal - self.sbSetPoint.value()) > self.sbSetPointErr.value()*1e-3:
            self.resetStyleSheet(color="red")

    def saveWavelengthChange(self, oldVal, newVal):

        if self.settings["logFile"] is None: return
        if self._logFile is None: return
        curTime = time.time()
        # Say, if it's more than 10 seconds?
        if curTime - self._lastWrite > 10:
            st = "{},{:.4f}\n{},{:.4f}\n".format(curTime, oldVal, curTime, newVal)
        else:
            st = "{},{:.4f}\n".format(curTime, newVal)

        try:
            self._logFile.write(st)
            self._logFile.flush()
            self._lastWrite = curTime
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
            oh += 'Time,wavelength\n'
            oh += 's,nm\n'
            oh += ',\n'
        try:
            print("opening file", loc)
            self._logFile = open(loc, 'a+')
            self._logFile.write(oh)
            self._logFile.flush()
        except:
            log.exception("Coudln't open the log file")

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
            value = round(converter[self.settings["units"]][units](self._value), 4)
        except ZeroDivisionError:
            return 1
        except:
            log.exception("Error converting value!")
            return 1
        return value

    def parseWSCallback(self, mode, intVal, dval):
        """
        function called by the callback function of the WS6
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
        if intVal in [WS6.c.ErrBigSignal, WS6.c.ErrLowSignal]:
            self.resetStyleSheet(color="blue")
            return
        if mode == WS6.c.cmiWavelength1:
            # don't waste time updating if there's no change
            if round(dval, 4) == self.value(): return
            self.sigWavelengthChanged.emit(self.value(), dval)
            self.updateValue(dval)
            self._value = dval
        elif mode == WS6.c.cmiPower:
            pass
        elif mode == WS6.c.cmiExposureValue1:
            # Warn me if the exposure is taking too long
            if intVal > 100:
                self.resetStyleSheet(color="green")

        else:
            print("Dunno mode", mode, intVal, dval)

    def updateValue(self, value, givenUnits="nm"):
        prec = {
            "nm": 4,
            "cm-1": 2,
            "eV": 6
        }

        units = self.settings["units"]
        value = converter[givenUnits][units](value)

        txt = f"{value:.{prec[units]}f} {units}"

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