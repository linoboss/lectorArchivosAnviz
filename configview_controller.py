import sys
from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, SIGNAL
import assets.sql as sql
import assets.helpers as helpers
from assets.anviz_reader import AnvizReader

# Uic Loader
qtCreatorFile = "ui\\config_dialog.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class ConfigViewController(Ui_MainWindow, QtBaseClass):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        # self.database_path = QtGui.QLabel()
        self.database_path.setText(
            sql.ConfigFile.get("database_path")
        )

    @pyqtSlot()
    def on_changeDB_clicked(self):
        filename = \
            QtGui.QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo Access",
                sql.ConfigFile().get("database_path"),
                "Access Database (*.mdb)"
            )

        if filename:
            sql.ConfigFile().set(
                "database_path", filename
            )
            self.database_path.setText(filename)

            self.emit(SIGNAL('dbChanged()'))

    @pyqtSlot()
    def on_init_clicked(self):
        if self.confirmar():
            helpers.PopUps.inform_user("Action not yet implemented!")
            pass
        else:
            return

    @pyqtSlot()
    def on_erase_clicked(self):
        if self.confirmar():
            anvRgs = sql.AnvizRegisters()
            anvRgs.deleteRegistersFrom('WorkDays')

            self.emit(SIGNAL('registersErased()'))
        else:
            return

    @pyqtSlot()
    def on_qupdate_clicked(self):
        if self.confirmar():
            anvReader = AnvizReader()
            anvReader.updateTable()
        else:
            return

    @pyqtSlot()
    def on_buttonBox_accepted(self):
        pass

    def confirmar(self):
        messageBox = QtGui.QMessageBox()
        messageBox.setStandardButtons(QtGui.QMessageBox.Yes |
                                      QtGui.QMessageBox.No)
        messageBox.setIcon(QtGui.QMessageBox.Question)
        messageBox.setText("Esta seguro?")
        return messageBox.exec() == QtGui.QMessageBox.Yes


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    schConfig_controller = ConfigViewController()
    schConfig_controller.show()
    sys.exit(app.exec())