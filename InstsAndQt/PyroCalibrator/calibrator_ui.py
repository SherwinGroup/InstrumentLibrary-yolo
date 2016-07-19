# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\PyroCalibrator\calibrator.ui'
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

class Ui_PyroCalibration(object):
    def setupUi(self, PyroCalibration):
        PyroCalibration.setObjectName(_fromUtf8("PyroCalibration"))
        PyroCalibration.resize(800, 600)
        self.centralwidget = QtGui.QWidget(PyroCalibration)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.splitter = QtGui.QSplitter(self.tab)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.pyroWid = OscWid(self.splitter)
        self.pyroWid.setObjectName(_fromUtf8("pyroWid"))
        self.TKWid = TKWid(self.splitter)
        self.TKWid.setObjectName(_fromUtf8("TKWid"))
        self.horizontalLayout.addWidget(self.splitter)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gRatio = PlotWidget(self.tab_2)
        self.gRatio.setObjectName(_fromUtf8("gRatio"))
        self.verticalLayout_2.addWidget(self.gRatio)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.bCal = QtGui.QPushButton(self.tab_2)
        self.bCal.setCheckable(True)
        self.bCal.setObjectName(_fromUtf8("bCal"))
        self.horizontalLayout_3.addWidget(self.bCal)
        self.bClear = QtGui.QPushButton(self.tab_2)
        self.bClear.setObjectName(_fromUtf8("bClear"))
        self.horizontalLayout_3.addWidget(self.bClear)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.bDoublePause = QtGui.QPushButton(self.centralwidget)
        self.bDoublePause.setCheckable(True)
        self.bDoublePause.setChecked(True)
        self.bDoublePause.setFlat(False)
        self.bDoublePause.setObjectName(_fromUtf8("bDoublePause"))
        self.horizontalLayout_2.addWidget(self.bDoublePause)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        PyroCalibration.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(PyroCalibration)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        PyroCalibration.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(PyroCalibration)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
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
