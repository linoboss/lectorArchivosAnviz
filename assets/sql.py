import sys, os
import datetime as dt
import shelve
from PyQt4 import QtSql
from PyQt4 import QtCore

global_var = globals()
base_directory = os.getcwd()
# get the correct base directory if accessed from any random file
aux = base_directory.split('\\')
while aux[-1] != 'PyExcel':
    aux = aux[:-1]
base_directory = str.join('\\', aux)
global_var['CONFIG_FILE'] = base_directory + '\\persistence\\config'


class ConfigFile:
    @staticmethod
    def create():
        shelve_ = shelve.open(global_var['CONFIG_FILE'],
                              flag='c')
        shelve_['dbadd'] = ''
        shelve_['print_path'] = ''
        shelve_.close()

    @staticmethod
    def exist():

        return (os.path.exists(global_var['CONFIG_FILE'] +
                               '.bak'))

    @staticmethod
    def set(option, value):
        """
        :param option: str
        :param value: variant
        :return: None
        """
        shelve_ = shelve.open(global_var['CONFIG_FILE'],
                              flag='w', protocol=None,
                              writeback=True)
        if option == "database_path":
            shelve_['dbadd'] = value
        elif option == "print_path":
            shelve_["print_path"] = value
        else:
            raise KeyError(option + " is not a valid option")
        shelve_.close()

    @staticmethod
    def get(option):
        shelve_ = shelve.open(global_var['CONFIG_FILE'],
                              flag='r', protocol=None,
                              writeback=True)
        if option == "database_path":
            value = shelve_['dbadd']
        elif option == "print_path":
            value = shelve_["print_path"]
        else:
            raise KeyError(option + " is not a valid option")
        shelve_.close()
        return value

    @staticmethod
    def updateOptions():
        shelve_ = shelve.open(global_var['CONFIG_FILE'],
                              flag='rw', protocol=None,
                              writeback=True)
        for option in ['dbadd', 'print_path']:
            if option not in shelve_.keys():
                shelve_[option] = ''


class SchMapping:
    def __init__(self, name, id_):
        self.name = name
        self.id = id_

    def __str__(self):
        return self.name

    def __int__(self):
        return self.id

    def __repr__(self):
        return "<{id}: {name}>".format(name=self.name, id=self.id)

    def __eq__(self, other):
        if isinstance(other, int):
            comp = self.id == other
        else:
            comp = self.id == other.id

        return comp

    def __hash__(self):
        return hash(int(self))


