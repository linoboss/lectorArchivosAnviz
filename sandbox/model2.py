from PyQt4 import QtSql
from PyQt4 import QtCore
from PyQt4 import QtGui
import assets.work_day_tools as tool
from pprint import pprint


(ID, DAY, WORKER,
 INTIME_1, OUTTIME_1, INTIME_2, OUTTIME_2, INTIME_3, OUTTIME_3,
 SHIFT, WORKED_TIME, EXTRA_TIME, ABSENT_TIME) = list(range(13))


class MainForm(QtGui.QDialog):
    def __init__(self):

        QtGui.QDialog.__init__(self)

        db = QtSql.QSqlDatabase.addDatabase("QODBC")

        MDB = r"C:\workspace\PyExcel\Att2003 - copia.mdb"
        DRV = '{Microsoft Access Driver (*.mdb)}'
        PWD = 'pw'
        db.setDatabaseName("DRIVER={};DBQ={};PWD={}".format(DRV, MDB, PWD))

        if not db.open():
            QtGui.QMessageBox.warning(None, "Error", "Database Error: {}".format(db.lastError().text()))
            sys.exit(1)

        self.model = QtSql.QSqlTableModel(self, db)
        self.model.setTable("WorkDays")
        self.model.select()

        while self.model.canFetchMore():
            self.model.fetchMore()

        self.proxymodel = tool.CalculusModel(self)
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.calculateWorkedHours()

        self.scheduleFilter = QtGui.QSortFilterProxyModel(self)
        self.scheduleFilter.setSourceModel(self.proxymodel)
        self.scheduleFilter.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.scheduleFilter.setFilterKeyColumn(DAY)

        self.printFilter = tool.DateFilterProxyModel()
        self.printFilter.setSourceModel(self.scheduleFilter)

        delegate = tool.WorkDayDelegate(self)

        self.tableView = QtGui.QTableView(self)
        self.tableView.setModel(self.printFilter)
        self.tableView.setItemDelegate(delegate)
        self.tableView.setSortingEnabled(True)

        self.tableView.clicked.connect(self.tableClicked)

        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.addWidget(self.tableView)
        self.scheduleFilter.setFilterRegExp("2015-10-27")

    def tableClicked(self, index):
        pprint(self.getRegister(index.row()))

    def getRegister(self, row):
        print(self.printFilter.rowCount())
        asd = [self.printFilter.index(row, 0).data()]
        for column in range(13):
            if column == ID:
                continue
            elif column == INTIME_3:
                continue
            elif column == OUTTIME_3:
                continue
            elif column == SHIFT:
                continue
            elif INTIME_1 <= column <= OUTTIME_3:
                qdate = self.printFilter.index(row, column).data().toString("hh:mm")
                if qdate == QtCore.QTime():
                    item = '--:--'
                else:
                    item = qdate
            elif column >= WORKED_TIME:
                item = self.printFilter.index(row, column).data().toString("hh:mm")
            else:
                item = self.printFilter.index(row, column).data()
            asd.append(item)
        return asd


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ventana = MainForm()
    ventana.setGeometry(100, 100, 1100, 500)
    ventana.show()
    sys.exit(app.exec_())
