import sys
from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui, QtSql
import assets.helpers as helpers
import assets.sql as sql
import assets.work_day_tools as tool
from assets.dates_tricks import MyDates as md
from assets.anviz_reader import AnvizReader


class PrintReport(QtCore.QObject):
    ACCEPTED = "accepted"
    CANCELED = "canceled"
    CREATED = "created"
    notCREATED = "notcreated"

    def __init__(self, parent=None):
        super().__init__()
        self.sourceModel = None
        self.doc = QtGui.QTextDocument()
        self.printer = QtGui.QPrinter()
        self.filename = ''
        self.parent = parent
        self.anvReader = parent.anvReader
        self.WDH = helpers.Db.tableHeader('WorkDays')
        self.file_created = False

        self.configuration = {"mode": "allWorkers"}

    def setSourceModel(self, sourceModel):
        self.sourceModel = sourceModel

    def setOutputFileName(self, filename=None):
        filename = helpers.PopUps.search_file(
            'Donde desea ubicar el archivo?',
            sql.ConfigFile.get('print_path'),
            'pdf',
            'save', parent=self.parent) if not filename else filename
        if filename == '':
            return self.CANCELED
        self.printer.setOutputFileName(filename)
        sql.ConfigFile.set('print_path',
                           str.join('\\', filename.split('\\')[:-1]))
        self.filename = filename
        return self.ACCEPTED

    def setup(self, **kwargs):
        dpi = 96
        self.printer.setResolution(dpi)
        self.printer.setPageSize(QtGui.QPrinter.Letter)
        self.printer.setOrientation(QtGui.QPrinter.Landscape)
        self.printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.doc.setDefaultFont(font)

        if kwargs is not None:
            for k, v in kwargs.items():
                self.configuration[k] = v

    def createFile(self):
        # printer.setPageMargins(30, 16, 12, 20, QtGui.QPrinter.Millimeter)
        self.doc.print_(self.printer)
        self.doc.documentLayout().setPaintDevice(self.printer)
        self.file_created = True

    def allWorkersDoc(self):
        self.file_created = False
        if self.filename == '':
            raise ValueError('Enter the filename before printing')
        if self.sourceModel is None:
            raise ValueError('Enter the sourceModel before printing')

        scheduleFilter = QtGui.QSortFilterProxyModel(self.parent)
        scheduleFilter.setSourceModel(self.sourceModel)
        scheduleFilter.setFilterCaseSensitivity(Qt.CaseInsensitive)
        scheduleFilter.setFilterKeyColumn(self.WDH['shift'])

        printFilter = tool.DateFilterProxyModel()
        printFilter.setSourceModel(scheduleFilter)

        FIRST_REGISTER = 0
        LAST_REGISTER = printFilter.rowCount() - 1

        # Si no hay registros retorna None
        if LAST_REGISTER == 0:
            return

        date1 = printFilter.index(FIRST_REGISTER, self.WDH['day']).data().toPyDateTime().date()
        date2 = printFilter.index(LAST_REGISTER, self.WDH['day']).data().toPyDateTime().date()
        from_date = min(date1, date2)
        to_date = max(date1, date2)

        not_css = {"td": "padding:5px;",
                   "table": "border-width: 1px;border-style: solid;border-color: black;color: black;"}
        html = ""

        for date in md.dates_range(from_date, to_date):

            printFilter.setSingleDateFilter(date)
            if printFilter.rowCount() == 0: continue
            html += ("<html>"
                     "<body>"
                     "<table><tr>"
                     # "<td><img src='C:\\ControlHorario\\PyExcel\\images\\SGlogo.png'></td>"
                     "<td align=right valign=bottom style='padding-left:450px'>"
                     "<div style='font-size:25px'><b>ASISTENCIAS<br>DIARIAS</b></div></td>"
                     "</tr></table><br><hr>")
            html += ("<p>"
                     "{} {} de {} del {}</p><br>".format(md.dayName(date),
                                                         date.day,
                                                         md.monthName(date.month),
                                                         date.year))
            for sch in self.anvReader.schedules:
                # if sch.lower() == 'nocturno': continue
                scheduleFilter.setFilterRegExp(sch)
                if printFilter.rowCount() == 0: continue
                html += "Horario {}".format(sch)
                html += "<table cellspacing='0' style='{}'>".format(not_css["table"])
                html += ("<tr>"
                         "<th width=170>Nombre</th>"
                         "<th width=70>Entrada</th>"
                         "<th width=70>Salida</th>"
                         "<th width=70>Entrada</th>"
                         "<th width=70>Salida</th>"
                         "<th width=70 style='font-size:10px'>Tiempo<br>Trabajado</th>"
                         "<th width=70 style='font-size:10px'>Tiempo<br>Extra</th>"
                         "<th width=70 style='font-size:10px'>Tiempo<br>Ausente</th>"
                         "<th width=200>Firma</th>"
                         "</tr>")
                for row in range(printFilter.rowCount()):
                    html += "<tr>"
                    QtGui.QApplication.processEvents()

                    for column in range(13):
                        if column == self.WDH['workdayid']:
                            continue
                        elif column == self.WDH['day']:
                            continue
                        elif column == self.WDH['InTime_3']:
                            continue
                        elif column == self.WDH['OutTime_3']:
                            continue
                        elif column == self.WDH['shift']:
                            continue
                        elif self.WDH['InTime_1'] <= column <= self.WDH['OutTime_3']:

                            qdate = printFilter.index(row, column).data()
                            if qdate == QtCore.QTime():
                                item = '--:--'
                            else:
                                item = qdate.toString("hh:mm")
                        elif 10 <= column <= 12:
                            item = printFilter.index(row, column).data().toString('hh:mm')
                        else:
                            item = printFilter.index(row, column).data()
                        html += "<td align=center style='{}'>".format(not_css["td"])
                        html += item
                        html += "</td>"

                    html += "<td style='{}'></td>".format(not_css["td"])
                    html += "</tr>"
                html += "</table><br>"

            # html += "<br>"*6
            # html += "<hr width=300>"
            # html += "<p style='margin-left:380px;'>Revisado por</p>"
            if date != to_date:
                html += "<div style='page-break-before:always'></div>"

        self.doc.setHtml(html)

    def singleWorkerDoc(self):
        self.file_created = False
        if self.filename == '':
            raise ValueError('Enter the filename before printing')
        if self.sourceModel is None:
            raise ValueError('Enter the sourceModel before printing')

        printFilter = tool.DateFilterProxyModel()
        printFilter.setSourceModel(self.sourceModel)

        worker = printFilter.index(0, self.WDH['worker']).data()

        FIRST_REGISTER = 0
        LAST_REGISTER = printFilter.rowCount() - 1

        # Si no hay registros retorna None
        if LAST_REGISTER == 0:
            return

        not_css = {"td": "padding:5px;",
                   "table": "border-width: 1px;border-style: solid;border-color: black;color: black;"}
        html = ""
        html += ("<html>"
                 "<body>"
                 "<table><tr>"
                 "<td align=right valign=bottom style='padding-left:450px'>"
                 "<div style='font-size:25px'><b>ASISTENCIAS<br>DIARIAS</b></div></td>"
                 "</tr></table><br><hr>")
        sch = self.anvReader.workers_shifts_name[worker]
        html += "<br>Trabajador {}, Horario {}<br>".format(worker, sch)
        html += "<table cellspacing='0' style='{}'>".format(not_css["table"])
        html += ("<tr>"
                 "<th width=270>Fecha</th>"
                 "<th width=70>Entrada</th>"
                 "<th width=70>Salida</th>"
                 "<th width=70>Entrada</th>"
                 "<th width=70>Salida</th>"
                 "<th width=70 style='font-size:10px'>Tiempo<br>Trabajado</th>"
                 "<th width=70 style='font-size:10px'>Tiempo<br>Extra</th>"
                 "<th width=70 style='font-size:10px'>Tiempo<br>Ausente</th>"
                 "</tr>")

        for row in range(printFilter.rowCount()):
            html += "<tr>"
            QtGui.QApplication.processEvents()

            for column in range(13):
                if column == self.WDH['workdayid']:
                    continue
                elif column == self.WDH['worker']:
                    continue
                elif column == self.WDH['InTime_3']:
                    continue
                elif column == self.WDH['OutTime_3']:
                    continue
                elif column == self.WDH['shift']:
                    continue
                elif column == self.WDH["day"]:
                    date = printFilter.index(row, column).data().toPyDateTime()
                    item = ("<p> {}, {}</p>".format(md.dayName(date),
                                                    str(date)))
                elif self.WDH['InTime_1'] <= column <= self.WDH['OutTime_3']:

                    qdate = printFilter.index(row, column).data()
                    if qdate == QtCore.QTime():
                        item = '--:--'
                    else:
                        item = qdate.toString("hh:mm")
                elif column >= self.WDH["workedtime"]:
                    item = printFilter.index(row, column).data().toString('hh:mm')
                else:
                    item = printFilter.index(row, column).data()
                html += "<td align=center style='{}'>".format(not_css["td"])
                html += item
                html += "</td>"
            html += "</tr>"
        html += "</table>"

        self.doc.setHtml(html)

    def totalsDoc(self):
        self.file_created = False
        if self.filename == '':
            raise ValueError('Enter the filename before printing')
        if self.sourceModel is None:
            raise ValueError('Enter the sourceModel before printing')

        printFilter = tool.TotalizeWorkedTime(self.sourceModel)

        upper = self.sourceModel.index(0, 1).data()
        lower = self.sourceModel.index(
                             self.sourceModel.rowCount() - 1,
                             1).data()
        fdate = min(upper, lower).toPyDateTime().date()
        tdate = max(upper, lower).toPyDateTime().date()

        # Si no hay registros retorna None
        if printFilter.rowCount() == 0:
            return

        not_css = {"td": "padding:5px;",
                   "table": "border-width: 1px;border-style: solid;border-color: black;color: black;"}
        html = ""

        html += ("<html>"
                 "<body>"
                 "<table><tr>"
                 "<td align=right valign=bottom style='padding-left:450px'>"
                 "<div style='font-size:25px'><b>TIEMPO TOTAL<br>DE ASISTENCIAS</b></div></td>"
                 "</tr></table><br><hr><br>")
        html += "El analisis abarca desde el {} hasta el {}<br>".format(md.dateToString(fdate),
                                                                        md.dateToString(tdate))

        html += "<table cellspacing='0' style='{}'>".format(not_css["table"])
        html += ("<tr>"
                 "<th width=170>Nombre</th>"
                 "<th width=210>Tiempo\nTrabajado</th>"
                 "<th width=210>Tiempo\nExtra</th>"
                 "<th width=210>Tiempo\nAusente</th>"
                 "</tr>")

        for row in range(printFilter.rowCount()):
            html += "<tr>"
            QtGui.QApplication.processEvents()

            for column in range(printFilter.columnCount()):
                item = printFilter.index(row, column).data()
                html += "<td align=center style='{}'>".format(not_css["td"])
                html += item
                html += "</td>"

            html += "</tr>"
        html += "</table>"

        self.doc.setHtml(html)

    def load_and_create_file(self):
        mode = self.configuration["mode"]
        if mode == "allWorkers":
            self.allWorkersDoc()
        elif mode == "singleWorker":
            self.singleWorkerDoc()
        elif mode == 'totals':
            self.totalsDoc()
        self.createFile()
