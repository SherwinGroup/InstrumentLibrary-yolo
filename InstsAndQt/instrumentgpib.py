from PyQt4 import QtGui, QtCore
import weakref
try:
    import visa
    rm = visa.ResourceManager()
except ImportError:
    raise ImportError("Need pyvisa to operate ComboBox")

def BaseInstrument(object):
    def __init__(GPIB=None):
        pass


class InstrumentGPIB(QtGui.QComboBox):
    sigInstrumentOpened = QtCore.pyqtSignal(object)
    sigInstrumentClosed = QtCore.pyqtSignal()
    def __init__(self, parent=None, *args, **kwargs):
        super(InstrumentGPIB, self).__init__(parent)

        self._GPIBList = []
        self._instrumentCls = BaseInstrument
        self._instrumentArgs = None
        self._instrument = None
        self.currentIndexChanged.connect(self.changeInstrument)

        self.closeOnChange = True

        self.refreshGPIBList()


    def refreshGPIBList(self):
        self.blockSignals(True)
        gpiblist = rm.list_resources()
        self.clear()

        self._GPIBList = [str(i) for i in gpiblist]

        self.addItem("None")

        self.addItems(self._GPIBList)
        self.addItem("Fake")
        self.addItem("Refresh...")

        self.blockSignals(False)

    def changeInstrument(self):
        if str(self.currentText()) == "None":
            self.closeInstrument()
            return

        if str(self.currentText())=="Refresh...":
            self.refreshGPIBList()
            return
        self.closeInstrument()

        try:
            if self._instrumentArgs is None or not self._instrumentArgs:
                inst = self._instrumentCls(str(self.currentText()))
            else:
                inst = self._instrumentCls(str(self.currentText()), *self._instrumentArgs)

        except Exception as e:
            print "Warning, unable to open desired instrument"
            print "\t",e
            print "cls/args:", self._instrumentCls, self._instrumentArgs
            self.setCurrentIndex(self.findData("Fake"))
            return

        self._instrument = weakref.ref(inst)
        self.sigInstrumentOpened.emit(inst)

    def closeInstrument(self):
        if self.closeOnChange and self._instrument is not None:
            try:
                self._instrument().close()
                self.sigInstrumentClosed.emit()
            except Exception as e:
                print "Error closing instrument", e


    def setHoverText(self, text=""):
        self.setToolTip(str(text))

    def setInstrumentClass(self, cls=BaseInstrument, *args):
        self._instrumentCls = cls
        if args:
            self.setInstrumentArgs(args)

    def setInstrumentArgs(self, *args):
        self._instrumentArgs = args


if __name__ == '__main__':
    app = QtGui.QApplication([])

    wid = InstrumentGPIB()
    wid.setHoverText("This is text")
    from NewportMotorDriver import esp300 as e
    from Instruments import Agilent6000 as a

    wid.setInstrumentClass(a)
    wid.show()
    app.exec_()



