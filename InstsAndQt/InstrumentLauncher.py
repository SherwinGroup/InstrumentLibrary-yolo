import sys, os, subprocess, time

from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg



import os, sys



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
        MainWindow.resize(559, 360)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.bRun = QtWidgets.QPushButton(self.tab)
        self.bRun.setObjectName("bRun")
        self.gridLayout.addWidget(self.bRun, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.splitter = QtWidgets.QSplitter(self.tab)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.lwNames = QtWidgets.QListWidget(self.splitter)
        self.lwNames.setObjectName("lwNames")
        self.wRenderer = QtWidgets.QWidget(self.splitter)
        self.wRenderer.setObjectName("wRenderer")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 2)
        self.horizontalLayout_2.addLayout(self.gridLayout)
        self.tabWidget.addTab(self.tab, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 559, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.bRun.setText(_translate("MainWindow", "Run", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "File List", None))


class WidgetInfo(object):
    def __init__(self, ui_file='', ui_cls_name='',
                 ui_cls = object, app_loc = ''):
        self.ui_fname = ui_file
        self.ui_clsn = ui_cls_name
        self.cls = ui_cls
        self.fname = app_loc

        self.ui = object

outputStreams = []

class AppOutputStream(QtCore.QObject):
    def __init__(self, parent=None, qtextedit=None):
        """
        :param qtextedit:
         :type qtextedit: QtGui.QTextEdit
        """
        super(AppOutputStream, self).__init__(parent)
        self.qText = qtextedit
        global outputStreams
        outputStreams.append(self)
        self.proc = QtCore.QProcess()

    def connectProcess(self, proc):
        self.proc = proc
        proc.readyReadStandardError.connect(self.readErr)
        proc.readyReadStandardOutput.connect(self.readOut)
        proc.error.connect(self.readErr)
        proc.finished.connect(self.finish)

    def readErr(self):
        text = self.proc.readAllStandardError()
        # self.append('-'*20, 'red')
        self.append(text, 'red')
        # self.append('-'*20, 'red')

    def readOut(self):
        text = self.proc.readAllStandardOutput()
        self.append(text)

    def append(self, text='', col=None):
        if col is not None:
            oldCol = self.qText.textColor()
            self.qText.setTextColor(QtGui.QColor(col))

        # The input from QProcess buffer reading is a bytearray, which
        # need to be reencoded to strings to avoid ugly printing
        if isinstance(text, QtCore.QByteArray):
            text = str(text, encoding="ascii")
        self.qText.append(text)
        if col is not None:
            self.qText.setTextColor(oldCol)

        # can access tab widget with self.qText.parent(), the parent is
            # set as the tabwidget.
        # load.ui.tabWidget.tabBar().setTabTextColor(1, QtGui.QColor("Red"))

    def finish(self):
        self.append("<application closed>", 'green')

applications = {
    "Delay Generator": WidgetInfo(r"DelayGenerator.delayGenerator_ui", "Ui_MainWindow",
                        QtWidgets.QMainWindow,os.path.join("DelayGenerator", "DG535Window.py")),
    "Temperature Monitor": WidgetInfo(r"Lakeshore330Monitor.lakeshore330Panel_ui", "Ui_MainWindow",
                        QtWidgets.QMainWindow, os.path.join("Lakeshore330Monitor","lakeshoreMonitor.py")),
    "Pyro Calibrator": WidgetInfo(r"PyroCalibrator.calibrator_ui", "Ui_PyroCalibration",
                        QtWidgets.QMainWindow, os.path.join("PyroCalibrator","pyroCal.py")),
    "FEL Pulse Monitor": WidgetInfo(None, None,
                        None, os.path.join("PyroOscope","FELMonitor.py")),
    "Wiregrid calibrator": WidgetInfo(r"MotorDriver.wiregridcal_ui", "Ui_MainWindow",
                        QtWidgets.QMainWindow, os.path.join("MotorDriver","TKCalibrator.py")),
    "THz Attenuator": WidgetInfo(r"MotorDriver.movementWindow_ui", "Ui_MainWindow",
                        QtWidgets.QMainWindow, os.path.join("MotorDriver","motorMain.py")),
    "Newport Motor Driver": WidgetInfo(r"NewportMotorDriver.UIs.axisPanel_ui", "Ui_ESPAxisPanel",
                        QtWidgets.QWidget, os.path.join("NewportMotorDriver","espMainPanel.py"))
    # "Temperature Monitor": WidgetInfo(r"Lakeshore330Monitor.lakeshore330Panel_ui", "Ui_Form",
    #                     QtWidgets.QWidget, os.path.join("Lakeshore330Monitor","lakeshoreMonitor.py"))
}

path = os.path.abspath(os.path.dirname(__file__))

class ExampleLoader(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        loadUiFiles()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.renderLayout = QtWidgets.QVBoxLayout()
        self.ui.wRenderer.setLayout(self.renderLayout)
        self.ui.bRun.clicked.connect(self.runApplication)

        self.populateList()
        self.ui.splitter.setStretchFactor(1, 0)
        self.ui.splitter.setStretchFactor(1, 1)

        self.ui.lwNames.currentItemChanged.connect(self.updateDisplayWidget)
        self.ui.lwNames.doubleClicked.connect(self.runApplication)

        self.show()

    def populateList(self):
        global applications
        for name in sorted(applications):
            self.ui.lwNames.addItem(name)

    def updateDisplayWidget(self, current, previous):
        global applications
        widInf = applications[str(current.text())]
        ui, wid = widInf.ui, widInf.cls

        newWin = QtWidgets.QMainWindow()
        newWin.setEnabled(False)
        newWin.blockSignals(True)

        if wid is QtWidgets.QWidget:
            newWid = QtWidgets.QWidget()
            newWid.ui = ui()
            newWid.ui.setupUi(newWid)
            newWin.setCentralWidget(newWid)
            newWin.layout().setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            # newWid.setFixedSize(newWid.size())
        elif wid is None:
            newWid = QtWidgets.QLabel("No UI file")
            newWin.setCentralWidget(newWid)

        else:
            newWin.ui = ui()
            try:
                newWin.ui.setupUi(newWin)
            except:
                print(ui)
                raise


        # Remove parent of the render layout and let it be garbage
        # collected
        QtWidgets.QWidget().setLayout(self.renderLayout)
        self.renderLayout = QtWidgets.QVBoxLayout()
        self.renderLayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.renderLayout.addWidget(newWin)

        self.ui.wRenderer.setLayout(self.renderLayout)

    def currentFile(self):
        global applications
        item = str(self.ui.lwNames.currentItem().text())

        return os.path.join(path, applications[item].fname)

    def runApplication(self):
        fn = self.currentFile()
        if fn is None:
            return
        # -u option causes the input/output buffers to be unbuffered,
        #   so things flush properly and can be read by the output stream
        excStr = "{} -u {}".format(sys.executable, fn)
        a = QtCore.QProcess()

        newText = QtWidgets.QTextEdit(self.ui.tabWidget)
        newText.setReadOnly(True)
        self.ui.tabWidget.addTab(newText, self.ui.lwNames.currentItem().text())

        stream = AppOutputStream(self, qtextedit=newText)
        stream.connectProcess(a)

        if  QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            a.startDetached("{} {}".format(sys.executable, fn))
            stream.append("<Proccess Detached...>", "purple")
        a.start(excStr, QtCore.QProcess.ReadOnly)

    def closeEvent(self, QCloseEvent):
        anyRunning = any([ii.proc.state()==QtCore.QProcess.Running for ii in outputStreams])


        if anyRunning:
            wid = QtWidgets.QMessageBox.warning(self, "Confirm exit",
                                            "Applications are still running. Are you sure you want to "
                                            "exit? (Running applications will be terminated)",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel,
                                            QtWidgets.QMessageBox.Cancel)
            if wid == QtWidgets.QMessageBox.Cancel:
                QCloseEvent.ignore()
                return
        super(ExampleLoader, self).closeEvent(QCloseEvent)


cons = None
def run():
    app = QtWidgets.QApplication([])
    loader = ExampleLoader()
    from pyqtgraph.console import ConsoleWidget as cw
    cons = cw(namespace={"win":loader, "os":outputStreams})
    cons.show()


    app.exec_()

def loadUiFiles():
    global applications
    for appName in applications:
        widInfo = applications[appName]
        localName, clsName, cls = widInfo.ui_fname, widInfo.ui_clsn, widInfo.cls
        try:
            execSt = "from {} import {} as ui".format(localName, clsName)

            # Need to pass the globals, otherwise the ui it imports
            # isn't in the same scope?
            exec(execSt, globals())
            # applications[appName] = (ui, cls)
            applications[appName].ui = ui
        except (SyntaxError):
            # happens when there isn't a ui file specified
            pass


if __name__ == '__main__':
    if '--test' in sys.argv[1:]:
        # get rid of orphaned cache files first
        pg.renamePyc(path)

        files = buildFileList(examples)
        if '--pyside' in sys.argv[1:]:
            lib = 'PySide'
        elif '--pyqt' in sys.argv[1:]:
            lib = 'PyQt5'
        else:
            lib = ''

        exe = sys.executable
        print(("Running tests:", lib, sys.executable))
        for f in files:
            testFile(f[0], f[1], exe, lib)
    else:
        run()
