import sys
from PyQt4 import QtGui


app = QtGui.QApplication(sys.argv)

messageBox = QtGui.QMessageBox()
messageBox.setText("mensaje")
messageBox.setInformativeText("search?")

messageBox.setStandardButtons(QtGui.QMessageBox.Yes |
                              QtGui.QMessageBox.No)
messageBox.setIcon(QtGui.QMessageBox.Warning)
print(messageBox.exec() == QtGui.QMessageBox.Yes)


sys.exit(app.exec())