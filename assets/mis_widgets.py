__author__ = 'Lino Bossio'
from PyQt4.QtGui import *

class MyQTable(QTableWidget):
    def __init__(self, parent):
        super(MyQTable, self).__init__(parent)
        self._row = 1

    def append(self, item, column=0):
        if type(item) == list:
            for i in item:
                newItem = QTableWidgetItem(i)
                self.setItem(self._row, column, newItem)
                column += 1
            index_increment = 1
        else:
            newItem = QTableWidgetItem(item)
            index_increment = 1
            self.setItem(self._row, column, newItem)

        self._row += index_increment

    def skip_line(self):
        self._row += 1

    def goto_line(self, line):
        self._row = line

    def index(self):
        return self._row
