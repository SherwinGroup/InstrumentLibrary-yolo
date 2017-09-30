# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\MotorDriver\wiregridcal.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(664, 417)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.wMotor = MotorWindow(self.centralwidget)
        self.wMotor.setObjectName("wMotor")
        self.verticalLayout.addWidget(self.wMotor)
        self.wTK = TKWid(self.centralwidget)
        self.wTK.setObjectName("wTK")
        self.verticalLayout.addWidget(self.wTK)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.bSaveDir = QtWidgets.QPushButton(self.centralwidget)
        self.bSaveDir.setObjectName("bSaveDir")
        self.horizontalLayout.addWidget(self.bSaveDir)
        self.bStartSweep = QtWidgets.QPushButton(self.centralwidget)
        self.bStartSweep.setCheckable(True)
        self.bStartSweep.setObjectName("bStartSweep")
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

