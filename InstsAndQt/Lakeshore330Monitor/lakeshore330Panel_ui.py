# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\Lakeshore330Monitor\lakeshore330Panel.ui'
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
        MainWindow.resize(255, 271)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1, 1))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(1, 1))
        self.centralwidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.gTemp = PlotWidget(self.splitter)
        self.gTemp.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gTemp.sizePolicy().hasHeightForWidth())
        self.gTemp.setSizePolicy(sizePolicy)
        self.gTemp.setMinimumSize(QtCore.QSize(1, 1))
        self.gTemp.setSizeIncrement(QtCore.QSize(1, 1))
        self.gTemp.setObjectName("gTemp")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.tTemp = QtWidgets.QLineEdit(self.layoutWidget)
        self.tTemp.setReadOnly(True)
        self.tTemp.setObjectName("tTemp")
        self.horizontalLayout_4.addWidget(self.tTemp)
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.sbSetpoint = SpinBox(self.layoutWidget)
        self.sbSetpoint.setObjectName("sbSetpoint")
        self.horizontalLayout_4.addWidget(self.sbSetpoint)
        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 10)
        self.horizontalLayout_4.setStretch(2, 100)
        self.horizontalLayout_4.setStretch(3, 1)
        self.horizontalLayout_4.setStretch(4, 10)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pHeater = QtWidgets.QProgressBar(self.layoutWidget)
        self.pHeater.setProperty("value", 38)
        self.pHeater.setTextVisible(True)
        self.pHeater.setOrientation(QtCore.Qt.Horizontal)
        self.pHeater.setInvertedAppearance(False)
        self.pHeater.setTextDirection(QtWidgets.QProgressBar.BottomToTop)
        self.pHeater.setObjectName("pHeater")
        self.horizontalLayout_5.addWidget(self.pHeater)
        self.cbHeater = QtWidgets.QComboBox(self.layoutWidget)
        self.cbHeater.setObjectName("cbHeater")
        self.cbHeater.addItem("")
        self.cbHeater.addItem("")
        self.cbHeater.addItem("")
        self.cbHeater.addItem("")
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

