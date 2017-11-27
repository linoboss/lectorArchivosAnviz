import sys
from PyQt4 import QtSql
from PyQt4 import QtGui
from PyQt4 import QtCore
import datetime as dt
from pprint import pprint


app = QtGui.QApplication(sys.argv)

db = QtSql.QSqlDatabase.addDatabase("QODBC")

MDB = r"C:\workspace\PyExcel\sandbox\Att2003.mdb"
DRV = '{Microsoft Access Driver (*.mdb)}'
PWD = 'pw'

db.setDatabaseName("DRIVER={};DBQ={};PWD={}".format(DRV, MDB, PWD))

if not db.open():
    QtGui.QMessageBox.warning(None, "Error", "Database Error: {}".format(db.lastError().text()))
    sys.exit(1)

query = QtSql.QSqlQuery()

query.exec_("DELETE FROM WorkDays "
            "WHERE CheckTime=#{}#".format(dt.datetime()))
i = 0
for name in ("Lino", "Febri", "Anderson"):
    query.exec_("INSERT INTO othertable (id, name) VALUES ({}, '{}')".format(i, name))
    i += 1
# Pg 451.
# Para evitar errores con las comillas y demas:
query.prepare("INSERT INTO setup (id, a, b, c)"
              "VALUES (:id, :a, :b, :c)")
data = [["1", dt.datetime(2011, 1, 1), 0],
        ["2", dt.datetime(2002, 2, 2), 1],
        ["3", dt.datetime(2001, 3, 3), 2]]
i = 0
for a, b, c in data:
    query.bindValue(":id", i)
    query.bindValue(":a", a)
    query.bindValue(":b", QtCore.QDateTime(b))
    query.bindValue(":c", c)
    query.exec_()
    i += 1

query.exec_("SELECT id, a, b, c FROM setup")
print('SETUP in disc:')
while query.next():
    print(query.value(0), query.value(1), query.value(2), query.value(3))

print(dir(query.lastError()))
print(query.lastError().number())