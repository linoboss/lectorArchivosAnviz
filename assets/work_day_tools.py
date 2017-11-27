from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui, QtSql
from assets.dates_tricks import MyDates as md
from assets import helpers

(ID, DAY, WORKER,
 INTIME_1, OUTTIME_1, INTIME_2, OUTTIME_2, INTIME_3, OUTTIME_3,
 SHIFT, WORKED_TIME, EXTRA_TIME, ABSENT_TIME) = list(range(13))


class WorkDayDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.holiday = {}
        self.workerpass = {}

        self.shift_map = {"Diurno": 4, "Nocturno": 2}
        self.week_workable_days = helpers.week_workable_days()
        self.holiday = helpers.table_to_dictionary("Holiday")
        self.workerpass = helpers.table_to_dictionary("WorkerPass")

    def paint(self, painter, option, index):
        document = QtGui.QTextDocument()
        column = index.column()
        row = index.row()
        model = index.model()
        item = model.data(index)

        # Configuration by Column
        color = QtGui.QColor(255, 255, 255)
        if column == DAY:
            if item.date().day() % 2 == 0:
                color = QtGui.QColor(200, 200, 255)
            else:
                color = QtGui.QColor(200, 255, 200)
            text = md.dateToString(item.toPyDateTime().date())

        elif column == WORKER:
            text = str(item)

        elif column == SHIFT:
            text = str(item)
        elif isinstance(item, QtCore.QDateTime):
            text = item.toString("hh:mm")
        elif isinstance(item, QtCore.QTime):
            text = item.toString('hh:mm')
        elif column == 13:
            text = str(self.holiday[item][1]) if isinstance(item, int) else ''
        elif column == 14:
            if isinstance(item, int):
                if self.workerpass[item][-1] == 2:
                    text = self.workerpass[item][-2]
                else:
                    text = "Vacaciones"
            else:
                text = ''
        else:
            text = str(item)

        # Configuration by Row
        date = model.index(row, DAY).data().date()
        day_number = md.dayNumber(date.year(), date.month(), date.day())
        shift = self.shift_map[model.index(row, SHIFT).data()]
        isnotregular = day_number not in self.week_workable_days[shift]
        isholiday = isinstance(model.index(row, 13).data(), int)
        isdayoff = isinstance(model.index(row, 14).data(), int)

        if column > DAY:
            if isdayoff:
                color = QtGui.QColor(220, 255, 220)
            elif isholiday:
                color = QtGui.QColor(255, 255, 200)
            elif isnotregular:
                color = QtGui.QColor(240, 240, 240)

        painter.save()
        painter.fillRect(option.rect, color)
        painter.translate(option.rect.x(), option.rect.y())
        document.setHtml(text)
        document.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        column = index.column()
        if column == DAY:
            return QtCore.QSize(180, 20)
        elif column == WORKER:
            return QtCore.QSize(150, 20)
        return QtCore.QSize(100, 20)


