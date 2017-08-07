# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\MotorDriver\wiregridcal.ui'
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(664, 417)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.wMotor = MotorWindow(self.centralwidget)
        self.wMotor.setObjectName(_fromUtf8("wMotor"))
        self.verticalLayout.addWidget(self.wMotor)
        self.wTK = TKWid(self.centralwidget)
        self.wTK.setObjectName(_fromUtf8("wTK"))
        self.verticalLayout.addWidget(self.wTK)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.bSaveDir = QtGui.QPushButton(self.centralwidget)
        self.bSaveDir.setObjectName(_fromUtf8("bSaveDir"))
        self.horizontalLayout.addWidget(self.bSaveDir)
        self.bStartSweep = QtGui.QPushButton(self.centralwidget)
        self.bStartSweep.setCheckable(True)
        self.bStartSweep.setObjectName(_fromUtf8("bStartSweep"))
        self.horizontalLayout.addWidget(self.bStartSweep)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 10)
        self.verticalLayout.setStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Wiregrid Calibrator", None))
        self.bSaveDir.setText(_translate("MainWindow", "Choose Save Dir", None))
        self.bStartSweep.setText(_translate("MainWindow", "Start TK Cal", None))

from InstsAndQt.MotorDriver.motorMain import MotorWindow
from InstsAndQt.TKOscope.TKWid import TKWid
