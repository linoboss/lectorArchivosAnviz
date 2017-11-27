import sys
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui, QtSql
from assets.anviz_reader import AnvizReader
import assets.work_day_tools as tool
import assets.dates_tricks as md
import assets.sql as sql
import assets.helpers as helpers
import time


# Uic Loader
qtCreatorFile = "progressBars.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class ProgressBars(Ui_MainWindow, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.progressBar1.setValue(0)
        self.progressBar2.setValue(0)


class Increment(QtCore.QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def increment(self):
        for i in range(101):
            self.window.progressBar1.setValue(i)
            time.sleep(0.02)

        self.emit(QtCore.SIGNAL("finished()"))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = ProgressBars()
    window.show()

    inc = Increment(window)

    thread = QtCore.QThread()
    inc.moveToThread(thread)

    QtCore.QObject().connect(thread, QtCore.SIGNAL("started()"), inc.increment)
    QtCore.QObject().connect(inc, QtCore.SIGNAL("finished()"), thread.quit)
    QtCore.QObject().connect(inc, QtCore.SIGNAL("finished()"), thread.deleteLater)
    QtCore.QObject().connect(thread, QtCore.SIGNAL("finished()"), inc.deleteLater)

    thread.start()

    sys.exit(app.exec())

