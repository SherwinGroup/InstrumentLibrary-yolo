# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\FELLab\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\NewportMotorDriver\UIs\espPanel.ui'
#
# Created: Wed Feb 24 10:23:48 2016
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
        ESPPanel.resize(634, 262)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(ESPPanel)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.layoutAxes = QtGui.QVBoxLayout()
        self.layoutAxes.setObjectName(_fromUtf8("layoutAxes"))
        self.verticalLayout.addLayout(self.layoutAxes)
        self.groupBox = QtGui.QGroupBox(ESPPanel)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cbGPIB = QtGui.QComboBox(self.groupBox)
        self.cbGPIB.setObjectName(_fromUtf8("cbGPIB"))
        self.horizontalLayout.addWidget(self.cbGPIB)
        self.verticalLayout.addWidget(self.groupBox)
        self.verticalLayout.setStretch(0, 10)
        self.verticalLayout.setStretch(1, 1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(ESPPanel)
        QtCore.QMetaObject.connectSlotsByName(ESPPanel)

    def retranslateUi(self, ESPPanel):
        ESPPanel.setWindowTitle(_translate("ESPPanel", "ESP300 Panel", None))
        self.groupBox.setTitle(_translate("ESPPanel", "GPIB", None))

