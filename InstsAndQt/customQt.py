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
        if str(self.text()) == '':
            return float(self._before)
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
        if str(self.text())=='':
            return int(self._before)
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

dialogList = []
class MessageDialog(QtGui.QDialog):
    def __init__(self, parent, message="", duration=3000):
        if isinstance(parent, str):
            message = parent
            parent = None
        super(MessageDialog, self).__init__(parent=parent)
        layout  = QtGui.QVBoxLayout(self)
        # text = QtGui.QLabel("<font size='6'>{}</font>".format(message), self)
        text = QtGui.QLabel(self)
        text.setTextFormat(QtCore.Qt.RichText)
        text.setText("<font size='6'>{}</font>".format(message))
        text.setWordWrap(True)
        layout.addWidget(text)
        self.setLayout(layout)
        self.setModal(False)

        dialogList.append(self)

        if duration:
            self.timer = QtCore.QTimer.singleShot(duration, self.close)
        self.show()
        self.raise_()

    def close(self):
        try:
            dialogList.remove(self)
        except Exception as E:
            print "ERror removing from list, ",E

        super(MessageDialog, self).close()

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

class BorderlessPgPlot(QtGui.QMainWindow):
    """ Dirt simple class for a window with a pyqtgraph plot
        that allows me to emit a signal wh en it's closed
    """
    closedSig = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        super(BorderlessPgPlot, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.pw = DraggablePlotWidget()
        self.setCentralWidget(self.pw)
        self.pw.plotItem.vb.sigDropEvent.connect(self.moveWindow)
        self.pw.plotItem.vb.sigCloseRequested.connect(self.close)
        self.show()

    def closeEvent(self, event):
        self.closedSig.emit()
        event.accept()

    def moveWindow(self, obj, pos):
        # newpos = QtCore.QPoint(self.frameGeometry().x(), self.frameGeometry().y())
        newpos = self.pos()
        newpos += pos.toQPoint()

        self.move(newpos)


class DraggablePlotWidget(pg.PlotWidget):
    def __init__(self, parent=None, background='default', **kargs):
        vb = DraggableViewBox()
        kargs["viewBox"] = vb
        super(DraggablePlotWidget, self).__init__(parent, background, **kargs)


class DraggableViewBox(pg.ViewBox):
    """
    Subclassing which allows me to have a viewbox
    where I can overwrite the dragging controls
    """
    # emits (<self>, <drop pos>)
    sigDropEvent = QtCore.pyqtSignal(object, object)
    sigCloseRequested = QtCore.pyqtSignal(object)
    def __init__(self, parent=None, border=None, lockAspect=False, enableMouse=True, invertY=False, enableMenu=True, name=None, invertX=False):
        super(DraggableViewBox, self).__init__(parent, border, lockAspect, enableMouse, invertY, enableMenu, name, invertX)
        close = QtGui.QAction("Close", self)
        close.triggered.connect(lambda val, self=self: self.sigCloseRequested.emit(self))
        self.menu.addAction(close)
        # self.canMove = QtCore.QTimer()

    def mouseDragEvent(self, ev, axis=None):
        # if QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ShiftModifier:
        if ev.modifiers() & QtCore.Qt.ShiftModifier:
            ev.accept()
            # if not ev.isFinish(): return
            self.sigDropEvent.emit(self, ev.screenPos()-ev.lastScreenPos())
        else:
            super(DraggableViewBox, self).mouseDragEvent(ev, axis)




class DoubleYPlot(pg.PlotWidget):
    """
    Often want to have a graph which has two independent
    y axes. it's a bit more work to always handle, so have
    a simple function with conveniences for easy calling
    and manipulating

    Add linear regions to plotItem1 or p2
    """
    def __init__(self, *args, **kwargs):
        super(DoubleYPlot, self).__init__(*args, **kwargs)

        self.plotOne = self.plot()
        self.plotItem1 = self.plotItem

        #http://bazaar.launchpad.net/~luke-campagnola/pyqtgraph/inp/view/head:/examples/MultiplePlotAxes.py
        #Need to do all this nonsense to make it plot on two different axes.
        #Also note the self.updatePhase plot which shows how to update the data.
        self.p2 = pg.ViewBox()
        self.plotItem1.showAxis('right')
        self.plotItem1.scene().addItem(self.p2)
        self.plotItem1.getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.plotItem1)
        self.plotTwo = pg.PlotCurveItem()
        self.p2.addItem(self.plotTwo)

        #need to set it up so that when the window (and thus main plotItem) is
        #resized, it informs the ViewBox for the second plot that it must update itself.
        self.plotItem1.vb.sigResized.connect(lambda: self.p2.setGeometry(self.plotItem1.vb.sceneBoundingRect()))
        self.setY1Color('k')
        self.setY2Color('r')

    def setXLabel(self, label="X", units=""):
        self.plotItem1.setLabel('bottom',text=label, units=units)

    def setY1Label(self, label="Y1", units=""):
        self.plotItem1.setLabel('left', text=label, units=units, color = self.y1Pen.color().name())

    def setY2Label(self, label="Y2", units=""):
        self.plotItem1.getAxis('right').setLabel(label, units=units, color=self.y2Pen.color().name())

    def setTitle(self, title="Title"):
        self.plotItem1.setTitle(title)

    def setY1Data(self, *data):
        if len(data)==1:
            self.plotOne.setData(data[0])
        elif len(data)==2:
            self.plotOne.setData(*data)
        else:
            raise ValueError("I don't know what you want me to plot {}".format(data))

    def setY2Data(self, data):
        if len(data.shape) == 2:
            self.plotTwo.setData(data[:,0], data[:,1])
        else:
            self.plotTwo.setData(data)
        self.p2.setGeometry(self.plotItem1.vb.sceneBoundingRect())

    def setY2Pen(self, *args, **kwargs):
        self.y2Pen = pg.mkPen(*args, **kwargs)
        self.plotItem1.getAxis("right").setPen(self.y2Pen)
        self.plotTwo.setPen(self.y2Pen)

    def setY1Color(self, color='k'):
        self.y1Pen = pg.mkPen(color)
        self.plotItem1.getAxis("left").setPen(self.y1Pen)
        self.plotOne.setPen(self.y1Pen)

    def setY2Color(self, color='r'):
        self.y2Pen = pg.mkPen(color)
        self.plotItem1.getAxis("right").setPen(self.y2Pen)
        self.plotTwo.setPen(self.y2Pen)

class LockableBool(object):
    def __init__(self, val = True):
        self._value = bool(val)
        self._changeable = True

    def __repr__(self):
        return str(bool(self._value))

    def __get__(self, instance, owner):
        return self

    def __set__(self, instance, value):
        if self._changeable: self._value = bool(value)

    def __nonzero__(self):
        return self._value

    def unlock(self):
        self._changeable = True

    def lock(self):
        self._changeable = False











