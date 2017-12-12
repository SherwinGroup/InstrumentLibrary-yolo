# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\ThorlabsRotationStage\UIs\thorlabsPanel.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ThorlabsPanel(object):
    def setupUi(self, ThorlabsPanel):
        ThorlabsPanel.setObjectName("ThorlabsPanel")
        ThorlabsPanel.resize(382, 77)
        self.verticalLayout = QtWidgets.QVBoxLayout(ThorlabsPanel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lPos = QtWidgets.QLabel(ThorlabsPanel)
        self.lPos.setObjectName("lPos")
        self.horizontalLayout.addWidget(self.lPos)
        self.sbPosition = SpinBox(ThorlabsPanel)
        self.sbPosition.setMinimumSize(QtCore.QSize(75, 0))
        self.sbPosition.setObjectName("sbPosition")
        self.horizontalLayout.addWidget(self.sbPosition)
        self.labelMoving = QtWidgets.QLabel(ThorlabsPanel)
        self.labelMoving.setObjectName("labelMoving")
        self.horizontalLayout.addWidget(self.labelMoving)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.bOpen = QtWidgets.QPushButton(ThorlabsPanel)
        self.bOpen.setCheckable(True)
        self.bOpen.setFlat(False)
        self.bOpen.setObjectName("bOpen")
        self.horizontalLayout_2.addWidget(self.bOpen)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.bGoHome = QtWidgets.QPushButton(ThorlabsPanel)
        self.bGoHome.setObjectName("bGoHome")
        self.horizontalLayout_2.addWidget(self.bGoHome)
        self.bSettings = QtWidgets.QToolButton(ThorlabsPanel)
        self.bSettings.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.bSettings.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.bSettings.setAutoRaise(False)
        self.bSettings.setArrowType(QtCore.Qt.DownArrow)
        self.bSettings.setObjectName("bSettings")
        self.horizontalLayout_2.addWidget(self.bSettings)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi(ThorlabsPanel)
        QtCore.QMetaObject.connectSlotsByName(ThorlabsPanel)

    def retranslateUi(self, ThorlabsPanel):
        _translate = QtCore.QCoreApplication.translate
        ThorlabsPanel.setWindowTitle(_translate("ThorlabsPanel", "K10CR1 Panel"))
        self.lPos.setText(_translate("ThorlabsPanel", "Motor Position (°)"))
        self.labelMoving.setText(_translate("ThorlabsPanel", "Ready"))
        self.bOpen.setText(_translate("ThorlabsPanel", "Open"))
        self.bGoHome.setText(_translate("ThorlabsPanel", "Goto Home"))
        self.bSettings.setText(_translate("ThorlabsPanel", "..."))

from pyqtgraph import SpinBox
