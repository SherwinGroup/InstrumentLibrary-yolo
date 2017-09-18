# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\FELLab\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\NewportMotorDriver\UIs\espPanel.ui'
#
# Created: Fri Sep 01 16:42:51 2017
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ESPPanel(object):
    def setupUi(self, ESPPanel):
        ESPPanel.setObjectName(_fromUtf8("ESPPanel"))
        ESPPanel.resize(634, 157)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(ESPPanel)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.layoutAxes = QtGui.QVBoxLayout()
        self.layoutAxes.setObjectName(_fromUtf8("layoutAxes"))
        self.verticalLayout.addLayout(self.layoutAxes)
        self.groupBox = QtGui.QGroupBox(ESPPanel)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cbGPIB = InstrumentGPIB(self.groupBox)
        self.cbGPIB.setObjectName(_fromUtf8("cbGPIB"))
        self.horizontalLayout.addWidget(self.cbGPIB)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.bErrors = QtGui.QPushButton(self.groupBox)
        self.bErrors.setObjectName(_fromUtf8("bErrors"))
        self.horizontalLayout.addWidget(self.bErrors)
        self.verticalLayout.addWidget(self.groupBox)
        self.verticalLayout.setStretch(0, 10)
        self.verticalLayout.setStretch(1, 1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(ESPPanel)
        QtCore.QMetaObject.connectSlotsByName(ESPPanel)

    def retranslateUi(self, ESPPanel):
        ESPPanel.setWindowTitle(_translate("ESPPanel", "ESP300 Panel", None))
        self.groupBox.setTitle(_translate("ESPPanel", "GPIB", None))
        self.bErrors.setText(_translate("ESPPanel", "Errors", None))

from InstsAndQt.instrumentgpib import InstrumentGPIB
