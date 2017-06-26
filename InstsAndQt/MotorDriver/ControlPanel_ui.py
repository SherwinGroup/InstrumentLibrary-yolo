# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\MotorDriver-cloaked\ControlPanel.ui'
#
# Created: Fri Apr 17 15:03:08 2015
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(716, 455)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.slideCurrent = QtGui.QSlider(self.groupBox)
        self.slideCurrent.setProperty("value", 0)
        self.slideCurrent.setSliderPosition(0)
        self.slideCurrent.setTracking(True)
        self.slideCurrent.setOrientation(QtCore.Qt.Horizontal)
        self.slideCurrent.setInvertedAppearance(False)
        self.slideCurrent.setInvertedControls(False)
        self.slideCurrent.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slideCurrent.setTickInterval(5)
        self.slideCurrent.setObjectName(_fromUtf8("slideCurrent"))
        self.horizontalLayout.addWidget(self.slideCurrent)
        self.sbCurrent = SpinBox(self.groupBox)
        self.sbCurrent.setMaximum(100)
        self.sbCurrent.setObjectName(_fromUtf8("sbCurrent"))
        self.horizontalLayout.addWidget(self.sbCurrent)
        self.horizontalLayout.setStretch(0, 5)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_5 = QtGui.QGroupBox(Form)
        self.groupBox_5.setFlat(True)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.slideStepRate = QtGui.QSlider(self.groupBox_5)
        self.slideStepRate.setMaximum(700)
        self.slideStepRate.setProperty("value", 0)
        self.slideStepRate.setSliderPosition(0)
        self.slideStepRate.setTracking(True)
        self.slideStepRate.setOrientation(QtCore.Qt.Horizontal)
        self.slideStepRate.setInvertedAppearance(False)
        self.slideStepRate.setInvertedControls(False)
        self.slideStepRate.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slideStepRate.setTickInterval(25)
        self.slideStepRate.setObjectName(_fromUtf8("slideStepRate"))
        self.horizontalLayout_5.addWidget(self.slideStepRate)
        self.sbStepRate = SpinBox(self.groupBox_5)
        self.sbStepRate.setMaximum(100)
        self.sbStepRate.setObjectName(_fromUtf8("sbStepRate"))
        self.horizontalLayout_5.addWidget(self.sbStepRate)
        self.horizontalLayout_5.setStretch(0, 5)
        self.horizontalLayout_5.setStretch(1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_5)
        self.horizontalLayout_6.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_2 = QtGui.QGroupBox(Form)
        self.groupBox_2.setFlat(True)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tVoltage = QtGui.QLineEdit(self.groupBox_2)
        self.tVoltage.setObjectName(_fromUtf8("tVoltage"))
        self.horizontalLayout_2.addWidget(self.tVoltage)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(Form)
        self.groupBox_3.setFlat(True)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.tWA = QtGui.QLineEdit(self.groupBox_3)
        self.tWA.setObjectName(_fromUtf8("tWA"))
        self.horizontalLayout_3.addWidget(self.tWA)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox_4 = QtGui.QGroupBox(Form)
        self.groupBox_4.setFlat(True)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.tWB = QtGui.QLineEdit(self.groupBox_4)
        self.tWB.setObjectName(_fromUtf8("tWB"))
        self.horizontalLayout_4.addWidget(self.tWB)
        self.verticalLayout.addWidget(self.groupBox_4)
        self.horizontalLayout_6.addLayout(self.verticalLayout)
        self.horizontalLayout_6.setStretch(0, 10)
        self.horizontalLayout_6.setStretch(1, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.bOK = QtGui.QPushButton(Form)
        self.bOK.setObjectName(_fromUtf8("bOK"))
        self.horizontalLayout_7.addWidget(self.bOK)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.verticalLayout_3.setStretch(0, 10)
        self.verticalLayout_3.setStretch(1, 100)
        self.verticalLayout_3.setStretch(2, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Motor Control", None))
        self.groupBox.setTitle(_translate("Form", "Set Current", None))
        self.groupBox_5.setTitle(_translate("Form", "Step Rate", None))
        self.groupBox_2.setTitle(_translate("Form", "Voltage", None))
        self.groupBox_3.setTitle(_translate("Form", "Winding A (A)", None))
        self.groupBox_4.setTitle(_translate("Form", "Winding B (A)", None))
        self.bOK.setText(_translate("Form", "OK", None))

from pyqtgraph import SpinBox
