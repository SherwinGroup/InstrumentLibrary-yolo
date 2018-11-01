# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Public\Documents\Github\InstrumentLibrary-yolo\InstsAndQt\PIDelayStage\UIs\piPanel.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PIPanel(object):
    def setupUi(self, PIPanel):
        PIPanel.setObjectName("PIPanel")
        PIPanel.resize(469, 163)
        self.verticalLayout = QtWidgets.QVBoxLayout(PIPanel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lPos = QtWidgets.QLabel(PIPanel)
        self.lPos.setObjectName("lPos")
        self.horizontalLayout.addWidget(self.lPos)
        self.sbPosition = SpinBox(PIPanel)
        self.sbPosition.setMinimumSize(QtCore.QSize(75, 0))
        self.sbPosition.setMaximum(10000)
        self.sbPosition.setObjectName("sbPosition")
        self.horizontalLayout.addWidget(self.sbPosition)
        self.labelMoving = QtWidgets.QLabel(PIPanel)
        self.labelMoving.setObjectName("labelMoving")
        self.horizontalLayout.addWidget(self.labelMoving)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_31 = QtWidgets.QGroupBox(PIPanel)
        self.groupBox_31.setFlat(True)
        self.groupBox_31.setObjectName("groupBox_31")
        self.horizontalLayout_29 = QtWidgets.QHBoxLayout(self.groupBox_31)
        self.horizontalLayout_29.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_29.setObjectName("horizontalLayout_29")
        self.cGPIB = InstrumentGPIB(self.groupBox_31)
        self.cGPIB.setObjectName("cGPIB")
        self.horizontalLayout_29.addWidget(self.cGPIB)
        self.horizontalLayout_2.addWidget(self.groupBox_31)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.bGoHome = QtWidgets.QPushButton(PIPanel)
        self.bGoHome.setObjectName("bGoHome")
        self.horizontalLayout_2.addWidget(self.bGoHome)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(17, 3, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi(PIPanel)
        QtCore.QMetaObject.connectSlotsByName(PIPanel)

    def retranslateUi(self, PIPanel):
        _translate = QtCore.QCoreApplication.translate
        PIPanel.setWindowTitle(_translate("PIPanel", "PI Delay Panel"))
        self.lPos.setText(_translate("PIPanel", "Position (fs)"))
        self.labelMoving.setText(_translate("PIPanel", "Ready"))
        self.groupBox_31.setTitle(_translate("PIPanel", "GPIB"))
        self.cGPIB.setToolTip(_translate("PIPanel", "GPIB0::5::INSTR"))
        self.bGoHome.setText(_translate("PIPanel", "Goto Home"))

from InstsAndQt.instrumentgpib import InstrumentGPIB
from pyqtgraph import SpinBox
