from PyQt5 import QtCore, QtGui, QtWidgets
from InstsAndQt.customQt import *
import numpy as np
import pyqtgraph
import visa

from InstsAndQt.NewportMotorDriver.UIs.espPanel_ui import Ui_ESPPanel
from InstsAndQt.NewportMotorDriver.espAxisPanel import ESPAxisPanel
# from .UIs.espPanel_ui import Ui_ESPPanel
# from .espAxisPanel import ESPAxisPanel




class ESPMainPanel(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super(ESPMainPanel, self).__init__(parent)
        self.initUI()
        self.detHWPWidget = None
        # reference to all motor axes added
        self.motorAxes = []
        self.addMotorAxes()

    def initUI(self):
        self.ui = Ui_ESPPanel()
        self.ui.setupUi(self)


        try:
            self.ui.cbGPIB.setAddress("GPIB0::2::INSTR")
        except RuntimeError:
            self.ui.cbGPIB.setAddress("Fake")

        self.ui.cbGPIB.currentIndexChanged.connect(self.updateGPIB)
        self.ui.bErrors.clicked.connect(self.displayErrors)

        self.errorWindow = QtWidgets.QPlainTextEdit()
        self.errorWindow.setReadOnly(True)
        self.errorWindow.setWindowTitle("ESP Error Log")

        self.show()


    def updateGPIB(self):
        if str(self.ui.cbGPIB.currentText()) in ["None", "Refresh..."]  :
            ## What's the safest thing to do here...?
            return
        for axis in self.motorAxes:
            axis.GPIB = str(self.ui.cbGPIB.currentText())
            axis.openESPAxis(axis=int(self.axis.ui.sbAxis.value()))

    def addMotorAxes(self):
        """
        Adds all the motor axes. This is the function to
        modify when you add a enw motor axis
        :return:
        """

        detHWPgroupbox = QtWidgets.QGroupBox("Detector Half Wave Plate")
        detHWPgroupbox.setFlat(True)
        detHWPgbLayout = QtWidgets.QVBoxLayout(detHWPgroupbox)
        self.detHWPWidget = ESPAxisPanel(parent=self,
                                         GPIB=str(self.ui.cbGPIB.currentText()),
                                         axis=2)
        self.detHWPWidget.sigErrorsEncountered.connect(self.updateInstrumentErrors)
        self.motorAxes.append(self.detHWPWidget)
        detHWPgbLayout.addWidget(self.detHWPWidget)
        detHWPgroupbox.setLayout(detHWPgbLayout)

        self.ui.layoutAxes.addWidget(detHWPgroupbox)

    def updateInstrumentErrors(self, err):
        self.errorWindow.appendPlainText(err)

        self.ui.bErrors.setStyleSheet("QPushButton { background-color : Red; color : black; }")

    def displayErrors(self):
        self.ui.bErrors.setStyleSheet("")
        self.errorWindow.show()
        self.errorWindow.raise_()






if __name__ == "__main__":
    import sys


    e = QtWidgets.QApplication(sys.argv)
    win = ESPMainPanel()
    sys.exit(e.exec_())
