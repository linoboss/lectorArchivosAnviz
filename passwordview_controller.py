import sys
from PyQt4 import uic
from PyQt4 import QtGui, QtSql, QtCore

# Uic Loader
qtCreatorFile = "ui\\passwordview.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class Passwordview_Controller(Ui_MainWindow, QtBaseClass):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.connect(self, QtCore.SIGNAL("correctPassword()"), self.accept)

    @QtCore.pyqtSlot()
    def on_qok_clicked(self):
        text = self.lineEdit.text()
        password = "1234321"
        if text == password:
            self.emit(QtCore.SIGNAL("correctPassword()"))
        else:
            self.lineEdit.setText("")


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    pss = Passwordview_Controller()
    print(pss.exec())

