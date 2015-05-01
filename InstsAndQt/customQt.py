# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 09:36:20 2015
Inspiration: http://stackoverflow.com/questions/12182133/pyqt4-combine-textchanged-and-editingfinished-for-qlineedit
@author: dvalovcin
"""

import numpy as np
import copy
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import re
import traceback


class QFNumberEdit(QtGui.QLineEdit):
    #a signal to emit the new, approved number. Will emit False if the 
    # inputted value is not accepted. Intended for float inputs
    textAccepted = QtCore.pyqtSignal(object)
    def __init__(self, parent = None, contents = ''):
        super(QFNumberEdit, self).__init__(parent)
        self.editingFinished.connect(self._handleEditingFinished)
        self.textChanged.connect(lambda: self._handleEditingFinished())
        self.returnPressed.connect(lambda: self._handleEditingFinished(True))
        self._before = contents
        
    
        
    def _handleEditingFinished(self, _return = False):
        before, after = self._before, str(self.text())
        if (not self.hasFocus() or _return) and before != after:
            val = self.parseInp(after)
            #if the return is False, need to catch that. Otherwise, may take
            #if val to be false when val=0, which is a valid input
            if type(val) is bool:
                self.setText(str(before))
                self.textAccepted.emit(False)
            else:
                self.setText(str(val))
                self._before = str(val)
                self.textAccepted.emit(val)
                
            
    def value(self):
        ret = -1
        try:
            ret = float(self.text())
        except:
            self._handleEditingFinished()
            ret = float(self.text())
        return ret
                
    def parseInp(self, inp):
        ret = None
        #see if we can just turn it into a number and leave if we can
        try:
            ret = float(inp)
            return ret
        except:
            pass

        toMatch = re.compile('(\d+\.?\d*|\d*\.\d+)\*(\d+\.?\d*|\d*\.\d+)')
        if re.match(toMatch, inp):
            print "it's a command! {}".format(inp)
            try:
                ret = eval(inp)
                return ret
            except Exception as e:
                print "Can't parse command", inp, e
        #tests to see whether digit is whole number or decimal, and if it has 
        #some modifier at the end
        toMatch = re.compile('-?(\d+\.?\d*|\d*\.\d+)(m|u|n|M|k)?\Z')
        if re.match(toMatch, inp):
            convDict = {'m': 1e-3, 'u':1e-6, 'n':1e-9, 'M':1e6, 'k':1e3}
            try:
                ret = (float(inp[:-1]) * #convert first part to number
                   convDict[[b for b in convDict.keys() if b in inp][0]]) #and multiply by the exponential
                return ret
            except Exception as e:
                print "Can't parse float string"
                print inp, type(inp)
                print e
                print ''
        else:
            return False

class QINumberEdit(QtGui.QLineEdit):
    #a signal to emit the new, approved number. Will emit False if the 
    # inputted value is not accepted. Intended for integer inputs
    textAccepted = QtCore.pyqtSignal(object)
    def __init__(self, parent = None, contents = ''):
        super(QINumberEdit, self).__init__(parent)
        self.editingFinished.connect(self._handleEditingFinished)
        self.textChanged.connect(lambda: self._handleEditingFinished())
        self.returnPressed.connect(lambda: self._handleEditingFinished(True))
        self._before = contents

    def __add__(self, other):
        ret = copy.deepcopy(self)
        ret.setText(str(self.value()+other))
        return ret

    def __sub__(self, other):
        ret = copy.deepcopy(self)
        ret.setText(str(self.value()-other))
        return ret
        
    def _handleEditingFinished(self, _return = False):
        before, after = self._before, str(self.text())
        if (not self.hasFocus() or _return) and before != after:
            val = self.parseInp(after)
            #if the return is False, need to catch that. Otherwise, may take
            #if val to be false when val=0, which is a valid input
            if type(val) is bool:
                self.setText(str(before))
                self.textAccepted.emit(False)
            else:
                self.setText(str(val))
                self._before = str(val)
                self.textAccepted.emit(val)
    def value(self):
        ret = -1
        try:
            ret = int(self.text())
        except:
            self._handleEditingFinished()
            ret = int(self.text())
        return ret
            
        
    def parseInp(self, inp):
        ret = None
        #see if we can just turn it into a number and leave if we can
        try:
            ret = int(inp)
            return ret
        except:
            return False

class QTimedText(QtGui.QLabel):
    showTime = 3000
    def setMessage(self, message, showTime = None):
        if showTime is None:
            showTime = self.showTime
        self.setText(str(message))
        QtCore.QTimer.singleShot(showTime, self.clearText)

    def clearText(self):
        self.setText("")

class QButtonDblClick(QtGui.QPushButton):
    """
    http://stackoverflow.com/questions/19247436/pyqt-mouse-mousebuttondblclick-event
    Handle whether the button was clicked multiple times or not
    """
    sigMultiClicked = QtCore.pyqtSignal(int)
    sigSingleClicked = QtCore.pyqtSignal(bool) # Emit a signal if single clicked and bool of whether the button is down or not

    def __init__(self, *args, **kwargs):
        QtGui.QPushButton.__init__(self, *args, **kwargs)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(250)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)
        self.left_click_count = 0
        self.downed = False # Need a persistent flag because single clicking will reup.

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.left_click_count += 1
        if not self.timer.isActive():
            self.timer.start()
        self.update()

    def timeout(self):
        if self.left_click_count == 1:
            if not self.downed:
                self.sigSingleClicked.emit(self.isChecked())
        else:
            self.sigMultiClicked.emit(self.left_click_count)
            self.downed = not self.downed
            self.setChecked(self.downed)
            self.update()
        self.left_click_count = 0

class TempThread(QtCore.QThread):
    """ Creates a QThread which will monitor the temperature changes in the
        CCD. Actually more general than that since it simply takes a function and some args...
    """
    def __init__(self, target = None, args = None):
        super(TempThread, self).__init__()
        self.target = target
        self.args = args

    def run(self):
        try:
            if self.args is None:
                self.target()
            else:
                self.target(self.args)
        except Exception as e:
            print "ERROR IN THREAD,",self.target.__name__
            print e
            traceback.print_exc()



class pgPlot(QtGui.QMainWindow):
    """ Dirt simple class for a window with a pyqtgraph plot
        that allows me to emit a signal wh en it's closed
    """
    closedSig = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        super(pgPlot, self).__init__(parent)
        self.pw = pg.PlotWidget()
        self.setCentralWidget(self.pw)
        self.show()

    def closeEvent(self, event):
        self.closedSig.emit()
        event.accept()









