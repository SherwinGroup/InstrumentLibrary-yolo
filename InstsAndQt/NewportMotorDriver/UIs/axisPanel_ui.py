# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\FELLab\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\NewportMotorDriver\UIs\axisPanel.ui'
#
# Created: Wed Feb 24 11:27:32 2016
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

class Ui_ESPAxisPanel(object):
    def setupUi(self, ESPAxisPanel):
        ESPAxisPanel.setObjectName(_fromUtf8("ESPAxisPanel"))
        ESPAxisPanel.resize(409, 88)
        self.verticalLayout = QtGui.QVBoxLayout(ESPAxisPanel)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lPos = QtGui.QLabel(ESPAxisPanel)
        self.lPos.setObjectName(_fromUtf8("lPos"))
        self.horizontalLayout.addWidget(self.lPos)
        self.sbPosition = SpinBox(ESPAxisPanel)
        self.sbPosition.setObjectName(_fromUtf8("sbPosition"))
        self.horizontalLayout.addWidget(self.sbPosition)
        self.labelMoving = QtGui.QLabel(ESPAxisPanel)
        self.labelMoving.setObjectName(_fromUtf8("labelMoving"))
        self.horizontalLayout.addWidget(self.labelMoving)
        self.lAxis = QtGui.QLabel(ESPAxisPanel)
        self.lAxis.setObjectName(_fromUtf8("lAxis"))
        self.horizontalLayout.addWidget(self.lAxis)
        self.sbAxis = QtGui.QSpinBox(ESPAxisPanel)
        self.sbAxis.setMinimum(1)
        self.sbAxis.setMaximum(3)
        self.sbAxis.setObjectName(_fromUtf8("sbAxis"))
        self.horizontalLayout.addWidget(self.sbAxis)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.lOn = QtGui.QLabel(ESPAxisPanel)
        self.lOn.setObjectName(_fromUtf8("lOn"))
        self.horizontalLayout_2.addWidget(self.lOn)
        self.cbOn = QtGui.QCheckBox(ESPAxisPanel)
        self.cbOn.setText(_fromUtf8(""))
        self.cbOn.setObjectName(_fromUtf8("cbOn"))
        self.horizontalLayout_2.addWidget(self.cbOn)
        self.bSetHome = QtGui.QPushButton(ESPAxisPanel)
        self.bSetHome.setObjectName(_fromUtf8("bSetHome"))
        self.horizontalLayout_2.addWidget(self.bSetHome)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi(ESPAxisPanel)
        QtCore.QMetaObject.connectSlotsByName(ESPAxisPanel)

    def retranslateUi(self, ESPAxisPanel):
        ESPAxisPanel.setWindowTitle(_translate("ESPAxisPanel", "Form", None))
        self.lPos.setText(_translate("ESPAxisPanel", "Motor Position (°)", None))
        self.labelMoving.setText(_translate("ESPAxisPanel", "Ready", None))
        self.lAxis.setText(_translate("ESPAxisPanel", "Motor Axis", None))
        self.lOn.setText(_translate("ESPAxisPanel", "Motor On", None))
        self.bSetHome.setText(_translate("ESPAxisPanel", "Set Home", None))

from pyqtgraph import SpinBox
