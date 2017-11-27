import sys, os
from PyQt4 import QtGui, QtCore, QtSql
from assets.dates_tricks import MyDates as md

YES = QtGui.QMessageBox.Yes
NO = QtGui.QMessageBox.No


class PopUps:

    @staticmethod
    def ask_user_to(text, infotext='', detailedtext=''):
        messageBox = QtGui.QMessageBox()
        messageBox.setStandardButtons(QtGui.QMessageBox.Yes |
                                      QtGui.QMessageBox.No)
        messageBox.setIcon(QtGui.QMessageBox.Question)
        messageBox.setText(text)
        messageBox.setInformativeText(infotext)
        messageBox.setDetailedText(detailedtext)
        return messageBox.exec()

    @staticmethod
    def inform_user(text):
        messageBox = QtGui.QMessageBox()
        messageBox.setText(text)
        messageBox.setStandardButtons(QtGui.QMessageBox.Ok)
        messageBox.setIcon(QtGui.QMessageBox.Information)
        messageBox.exec()

    @staticmethod
    def error_message(text, infotext='', detailedtext=''):
        messageBox = QtGui.QMessageBox()
        messageBox.setText(text)
        messageBox.setInformativeText(infotext)
        messageBox.setDetailedText(detailedtext)
        messageBox.setStandardButtons(QtGui.QMessageBox.Ok)
        messageBox.setIcon(QtGui.QMessageBox.Warning)
        messageBox.exec()

    @staticmethod
    def search_file(text, initial_path, target, action='get', parent=None):
        if target == 'database':
            filter_ = "Access db (*.mdb)"
        elif target == 'pdf':
            filter_ = "pdf (*.pdf)"
        else:
            filter_ = '*'
        filename = initial_path
        while True:
            if action == 'get':
                filename = QtGui.QFileDialog.getOpenFileName(
                    parent, text, initial_path, filter_)
            elif action == 'save':
                filename = QtGui.QFileDialog.getSaveFileName(
                    parent, text, initial_path, filter_)
            filename = filename.replace('/', '\\')
            if filename:
                break
            if PopUps.ask_user_to('Intentar nuevamente?') == NO:
                return ''

        if filename.split('.')[-1] != 'pdf':
            filename += '.pdf'

        return filename


class Db:
    @staticmethod
    def tableHeader(table):
        model = QtSql.QSqlTableModel()
        model.setTable(table)
        model.select()

        from collections import OrderedDict
        headerMap = OrderedDict()
        i = 0
        for i in range(model.columnCount()):
            headerMap[model.headerData(i, QtCore.Qt.Horizontal,
                                       QtCore.Qt.DisplayRole)] = i
        if table == "WorkDays":
            headerMap["workedtime"] = i + 1
            headerMap["extratime"] = i + 2
            headerMap["absenttime"] = i + 3
        return headerMap


class Thread(QtCore.QThread):
    def __init__(self, func):
        super().__init__()
        self.func = func

    # the execution oh the thread will be by calling
    # the start method, which calls the run method
    def run(self):
        self.func()

    def finishWith(self, func):
        self.finished.connect(func)


def getField(sql_model, field_name):
    """
    :return a list of the selected field from the model
    :param sql_model: QtSql.QsqlTableModel
    :param field: str
    :return: list
    """
    column = sql_model.fieldIndex(field_name)
    liste = [sql_model.index(row, column).data()
             for row in range(sql_model.rowCount())]
    return liste


def schedules():
    """
    Get schedules and create dict(Schname: Schid)
    :return: dict
    """
    schedules = {}

    table = QtSql.QSqlRelationalTableModel()
    table.setTable("Schedule")
    table.select()

    for row in range(table.rowCount()):
        schedules[table.record(row).value("Schid")] = table.record(row).value("Schname")

    return schedules


def regularWorkDays():
    """
    Setups of the regular workable days
    e.g.:Mon - Fri on Diurno, Thu - Sat on Nocturno
    :return: dict
    """
    sch_reg_days = {}

    scheds = schedules()
    table = QtSql.QSqlRelationalTableModel()
    table.setTable("SchTime")
    for sch in scheds.keys():
        table.setFilter("Schid = {}".format(sch))
        table.select()
        workable_days = []
        for row in range(table.rowCount()):
            workable_days.append(table.record(row).value("BeginDay"))

        sch_reg_days[sch] = list(set(workable_days))

    return sch_reg_days


def holidays():
    table = QtSql.QSqlRelationalTableModel()
    table.setTable("Holiday")
    table.select()
    holiday = {}
    specialevent = {}
    for row in range(table.rowCount()):
        id_ = table.record(row).value("Holidayid")
        name = table.record(row).value("Name")
        date = table.record(row).value("BDate").date()
        days = table.record(row).value("Days")
        for d in range(days):
            if date.year() == 2000:
                holiday[date] = id_
            else:
                specialevent[date] = id_
            date = date.addDays(1)

    return holiday, specialevent


def workerPass():
    table = QtSql.QSqlRelationalTableModel()
    table.setTable("WorkerPass")
    table.select()
    dayoff = {}
    for row in range(table.rowCount()):
        id_ = table.record(row).value("WPid")
        userid = table.record(row).value("Userid")
        bdate = table.record(row).value("BDate")
        tdate = table.record(row).value("TDate")
        description = table.record(row).value("Description")
        type_ = table.record(row).value("Type")
        date = bdate

        datesrange = md.dates_range(bdate.toPyDateTime(),
                                    tdate.toPyDateTime())

        if userid not in dayoff:
            dayoff[userid] = {}
        for d in datesrange:
            dayoff[userid][QtCore.QDate(d)] = id_
            date = date.addDays(1)

    return dayoff


def table_to_dictionary(table, primary_key=0):
    model = QtSql.QSqlTableModel()
    model.setTable(table)
    model.select()
    model_dict = {}
    for row in range(model.rowCount()):
        key = model.record(row).value(primary_key)
        value = []
        for c in range(model.columnCount()):
            value.append(model.index(row, c).data())
        model_dict[key] = value
    return model_dict


def week_workable_days():
    model = QtSql.QSqlTableModel()
    model.setTable("SchTime")
    model.select()
    model_pair = []
    for row in range(model.rowCount()):
        key = model.record(row).value("Schid")
        value = model.record(row).value("BeginDay") - 1
        model_pair.append((key, value))
    model_pair = list(set(model_pair))
    model_dict = {}
    for k, v in model_pair:
        if k not in model_dict:
            model_dict[k] = [v]
        else:
            model_dict[k].append(v)
    return model_dict


if __name__ == "__main__":
    from assets.sql import AnvizRegisters
    from pprint import pprint

    app = QtGui.QApplication(sys.argv)
    av = AnvizRegisters()

    pprint(table_to_dictionary("WorkerPass", 0))