class AnvizRegisters:
    def __init__(self, database_path=None, startQuery=True):
        # *** Variable declaration ***
        self.db = QtSql.QSqlDatabase().database()

        # *** init actions ***
        if not self.db.open():
            self.__connect(database_path)
        if startQuery:
            self.query = QtSql.QSqlQuery()

    def addColumn(self, table, name, type_):
        self.query = QtSql.QSqlQuery()
        if type_ is bool: type_ = "BIT"
        self.query.exec("ALTER TABLE {table} "
                        "ADD COLUMN {name} {type}".format(table=table,
                                                          name=name,
                                                          type=type_))
        return self.howthequerydid()

    def __connect(self, dbp=None):

        self.db = QtSql.QSqlDatabase.addDatabase("QODBC")
        MDB = ConfigFile.get("database_path") if not dbp else dbp
        DRV = '{Microsoft Access Driver (*.mdb)}'
        PWD = 'pw'

        self.db.setDatabaseName("DRIVER={};DBQ={};PWD={}".format(DRV, MDB, PWD))
        if not self.db.open():
            raise ConnectionError("UNABLE TO CONECT TO THE DATABASE IN " +
                                  MDB)

    def createTable(self, name):
        """
        Creates the tables required by the program
        :param name:  select one of the available tables to create
                __Available Tables__
                -> Workdays

        :return: a message of success or failure depending of the outcome.
        """
        if name == "WorkDays":
            self.query.exec("CREATE TABLE WorkDays "
                            "("
                            "workdayid AUTOINCREMENT PRIMARY KEY, "
                            "day DATE NOT NULL, "
                            "worker VARCHAR(255) REFERENCES Userinfo(Userid), "
                            "InTime_1 DATETIME, "
                            "OutTime_1 DATETIME, "
                            "InTime_2 DATETIME, "
                            "OutTime_2 DATETIME, "
                            "InTime_3 DATETIME, "
                            "OutTime_3 DATETIME, "
                            "shift INTEGER REFERENCES Schedule(Schid), "
                            "Holidayid INTEGER REFERENCES Holiday(Holidayid), "
                            "WPid INTEGER REFERENCES WorkerPass(WPid)"
                            ")")
        elif name == "WorkerPass":
            self.query.exec("CREATE TABLE WorkerPass "
                            "("
                            "WPid AUTOINCREMENT PRIMARY KEY, "
                            "Userid VARCHAR(255) REFERENCES Userinfo(Userid), "
                            "BDate DATETIME, "
                            "TDate DATETIME, "
                            "Description VARCHAR(255), "
                            "Type INTEGER"
                            ")")
        elif name == "WorkerPassTypes":
            self.query.exec("CREATE TABLE WorkerPassTypes "
                            "("
                            "Id AUTOINCREMENT PRIMARY KEY, "
                            "Type VARCHAR(255)"
                            ")")
        else:
            raise KeyError(name + ' is not a valid option')
        return self.howthequerydid()

    def did_query_failed(self):
        if self.query.lastError().number() == -1:
            return False
        else:
            return True

    def disconnect(self):
        self.db.close()
        QtSql.QSqlDatabase().removeDatabase("QODBC")
        del self.db

    def deleteDay(self, day):
        self.query.prepare("DELETE FROM WorkDays "
                           "WHERE day=:day")
        self.query.bindValue(":day", QtCore.QDate(day))
        self.query.exec_()
        return self.howthequerydid()

    def deleteRegistersFrom(self, table):
        self.query.exec("DELETE FROM {}".format(table))
        return self.howthequerydid()

    def deleteRegister(self, table, *args):
        if table == "Userinfo":
            self.query.prepare("DELETE FROM Userinfo "
                               "WHERE Userid=:id")
            self.query.bindValue(":id", args[0])
            self.query.exec_()
        return self.howthequerydid()

    def first(self):
        return self.query.first()

    def getShcedulesDetails(self, option="byId"):
        """
        :return: a dictionary with the parameters of the work shifts defined in the databse
        """
        shift_details = dict()
        if option == "byName":
            self.query.exec("SELECT DISTINCT c.Schname, Timename, Intime, Outtime, "
                            "   BIntime, EIntime, BOuttime, EOuttime "
                            "FROM ("
                            "   TimeTable a "
                            "   INNER JOIN "
                            "   SchTime b "
                            "       ON (a.Timeid = b.Timeid)) "
                            "   INNER JOIN "
                            "   Schedule c "
                            "       ON (b.Schid = c.Schid)")
        elif option == "byId":
            self.query.exec("SELECT DISTINCT c.Schid, a.Timeid, "
                            "   Intime, Outtime, BIntime, EIntime, BOuttime, EOuttime "
                            "FROM ("
                            "   TimeTable a "
                            "   INNER JOIN "
                            "   SchTime b "
                            "       ON (a.Timeid = b.Timeid)) "
                            "   INNER JOIN "
                            "   Schedule c "
                            "       ON (b.Schid = c.Schid)")
        else:
            raise KeyError("INVALID OPTION \"{}\", only available: byName and byId".format(option))

        while self.query.next():
            shift = self.query.value(0)
            schedule = self.query.value(1)

            if shift not in shift_details:
                shift_details[shift] = {}
            else: pass

            shift_details[shift][schedule] = [self.query.value(i) for i in range(2, 8)]

        return shift_details

    def getWorkers(self, option="byName", isActive=True):
        """
        Grants access to the information related to the workers
        :param option: defines the information to be returned
        :param isActive: sets the workers to search
            if True -> return only active workers
            if False -> returns only inactive workers
            else -> returns all the workers in registers
        :return: a dict with the info specified by the option parameter
        """
        workers = {}

        if isActive is True:
            ifActive = "WHERE isActive=true"
        elif isActive is False:
            ifActive = "WHERE isActive=false"
        else:
            ifActive = ''

        if option == "byName":
            self.query.exec("SELECT Userid, Name "
                            "FROM Userinfo " +
                            ifActive)

            while self.query.next():
                id_ = self.query.value(0)
                name = self.query.value(1)
                workers[name] = id_

        elif option == "byId":
            self.query.exec("SELECT Userid, Name "
                            "FROM Userinfo " +
                            ifActive)

            while self.query.next():
                id_ = self.query.value(0)
                name = self.query.value(1)
                workers[id_] = name

        elif option == "shifts by name":
            self.query.exec("SELECT Name, Schname "
                            "FROM ("
                            "   Userinfo a "
                            "   INNER JOIN "
                            "   UserShift b "
                            "       ON (a.Userid = b.Userid)) "
                            "   INNER JOIN "
                            "   Schedule c "
                            "       ON (b.Schid = c.Schid) " +
                            ifActive)
            while self.query.next():
                name = self.query.value(0)
                sch = self.query.value(1).lower()
                workers[name] = sch

        elif option == "shifts by id":
            self.query.exec("SELECT a.Userid, b.Schid "
                            "FROM ("
                            "   Userinfo a "
                            "   INNER JOIN "
                            "   UserShift b "
                            "       ON (a.Userid = b.Userid)) "
                            "   INNER JOIN "
                            "   Schedule c "
                            "       ON (b.Schid = c.Schid) " +
                            ifActive)
            while self.query.next():
                name = self.query.value(0)
                sch = self.query.value(1)
                workers[name] = sch

        elif option == "names":

            workers = []

            self.query.exec("SELECT Name "
                            "FROM Userinfo " +
                            ifActive)
            while self.query.next():
                name = self.query.value(0)
                workers.append(name)

        else:
            raise KeyError("invalid option \"{}\"".format(option))

        return workers

    def howthequerydid(self, optional_info=''):
        error = self.query.lastError().text()
        if error is None:
            message = optional_info + ' NOT a valid option'
        elif error == ' ':
            message = "Query completed"
        else:
            message = error

        return message

    def insertInto(self, table, *args, **kwargs):
        if table == "WorkDays":
            self.query.prepare("INSERT INTO WorkDays ("
                               "    day, worker, InTime_1, OutTime_1, InTime_2, "
                               "    OutTime_2, InTime_3 , OutTime_3, shift, holidayid, WPid) "
                               "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            for i, value in enumerate(args):
                self.query.bindValue(i, value)
            self.query.exec_()

        else:
            keys = ', '.join(kwargs.keys())
            values = kwargs.values()
            self.query.prepare("INSERT INTO {} ({}) ".format(table, keys) +
                               "VALUES ({})".format(", ".join(['?' for v in values])))
            for v in values:
                self.query.addBindValue(v)
            self.query.exec_()

            print(self.query.lastQuery())

    def last(self):
        return self.query.last()

    def min_date_of(self, table):

        if table == 'Checkinout':
            self.query.exec("SELECT MIN(CheckTime) "
                            "FROM Checkinout".format(table))

        elif table == 'WorkDays':
            self.query.exec("SELECT MIN(CheckTime) "
                            "FROM WorkDays")
        else:
            raise KeyError(table + " is not a valid option")

        if self.query.next():
            date_ = self.query.value(0).toPyDateTime()
        else:
            date_ = None

        return date_

    def max_date_of(self, table):
        if table == 'Checkinout':
            self.query.exec("SELECT MAX(CheckTime) "
                            "FROM Checkinout".format(table))
        elif table == 'WorkDays':
            self.query.exec("SELECT MAX(InTime_1), "
                            "   MAX(OutTime_1), "
                            "   MAX(InTime_2), "
                            "   MAX(OutTime_2), "
                            "   MAX(InTime_3), "
                            "   MAX(OutTime_3) "
                            "FROM WorkDays")

            self.query.next()

            values = [self.query.value(i) for i in range(6)]
            if all([v is None for v in values]):
                return None

            max_date = max(values)
            if max_date == QtCore.QDateTime():
                return None
            else:
                return max_date.toPyDateTime()
        else:
            raise KeyError(table + " is not a valid option")

        if self.query.next():
            date_ = self.query.value(0).toPyDateTime()
        else:
            date_ = None

        return date_

    def max_index_of(self, table):
        if table == 'WorkDays':
            self.query.exec("SELECT MAX(workdayid) "
                            "FROM WorkDays")
        else:
            raise KeyError(table + " is not a valid option")

        if self.query.next():
            id_ = self.query.value(0)
        else:
            id_ = None

        return id_

    def min_index_of(self, table):
        if table == 'WorkDays':
            self.query.exec("SELECT MIN(workdayid) "
                            "FROM WorkDays")
        else:
            raise KeyError(table + " is not a valid option")

        if self.query.next():
            id_ = self.query.value(0)
        else:
            id_ = None

        return id_

    def new_query(self):
        self.query = QtSql.QSqlQuery()

    def next(self):
        return self.query.next()

    def query_failed(self):
        if self.query.lastError().number() == -1:
            return False
        else:
            return True

    def refreshConnection(self):
        self.__connect()

    def readTable(self, name,
                  from_date=dt.datetime(1999, 1, 1),  # minimum valid date
                  till_date=dt.datetime(2100, 1, 1)   # large valid date
                  ):
        """

        Makes a READ query on the "name" table

        :param name: indicates the table in which the query wants to be made
        :param from_date: \ _  date filters, as most of the queries will be
        :param till_date: /    bounded by a date range restrain
        :return: a message with the result status of the query
        """
        if name == "Checkinout":
            self.query.prepare("SELECT Logid, Userid, CheckTime, CheckType "
                               "FROM Checkinout "
                               "WHERE CheckTime >= :from_date AND CheckTime <= :till_date")
            self.query.bindValue(":from_date", QtCore.QDateTime(from_date))
            self.query.bindValue(":till_date", QtCore.QDateTime(till_date))
            self.query.exec_()

        return self.howthequerydid(name)

    def randomLoad(self, name):
        if name == "WorkDays":
            self.query.prepare("INSERT INTO WorkDays (workdayid, worker, checkin, checkout, shift) "
                               "VALUES (:id, :worker, :checkin, :checkout, :shift)")

            self.query.bindValue(":id", 2)
            self.query.bindValue(":worker", 20)
            self.query.bindValue(":checkin", QtCore.QDateTime(dt.datetime(2016, 1, 1)))
            self.query.bindValue(":checkout", QtCore.QDateTime(dt.datetime(2016, 1, 1)))
            self.query.bindValue(":shift", 3)

            self.query.exec_()

        return self.howthequerydid(name)

    def schedules_overnight_map(self):
        overnight_map = {}
        self.query.exec("SELECT Schid, isOvernight FROM Schedule")
        while self.query.next():
            overnight_map[self.query.value(0)] = self.query.value(1) > 0
        return overnight_map

    def schedules_map(self):
        """
        Returns a relation for all the schedules and the shifts
        :return: dict
        """
        schmap = dict([])

        self.query.exec("SELECT DISTINCT a.Schid, b.Schname, a.Timeid, c.Timename "
                        "FROM ("
                        "   SchTime a "
                        "   INNER JOIN Schedule b "
                        "       ON (a.Schid = b.Schid)) "
                        "   INNER JOIN "
                        "   TimeTable c "
                        "       ON (a.Timeid = c.Timeid)")

        while self.query.next():
            schid = self.query.value(0)
            schname = self.query.value(1)
            timeid = self.query.value(2)
            timename = self.query.value(3)

            sch = SchMapping(schname, schid)
            time = SchMapping(timename, timeid)

            if sch not in schmap:
                schmap[sch] = [time]
            else:
                schmap[sch] += [time]

        return schmap

    def tableExists(self, name):
        print(name, self.db.tables(), name in self.db.tables())
        return name in self.db.tables()

    def value(self, i):
        return self.query.value(i)


# *** TESTS ***


def setDatabasePath():
    filename = QtGui.QFileDialog.getOpenFileName()
    ConfigFile.set('database_path', filename)


def createTable(name):
    print(anvRgs.createTable(name))


def readTable(name):
    print(anvRgs.readTable(name,
                              dt.datetime(2015, 1, 1),
                              dt.datetime(2015, 3, 1)))


def genericTest():
    pprint(anvRgs.getShcedulesDetails())
    pprint(list(map(lambda x: str(x.id), anvRgs.schedules_map().keys())))
    pprint(anvRgs.getWorkers("shifts by name"))


def getShcedules():
    anvRgs.getShcedulesDetails()


def getWorkers():
    print("byName")
    pprint(anvRgs.getWorkers("byName"))
    print("byId")
    pprint(anvRgs.getWorkers("byId"))
    print("shift")
    pprint(anvRgs.getWorkers("andShift"))
    print(anvRgs.howthequerydid())


def configfile_updateOptions():
    ConfigFile.updateOptions()


def insertInto():

    pprint(anvRgs.insertInto("WorkDays", *(
        QtCore.QDate(dt.date(2014, 9, 2)),
        '10',
        None,
        None,
        None,
        None,
        None,
        None,
        4
    )))


def insertIntoUserShift():
    anvRgs.insertInto("UserShift", a=1, b=2, c=3)


def deleteDay(day):
    anvRgs.deleteDay(day)


def dates():
    print(anvRgs.max_date_of("WorkDays"))


def addColumn():
    print(anvRgs.addColumn("Userinfo", "isActive", bool))
    print(anvRgs.query.lastQuery())



if __name__ == "__main__":
    from PyQt4 import QtGui
    from pprint import pprint
    app = QtGui.QApplication(sys.argv)

    # configfile_updateOptions()

    # setDatabasePath()

    anvRgs = AnvizRegisters()

    # setSetupPath()
    # getShcedulesDetails()
    # getWorkers()
    # update()
    # createTable("WorkDays")
    # genericTest()
    # insertInto()
    # dates()
    # deleteDay(dt.datetime.today().date())
    # addColumn()
    # insertIntoUserShift()
    print(anvRgs.getWorkers("shifts by name"))
    anvRgs.db.close()
    sys.exit(app.closeAllWindows())
