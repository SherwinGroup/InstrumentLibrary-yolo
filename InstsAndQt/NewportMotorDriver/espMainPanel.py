from PyQt4 import QtCore, QtGui
from UIs.espPanel_ui import Ui_ESPPanel
from InstsAndQt.customQt import *
import numpy as np
import pyqtgraph
import visa

from espAxisPanel import ESPAxisPanel


class ESPMainPanel(QtGui.QWidget):

    def __init__(self, parent = None):
        super(ESPMainPanel, self).__init__(parent)
        self.initUI()

        self.detHWPWidget = None

        self.addMotorAxes()

    def initUI(self):
        self.ui = Ui_ESPPanel()
        self.ui.setupUi(self)

        try:
            rm = visa.ResourceManager()
            GPIBList = [i.encode('ascii') for i in rm.list_resources()]
            GPIBList.append('Fake')
        except Exception as e:
            # log.warning("Error loading GPIB list")
            print "Error loading GPIB list", e
            GPIBList = ['a', 'b', 'c', 'Fake']

        try:
            GPIBidx = GPIBList.index("GPIB0::2::INSTR")
        except ValueError:
            GPIBidx = GPIBList.index("Fake")

        self.ui.cbGPIB.addItems(GPIBList)
        self.ui.cbGPIB.setCurrentIndex(GPIBidx)

        self.ui.cbGPIB.currentIndexChanged.connect(self.updateGPIB)

        self.show()


    def updateGPIB(self):
        # readd the motor axes, having the
        # garbage collector remove old references
        self.addMotorAxes()


    def addMotorAxes(self):
        """
        Adds all the motor axes. This is the function to
        modify when you add a enw motor axis
        :return:
        """

        detHWPgroupbox = QtGui.QGroupBox("Detector Half Wave Plate")
        detHWPgbLayout = QtGui.QVBoxLayout(detHWPgroupbox)
        self.detHWPWidget = ESPAxisPanel(parent=self,
                                         GPIB=str(self.ui.cbGPIB.currentText()),
                                         axis=1)
        detHWPgbLayout.addWidget(self.detHWPWidget)
        detHWPgroupbox.setLayout(detHWPgbLayout)

        self.ui.layoutAxes.addWidget(detHWPgroupbox)





if __name__ == "__main__":
    import sys
    e = QtGui.QApplication(sys.argv)
    win = ESPMainPanel()
    sys.exit(e.exec_())