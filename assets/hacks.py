import sys, os
path = '\\'.join(os.getcwd().split('\\')[:-1])
print(path)
sys.path.append(path)
from PyQt4 import QtGui, QtCore, QtSql
from assets.anviz_reader import AnvizReader
import assets.helpers as helpers
from assets.dates_tricks import MyDates as md
import random
from pprint import pprint


def crearCheckInOuts(fdate, tdate):
    """
    Creates a list of checks for all the active workers of all the shifts
    within the specified date
    :param fdate: QtCore.QDate
    :param: tdate: QtCore.QDate
    :return: list <str, QtCore.QDate>
    """

    checks = []
    for fecha in md.dates_range(fdate.toPyDate(),
                                tdate.toPyDate()):
        fecha = QtCore.QDate(fecha)
        day_number = md.dayNumber(fecha.year(), fecha.month(), fecha.day())

        workersdetails = WorkerDetails()
        schdetails = SchsDetails()
        shift_to_sch = ShiftToSch()
        # holidaymapper = HolidayMapper()
        week_workable_days = helpers.week_workable_days()

        for action, shift in [("Outtime", 3),
                              ("Intime", 4),
                              ("Outtime", 4),
                              ("Intime", 5),
                              ("Outtime", 5),
                              ("Intime", 3)]:
            sch = shift_to_sch.map(shift)
            workers = workersdetails.users_on_shift(sch)
            print(day_number)

            if day_number not in week_workable_days[sch]:
                continue

            for worker in workers:
                checks.append([worker,
                               QtCore.QDateTime(
                                   fecha,
                                   random_time(
                                       schdetails.get(action, shift)
                                   )
                               )
                               ])
    return checks


def addChecksToDB(checks):
    model = QtSql.QSqlTableModel()
    model.setTable("Checkinout")
    for check in checks:
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, 1), check[0])
        model.setData(model.index(row, 2), check[1])
        model.submit()
    model.submitAll()


def random_time(center):
    """
    adds a random amount of time to the center paramenter
    :param center: QtCore.QTime
    :return: QtCore.QTime
    """
    assert(isinstance(center, QtCore.QTime))
    min20 = 60 * 20  # 20 min
    min5 = 60 * 5  # 5 min
    center = center.addSecs(random.randint(0, min20) - min5)
    return center


class ShiftToSch:
    def __init__(self):
        super().__init__()
        self.model = QtSql.QSqlTableModel()
        self.model.setTable("SchTime")
        self.model.select()

    def map(self, timeid):
        """
        gets the schid related to the timeid
        :param timeid: int
        :return: int
        """
        self.model.setFilter("Timeid={}".format(timeid))
        schid = self.model.record(0).value("Schid")
        return schid


class SchsDetails:
    def __init__(self):
        super().__init__()
        self.model = QtSql.QSqlTableModel()
        self.model.setTable("TimeTable")
        self.model.select()

    def get(self, option, timeid):
        """
        retrives the time requested
        :param option: str
        :param timeid: int
        :return:
        """
        self.model.setFilter("Timeid={}".format(timeid))
        value = self.model.record(0).value(option)
        qtime = QtCore.QTime.fromString(value, "hh:mm")
        return qtime


class WorkerDetails:
    def __init__(self):
        super().__init__()
        self.model = QtSql.QSqlTableModel()
        self.model.setTable("UserShift")
        self.model.select()

    def users_on_shift(self, schid):
        """
        gets a list of users that relate to the schid
        :param schid: int
        :return: str
        """
        self.model.setFilter("Schid={}".format(schid))
        users = [self.model.record(row).value("Userid")
                 for row in range(self.model.rowCount())]
        return users


if __name__ == "__main__" :
    app = QtGui.QApplication(sys.argv)
    anvreader = AnvizReader()
    checks = crearCheckInOuts(QtCore.QDate(2016, 11, 18), QtCore.QDate(2016, 11, 24))
    addChecksToDB(checks)

