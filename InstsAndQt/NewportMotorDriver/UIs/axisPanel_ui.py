# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\FELLab\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\NewportMotorDriver\UIs\axisPanel.ui'
#
# Created: Wed Apr 13 10:35:41 2016
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

class Ui_ESPAxisPanel(object):
    def setupUi(self, ESPAxisPanel):
        ESPAxisPanel.setObjectName("ESPAxisPanel")
        ESPAxisPanel.resize(409, 77)
        self.verticalLayout = QtWidgets.QVBoxLayout(ESPAxisPanel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lPos = QtWidgets.QLabel(ESPAxisPanel)
        self.lPos.setObjectName("lPos")
        self.horizontalLayout.addWidget(self.lPos)
        self.sbPosition = SpinBox(ESPAxisPanel)
        self.sbPosition.setObjectName("sbPosition")
        self.horizontalLayout.addWidget(self.sbPosition)
        self.labelMoving = QtWidgets.QLabel(ESPAxisPanel)
        self.labelMoving.setObjectName("labelMoving")
        self.horizontalLayout.addWidget(self.labelMoving)
        self.lAxis = QtWidgets.QLabel(ESPAxisPanel)
        self.lAxis.setObjectName("lAxis")
        self.horizontalLayout.addWidget(self.lAxis)
        self.sbAxis = QtWidgets.QSpinBox(ESPAxisPanel)
        self.sbAxis.setMinimum(1)
        self.sbAxis.setMaximum(3)
        self.sbAxis.setObjectName("sbAxis")
        self.horizontalLayout.addWidget(self.sbAxis)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.lOn = QtWidgets.QLabel(ESPAxisPanel)
        self.lOn.setObjectName("lOn")
        self.horizontalLayout_2.addWidget(self.lOn)
        self.cbOn = QtWidgets.QCheckBox(ESPAxisPanel)
        self.cbOn.setText("")
        self.cbOn.setObjectName("cbOn")
        self.horizontalLayout_2.addWidget(self.cbOn)
        self.bSetPosition = QtWidgets.QPushButton(ESPAxisPanel)
        self.bSetPosition.setObjectName("bSetPosition")
        self.horizontalLayout_2.addWidget(self.bSetPosition)
        self.bGoHome = QtWidgets.QPushButton(ESPAxisPanel)
        self.bGoHome.setObjectName("bGoHome")
        self.horizontalLayout_2.addWidget(self.bGoHome)
        self.bSettings = QtWidgets.QPushButton(ESPAxisPanel)
        self.bSettings.setObjectName("bSettings")
        self.horizontalLayout_2.addWidget(self.bSettings)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi(ESPAxisPanel)
        QtCore.QMetaObject.connectSlotsByName(ESPAxisPanel)

    def retranslateUi(self, ESPAxisPanel):
        ESPAxisPanel.setWindowTitle(_translate("ESPAxisPanel", "Form", None))
        self.lPos.setText(_translate("ESPAxisPanel", "Motor Position (°)", None))
        self.labelMoving.setText(_translate("ESPAxisPanel", "Ready", None))
        self.lAxis.setText(_translate("ESPAxisPanel", "Motor Axis", None))
        self.lOn.setText(_translate("ESPAxisPanel", "Motor On", None))
        self.bSetPosition.setText(_translate("ESPAxisPanel", "Set Position", None))
        self.bGoHome.setText(_translate("ESPAxisPanel", "Goto Home", None))
        self.bSettings.setText(_translate("ESPAxisPanel", "Settings...", None))

from pyqtgraph import SpinBox

