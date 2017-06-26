# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\OscilloscopeCollection\singleChannel.ui'
#
# Created: Wed May 27 14:35:31 2015
#      by: PyQt4 UI code generator 4.10.4
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
        Form.resize(583, 525)
        self.horizontalLayout_8 = QtGui.QHBoxLayout(Form)
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.splitter = QtGui.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.gPlot = PlotWidget(self.splitter)
        self.gPlot.setObjectName(_fromUtf8("gPlot"))
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(self.widget)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tBGStart = QFNumberEdit(self.groupBox)
        self.tBGStart.setObjectName(_fromUtf8("tBGStart"))
        self.horizontalLayout.addWidget(self.tBGStart)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.bInit = QtGui.QPushButton(self.widget)
        self.bInit.setObjectName(_fromUtf8("bInit"))
        self.gridLayout.addWidget(self.bInit, 0, 3, 1, 1)
        self.groupBox_4 = QtGui.QGroupBox(self.widget)
        self.groupBox_4.setFlat(True)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_4.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.tSGEnd = QFNumberEdit(self.groupBox_4)
        self.tSGEnd.setObjectName(_fromUtf8("tSGEnd"))
        self.horizontalLayout_4.addWidget(self.tSGEnd)
        self.gridLayout.addWidget(self.groupBox_4, 1, 1, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.widget)
        self.groupBox_3.setFlat(True)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.tSGStart = QFNumberEdit(self.groupBox_3)
        self.tSGStart.setObjectName(_fromUtf8("tSGStart"))
        self.horizontalLayout_3.addWidget(self.tSGStart)
        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.widget)
        self.groupBox_2.setFlat(True)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tBGEnd = QFNumberEdit(self.groupBox_2)
        self.tBGEnd.setObjectName(_fromUtf8("tBGEnd"))
        self.horizontalLayout_2.addWidget(self.tBGEnd)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 1, 1)
        self.groupBox_5 = QtGui.QGroupBox(self.widget)
        self.groupBox_5.setEnabled(False)
        self.groupBox_5.setFlat(True)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_5.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.tBGBoxcar = QFNumberEdit(self.groupBox_5)
        self.tBGBoxcar.setObjectName(_fromUtf8("tBGBoxcar"))
        self.horizontalLayout_5.addWidget(self.tBGBoxcar)
        self.gridLayout.addWidget(self.groupBox_5, 0, 2, 1, 1)
        self.groupBox_6 = QtGui.QGroupBox(self.widget)
        self.groupBox_6.setEnabled(False)
        self.groupBox_6.setFlat(True)
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_6.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.tSGBoxcar = QFNumberEdit(self.groupBox_6)
        self.tSGBoxcar.setObjectName(_fromUtf8("tSGBoxcar"))
        self.horizontalLayout_6.addWidget(self.tSGBoxcar)
        self.gridLayout.addWidget(self.groupBox_6, 1, 2, 1, 1)
        self.groupBox_7 = QtGui.QGroupBox(self.widget)
        self.groupBox_7.setFlat(True)
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_7.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.cSave = QtGui.QCheckBox(self.groupBox_7)
        self.cSave.setText(_fromUtf8(""))
        self.cSave.setChecked(True)
        self.cSave.setObjectName(_fromUtf8("cSave"))
        self.horizontalLayout_7.addWidget(self.cSave)
        self.gridLayout.addWidget(self.groupBox_7, 1, 3, 1, 1)
        self.horizontalLayout_8.addWidget(self.splitter)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.groupBox.setTitle(_translate("Form", "BG Start", None))
        self.tBGStart.setText(_translate("Form", "0", None))
        self.bInit.setText(_translate("Form", "Initialize", None))
        self.groupBox_4.setTitle(_translate("Form", "Sig End", None))
        self.tSGEnd.setText(_translate("Form", "0", None))
        self.groupBox_3.setTitle(_translate("Form", "Sig Start", None))
        self.tSGStart.setText(_translate("Form", "0", None))
        self.groupBox_2.setTitle(_translate("Form", "BG End", None))
        self.tBGEnd.setText(_translate("Form", "0", None))
        self.groupBox_5.setTitle(_translate("Form", "Value:", None))
        self.groupBox_6.setTitle(_translate("Form", "Value:", None))
        self.groupBox_7.setTitle(_translate("Form", "Save?", None))

from pyqtgraph import PlotWidget
from InstsAndQt.customQt import QFNumberEdit
