__author__ = 'Lino Bossio'

import sys
import datetime as dt
from assets.sql import AnvizRegisters
from assets.dates_tricks import MyDates as md
from PyQt4 import QtGui
from PyQt4 import QtCore
import assets.helpers as helpers
from pprint import pprint

schedules = ['Vespertino', 'Matutino', 'nocturno']
work_time_reference = dt.timedelta(hours=8)


schedules_regular_workdays = {'diurno': ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes'),
                              'nocturno': ('Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado')}


class AnvizReader:
    def __init__(self):
        """
        Reorganiza la información en las distintas tablas de la base de datos y
        la almacena en la tabla WorDays que funciona como una tabla temporal para acelerar el accesso a los datos y
        mantener cierta referencia de configuración vigente al momento de la captura del captahuellas

        As WorkDays table contains all the relevant information to the personel logs,
        it will be the main table of the AnvizReader class, so, unless explicitly, all Table actions will be
        referred to the WorkDays table

        """
        self.anvRgs = AnvizRegisters()  # sets the connection to the database

        self.schedules_details = self.anvRgs.getShcedulesDetails()
        self.schedules_map = self.anvRgs.schedules_map()
        self.schedules = list(map(lambda x: str(x.name), self.schedules_map.keys()))
        self.workers_by_id = self.anvRgs.getWorkers("byId")
        self.workers_shifts_id = self.anvRgs.getWorkers("shifts by id")
        self.workers_shifts_name = self.anvRgs.getWorkers("shifts by name")

        self.exeptions = []  # list of indexes of Checkinout logs that failed the validation

    @property
    def first_date(self):
        return self.anvRgs.min_date_of("WorkDays")

    @property
    def last_date(self):
        return self.anvRgs.max_date_of("WorkDays")

    @property
    def workers_names(self):
        return self.anvRgs.getWorkers("names")

    @property
    def workers_shifts(self):
        return self.anvRgs.getWorkers('shifts by name')

    def workers_shift_by(self, option):
        if option == "id":
            return self.anvRgs.getWorkers("shifts by id")

    def updateTable(self):
        holiday, specialdate = helpers.holidays()
        daysoff = helpers.workerPass()
        from_ = self.anvRgs.max_date_of("WorkDays")

        if from_ is None:
            from_ = self.anvRgs.min_date_of("Checkinout")

        from_datetime = dt.datetime(from_.year, from_.month, from_.day,
                                    0, 0, 0)

        self.anvRgs.deleteDay(from_datetime)
        self.anvRgs.deleteDay(from_datetime)

        to_datetime = self.anvRgs.max_date_of("Checkinout")
        """
        Iterate over dates
        """
        if (md.isValid(to_datetime) is not True
                or md.isValid(to_datetime) is not True):
            return
        dates_range = md.dates_range(from_datetime.date(), to_datetime.date())

        self.anvRgs.query.exec("SELECT Logid, Userid, CheckTime "
                               "FROM Checkinout "
                               "WHERE CheckTime >= #{from_date}# AND CheckTime <= #{to_date}# "
                               "ORDER BY CheckTime ASC".format(from_date=from_datetime,
                                                               to_date=to_datetime))

        LOGID, USERID, CHECKTIME = 0, 1, 2

        if not self.anvRgs.next():
            return

        CheckDate = self.anvRgs.value(CHECKTIME).toPyDateTime().date()

        workdays = []
        for d in dates_range:
            yield d
            QtGui.QApplication.processEvents()
            # WorkDay day template
            workday = self.workdayTemplate(d)
            while CheckDate == d:
                logid = self.anvRgs.value(LOGID)
                userid = self.anvRgs.value(USERID)
                checktime = self.anvRgs.value(CHECKTIME)
                if userid in self.workers_by_id.keys():
                    time_pos = self.__map_to_schedules(userid, checktime)
                    workday[userid][0] = QtCore.QDate(CheckDate)
                    workday[userid][1] = str(userid)

                    if time_pos is not None:
                        workday[userid][2 + time_pos] = checktime
                    else:
                        self.exeptions.append(logid)

                    workday[userid][8] = self.workers_shifts_id[userid]

                # user defines the schedule, while the checktime defines the shift
                # go to the next register
                if not self.anvRgs.next():
                    break
                CheckDate = self.anvRgs.value(CHECKTIME).toPyDateTime().date()

            # Add Holidays and SpecialDates
            for userid in workday.keys():
                date = QtCore.QDate(d)
                # holidays
                hdate = QtCore.QDate(2000, date.month(), date.day())
                if hdate in holiday:
                    workday[userid][9] = holiday[hdate]
                # special dates
                if date in specialdate:
                    workday[userid][9] = specialdate[date]
                # vacations and days off
                if userid in daysoff:
                    if date in daysoff[userid]:
                        workday[userid][10] = daysoff[userid][date]

            workdays.append(workday)
        """
        Una vez analizados todos los registros, estos seran almacenados en la tabla
        """
        overnight_workers = self.overnightWorkers()

        out_aux = [None, None]
        for workday in workdays[::-1]:
            for w in overnight_workers:
                out = [workday[w][3], workday[w][5]]
                workday[w][3], workday[w][5] = out_aux
                out_aux = out

        for workday in workdays:
            for w, register in sorted(workday.items()):
                self.anvRgs.insertInto("WorkDays", *register)

    def map_to_schedules(self, userid, checktime):
        return self.__map_to_schedules(userid, checktime)

    def __map_to_schedules(self, userid, checktime):
        """
        This is a helper function to complement the workday template dictionary.
        It maps the checktime to the correct schedule by comparing it to the
        shift margins.

        :param userid:
        :param checktime:
        :return:
        """
        coords = 0
        # determine CheckTime Shift
        schedule = self.workers_shifts_id[userid]
        log = checktime.toPyDateTime().time()
        i = 0
        for id_, details in self.schedules_details[schedule].items():

            [in_1, in_2, out_1, out_2] = map(lambda h: dt.datetime.strptime(h, "%H:%M").time(),
                                             [details[2], details[3], details[4], details[5]])
            if in_1 <= log <= in_2:
                i += 1
                break
            coords += 1
            if out_1 <= log <= out_2:
                break
            coords += 1
            i += 1
        if coords != 0 and coords == i * 2:
            coords = None

        return coords

    def workdayTemplate(self, day):
        """
        Creates a template of a day in the WorkDays table
        which includes all the workers and their logs that day
        :return: a dict with the structure of a work day
        """
        INTIME_1, OUTTIME_1, INTIME_2, OUTTIME_2, INTIME_3, OUTTIME_3, SHIFT, HOLIDAY, DAYOFF = [None for n in range(9)]

        day = QtCore.QDate(day)
        wd_temp = {}
        for w in self.workers_by_id:
            SHIFT = self.workers_shifts_id[w]
            wd_temp[w] = [day, str(w), INTIME_1, OUTTIME_1, INTIME_2, OUTTIME_2, INTIME_3, OUTTIME_3, SHIFT, HOLIDAY, DAYOFF]

        return wd_temp

    def overnightWorkers(self):
        overnight_workers = []
        overnight_map = self.anvRgs.schedules_overnight_map()
        for w, shift in self.workers_shift_by('id').items():
            if overnight_map[shift]:
                overnight_workers.append(w)
        return overnight_workers

    def close_conection(self):
        self.anvRgs.disconnect()

# *** Tests ***


def update():
    reader.updateTable()


def tests():
    pprint(reader.schedules_map)


def getShifts():
    print(reader.schedules)


def run():
    pprint(reader.workers_names)

if __name__ == "__main__":    # run()
    from pprint import pprint
    app = QtGui.QApplication(sys.argv)
    reader = AnvizReader()
    # getShifts()
    # update()
    sys.exit()

