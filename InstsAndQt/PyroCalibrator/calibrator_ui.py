# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\PyroCalibrator\calibrator.ui'
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

class Ui_PyroCalibration(object):
    def setupUi(self, PyroCalibration):
        PyroCalibration.setObjectName("PyroCalibration")
        PyroCalibration.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(PyroCalibration)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(self.tab)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.pyroWid = OscWid(self.splitter)
        self.pyroWid.setObjectName("pyroWid")
        self.TKWid = TKWid(self.splitter)
        self.TKWid.setObjectName("TKWid")
        self.horizontalLayout.addWidget(self.splitter)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gRatio = PlotWidget(self.tab_2)
        self.gRatio.setObjectName("gRatio")
        self.verticalLayout_2.addWidget(self.gRatio)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.bCal = QtWidgets.QPushButton(self.tab_2)
        self.bCal.setCheckable(True)
        self.bCal.setObjectName("bCal")
        self.horizontalLayout_3.addWidget(self.bCal)
        self.bClear = QtWidgets.QPushButton(self.tab_2)
        self.bClear.setObjectName("bClear")
        self.horizontalLayout_3.addWidget(self.bClear)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.bDoublePause = QtWidgets.QPushButton(self.centralwidget)
        self.bDoublePause.setCheckable(True)
        self.bDoublePause.setChecked(True)
        self.bDoublePause.setFlat(False)
        self.bDoublePause.setObjectName("bDoublePause")
        self.horizontalLayout_2.addWidget(self.bDoublePause)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        PyroCalibration.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PyroCalibration)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        PyroCalibration.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(PyroCalibration)
        self.statusbar.setObjectName("statusbar")
        PyroCalibration.setStatusBar(self.statusbar)

        self.retranslateUi(PyroCalibration)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PyroCalibration)

    def retranslateUi(self, PyroCalibration):
        PyroCalibration.setWindowTitle(_translate("PyroCalibration", "Pyro Calibrator", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("PyroCalibration", "Scope Traces", None))
        self.bCal.setText(_translate("PyroCalibration", "Calibrate", None))
        self.bClear.setText(_translate("PyroCalibration", "Clear", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PyroCalibration", "Calibration", None))
        self.bDoublePause.setText(_translate("PyroCalibration", "Pause Both", None))

from InstsAndQt.PyroOscope.OscWid import OscWid

from InstsAndQt.TKOscope.TKWid import TKWid

from pyqtgraph import PlotWidget

