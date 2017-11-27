__author__ = 'SG_LAURA'
from PyQt4 import QtGui, QtSql
import sys
import assets.sql as sql
import datetime


app = QtGui.QApplication(sys.argv)
a = sql.AnvizRegisters('C:\\ControlHorario\\PyExcel\\sandbox\\Att2003.mdb')

print(QtSql.QSqlDatabase().database().tables())
print('Vacations' in QtSql.QSqlDatabase().database().tables())





query = QtSql.QSqlQuery()

date = datetime.datetime(2014, 9, 7).strftime("%y-%m-%d")
query.exec_("""
    UPDATE WorkDays
    SET Holidayid={}
    WHERE (day=#{}#)
""".format(1, date))


sys.exit(app.exec())