import sys
from PyQt4 import QtCore, QtGui, QtSql
from assets.work_day_tools import DateFilterProxyModel
from assets.anviz_reader import AnvizReader
from assets.dates_tricks import MyDates as md


class HolidayMapper(QtCore.QObject):
    VACATIONS, DAYOFF, HOLIDAY, SPECIAL_DATE = range(100, 104)

    def __init__(self):
        super().__init__()

        holiday_model = QtSql.QSqlRelationalTableModel(self)
        holiday_model.setTable("Holiday")
        holiday_model.select()
        self.holiday_model = DateFilterProxyModel(self)
        self.holiday_model.setFilterKeyColumn(holiday_model.fieldIndex("BDate"))
        self.holiday_model.setSourceModel(holiday_model)

        # Special dates model setup
        """
        The specialdates model uncomprises the specialdates
        from { BDate=(2016, 1, 2) -> Days=3 }
        to { [(2016, 1, 2), (2016, 1, 3), (2016, 1, 4)] }
        """
        specialdates = []
        for row in range(holiday_model.rowCount()):
            record = holiday_model.record(row)
            date = record.value("BDate")
            assert isinstance(date, QtCore.QDateTime)
            if date.date().year() == 2000:
                continue
            for day in range(record.value("Days")):
                specialdates.append(
                    [
                        record.value("Name"),
                        date.addDays(day)
                    ]
                )
        else:
            if not specialdates:
                specialdates = [[]]
        specialdates_model = HolidaysModel(specialdates)
        specialdates_model.setHeaders("Name Date".split())
        self.specialdates_model = DateFilterProxyModel(self)
        self.specialdates_model.setFilterKeyColumn(holiday_model.fieldIndex("Date"))
        self.specialdates_model.setSourceModel(specialdates_model)

        # Vacations model setup
        """
        The vacations model uncomprises the daysoff type vacation
        from { BDate=(2016, 1, 2) -> TDate=(2016, 1, 4) }
        to { [(2016, 1, 2), (2016, 1, 3), (2016, 1, 4)] }
        """
        daysoff_model = QtSql.QSqlRelationalTableModel(self)
        daysoff_model.setTable("WorkerPass")
        daysoff_model.select()

        vacations = []
        daysoff = []
        for row in range(daysoff_model.rowCount()):
            record = daysoff_model.record(row)
            worker = record.value("Userid")
            bdate = record.value("BDate").toPyDateTime().date()
            tdate = record.value("TDate").toPyDateTime().date()
            descrip = record.value("Description")
            type_ = record.value("Type")
            dates_range = md.dates_range(bdate, tdate)

            for date in dates_range:
                if type_ == 1:
                    vacations.append(
                        [
                            worker,
                            date,
                            descrip
                        ]
                    )
                elif type_ == 2:
                    daysoff.append(
                        [
                            worker,
                            date,
                            descrip
                        ]
                    )
        if not vacations:
            vacations = [[]]
        if not daysoff:
            daysoff =[[]]

        vacation_model = HolidaysModel(vacations)
        vacation_model.setHeaders("worker date descrip".split())
        worker_model = QtGui.QSortFilterProxyModel(self)
        worker_model.setSourceModel(vacation_model)
        worker_model.setFilterKeyColumn(0)
        self.vacation_model = DateFilterProxyModel(self)
        self.vacation_model.setFilterKeyColumn(1)
        self.vacation_model.setSourceModel(worker_model)

        dayoff_model = HolidaysModel(daysoff)
        dayoff_model.setHeaders("worker date descrip".split())
        worker1_model = QtGui.QSortFilterProxyModel(self)
        worker1_model.setSourceModel(dayoff_model)
        worker1_model.setFilterKeyColumn(0)
        self.daysoff_model = DateFilterProxyModel(self)
        self.daysoff_model.setFilterKeyColumn(1)
        self.daysoff_model.setSourceModel(worker1_model)

    def checkdate(self, date):
        # First check for holidays
        self.holiday_model.setSingleDateFilter(QtCore.QDate(2000,
                                                            date.month(),
                                                            date.day()))
        if self.holiday_model.rowCount():
            return (True,
                    self.HOLIDAY,
                    self.holiday_model.index(0, self.holiday_model.fieldIndex("Name")).data())
        # Second, check for Special Dates
        self.specialdates_model.setSingleDateFilter(date)
        if self.specialdates_model.rowCount():
            return (True,
                    self.SPECIAL_DATE,
                    self.specialdates_model.index(0, self.specialdates_model.fieldIndex("Name")).data())

    def checkworker(self, worker, date):
        worker_model = self.vacation_model.sourceModel()
        worker_model.setFilterRegExp(worker)
        self.vacation_model.setSingleDateFilter(date)
        if self.vacation_model.rowCount():
            return (True,
                    self.VACATIONS,
                    self.vacation_model.index(0, 2).data())

        worker_model = self.vacation_model.sourceModel()
        worker_model.setFilterRegExp(worker)
        self.daysoff_model.setSingleDateFilter(date)
        if self.daysoff_model.rowCount():
            return (True,
                    self.DAYOFF,
                    self.daysoff_model.index(0, 2).data())


class HolidaysModel(QtCore.QAbstractTableModel):
    def __init__(self, _data, parent=None):
        super().__init__(parent)
        self._data = _data
        self._headers = [None for i in range(self.columnCount())]

    def fieldIndex(self, field):
        assert isinstance(self._headers, list)
        return self._headers.index(field)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data[0])

    def data(self, index, role=None):
        row = index.row()
        column = index.column()
        return self._data[row][column]

    def setHeaders(self, headers):
        # assert len(headers) == self.columnCount()
        self._headers = headers


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    a = AnvizReader()

    holiday_mapper = HolidayMapper()
    response = holiday_mapper.checkdate(QtCore.QDate(2016, 1, 1))
    print(response)
    response = holiday_mapper.checkworker("10", QtCore.QDate(2016, 10, 14))
    print(response)
    response = holiday_mapper.checkworker("10", QtCore.QDate(2016, 10, 28))
    print(response)
