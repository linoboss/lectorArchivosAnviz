import sys
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui, QtSql
from assets.anviz_reader import AnvizReader
import assets.work_day_tools as tool
from assets.printReport import PrintReport

qtCreatorFile = "ui\\assistence_table.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


(ID, DAY, WORKER,
 INTIME_1, OUTTIME_1, INTIME_2, OUTTIME_2, INTIME_3, OUTTIME_3,
 SHIFT, WORKED_TIME, EXTRA_TIME, ABSENT_TIME) = list(range(13))


class AssistenceTableController(Ui_MainWindow, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #self.showMaximized()
        self.stackedWidget.setCurrentIndex(0)

        self.initProcedure()

        self.anvReader = AnvizReader()

        # setting the models and filters

        self.model = QtSql.QSqlRelationalTableModel(self)
        self.model.setTable('WorkDays')
        self.model.setRelation(WORKER, QtSql.QSqlRelation("Userinfo", "Userid",
                                                          "Name"))
        self.model.setRelation(SHIFT, QtSql.QSqlRelation("Schedule", "Schid",
                                                         "Schname"))
        self.model.sort(DAY, Qt.AscendingOrder)
        self.model.select()
        self.model.sort(1, Qt.DescendingOrder)
        for i in range(4):
            if not self.model.canFetchMore(): break
            self.model.fetchMore()
            QtGui.QApplication.processEvents()

        self.calculusModel = tool.CalculusModel(self)
        self.calculusModel.setSourceModel(self.model)
        self.calculusModel.calculateWorkedHours()

        self.nameFilter = QtGui.QSortFilterProxyModel(self)
        self.nameFilter.setSourceModel(self.calculusModel)
        self.nameFilter.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.nameFilter.setFilterKeyColumn(WORKER)

        self.scheduleFilter = QtGui.QSortFilterProxyModel(self)
        self.scheduleFilter.setSourceModel(self.nameFilter)
        self.scheduleFilter.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.scheduleFilter.setFilterKeyColumn(SHIFT)

        self.dateFilter = tool.DateFilterProxyModel(self)
        self.dateFilter.setSourceModel(self.scheduleFilter)

        # configuring the table
        self.tableView.setModel(self.dateFilter)
        self.tableView.setItemDelegate(tool.WorkDayDelegate(self))
        for column in (0, 7, 8): self.tableView.setColumnHidden(column, True)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSortingEnabled(False)

        # setting the initial values of the comboboxes
        self.qworkers.addItems(
            ["Todos"] + self.anvReader.workers_names)
        self.qschedules.addItems(
            ["Todos"] + self.anvReader.schedules)
        self.qdatesfilter.setCurrentIndex(0)

        # setting the initial values of the filters
        self.qdate.setDate(QtCore.QDate().currentDate())
        self.qtodate.setDate(QtCore.QDate().currentDate())
        self.qfromdate.setDate(QtCore.QDate().currentDate())

        # mostrar todos los registros al inicio
        self.nameFilter.setFilterRegExp('.*')
        self.dateFilter.removeFilter()

        # set initial display tab
        self.tabWidget.setCurrentIndex(0)

        self.tableView_total.setItemDelegate(tool.SizeDalegate(200, self))

    @QtCore.pyqtSlot("QString")
    def on_qworkers_currentIndexChanged(self, text):
        if text == "Todos":
            self.nameFilter.setFilterRegExp('.*')
        else:
            self.nameFilter.setFilterRegExp(text)

    @QtCore.pyqtSlot("QString")
    def on_qschedules_currentIndexChanged(self, text):
        if text == "Todos":
            self.scheduleFilter.setFilterRegExp('.*')
        else:
            self.scheduleFilter.setFilterRegExp(text)

    @QtCore.pyqtSlot("QDate")
    def on_qdate_dateChanged(self, d):
        self.dateFilter.setSingleDateFilter(d)

    @QtCore.pyqtSlot("int")
    def on_qdatesfilter_activated(self, option):
        self.dateFilter.removeFilter()
        if option == 1:
            self.dateFilter.setSingleDateFilter(option)

    @QtCore.pyqtSlot()
    def on_qprint_clicked(self):
        print_report = PrintReport(self)
        if print_report.setOutputFileName() == print_report.CANCELED:
            return
        if self.qworkers.currentIndex() == 0:
            print_report.setup(mode="allWorkers")
        else:
            print_report.setup(mode="singleWorker")
        print_report.setSourceModel(self.dateFilter)
        print_report.load_and_create_file()
        self.documentCreated()
        QtGui.QApplication.processEvents()  # flushes the signal queue and prevents multiple clicks

    @QtCore.pyqtSlot()
    def on_qdatesrangebutton_clicked(self):
        self.dateFilter.setRangeDateFilter(self.qfromdate.date(),
                                           self.qtodate.date())

    @QtCore.pyqtSlot("int")
    def on_tabWidget_currentChanged(self, index):
        pass

    @QtCore.pyqtSlot()
    def on_qcalculate_clicked(self):
        self.tableView_total.setModel(
            tool.TotalizeWorkedTime(self.tableView.model())
        )
        self.tableView_total.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def on_printTotals_clicked(self):
        model = self.tableView.model()
        print_report = PrintReport(self)
        if print_report.setOutputFileName() == print_report.CANCELED:
            return
        print_report.setup(mode="totals")
        print_report.setSourceModel(model)
        print_report.load_and_create_file()
        self.documentCreated()
        QtGui.QApplication.processEvents()

    def initProcedure(self):
        pass

    def documentCreated(self):
        from assets.helpers import PopUps
        PopUps.inform_user("El documento fue creado exitosamente")

    def updateModel(self):
        self.model.select()

        while self.model.canFetchMore():
            self.model.fetchMore()

        self.calculusModel = tool.CalculusModel(self)
        self.calculusModel.setSourceModel(self.model)
        self.calculusModel.calculateWorkedHours()

        self.tableView.setItemDelegate(tool.WorkDayDelegate(self))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = AssistenceTableController()
    window.show()
    sys.exit(app.exec())



