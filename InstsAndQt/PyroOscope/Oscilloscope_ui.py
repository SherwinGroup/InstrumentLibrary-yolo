# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\dvalovcin\Documents\GitHub\InstrumentLibrary-yolo\InstsAndQt\PyroOscope\Oscilloscope.ui'
#
# Created: Wed Jan 13 12:48:10 2016
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

class Ui_Oscilloscope(object):
    def setupUi(self, Oscilloscope):
        Oscilloscope.setObjectName(_fromUtf8("Oscilloscope"))
        Oscilloscope.resize(741, 543)
        self.verticalLayout = QtGui.QVBoxLayout(Oscilloscope)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gOsc = PlotWidget(Oscilloscope)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.gOsc.sizePolicy().hasHeightForWidth())
        self.gOsc.setSizePolicy(sizePolicy)
        self.gOsc.setObjectName(_fromUtf8("gOsc"))
        self.verticalLayout.addWidget(self.gOsc)
        self.tabWidget_2 = QtGui.QTabWidget(Oscilloscope)
        self.tabWidget_2.setObjectName(_fromUtf8("tabWidget_2"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.tab)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.groupBox_25 = QtGui.QGroupBox(self.tab)
        self.groupBox_25.setFlat(True)
        self.groupBox_25.setObjectName(_fromUtf8("groupBox_25"))
        self.horizontalLayout_23 = QtGui.QHBoxLayout(self.groupBox_25)
        self.horizontalLayout_23.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_23.setObjectName(_fromUtf8("horizontalLayout_23"))
        self.tBgSt = QFNumberEdit(self.groupBox_25)
        self.tBgSt.setText(_fromUtf8(""))
        self.tBgSt.setObjectName(_fromUtf8("tBgSt"))
        self.horizontalLayout_23.addWidget(self.tBgSt)
        self.gridLayout_5.addWidget(self.groupBox_25, 0, 0, 1, 1)
        self.groupBox_27 = QtGui.QGroupBox(self.tab)
        self.groupBox_27.setFlat(True)
        self.groupBox_27.setObjectName(_fromUtf8("groupBox_27"))
        self.horizontalLayout_25 = QtGui.QHBoxLayout(self.groupBox_27)
        self.horizontalLayout_25.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_25.setObjectName(_fromUtf8("horizontalLayout_25"))
        self.tFpSt = QFNumberEdit(self.groupBox_27)
        self.tFpSt.setObjectName(_fromUtf8("tFpSt"))
        self.horizontalLayout_25.addWidget(self.tFpSt)
        self.gridLayout_5.addWidget(self.groupBox_27, 0, 1, 1, 1)
        self.groupBox_29 = QtGui.QGroupBox(self.tab)
        self.groupBox_29.setFlat(True)
        self.groupBox_29.setObjectName(_fromUtf8("groupBox_29"))
        self.horizontalLayout_27 = QtGui.QHBoxLayout(self.groupBox_29)
        self.horizontalLayout_27.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_27.setObjectName(_fromUtf8("horizontalLayout_27"))
        self.tCdSt = QFNumberEdit(self.groupBox_29)
        self.tCdSt.setObjectName(_fromUtf8("tCdSt"))
        self.horizontalLayout_27.addWidget(self.tCdSt)
        self.gridLayout_5.addWidget(self.groupBox_29, 0, 2, 1, 1)
        self.groupBox_26 = QtGui.QGroupBox(self.tab)
        self.groupBox_26.setFlat(True)
        self.groupBox_26.setObjectName(_fromUtf8("groupBox_26"))
        self.horizontalLayout_24 = QtGui.QHBoxLayout(self.groupBox_26)
        self.horizontalLayout_24.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_24.setObjectName(_fromUtf8("horizontalLayout_24"))
        self.tBgEn = QFNumberEdit(self.groupBox_26)
        self.tBgEn.setText(_fromUtf8(""))
        self.tBgEn.setObjectName(_fromUtf8("tBgEn"))
        self.horizontalLayout_24.addWidget(self.tBgEn)
        self.gridLayout_5.addWidget(self.groupBox_26, 1, 0, 1, 1)
        self.groupBox_28 = QtGui.QGroupBox(self.tab)
        self.groupBox_28.setFlat(True)
        self.groupBox_28.setObjectName(_fromUtf8("groupBox_28"))
        self.horizontalLayout_26 = QtGui.QHBoxLayout(self.groupBox_28)
        self.horizontalLayout_26.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_26.setObjectName(_fromUtf8("horizontalLayout_26"))
        self.tFpEn = QFNumberEdit(self.groupBox_28)
        self.tFpEn.setObjectName(_fromUtf8("tFpEn"))
        self.horizontalLayout_26.addWidget(self.tFpEn)
        self.gridLayout_5.addWidget(self.groupBox_28, 1, 1, 1, 1)
        self.groupBox_30 = QtGui.QGroupBox(self.tab)
        self.groupBox_30.setFlat(True)
        self.groupBox_30.setObjectName(_fromUtf8("groupBox_30"))
        self.horizontalLayout_28 = QtGui.QHBoxLayout(self.groupBox_30)
        self.horizontalLayout_28.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_28.setObjectName(_fromUtf8("horizontalLayout_28"))
        self.tCdEn = QFNumberEdit(self.groupBox_30)
        self.tCdEn.setObjectName(_fromUtf8("tCdEn"))
        self.horizontalLayout_28.addWidget(self.tCdEn)
        self.gridLayout_5.addWidget(self.groupBox_30, 1, 2, 1, 1)
        self.bOscInit = QtGui.QPushButton(self.tab)
        self.bOscInit.setObjectName(_fromUtf8("bOscInit"))
        self.gridLayout_5.addWidget(self.bOscInit, 0, 3, 1, 1)
        self.horizontalLayout_4.addLayout(self.gridLayout_5)
        self.tabWidget_2.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.horizontalLayout_48 = QtGui.QHBoxLayout(self.tab_2)
        self.horizontalLayout_48.setObjectName(_fromUtf8("horizontalLayout_48"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox_10 = QtGui.QGroupBox(self.tab_2)
        self.groupBox_10.setFlat(True)
        self.groupBox_10.setObjectName(_fromUtf8("groupBox_10"))
        self.horizontalLayout_45 = QtGui.QHBoxLayout(self.groupBox_10)
        self.horizontalLayout_45.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_45.setObjectName(_fromUtf8("horizontalLayout_45"))
        self.tOscPulses = QtGui.QLineEdit(self.groupBox_10)
        self.tOscPulses.setEnabled(False)
        self.tOscPulses.setObjectName(_fromUtf8("tOscPulses"))
        self.horizontalLayout_45.addWidget(self.tOscPulses)
        self.gridLayout.addWidget(self.groupBox_10, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.tab_2)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.cPyroMode = QtGui.QComboBox(self.groupBox)
        self.cPyroMode.setObjectName(_fromUtf8("cPyroMode"))
        self.cPyroMode.addItem(_fromUtf8(""))
        self.cPyroMode.addItem(_fromUtf8(""))
        self.horizontalLayout_2.addWidget(self.cPyroMode)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.tab_2)
        self.groupBox_2.setFlat(True)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_3.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.cFELCoupler = QtGui.QComboBox(self.groupBox_2)
        self.cFELCoupler.setObjectName(_fromUtf8("cFELCoupler"))
        self.cFELCoupler.addItem(_fromUtf8(""))
        self.cFELCoupler.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.cFELCoupler)
        self.gridLayout.addWidget(self.groupBox_2, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.groupBox_53 = QtGui.QGroupBox(self.tab_2)
        self.groupBox_53.setFlat(True)
        self.groupBox_53.setObjectName(_fromUtf8("groupBox_53"))
        self.horizontalLayout_47 = QtGui.QHBoxLayout(self.groupBox_53)
        self.horizontalLayout_47.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_47.setObjectName(_fromUtf8("horizontalLayout_47"))
        self.tOscCDRatio = QFNumberEdit(self.groupBox_53)
        self.tOscCDRatio.setObjectName(_fromUtf8("tOscCDRatio"))
        self.horizontalLayout_47.addWidget(self.tOscCDRatio)
        self.gridLayout.addWidget(self.groupBox_53, 0, 1, 1, 1)
        self.horizontalLayout_48.addLayout(self.gridLayout)
        self.tabWidget_2.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.tab_3)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox_40 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_40.setFlat(True)
        self.groupBox_40.setCheckable(False)
        self.groupBox_40.setObjectName(_fromUtf8("groupBox_40"))
        self.gridLayout_10 = QtGui.QGridLayout(self.groupBox_40)
        self.gridLayout_10.setSpacing(0)
        self.gridLayout_10.setContentsMargins(0, 10, 0, 0)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.tFELP = QFNumberEdit(self.groupBox_40)
        self.tFELP.setObjectName(_fromUtf8("tFELP"))
        self.gridLayout_10.addWidget(self.tFELP, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_40, 0, 0, 1, 1)
        self.groupBox_55 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_55.setFlat(True)
        self.groupBox_55.setObjectName(_fromUtf8("groupBox_55"))
        self.horizontalLayout_53 = QtGui.QHBoxLayout(self.groupBox_55)
        self.horizontalLayout_53.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_53.setObjectName(_fromUtf8("horizontalLayout_53"))
        self.tSpotSize = QFNumberEdit(self.groupBox_55)
        self.tSpotSize.setObjectName(_fromUtf8("tSpotSize"))
        self.horizontalLayout_53.addWidget(self.tSpotSize)
        self.gridLayout_2.addWidget(self.groupBox_55, 1, 1, 1, 1)
        self.groupBox_59 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_59.setEnabled(False)
        self.groupBox_59.setFlat(True)
        self.groupBox_59.setObjectName(_fromUtf8("groupBox_59"))
        self.horizontalLayout_56 = QtGui.QHBoxLayout(self.groupBox_59)
        self.horizontalLayout_56.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_56.setObjectName(_fromUtf8("horizontalLayout_56"))
        self.tEField = QtGui.QLineEdit(self.groupBox_59)
        self.tEField.setObjectName(_fromUtf8("tEField"))
        self.horizontalLayout_56.addWidget(self.tEField)
        self.gridLayout_2.addWidget(self.groupBox_59, 0, 1, 1, 1)
        self.groupBox_60 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_60.setEnabled(False)
        self.groupBox_60.setFlat(True)
        self.groupBox_60.setObjectName(_fromUtf8("groupBox_60"))
        self.horizontalLayout_57 = QtGui.QHBoxLayout(self.groupBox_60)
        self.horizontalLayout_57.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_57.setObjectName(_fromUtf8("horizontalLayout_57"))
        self.tIntensity = QtGui.QLineEdit(self.groupBox_60)
        self.tIntensity.setObjectName(_fromUtf8("tIntensity"))
        self.horizontalLayout_57.addWidget(self.tIntensity)
        self.gridLayout_2.addWidget(self.groupBox_60, 0, 2, 1, 1)
        self.groupBox_39 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_39.setFlat(True)
        self.groupBox_39.setCheckable(False)
        self.groupBox_39.setObjectName(_fromUtf8("groupBox_39"))
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox_39)
        self.gridLayout_9.setSpacing(0)
        self.gridLayout_9.setContentsMargins(0, 10, 0, 0)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.tFELFreq = QFNumberEdit(self.groupBox_39)
        self.tFELFreq.setObjectName(_fromUtf8("tFELFreq"))
        self.gridLayout_9.addWidget(self.tFELFreq, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_39, 1, 0, 1, 1)
        self.groupBox_58 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_58.setFlat(True)
        self.groupBox_58.setObjectName(_fromUtf8("groupBox_58"))
        self.horizontalLayout_55 = QtGui.QHBoxLayout(self.groupBox_58)
        self.horizontalLayout_55.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_55.setObjectName(_fromUtf8("horizontalLayout_55"))
        self.tEffectiveField = QFNumberEdit(self.groupBox_58)
        self.tEffectiveField.setObjectName(_fromUtf8("tEffectiveField"))
        self.horizontalLayout_55.addWidget(self.tEffectiveField)
        self.gridLayout_2.addWidget(self.groupBox_58, 1, 3, 1, 1)
        self.groupBox_57 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_57.setFlat(True)
        self.groupBox_57.setObjectName(_fromUtf8("groupBox_57"))
        self.horizontalLayout_51 = QtGui.QHBoxLayout(self.groupBox_57)
        self.horizontalLayout_51.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_51.setObjectName(_fromUtf8("horizontalLayout_51"))
        self.tWindowTransmission = QFNumberEdit(self.groupBox_57)
        self.tWindowTransmission.setObjectName(_fromUtf8("tWindowTransmission"))
        self.horizontalLayout_51.addWidget(self.tWindowTransmission)
        self.gridLayout_2.addWidget(self.groupBox_57, 1, 2, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_3.setFlat(True)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_5.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.tFELPol = QtGui.QLineEdit(self.groupBox_3)
        self.tFELPol.setObjectName(_fromUtf8("tFELPol"))
        self.horizontalLayout_5.addWidget(self.tFELPol)
        self.gridLayout_2.addWidget(self.groupBox_3, 0, 3, 1, 1)
        self.groupBox_41 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_41.setFlat(True)
        self.groupBox_41.setCheckable(False)
        self.groupBox_41.setObjectName(_fromUtf8("groupBox_41"))
        self.gridLayout_11 = QtGui.QGridLayout(self.groupBox_41)
        self.gridLayout_11.setSpacing(0)
        self.gridLayout_11.setContentsMargins(0, 10, 0, 0)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.tFELRR = QtGui.QLineEdit(self.groupBox_41)
        self.tFELRR.setObjectName(_fromUtf8("tFELRR"))
        self.gridLayout_11.addWidget(self.tFELRR, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_41, 0, 4, 1, 1)
        self.horizontalLayout_6.addLayout(self.gridLayout_2)
        self.tabWidget_2.addTab(self.tab_3, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.bOPause = QtGui.QPushButton(Oscilloscope)
        self.bOPause.setCheckable(True)
        self.bOPause.setChecked(True)
        self.bOPause.setObjectName(_fromUtf8("bOPause"))
        self.horizontalLayout.addWidget(self.bOPause)
        self.groupBox_31 = QtGui.QGroupBox(Oscilloscope)
        self.groupBox_31.setFlat(True)
        self.groupBox_31.setObjectName(_fromUtf8("groupBox_31"))
        self.horizontalLayout_29 = QtGui.QHBoxLayout(self.groupBox_31)
        self.horizontalLayout_29.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_29.setObjectName(_fromUtf8("horizontalLayout_29"))
        self.cOGPIB = QtGui.QComboBox(self.groupBox_31)
        self.cOGPIB.setObjectName(_fromUtf8("cOGPIB"))
        self.horizontalLayout_29.addWidget(self.cOGPIB)
        self.horizontalLayout.addWidget(self.groupBox_31)
        self.groupBox_32 = QtGui.QGroupBox(Oscilloscope)
        self.groupBox_32.setFlat(True)
        self.groupBox_32.setObjectName(_fromUtf8("groupBox_32"))
        self.horizontalLayout_30 = QtGui.QHBoxLayout(self.groupBox_32)
        self.horizontalLayout_30.setContentsMargins(0, 10, 0, 0)
        self.horizontalLayout_30.setObjectName(_fromUtf8("horizontalLayout_30"))
        self.cOChannel = QtGui.QComboBox(self.groupBox_32)
        self.cOChannel.setObjectName(_fromUtf8("cOChannel"))
        self.cOChannel.addItem(_fromUtf8(""))
        self.cOChannel.addItem(_fromUtf8(""))
        self.cOChannel.addItem(_fromUtf8(""))
        self.cOChannel.addItem(_fromUtf8(""))
        self.horizontalLayout_30.addWidget(self.cOChannel)
        self.horizontalLayout.addWidget(self.groupBox_32)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.bOPop = QtGui.QPushButton(Oscilloscope)
        self.bOPop.setObjectName(_fromUtf8("bOPop"))
        self.horizontalLayout.addWidget(self.bOPop)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Oscilloscope)
        self.tabWidget_2.setCurrentIndex(0)
        self.cPyroMode.setCurrentIndex(1)
        self.cOChannel.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Oscilloscope)

    def retranslateUi(self, Oscilloscope):
        Oscilloscope.setWindowTitle(_translate("Oscilloscope", "Form", None))
        self.groupBox_25.setTitle(_translate("Oscilloscope", "Background Start", None))
        self.groupBox_27.setTitle(_translate("Oscilloscope", "Front Porch Start", None))
        self.groupBox_29.setTitle(_translate("Oscilloscope", "Cavity Dump Start", None))
        self.groupBox_26.setTitle(_translate("Oscilloscope", "Background End", None))
        self.groupBox_28.setTitle(_translate("Oscilloscope", "Front Porch End", None))
        self.groupBox_30.setTitle(_translate("Oscilloscope", "Cavity Dump End", None))
        self.bOscInit.setText(_translate("Oscilloscope", "Initialize Regions", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab), _translate("Oscilloscope", "Boxcar Regions", None))
        self.groupBox_10.setTitle(_translate("Oscilloscope", "No. Pulses", None))
        self.groupBox.setTitle(_translate("Oscilloscope", "Pyro Mode", None))
        self.cPyroMode.setItemText(0, _translate("Oscilloscope", "Instant", None))
        self.cPyroMode.setItemText(1, _translate("Oscilloscope", "Integrating", None))
        self.groupBox_2.setTitle(_translate("Oscilloscope", "Coupler", None))
        self.cFELCoupler.setItemText(0, _translate("Oscilloscope", "Cavity Dump", None))
        self.cFELCoupler.setItemText(1, _translate("Oscilloscope", "Hole", None))
        self.groupBox_53.setTitle(_translate("Oscilloscope", "CD Ratio", None))
        self.tOscCDRatio.setText(_translate("Oscilloscope", "5", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_2), _translate("Oscilloscope", "Pulse Counting Settings", None))
        self.groupBox_40.setTitle(_translate("Oscilloscope", "FEL Energy (mJ)", None))
        self.tFELP.setText(_translate("Oscilloscope", "0", None))
        self.groupBox_55.setTitle(_translate("Oscilloscope", "Spot Size(cm)", None))
        self.tSpotSize.setToolTip(_translate("Oscilloscope", "Radius of FEL spot size", None))
        self.tSpotSize.setText(_translate("Oscilloscope", "0.05", None))
        self.groupBox_59.setTitle(_translate("Oscilloscope", "E (kV/cm)", None))
        self.tEField.setText(_translate("Oscilloscope", "0.0", None))
        self.groupBox_60.setTitle(_translate("Oscilloscope", "I (kW/cm2)", None))
        self.tIntensity.setText(_translate("Oscilloscope", "0.0", None))
        self.groupBox_39.setTitle(_translate("Oscilloscope", "FEL Freq (cm-1)", None))
        self.tFELFreq.setText(_translate("Oscilloscope", "0", None))
        self.groupBox_58.setTitle(_translate("Oscilloscope", "Sample E_eff", None))
        self.tEffectiveField.setText(_translate("Oscilloscope", "1.0", None))
        self.groupBox_57.setTitle(_translate("Oscilloscope", "Window Trans", None))
        self.tWindowTransmission.setText(_translate("Oscilloscope", "1.0", None))
        self.groupBox_3.setTitle(_translate("Oscilloscope", "FEL Pol", None))
        self.groupBox_41.setTitle(_translate("Oscilloscope", "Rep Rate (Hz)", None))
        self.tFELRR.setText(_translate("Oscilloscope", "0.75", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), _translate("Oscilloscope", "Field Parameters", None))
        self.bOPause.setText(_translate("Oscilloscope", "Pause", None))
        self.groupBox_31.setTitle(_translate("Oscilloscope", "GPIB", None))
        self.cOGPIB.setToolTip(_translate("Oscilloscope", "GPIB0::5::INSTR", None))
        self.groupBox_32.setTitle(_translate("Oscilloscope", "Channel", None))
        self.cOChannel.setItemText(0, _translate("Oscilloscope", "1", None))
        self.cOChannel.setItemText(1, _translate("Oscilloscope", "2", None))
        self.cOChannel.setItemText(2, _translate("Oscilloscope", "3", None))
        self.cOChannel.setItemText(3, _translate("Oscilloscope", "4", None))
        self.bOPop.setText(_translate("Oscilloscope", "Pop Out", None))

from pyqtgraph import PlotWidget
from InstsAndQt.customQt import QFNumberEdit
