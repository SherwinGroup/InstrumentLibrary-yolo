"""
PyQt4 would print exceptions but not exit the program
PyQt5 changed that behaviour, now crashing, and worse, without printing
the error.

Looking around, I can see the point that programs should exit when an
exception is hit, but I'm not going to risk expensive software to
fit into this ideology. I'm going to try to be better at fixing
errors when they occur, but it's not worth $150k.

I've put this here because I'm pretty sure every library I use for
hardware calls this module, and it's when using hardware that I
can't allow crashing.

found here:
https://stackoverflow.com/questions/34363552/python-process-finished-with-exit-code-1-when-using-pycharm-and-pyqt5/37837374#37837374
https://stackoverflow.com/questions/38020020/pyqt5-app-exits-on-error-where-pyqt4-app-would-not

"""
print("WARNING: OVERRIDING PYTHON EXCEPTION HANDLING")
print("   InstsAndQt __init__ file")
import sys
import traceback
def my_excepthook(type, value, tback):
    # log the exception here
    # print(type, value, tback)
    # traceback.print_exception(type, value, tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)

sys.excepthook = my_excepthook