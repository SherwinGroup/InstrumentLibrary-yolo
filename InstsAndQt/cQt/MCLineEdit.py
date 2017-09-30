from PyQt5 import QtCore, QtGui, QtWidgets
try:
    QString = unicode
except NameError:
    # Python 3
    QString = str

class MCLineEdit(QtWidgets.QLineEdit):
    """
    Subclassed LineEdit which forces QCompleter to be checked
    constantly at arbitrary points in the string, not just
    requiring matches of the total string.

    Note: Hardcoded to require the desired completer to have the
    keywords surrounded in curly braces.
    """
    def keyPressEvent(self, e):
        super(MCLineEdit, self).keyPressEvent(e)
        # stop popup for only holding shift.
        if e.key() in (QtCore.Qt.Key_Shift, QtCore.Qt.Key_Control):
            return
        c = self.c
        c.setCompletionPrefix(self.cursorWord(self.text()))
        if not str(self.text()):
            c.popup().hide()
            return
        cr = self.cursorRect()
        cr.setWidth(c.popup().sizeHintForColumn(0) +
                    c.popup().verticalScrollBar().sizeHint().width())
        c.complete(cr)

    def cursorWord(self, string):
        sentence = QString(string)
        return sentence.mid(sentence.left(self.cursorPosition()).lastIndexOf("{"),
                        self.cursorPosition() -
                        sentence.left(self.cursorPosition()).lastIndexOf("{"))

    def insertCompletion(self,arg):
        self.setText(self.text().replace(self.text().left(self.cursorPosition()).lastIndexOf("{"),
                           self.cursorPosition() -
                           self.text().left(self.cursorPosition()).lastIndexOf("{"),
                           arg))

    def setMultipleCompleter(self, completer):
        self.c = completer
        self.c.setWidget(self)
        self.c.activated.connect(self.insertCompletion)







































