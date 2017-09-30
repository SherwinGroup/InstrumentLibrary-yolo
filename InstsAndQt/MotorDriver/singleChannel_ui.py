# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\OscilloscopeCollection\singleChannel.ui'
#
# Created: Wed May 27 14:35:31 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(583, 525)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.gPlot = PlotWidget(self.splitter)
        self.gPlot.setObjectName("gPlot")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tBGStart = QFNumberEdit(self.groupBox)
        self.tBGStart.setObjectName("tBGStart")
        self.horizontalLayout.addWidget(self.tBGStart)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.bInit = QtWidgets.QPushButton(self.widget)
        self.bInit.setObjectName("bInit")
        self.gridLayout.addWidget(self.bInit, 0, 3, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_4.setFlat(True)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_4.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tSGEnd = QFNumberEdit(self.groupBox_4)
        self.tSGEnd.setObjectName("tSGEnd")
        self.horizontalLayout_4.addWidget(self.tSGEnd)
        self.gridLayout.addWidget(self.groupBox_4, 1, 1, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_3.setFlat(True)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tSGStart = QFNumberEdit(self.groupBox_3)
        self.tSGStart.setObjectName("tSGStart")
        self.horizontalLayout_3.addWidget(self.tSGStart)
        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_2.setFlat(True)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tBGEnd = QFNumberEdit(self.groupBox_2)
        self.tBGEnd.setObjectName("tBGEnd")
        self.horizontalLayout_2.addWidget(self.tBGEnd)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_5.setEnabled(False)
        self.groupBox_5.setFlat(True)
        self.groupBox_5.setObjectName("groupBox_5")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_5.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tBGBoxcar = QFNumberEdit(self.groupBox_5)
        self.tBGBoxcar.setObjectName("tBGBoxcar")
        self.horizontalLayout_5.addWidget(self.tBGBoxcar)
        self.gridLayout.addWidget(self.groupBox_5, 0, 2, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_6.setEnabled(False)
        self.groupBox_6.setFlat(True)
        self.groupBox_6.setObjectName("groupBox_6")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_6.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.tSGBoxcar = QFNumberEdit(self.groupBox_6)
        self.tSGBoxcar.setObjectName("tSGBoxcar")
        self.horizontalLayout_6.addWidget(self.tSGBoxcar)
        self.gridLayout.addWidget(self.groupBox_6, 1, 2, 1, 1)
        self.groupBox_7 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_7.setFlat(True)
        self.groupBox_7.setObjectName("groupBox_7")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_7.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.cSave = QtWidgets.QCheckBox(self.groupBox_7)
        self.cSave.setText("")
        self.cSave.setChecked(True)
        self.cSave.setObjectName("cSave")
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

