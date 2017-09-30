from PyQt5 import QtCore, QtGui, QtWidgets
import weakref


try:
    import visa


    rm = visa.ResourceManager()
except ImportError:
    raise ImportError("Need pyvisa to operate ComboBox")

import logging


log = logging.getLogger("Instruments")


def BaseInstrument(object):
    def __init__(GPIB=None):
        pass


class InstrumentGPIB(QtWidgets.QComboBox):
    # Emits the instrument when it's opened
    sigInstrumentOpened = QtCore.pyqtSignal(object)
    # emits when a close is requested, not necessarily
    # when it's closed (as it can be set by closeOnChange)
    sigInstrumentClosed = QtCore.pyqtSignal()
    # signal which connects to the function so it can be
    # called in threads
    sigSetAddress = QtCore.pyqtSignal(object)
    def __init__(self, parent=None, *args, **kwargs):
        super(InstrumentGPIB, self).__init__(parent)

        self._GPIBList = []
        self._instrumentCls = BaseInstrument
        self._instrumentArgs = None
        self._instrument = None
        self.currentIndexChanged.connect(self.changeInstrument)
        self.sigSetAddress.connect(self.setAddress)

        self.closeOnChange = True

        self.refreshGPIBList()

    def __contains__(self, item):
        return item in self._GPIBList or item is "None" or item is "Fake"

    def refreshGPIBList(self):
        self.blockSignals(True)
        gpiblist = rm.list_resources()
        curLabel = self.currentText()
        if not curLabel: curLabel = "None"
        self.clear()

        self._GPIBList = [str(i) for i in gpiblist]

        self.addItem("None")

        self.addItems(self._GPIBList)
        self.addItem("Fake")
        self.addItem("Refresh...")

        self.setAddress(curLabel)

        self.blockSignals(False)

    def changeInstrument(self):
        if str(self.currentText()) == "None":
            self.closeInstrument()
            return

        if str(self.currentText()) == "Refresh...":
            self.refreshGPIBList()
            return
        self.closeInstrument()

        # If you've set an instrument to open, open it
        if not self._instrumentCls is BaseInstrument:
            try:
                if self._instrumentArgs is None or not self._instrumentArgs:
                    inst = self._instrumentCls(str(self.currentText()))
                else:
                    inst = self._instrumentCls(str(self.currentText()), *self._instrumentArgs)

            except Exception as e:
                print("Warning, unable to open desired instrument at addr. {}".format(self.currentText()))
                print("\t",e)
                print("cls/args:", self._instrumentCls, self._instrumentArgs)
                self.blockSignals(True)
                self.setCurrentIndex(self.findText("Fake"))
                self.blockSignals(False)
                return

            self._instrument = weakref.ref(inst)
            self.sigInstrumentOpened.emit(inst)

    def setAddress(self, address):
        if address not in self:
            # raise RuntimeError("Not a valid hardware address: {}".format(address))
            log.warning("Not a valid hardware address: {}".format(address))
            return
        self.setCurrentIndex(self.findText(address))


    def closeInstrument(self):
        self.sigInstrumentClosed.emit()
        if self.closeOnChange and self._instrument is not None:
            try:
                self._instrument().close()
            except Exception as e:
                log.exception("Error closing instrument in GPIB combo")


    def setHoverText(self, text=""):
        self.setToolTip(str(text))

    def setInstrumentClass(self, cls=BaseInstrument, *args):
        self._instrumentCls = cls
        if args:
            self.setInstrumentArgs(args)

    def setInstrumentArgs(self, *args):
        self._instrumentArgs = args


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    wid = InstrumentGPIB()
    wid.setHoverText("This is text")
    from .Instruments import Agilent6000 as a



    wid.setInstrumentClass(a)
    wid.show()
    app.exec_()



