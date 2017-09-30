# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\FELLab\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\NewportMotorDriver\UIs\espPanel.ui'
#
# Created: Fri Sep 01 16:42:51 2017
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig)

class Ui_ESPPanel(object):
    def setupUi(self, ESPPanel):
        ESPPanel.setObjectName("ESPPanel")
        ESPPanel.resize(634, 157)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(ESPPanel)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.layoutAxes = QtWidgets.QVBoxLayout()
        self.layoutAxes.setObjectName("layoutAxes")
        self.verticalLayout.addLayout(self.layoutAxes)
        self.groupBox = QtWidgets.QGroupBox(ESPPanel)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cbGPIB = InstrumentGPIB(self.groupBox)
        self.cbGPIB.setObjectName("cbGPIB")
        self.horizontalLayout.addWidget(self.cbGPIB)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.bErrors = QtWidgets.QPushButton(self.groupBox)
        self.bErrors.setObjectName("bErrors")
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

