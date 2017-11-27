import sys
from PyQt4 import uic
from PyQt4 import QtGui, QtSql, QtCore
import assets.sql as sql
import assets.helpers as helpers
import assets.work_day_tools as tool

# Uic Loader
qtCreatorFile = "ui\\checkinoutview.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


(LOGID, USERID, CHECKTIME, CHECKTYPE,
 SENSORID, CHECHED, WORKTYPE, ATTFLAG) = range(8)


class CheckinoutViewController(Ui_MainWindow, QtBaseClass):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent

        self.model = QtSql.QSqlRelationalTableModel(self)
        self.model.setTable('Checkinout')
        self.model.setRelation(USERID,
                               QtSql.QSqlRelation(
                                   "Userinfo",
                                   "Userid", "Name"))
        self.model.select()

        self.dateFilter = tool.DateFilterProxyModel(self)
        self.dateFilter.setSourceModel(self.model)
        self.dateFilter.setFilterKeyColumn(self.model.fieldIndex("CheckTime"))

        self.tableView.setModel(self.dateFilter)
        self.tableView.setItemDelegate(CustomDelegate())
        for hc in (0, 3, 4, 5, 6, 7):
            self.tableView.hideColumn(hc)
        self.tableView.sortByColumn(CHECKTIME, QtCore.Qt.AscendingOrder)
        self.tableView.setSortingEnabled(True)
        self.tableView.resizeColumnsToContents()

        curr_date = QtCore.QDate().currentDate()
        one_month_back = curr_date.addMonths(-1)
        self.dateEdit.setDate(curr_date)

        self.dateFilter.removeFilter()

        self.model.setFilter("CheckTime >= #{}#".format(one_month_back))

    @QtCore.pyqtSlot("QDate")
    def on_dateEdit_dateChanged(self, date):
        self.dateFilter.setSingleDateFilter(date)

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        self.dateFilter.removeFilter()

    @QtCore.pyqtSlot()
    def on_qloadmore_clicked(self):
        self.model.setFilter("")
        self.model.select()
        while self.model.canFetchMore():
            self.model.fetchMore()
            QtGui.QApplication.processEvents()


class CustomDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        document = QtGui.QTextDocument()
        column = index.column()
        item = index.model().data(index)

        if column == CHECKTIME:
            text = item.toString('yyyy/MM/dd | hh:mm')
        else:
            text = str(item)

        painter.save()
        painter.translate(option.rect.x(), option.rect.y())
        document.setHtml(text)
        document.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        column = index.column()
        if column == 1:
            return QtCore.QSize(175, 20)
        else:
            return QtCore.QSize(125, 20)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    sql.AnvizRegisters()

    checkioview = CheckinoutViewController()
    checkioview.show()

    sys.exit(app.exec())
