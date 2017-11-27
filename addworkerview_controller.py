import sys
from PyQt4 import uic
from PyQt4 import QtGui, QtSql, QtCore
import assets.sql as sql
import assets.helpers as helpers
import assets.work_day_tools as tool

# Uic Loader
qtCreatorFile = "ui\\addworkerview.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class AddWorkerView_controller(Ui_MainWindow, QtBaseClass):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)
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
        self.parent.tableView.model().select()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    aw = AddWorkerView_controller()
    aw.show()
    sys.exit(app.exec())

