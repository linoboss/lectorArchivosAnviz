import sys
import datetime
from PyQt4 import uic
from PyQt4 import QtGui, QtSql, QtCore
import assets.sql as sql
import assets.helpers as helpers

# Uic Loader
qtCreatorFile = "ui\\workersview.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


(USERID, NAME, SEX) = range(3)
ISACTIVE = 28


class WorkersViewController(Ui_MainWindow, QtBaseClass):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent

        model = QtSql.QSqlRelationalTableModel(self)
        model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        model.setTable('Userinfo')
        model.select()

        model.setHeaderData(USERID, QtCore.Qt.Horizontal, "ID en\nCaptahuellase")
        model.setHeaderData(NAME, QtCore.Qt.Horizontal, "Nombre")
        model.setHeaderData(SEX, QtCore.Qt.Horizontal, "Sexo")
        model.setHeaderData(ISACTIVE, QtCore.Qt.Horizontal, "Esta\nActivo?")

        # self.tableView = QtGui.QTableView()
        self.tableView.setModel(model)
        self.tableView.setItemDelegate(CustomDelegate(self))
        from itertools import chain
        for hc in chain(range(3, 28), range(29, 40)):
            self.tableView.hideColumn(hc)
        self.tableView.setSelectionMode(QtGui.QTableView.SingleSelection)
        self.tableView.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.stackedWidget.setCurrentIndex(0)

        # ADD WORKER INTERFACE

        self.qindate.setDate(QtCore.QDate(1, 1, 1).currentDate())
        self.toolBox.setCurrentIndex(0)

        # workers id
        workers_model = QtSql.QSqlTableModel(self)
        workers_model.setTable("Userinfo")
        workers_model.select()
        self.workersid = helpers.getField(workers_model, "Userid")

        # schedules
        shifts_model = QtSql.QSqlTableModel(self)
        shifts_model.setTable("Schedule")
        shifts_model.select()
        self.qschedule.setModel(shifts_model)
        self.qschedule.setModelColumn(
            1)

        # ghost widgets to include in the mapper
        self.sch_id = QtGui.QSpinBox()
        self.end_date = QtGui.QLineEdit()

        usershift_table = QtSql.QSqlTableModel(self)
        usershift_table.setTable("UserShift")
        usershift_table.select()

        self.mapper_1 = QtGui.QDataWidgetMapper(self)
        self.mapper_1.setModel(usershift_table)
        self.mapper_1.setSubmitPolicy(QtGui.QDataWidgetMapper.ManualSubmit)
        for k, v in ((self.qid, 0),
                     (self.sch_id, 1),
                     (self.qindate, 2),
                     (self.end_date, 3)):
            self.mapper_1.addMapping(k, v)

        userinfo_table = QtSql.QSqlTableModel(self)
        userinfo_table.setTable("Userinfo")
        userinfo_table.select()
        self.mapper_2 = QtGui.QDataWidgetMapper(self)
        self.mapper_2.setModel(userinfo_table)
        self.mapper_2.setSubmitPolicy(QtGui.QDataWidgetMapper.ManualSubmit)
        for k, v in ((self.qid, 0),
                     (self.qname, 1),
                     (self.qsex, 2),
                     (self.qbirthdate, 4),
                     (self.qindate, 7),
                     (self.qphone, 8),
                     (self.qposition, 9),
                     (self.qci, 11),
                     (self.qaddress, 12),
                     (self.qisactive, 28)):
            self.mapper_2.addMapping(k, v)

        for model, mapper in [(usershift_table, self.mapper_1), (userinfo_table, self.mapper_2)]:
            row = model.rowCount()
            model.insertRow(row)
            mapper.setCurrentIndex(row)

    @QtCore.pyqtSlot()
    def on_qaddworker_clicked(self):
        self.stackedWidget.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_qdeleteworker_clicked(self):
        table_model = self.tableView.model()
        selection = self.tableView.selectionModel()
        row = selection.currentIndex().row()
        worker_id = table_model.index(row, 0).data()
        worker_name = table_model.index(row, 1).data()
        worker_gender = table_model.index(row, 2).data()
        letter = 'a' if worker_gender == "Femenino" else 'o'

        user_ans = helpers.PopUps.ask_user_to("{} sera eliminad{} de la base de "
                                              "datos permanentemente, proceder?".format(worker_name, letter))
        if user_ans == helpers.YES:
            self.removeWorker(worker_id)
            table_model.select()

    @staticmethod
    def removeWorker(worker_id):
        workdays_model = QtSql.QSqlTableModel()
        workdays_model.setTable("WorkDays")
        workdays_model.setFilter("worker='{}'".format(worker_id))
        workdays_model.select()
        for row in range(workdays_model.rowCount()):
            workdays_model.removeRow(row)
        workdays_model.submitAll()

        usershift_model = QtSql.QSqlTableModel()
        usershift_model.setTable("UserShift")
        usershift_model.setFilter("Userid='{}'".format(worker_id))
        usershift_model.select()
        usershift_model.removeRow(0)
        usershift_model.submitAll()

        userinfo_model = QtSql.QSqlTableModel()
        userinfo_model.setTable("Userinfo")
        userinfo_model.setFilter("Userid='{}'".format(worker_id))
        userinfo_model.select()
        userinfo_model.removeRow(0)
        userinfo_model.submitAll()
        userinfo_model.select()

    @QtCore.pyqtSlot()
    def on_qadd_clicked(self):
        # get schedule id
        schid = self.qschedule.model().index(
            self.qschedule.currentIndex(),
            0).data()

        self.sch_id.setValue(schid)
        self.end_date.setText("No")

        # Checking for no duplicated ids
        id_worker = self.qid.value()
        if id_worker == 0:
            helpers.PopUps.inform_user("ID en captahuellas no puede ser cero")
            return
        elif id_worker in self.workersid:
            helpers.PopUps.inform_user("ID en captahuellas duplicada")
            return

        for mapper in (self.mapper_1, self.mapper_2):
            self.qid.setValue(id_worker)
            model = mapper.model()
            row = model.rowCount()
            mapper.submit()
            model.insertRow(row)
            mapper.setCurrentIndex(row)
            model.select()
            model.submitAll()
        self.tableView.model().select()

        self.stackedWidget.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_qcancel_clicked(self):
        self.clear_fields()
        self.stackedWidget.setCurrentIndex(0)

    def clear_fields(self):
        for widget in (self.qid,
                       self.sch_id,
                       self.qindate,
                       self.end_date,
                       self.qid,
                       self.qname,
                       self.qsex,
                       self.qbirthdate,
                       self.qindate,
                       self.qphone,
                       self.qposition,
                       self.qci,
                       self.qaddress,
                       self.qisactive):
            if type(widget) is QtGui.QLineEdit:
                widget.setText("")
            elif type(widget) is QtGui.QTextEdit:
                widget.setText("")
            elif type(widget) is QtGui.QDateEdit:
                widget.setDate(datetime.datetime.now().date())
            elif type(widget) is QtGui.QSpinBox:
                widget.setValue(0)



class CustomDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent = None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        column = index.column()
        item = index.data()
        if column == ISACTIVE:
            painter.save()
            if option.state & QtGui.QStyle.State_Selected:
                painter.setPen(QtCore.Qt.white)
                painter.setBrush(option.palette.highlightedText())
                painter.fillRect(option.rect, option.palette.highlight())
            isActive = 'Si' if item else 'No'
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, isActive)
            painter.restore()
        else:
            QtSql.QSqlRelationalDelegate().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        column = index.column()
        if column == ISACTIVE:
            editor = QtGui.QComboBox(parent)
        elif column == SEX:
            editor = QtGui.QComboBox(parent)
        else:
            editor = QtGui.QTextEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        column = index.column()
        item = index.data()
        if column == ISACTIVE:
            # editor = QtGui.QComboBox()
            editor.addItems('No Si'.split())
            editor.setCurrentIndex(item)
        elif column == SEX:
            editor.addItems("Femenino Masculino".split())
            editor.setCurrentText(item)
        else:
            editor.setText(item)

    def commitAndCloseEditor(self):
        pass

    def setModelData(self, editor, model, index):
        # model = QtSql.QSqlRelationalTableModel()
        if isinstance(editor, QtGui.QTextEdit):
            item = editor.toPlainText()
        elif isinstance(editor, QtGui.QComboBox):
            item = editor.currentText()
        else:
            # editor = QtGui.QComboBox()
            item = editor.currentIndex()
        model.setData(index, item)

    def sizeHint(self, option, item):
        return QtCore.QSize(100, 20)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    sql.AnvizRegisters()

    checkioview = WorkersViewController()
    checkioview.show()

    sys.exit(app.exec())
