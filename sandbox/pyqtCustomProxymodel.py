import sys
from PyQt4 import uic
from PyQt4 import QtSql, QtCore, QtGui
from PyQt4.QtSql import QSqlDatabase
from PyQt4.QtCore import SIGNAL, Qt, pyqtSlot
import datetime as dt


# Uic Loader
qtCreatorFile = "table.ui"
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

        self.proxymodel = MyProxyModel(self)
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.sort(1, Qt.AscendingOrder)
        self.proxymodel.setDynamicSortFilter(True)
        self.proxymodel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        #self.tableView = QTableView()
        self.tableView.setModel(self.proxymodel)
        self.tableView.setSelectionMode(QtGui.QTableView.SingleSelection)
        self.tableView.setSelectionBehavior(QtGui.QTableView.SelectRows)
        for column in [4, 5, 6, 7]: self.tableView.setColumnHidden(column, True)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(True)
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        query = QtSql.QSqlQuery("SELECT Userid FROM Userinfo WHERE int(Userid) < 100")
        print(query.lastError().text())
        while query.next():
            # self.workersList = QtGui.QComboBox()
            self.workersList.addItem(query.value(0))

    @QtCore.pyqtSlot()
    def on_button_clicked(self):
        print('aki')
        self.proxymodel.d1 = self.d1.date()
        self.proxymodel.d2 = self.d2.date()
        self.proxymodel.invalidateFilter()


class MyProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.filterFunctions = {}
        self.i = 0
        self.d1 = QtCore.QDate(2014,1,1)
        self.d2 = QtCore.QDate(2016,1,1)

    def addFilterFunction(self, name, new_func):
        self.filterFunctions[name] = new_func
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        """
        Reimplemented from base class
        Executes a set of tests from the filterFunctions, if any fails, the row is rejected
        """
        dateindex = self.sourceModel().index(row, 2, parent)
        date = self.sourceModel().data(dateindex).date()
        return self.d1 <= date <= self.d2

    def lessThan(self, left, right):
        """
        Return the comparation of 2 rows
        :param left: QModelIndex
        :param right: QModelIndex_1
        :return:
        """
        leftdate = self.sourceModel().data(left)
        rightdate = self.sourceModel().data(right)
        if isinstance(left, QtCore.QDateTime):
            return leftdate < rightdate
        else: return True


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = LearningSqlModel()
    window.show()
    sys.exit(app.exec())

