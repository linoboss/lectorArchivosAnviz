import sys, os
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui, QtSql

qtCreatorFile = "menubar.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class Window(Ui_MainWindow, QtBaseClass):
    def __init__(self,  parent = None):
        super().__init__(parent)
        self.setupUi(self)

    @QtCore.pyqtSlot("QAction*")
    def on_menubar_triggered(self, action):
        # action = QtGui.QAction()
        print(action is self.action1)

app = QtGui.QApplication(sys.argv)

window = Window()
window.show()

sys.exit(app.exec())