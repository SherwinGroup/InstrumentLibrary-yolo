# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\Lakeshore330Monitor\lakeshore330Panel.ui'
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
        MainWindow.resize(255, 271)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1, 1))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(1, 1))
        self.centralwidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.gTemp = PlotWidget(self.splitter)
        self.gTemp.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gTemp.sizePolicy().hasHeightForWidth())
        self.gTemp.setSizePolicy(sizePolicy)
        self.gTemp.setMinimumSize(QtCore.QSize(1, 1))
        self.gTemp.setSizeIncrement(QtCore.QSize(1, 1))
        self.gTemp.setObjectName(_fromUtf8("gTemp"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_4.addWidget(self.label)
        self.tTemp = QtGui.QLineEdit(self.layoutWidget)
        self.tTemp.setReadOnly(True)
        self.tTemp.setObjectName(_fromUtf8("tTemp"))
        self.horizontalLayout_4.addWidget(self.tTemp)
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_4.addWidget(self.label_2)
        self.sbSetpoint = SpinBox(self.layoutWidget)
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
        self.pHeater = QtGui.QProgressBar(self.layoutWidget)
        self.pHeater.setProperty("value", 38)
        self.pHeater.setTextVisible(True)
        self.pHeater.setOrientation(QtCore.Qt.Horizontal)
        self.pHeater.setInvertedAppearance(False)
        self.pHeater.setTextDirection(QtGui.QProgressBar.BottomToTop)
        self.pHeater.setObjectName(_fromUtf8("pHeater"))
        self.horizontalLayout_5.addWidget(self.pHeater)
        self.cbHeater = QtGui.QComboBox(self.layoutWidget)
        self.cbHeater.setObjectName(_fromUtf8("cbHeater"))
        self.cbHeater.addItem(_fromUtf8(""))
        self.cbHeater.addItem(_fromUtf8(""))
        self.cbHeater.addItem(_fromUtf8(""))
        self.cbHeater.addItem(_fromUtf8(""))
        self.horizontalLayout_5.addWidget(self.cbHeater)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Sample Monitor", None))
        self.label.setText(_translate("MainWindow", "Sample Temp (K):  ", None))
        self.label_2.setText(_translate("MainWindow", "Setpoint (K):  ", None))
        self.cbHeater.setItemText(0, _translate("MainWindow", "Off", None))
        self.cbHeater.setItemText(1, _translate("MainWindow", "Low", None))
        self.cbHeater.setItemText(2, _translate("MainWindow", "Medium", None))
        self.cbHeater.setItemText(3, _translate("MainWindow", "High", None))

from pyqtgraph import PlotWidget, SpinBox