class DateFilterProxyModel(QtGui.QSortFilterProxyModel):
    """
    Filters the dates by range or individually by reimplementing
    the lessThan and filterAcceptsRow methods
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.single_date = None
        self.from_date = None
        self.to_date = None
        self.mode = "no filter"
        self.key_column = DAY
        self.ignoreYear = False

    def setFilterKeyColumn(self, column):
        self.key_column = column

    def removeFilter(self):
        self.mode = "no filter"
        self.invalidateFilter()

    def fieldIndex(self, field):
        return self.sourceModel().fieldIndex(field)

    def setSingleDateFilter(self, date):
        self.mode = "single"
        self.single_date = date
        self.invalidateFilter()

    def setRangeDateFilter(self, from_date, to_date):
        self.mode = "range"
        self.from_date = from_date
        self.to_date = to_date
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        """
        Reimplemented from base class
        Executes a set of tests from the filterFunctions, if any fails, the row is rejected
        """
        date = self.sourceModel().index(row, self.key_column, parent).data()
        if date is None:
            return False

        if isinstance(date, QtCore.QDateTime):
            date = date.date()

        if self.mode == "single":
            return date == self.single_date

        elif self.mode == "range":
            fdate = self.from_date
            tdate = self.to_date

            # This segment allows to compare dates in the conext of
            # the cyclical nature of the calendar
            if self.ignoreYear:
                date = QtCore.QDate(2000,
                                    date.month(),
                                    date.day())
                fdate = QtCore.QDate(2000,
                                     fdate.month(),
                                     fdate.day())
                tdate = QtCore.QDate(2000,
                                     tdate.month(),
                                     tdate.day())

            return fdate <= date <= tdate

        elif self.mode == "no filter":
            return True
        else:
            raise ValueError(str(self.mode) + " is not a valid mode")

    def lessThan(self, left, right):
        """
        Return the comparation of 2 rows
        :param left: QModelIndex
        :param right: QModelIndex_1
        :return:
        """
        leftdate = self.sourceModel().data(left)
        rightdate = self.sourceModel().data(right)
        if isinstance(left, QtCore.QDateTime):
            return leftdate < rightdate
        else: return True


class CalculusModel(QtGui.QIdentityProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.calculations = []

        self.shift_map = {"Diurno": 4, "Nocturno": 2}
        self.week_workable_days = helpers.week_workable_days()
        self.holiday = helpers.table_to_dictionary("Holiday", 0)
        self.workerpass = helpers.table_to_dictionary("WorkerPass", 0)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.sourceModel().columnCount()

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.sourceModel().rowCount()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return Qt.AlignVCenter |\
                       Qt.AlignHCenter
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == DAY:
                return "Dia"
            elif section == WORKER:
                return "Trabajador"
            elif (section == INTIME_1 or
                  section == INTIME_2 or
                  section == INTIME_3):
                return "Entrada"
            elif (section == OUTTIME_1 or
                  section == OUTTIME_2 or
                  section == OUTTIME_3):
                return "Salida"
            elif section == SHIFT:
                return "Turno"
            elif section == WORKED_TIME:
                return "Tiempo\nTrabajado"
            elif section == EXTRA_TIME:
                return "Tiempo\nExtra"
            elif section == ABSENT_TIME:
                return "Tiempo\nAusente"
            elif section == 13:
                return "Fecha\nEspecial"
            elif section == 14:
                return "Permiso\nLaboral"
        return str(section)

    def data(self, index, role=None):
        row = index.row()
        column = index.column()
        if not index.isValid():
            return None
        item = self.sourceModel().data(self.sourceModel().index(row, column))

        if role == Qt.EditRole:
            return None
        elif role == Qt.DisplayRole:
            if column == DAY:
                return item
            elif column >= WORKED_TIME:
                if self.calculations:
                    if column == 10:
                        return self.calculations[row][0]
                    elif column == 11:
                        return self.calculations[row][1]
                    elif column == 12:
                        return self.calculations[row][2]
        elif column == 10:
            return self.calculations[row][0]
        elif column == 11:
            return self.calculations[row][1]
        elif column == 12:
            return self.calculations[row][2]
        return item

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def calculateWorkedHours(self):
        self.beginInsertColumns(QtCore.QModelIndex(), 10, 13)
        self.insertColumns(10, 3)
        self.endInsertColumns()

        for row in range(self.rowCount()):
            # index = self.proxymodel.createIndex(r, 10)
            total_seconds = 0
            for column in (INTIME_1, INTIME_2, INTIME_3):
                in_ = self.data(self.sourceModel().index(row, column))
                out = self.data(self.sourceModel().index(row, column + 1))
                if in_ is None or out is None:
                    return [QtCore.QTime(0, 0, 0)] * 3
                total_seconds += in_.secsTo(out)
            worked_time = QtCore.QTime(0, 0, 0).addSecs(
                total_seconds)

            date = self.sourceModel().index(row, DAY).data()
            shift = self.shift_map[self.sourceModel().index(row, SHIFT).data()]
            specialdate = self.sourceModel().index(row, 13).data()
            workerpass = self.sourceModel().index(row, 14).data()
            dayisregular = True
            day_number = md.dayNumber(date.date().year(), date.date().month(), date.date().day())

            # Non workable day conditions
            if day_number not in self.week_workable_days[shift]:
                dayisregular = False
            if isinstance(specialdate, int) or isinstance(workerpass, int):
                dayisregular = False

            # base calculus values
            relative_time = QtCore.QTime(8, 0, 0).secsTo(worked_time)
            extra_time = QtCore.QTime(0, 0, 0)
            absent_time = QtCore.QTime(0, 0, 0)

            if dayisregular:
                if relative_time > 0:
                    extra_time = QtCore.QTime(0, 0, 0).addSecs(relative_time)
                else:
                    absent_time = QtCore.QTime(0, 0, 0).addSecs(- relative_time)
            else:
                extra_time = QtCore.QTime(0, 0, 0).addSecs(total_seconds)

            self.calculations.append(
                [worked_time, extra_time, absent_time]
            )
        self.emit(QtCore.SIGNAL("dataChanged()"), self)


class TotalizeModel(QtCore.QAbstractTableModel):
    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self._data = []
        for row in self.source:
            data_row = []
            for elem in row:
                if isinstance(elem, str):
                    data_row.append(elem)
                elif isinstance(elem, int):
                    data_row.append(secondsToTime(elem))
            self._data.append(data_row)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 4

    def data(self, index, role=None):

        column = index.column()

        if role == Qt.DisplayRole:
            row = index.row()
            item = self._data[row][column]
            return item
        elif role == Qt.TextAlignmentRole:
            if column > 0:
                return Qt.AlignCenter | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=None):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return Qt.AlignCenter | Qt.AlignVCenter
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'Nombre'
            elif section == 1:
                return 'Tiempo\nTrabajado'
            elif section == 2:
                return 'Tiempo\nExtra'
            elif section == 3:
                return 'Tiempo\nAusente'

        return None


def TotalizeWorkedTime(model):
    """

    :param model: CalculusModel()
    :return:
    """
    # assert isinstance(model, CalculusModel)
    workers_workedTime = {}
    # read and organize data from model
    for i in range(model.rowCount()):
        worker = model.index(i, WORKER).data()
        worked_time = model.index(i, WORKED_TIME).data()
        extra_time = model.index(i, EXTRA_TIME).data()
        absent_time = model.index(i, ABSENT_TIME).data()

        if worker not in workers_workedTime.keys():
            workers_workedTime[worker] = [0] * 3
        else:
            workers_workedTime[worker][0] += QtCore.QTime(0, 0, 0).secsTo(worked_time)
            workers_workedTime[worker][1] += QtCore.QTime(0, 0, 0).secsTo(extra_time)
            workers_workedTime[worker][2] += QtCore.QTime(0, 0, 0).secsTo(absent_time)

    # transform dict to matrix
    matrix = []
    for k, v in workers_workedTime.items():
        matrix.append([k] + v)

    return TotalizeModel(matrix)


def secondsToTime(seconds):
    def secToTime(workdays=0, hours=0, mins=0, secs=0):
        if secs < 60:
            text = "{} jornadas, {}:{} horas"
            if workdays == 1:
                text = "{} jornada, {}:{} horas"
            return text.format(workdays, hours, mins)
        elif secs >= 28800:
            return secToTime(workdays + 1, hours, mins, secs - 28800)
        elif secs >= 3600:
            return secToTime(workdays, hours + 1, mins, secs - 3600)
        elif secs >= 60:
            return secToTime(workdays, hours, mins + 1, secs - 60)

    return secToTime(secs=seconds)


class SizeDalegate(QtGui.QStyledItemDelegate):
    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.size = size

    def sizeHint(self, options, index):
        return QtCore.QSize(self.size, 20)
