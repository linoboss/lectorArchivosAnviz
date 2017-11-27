import sys
from PyQt4 import uic
from PyQt4 import QtSql, QtCore, QtGui
from PyQt4.QtSql import QSqlDatabase
from PyQt4.QtCore import SIGNAL, Qt, pyqtSlot
import datetime as dt


# Uic Loader
qtCreatorFile = "tableView.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class LearningSqlModel(Ui_MainWindow, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        db = QSqlDatabase.addDatabase("QODBC")
        MDB = r"C:\workspace\PyExcel\sandbox\Att2003.mdb"
        DRV = '{Microsoft Access Driver (*.mdb)}'
        PWD = 'pw'

        db.setDatabaseName("DRIVER={};DBQ={};PWD={}".format(DRV, MDB, PWD))
        if not db.open():
            QtGui.QMessageBox.warning(None, "Error", "Database Error: {}".format(db.lastError().text()))
            sys.exit(1)

        self.model = QtSql.QSqlTableModel(self)
        self.model.setTable('Checkinout')

        # Headings indexes
        ID, A, B, C = 0, 1, 2, 3

        self.model.sort(B, Qt.AscendingOrder)
        self.model.select()

        self.proxymodel = QtGui.QSortFilterProxyModel(self)
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.sort(1, Qt.AscendingOrder)
        self.proxymodel.setDynamicSortFilter(True)
        self.proxymodel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        # self.tableView = QTableView()
        self.tableView.setModel(self.proxymodel)
        self.tableView.setSelectionMode(QtGui.QTableView.SingleSelection)
        self.tableView.setSelectionBehavior(QtGui.QTableView.SelectRows)
        for column in [4, 5, 6, 7]: self.tableView.setColumnHidden(column, True)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.mapper = QtGui.QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QtGui.QDataWidgetMapper.AutoSubmit)
        self.mapper.setModel(self.proxymodel)
        self.mapper.addMapping(self.a, A)
        self.mapper.addMapping(self.b, B)
        self.mapper.addMapping(self.c, C)
        self.mapper.addMapping(self.id, ID)

        query = QtSql.QSqlQuery("SELECT Userid FROM Userinfo WHERE int(Userid) < 100")
        print(query.lastError().text())
        while query.next():
            # self.workersList = QtGui.QComboBox()
            self.workersList.addItem(query.value(0))

    @pyqtSlot("QModelIndex")
    def on_tableView_clicked(self, index):
        self.mapper.setCurrentIndex(index.row())

    @pyqtSlot("QString")
    def on_workersList_activated(self, worker):
        self.proxymodel.setFilterKeyColumn(1)
        self.proxymodel.setFilterRegExp("^{}$".format(worker))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = LearningSqlModel()
    window.show()
    sys.exit(app.exec())

