import sys
from PyQt4 import QtSql
from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)

db = QtSql.QSqlDatabase.addDatabase("QODBC")

MDB = r"C:\workspace\PyExcel\sandbox\Att2003.mdb"
DRV = '{Microsoft Access Driver (*.mdb)}'
PWD = 'pw'

db.setDatabaseName("DRIVER={};DBQ={};PWD={}".format(DRV, MDB, PWD))

if not db.open():
    QtGui.QMessageBox.warning(None, "Error", "Database Error: {}".format(db.lastError().text()))
    sys.exit(1)

model = QtSql.QSqlQueryModel()
model.setQuery("SELECT Checkinout FROM Checkinout")