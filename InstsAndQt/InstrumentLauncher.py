import sys, os, subprocess, time
import pyqtgraph.examples
# if __name__ == "__main__" and (__package__ is None or __package__==''):
#     parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     sys.path.insert(0, parent_dir)
#     import examples
#     __package__ = "examples"


from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

import os, sys

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
        MainWindow.resize(559, 360)
        MainWindow.setTabShape(QtGui.QTabWidget.Triangular)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.tab)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.bRun = QtGui.QPushButton(self.tab)
        self.bRun.setObjectName(_fromUtf8("bRun"))
        self.gridLayout.addWidget(self.bRun, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.splitter = QtGui.QSplitter(self.tab)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.lwNames = QtGui.QListWidget(self.splitter)
        self.lwNames.setObjectName(_fromUtf8("lwNames"))
        self.wRenderer = QtGui.QWidget(self.splitter)
        self.wRenderer.setObjectName(_fromUtf8("wRenderer"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 2)
        self.horizontalLayout_2.addLayout(self.gridLayout)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.horizontalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 559, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
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


class AppOutputStream(object):
    def __init__(self, qtextedit=None):
        """

        :param qtextedit:
         :type qtextedit: QtGui.QTextEdit
        """
        self.qText = qtextedit
        global outputStreams
        outputStreams.append(self)
        self.proc = QtCore.QProcess()

    def connectProcess(self, proc):
        self.proc = proc
        proc.readyReadStandardError.connect(self.readErr)
        proc.readyReadStandardOutput.connect(self.readOut)
        proc.finished.connect(self.finish)

    def readErr(self):
        self.proc.setReadChannel(QtCore.QProcess.StandardError)
        text = str(self.proc.readAll())
        # self.qText.setTextColor(QtGui.QColor("red"))
        # self.qText.append(text)
        # self.qText.setTextColor(QtGui.QColor("black"))
        self.append(text, 'red')

    def readOut(self):
        self.proc.setReadChannel(QtCore.QProcess.StandardOutput)
        text = str(self.proc.readAll())

        self.append(text)

    def append(self, text='', col=None):
        if col is not None:
            oldCol = self.qText.textColor()
            self.qText.setTextColor(QtGui.QColor(col))
        self.qText.append(text)
        if col is not None:
            self.qText.setTextColor(oldCol)

    def finish(self):
        # self.qText.setTextColor(QtGui.QColor("green"))
        # self.qText.append("<application closed>")
        # self.qText = QtGui.QTextEdit()
        self.append("<application closed>", 'green')
        # self.qText.setTextColor(QtGui.QColor("black"))




applications = {
    "Delay Generator": WidgetInfo(r"DelayGenerator.delayGenerator_ui", "Ui_MainWindow",
                        QtGui.QMainWindow,os.path.join("DelayGenerator", "DG535Window.py")),
    "Temperature Monitor": WidgetInfo(r"Lakeshore330Monitor.lakeshore330Panel_ui", "Ui_Form",
                        QtGui.QWidget, os.path.join("Lakeshore330Monitor","lakeshoreMonitor.py"))
    # "Temperature Monitor": WidgetInfo(r"Lakeshore330Monitor.lakeshore330Panel_ui", "Ui_Form",
    #                     QtGui.QWidget, os.path.join("Lakeshore330Monitor","lakeshoreMonitor.py"))
}

path = os.path.abspath(os.path.dirname(__file__))


class ExampleLoader(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        loadUiFiles()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.renderLayout = QtGui.QVBoxLayout()
        self.ui.wRenderer.setLayout(self.renderLayout)
        self.ui.bRun.clicked.connect(self.runApplication)

        self.populateList()
        self.ui.splitter.setStretchFactor(1, 0)
        self.ui.splitter.setStretchFactor(1, 1)

        self.ui.lwNames.currentItemChanged.connect(self.updateDisplayWidget)

        self.show()

    def populateList(self):
        global applications
        for name in sorted(applications):
            self.ui.lwNames.addItem(name)

    def updateDisplayWidget(self, current, previous):
        global applications
        widInf = applications[str(current.text())]
        ui, wid = widInf.ui, widInf.cls
        newWid = wid()
        newWid.ui = ui()
        newWid.ui.setupUi(newWid)

        # Remove parent of the render layout and let it be garbage
        # collected
        QtGui.QWidget().setLayout(self.renderLayout)
        self.renderLayout = QtGui.QVBoxLayout()
        self.renderLayout.addWidget(newWid)

        self.ui.wRenderer.setLayout(self.renderLayout)
    
    def currentFile(self):
        global applications
        item = str(self.ui.lwNames.currentItem().text())

        return os.path.join(path, applications[item].fname)
    
    def loadFile(self, edited=False):
        
        extra = []
        if self.ui.pyqtCheck.isChecked():
            extra.append('pyqt')
        elif self.ui.pysideCheck.isChecked():
            extra.append('pyside')
        
        if self.ui.forceGraphicsCheck.isChecked():
            extra.append(str(self.ui.forceGraphicsCombo.currentText()))

        
        #if sys.platform.startswith('win'):
            #os.spawnl(os.P_NOWAIT, sys.executable, '"'+sys.executable+'"', '"' + fn + '"', *extra)
        #else:
            #os.spawnl(os.P_NOWAIT, sys.executable, sys.executable, fn, *extra)
        
        if edited:
            path = os.path.abspath(os.path.dirname(__file__))
            proc = subprocess.Popen([sys.executable, '-'] + extra, stdin=subprocess.PIPE, cwd=path)
            code = str(self.ui.codeView.toPlainText()).encode('UTF-8')
            proc.stdin.write(code)
            proc.stdin.close()
        else:
            fn = self.currentFile()
            if fn is None:
                return
            if sys.platform.startswith('win'):
                os.spawnl(os.P_NOWAIT, sys.executable, '"'+sys.executable+'"', '"' + fn + '"', *extra)
            else:
                os.spawnl(os.P_NOWAIT, sys.executable, sys.executable, fn, *extra)

    def runApplication(self):
        fn = self.currentFile()
        if fn is None:
            return
        excStr = "{} {}".format(sys.executable, fn)
        a = QtCore.QProcess()

        newText = QtGui.QTextEdit()
        newText.setReadOnly(True)
        self.ui.tabWidget.addTab(newText, self.ui.lwNames.currentItem().text())

        stream = AppOutputStream(qtextedit=newText)
        stream.connectProcess(a)


        if  QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            a.startDetached("{} {}".format(sys.executable, fn))
            stream.append("<Proccess Detached...>", "purple")
        if sys.platform.startswith('win'):
            raise
            # self.a = os.spawnl(os.P_NOWAIT, sys.executable, '"' + sys.executable + '"',
            #           '"' + fn + '"')
        else:
            a.start(excStr)


    def close(self):
        print "Tried to close"

    def closeEvent(self, QCloseEvent):
        print "tried to closeEvent"

        # QtCore.QProcess.state()
        anyRunning = any([ii.proc.state()==QtCore.QProcess.Running for ii in outputStreams])
        if anyRunning:
            print "Process is running"
        else:
            print "No Processing running"
        super(ExampleLoader, self).closeEvent(QCloseEvent)


cons = None
def run():
    app = QtGui.QApplication([])
    loader = ExampleLoader()

    import pyqtgraph.console as pgc

    global cons
    # cons = pgc.ConsoleWidget(namespace={"load":loader})
    # cons.show()
    
    app.exec_()

def buildFileList(examples, files=None):
    if files == None:
        files = []
    for key, val in examples.items():
        #item = QtGui.QTreeWidgetItem([key])
        if isinstance(val, basestring):
            #item.file = val
            files.append((key,val))
        else:
            buildFileList(val, files)
    return files
            
def testFile(name, f, exe, lib, graphicsSystem=None):
    global path
    fn =  os.path.join(path,f)
    #print "starting process: ", fn
    os.chdir(path)
    sys.stdout.write(name)
    sys.stdout.flush()
    
    import1 = "import %s" % lib if lib != '' else ''
    import2 = os.path.splitext(os.path.split(fn)[1])[0]
    graphicsSystem = '' if graphicsSystem is None else "pg.QtGui.QApplication.setGraphicsSystem('%s')" % graphicsSystem
    code = """
try:
    %s
    import initExample
    import pyqtgraph as pg
    %s
    import %s
    import sys
    print("test complete")
    sys.stdout.flush()
    import time
    while True:  ## run a little event loop
        pg.QtGui.QApplication.processEvents()
        time.sleep(0.01)
except:
    print("test failed")
    raise

"""  % (import1, graphicsSystem, import2)

    if sys.platform.startswith('win'):
        process = subprocess.Popen([exe], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        process.stdin.write(code.encode('UTF-8'))
        process.stdin.close()
    else:
        process = subprocess.Popen(['exec %s -i' % (exe)], shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        process.stdin.write(code.encode('UTF-8'))
        process.stdin.close() ##?
    output = ''
    fail = False
    while True:
        c = process.stdout.read(1).decode()
        output += c
        #sys.stdout.write(c)
        #sys.stdout.flush()
        if output.endswith('test complete'):
            break
        if output.endswith('test failed'):
            fail = True
            break
    time.sleep(1)
    process.kill()
    #res = process.communicate()
    res = (process.stdout.read(), process.stderr.read())
    
    if fail or 'exception' in res[1].decode().lower() or 'error' in res[1].decode().lower():
        print('.' * (50-len(name)) + 'FAILED')
        print(res[0].decode())
        print(res[1].decode())
    else:
        print('.' * (50-len(name)) + 'passed')

def loadUiFiles():
    global applications
    for appName in applications:
        widInfo = applications[appName]
        localName, clsName, cls = widInfo.ui_fname, widInfo.ui_clsn, widInfo.cls
        exec("from {} import {} as ui".format(localName, clsName))
        # applications[appName] = (ui, cls)
        applications[appName].ui = ui


if __name__ == '__main__':
    if '--test' in sys.argv[1:]:
        # get rid of orphaned cache files first
        pg.renamePyc(path)

        files = buildFileList(examples)
        if '--pyside' in sys.argv[1:]:
            lib = 'PySide'
        elif '--pyqt' in sys.argv[1:]:
            lib = 'PyQt4'
        else:
            lib = ''
            
        exe = sys.executable
        print("Running tests:", lib, sys.executable)
        for f in files:
            testFile(f[0], f[1], exe, lib)
    else: 
        run()
