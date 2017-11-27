import sys
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui, QtSql
from assets.anviz_reader import AnvizReader

ID, DAY, WORKER, INTIME_1, OUTTIME_1, INTIME_2, OUTTIME_2, INTIME_3, OUTTIME_3,  SHIFT = list(range(10))


class WorkDayDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        document = QtGui.QTextDocument()

        color = QtGui.QColor(255, 255, 255)

        if index.column() == DAY:
            datetime = index.model().data(index)
            if datetime.date().day() % 2 == 0:

                color = QtGui.QColor(200, 200, 255)
            else:
                color = QtGui.QColor(200, 255, 200)
            text = str(datetime.date().toString())

        elif index.column() == WORKER:
            worker = index.model().data(index)
            text = worker

        else:
            date = index.model().data(index)
            text = str(date.time().toString())

        painter.save()
        painter.fillRect(option.rect, color)
        painter.translate(option.rect.x(), option.rect.y())
        document.setHtml(text)
        document.drawContents(painter)
        painter.restore()

    def setEditorData(self, editor, index):
        print('1')
        pass

    def createEditor(self, parent, option, index):
        print('2')
        pass

"""
    def sizeHint(self, option, index):
        pass

    def createEditor(self, parent, option, index):
        pass

    def commitAndCloseEditor(self):
        pass



    def setModelData(self, editor, model, index):
        pass
"""

qtCreatorFile = "tableView.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class WorkCalculus(Ui_MainWindow, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        anvReader = AnvizReader()
        anvReader.updateTable()

        self.model = QtSql.QSqlRelationalTableModel(self)
        self.model.setTable('WorkDays')
        self.model.setRelation(WORKER, QtSql.QSqlRelation("Userinfo", "Userid", "Name"                                                                                        ""))
        self.model.select()

        self.proxymodel = QtGui.QSortFilterProxyModel(self)
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.sort(DAY, Qt.AscendingOrder)

        # self.tableView = QtGui.QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setItemDelegate(WorkDayDelegate(self))
        for column in (0, 7, 8, 9): self.tableView.setColumnHidden(column, True)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(False)
        self.proxymodel.sort(1, Qt.AscendingOrder)
        # self.tableView.setSelectionBehavior(QtGui.QTableView.SelectRows)
        # self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        ID, A, B, C = 0, 1, 2, 3
        self.mapper = QtGui.QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.addMapping(self.a, A)
        self.mapper.addMapping(self.b, B)
        self.mapper.addMapping(self.c, C)
        self.mapper.addMapping(self.id, ID)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    wc = WorkCalculus()
    wc.show()

    sys.exit(app.exec())
