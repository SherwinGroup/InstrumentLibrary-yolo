# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\Darren\Python\junk\lakeshore330Panel.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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
        Form.resize(305, 289)
        self.horizontalLayout_6 = QtGui.QHBoxLayout(Form)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.splitter = QtGui.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setHandleWidth(2)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gTemp = PlotWidget(self.verticalLayoutWidget_2)
        self.gTemp.setEnabled(True)
        self.gTemp.setMinimumSize(QtCore.QSize(0, 1))
        self.gTemp.setObjectName(_fromUtf8("gTemp"))
        self.verticalLayout_2.addWidget(self.gTemp)
        self.verticalLayout_2.setStretch(0, 1000)
        self.verticalLayoutWidget = QtGui.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_4.addWidget(self.label)
        self.tTemp = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.tTemp.setReadOnly(True)
        self.tTemp.setObjectName(_fromUtf8("tTemp"))
        self.horizontalLayout_4.addWidget(self.tTemp)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_4.addWidget(self.label_2)
        self.sbSetpoint = SpinBox(self.verticalLayoutWidget)
        self.sbSetpoint.setObjectName(_fromUtf8("sbSetpoint"))
        self.horizontalLayout_4.addWidget(self.sbSetpoint)
        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 10)
        self.horizontalLayout_4.setStretch(2, 100)
        self.horizontalLayout_4.setStretch(3, 1)
        self.horizontalLayout_4.setStretch(4, 10)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.pHeater = QtGui.QProgressBar(self.verticalLayoutWidget)
        self.pHeater.setProperty("value", 38)
        self.pHeater.setTextVisible(True)
        self.pHeater.setOrientation(QtCore.Qt.Horizontal)
        self.pHeater.setInvertedAppearance(False)
        self.pHeater.setTextDirection(QtGui.QProgressBar.BottomToTop)
        self.pHeater.setObjectName(_fromUtf8("pHeater"))
        self.horizontalLayout_5.addWidget(self.pHeater)
        self.cbHeater = QtGui.QComboBox(self.verticalLayoutWidget)
        self.cbHeater.setObjectName(_fromUtf8("cbHeater"))
        self.cbHeater.addItem(_fromUtf8(""))
        self.cbHeater.addItem(_fromUtf8(""))
        self.cbHeater.addItem(_fromUtf8(""))
        self.cbHeater.addItem(_fromUtf8(""))
        self.horizontalLayout_5.addWidget(self.cbHeater)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6.addWidget(self.splitter)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "Sample Temp (K):  ", None))
        self.label_2.setText(_translate("Form", "Setpoint (K):  ", None))
        self.cbHeater.setItemText(0, _translate("Form", "Off", None))
        self.cbHeater.setItemText(1, _translate("Form", "Low", None))
        self.cbHeater.setItemText(2, _translate("Form", "Medium", None))
        self.cbHeater.setItemText(3, _translate("Form", "High", None))

from pyqtgraph import PlotWidget, SpinBox
