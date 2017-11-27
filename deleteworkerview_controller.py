import sys
from PyQt4 import uic
from PyQt4 import QtGui, QtSql, QtCore
import assets.sql as sql
import assets.helpers as helpers
import assets.work_day_tools as tool

# Uic Loader
qtCreatorFile = "ui\\deleteworkerview.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


(USERID, NAME, SEX, ISACTIVE) = range(4)
ISACTIVE = 28


class DeleteWorkerView_controller(Ui_MainWindow, QtBaseClass):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent

        self.model = QtSql.QSqlRelationalTableModel(self)
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.setTable('Userinfo')
        self.model.select()

        self.model.setHeaderData(USERID, QtCore.Qt.Horizontal, "ID en\nCaptahuellase")
        self.model.setHeaderData(NAME, QtCore.Qt.Horizontal, "Nombre")
        self.model.setHeaderData(SEX, QtCore.Qt.Horizontal, "Sexo")
        self.model.setHeaderData(ISACTIVE, QtCore.Qt.Horizontal, "Esta\nActivo?")

        # self.tableView = QtGui.QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setItemDelegate(CustomDelegate())
        from itertools import chain
        for hc in chain(range(3, 28), range(29, 40)):
            self.tableView.hideColumn(hc)
        self.tableView.setSelectionMode(QtGui.QTableView.SingleSelection)
        self.tableView.setSelectionBehavior(QtGui.QTableView.SelectRows)

    @QtCore.pyqtSlot()
    def on_qdelete_clicked(self):
        # QtGui.QTableView().selectedIndexes()
        index = self.tableView.selectedIndexes()[0].data()
        sql.AnvizRegisters().deleteRegister("Userinfo", index)
        self.model.select()


class CustomDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        column = index.column()
        item = index.data()
        if column == ISACTIVE:
            painter.save()
            if option.state & QtGui.QStyle.State_Selected:
                painter.setPen(QtCore.Qt.white)
                painter.setBrush(option.palette.highlightedText())
                painter.fillRect(option.rect, option.palette.highlight())
            isActive = 'Si' if item else 'No'
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, isActive)
            painter.restore()
        else:
            QtSql.QSqlRelationalDelegate().paint(painter, option, index)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    sql.AnvizRegisters()
    DeleteWorkerView_controller().exec()
    sys.exit(app.exec())
