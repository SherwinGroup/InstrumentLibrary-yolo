# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Public\Documents\Github\InstrumentLibrary-yolo\InstsAndQt\SR830Polarimetry\SR830Polar.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SR830PolMeasure(object):
    def setupUi(self, SR830PolMeasure):
        SR830PolMeasure.setObjectName("SR830PolMeasure")
        SR830PolMeasure.resize(713, 600)
        self.centralwidget = QtWidgets.QWidget(SR830PolMeasure)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gPolaragram = PlotWidget(self.centralwidget)
        self.gPolaragram.setObjectName("gPolaragram")
        self.verticalLayout.addWidget(self.gPolaragram)
        self.wK10CR1 = K10CR1Panel(self.centralwidget)
        self.wK10CR1.setObjectName("wK10CR1")
        self.verticalLayout.addWidget(self.wK10CR1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cbGPIB = InstrumentGPIB(self.groupBox)
        self.cbGPIB.setObjectName("cbGPIB")
        self.horizontalLayout_2.addWidget(self.cbGPIB)
        self.horizontalLayout.addWidget(self.groupBox)
        self.bStart = QtWidgets.QPushButton(self.centralwidget)
        self.bStart.setCheckable(True)
        self.bStart.setObjectName("bStart")
        self.horizontalLayout.addWidget(self.bStart)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 10)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        SR830PolMeasure.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SR830PolMeasure)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 713, 38))
        self.menubar.setObjectName("menubar")
        SR830PolMeasure.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SR830PolMeasure)
        self.statusbar.setObjectName("statusbar")
        SR830PolMeasure.setStatusBar(self.statusbar)

        self.retranslateUi(SR830PolMeasure)
        QtCore.QMetaObject.connectSlotsByName(SR830PolMeasure)

    def retranslateUi(self, SR830PolMeasure):
        _translate = QtCore.QCoreApplication.translate
        SR830PolMeasure.setWindowTitle(_translate("SR830PolMeasure", "Lock-in Polarimetry"))
        self.groupBox.setTitle(_translate("SR830PolMeasure", "GPIB"))
        self.bStart.setText(_translate("SR830PolMeasure", "Start"))

from InstsAndQt.ThorlabsCageRotator.K10CR1Panel import K10CR1Panel
from InstsAndQt.instrumentgpib import InstrumentGPIB
from pyqtgraph import PlotWidget
