import sys
from PyQt4 import uic
from PyQt4.QtCore import Qt, QDateTime, QDate, QVariant, SIGNAL
from PyQt4.QtSql import QSqlQuery, QSqlTableModel, QSqlDatabase
from PyQt4.QtGui import QTableView, QMessageBox, QApplication, QDialog,\
    QDataWidgetMapper, QAbstractItemView
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
            QMessageBox.warning(None, "Error", "Database Error: {}".format(db.lastError().text()))
            sys.exit(1)

        self.model = QSqlTableModel(self)
        self.model.setTable('Checkinout')

        # Headings indexes
        ID, A, B, C = 0, 1, 2, 3

        self.model.sort(B, Qt.AscendingOrder)
        self.model.select()

        #self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        for column in [4, 5, 6, 7]: self.tableView.setColumnHidden(column, True)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.mapper = QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
        self.mapper.setModel(self.model)
        self.mapper.addMapping(self.a, A)
        self.mapper.addMapping(self.b, B)
        self.mapper.addMapping(self.c, C)
        self.mapper.addMapping(self.id, ID)
        self.mapper.toFirst()

    def saveRecord(self):
        self.model.submitAll()

    def getHorizontalHeaders(self):
        headerData = [self.model.headerData(i, Qt.Horizontal, Qt.DisplayRole)
                      for i in range(self.model.columnCount())]
        return headerData

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LearningSqlModel()
    window.show()
    print(window.getHorizontalHeaders())
    sys.exit(app.exec())

