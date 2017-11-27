__author__ = 'SG_LAURA'
from PyQt4 import QtGui, QtSql
import sys
import assets.sql as sql
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    a = sql.AnvizRegisters('C:\\ControlHorario\\PyExcel\\sandbox\\Att2003.mdb')

    print(QtSql.QSqlDatabase().database().tables())
    print('Vacations' in QtSql.QSqlDatabase().database().tables())
    sys.exit(app.exec())