import sys
from PyQt4 import uic
from PyQt4 import QtCore, QtGui, QtSql
from assets.anviz_reader import AnvizReader


qtCreatorFile = "tableViews.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class View(Ui_MainWindow, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        anvReader = AnvizReader()

        model = QtSql.QSqlRelationalTableModel()
        model.setTable('AddTimeSet')
        model.select()
        self.tableView.setModel(model)
        model_2 = QtSql.QSqlRelationalTableModel()
        model_2.setTable('OPinfo')
        model_2.select()
        self.tableView_2.setModel(model_2)

        self.mapper = QtGui.QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QtGui.QDataWidgetMapper.ManualSubmit)
        self.mapper.setModel(model)
        self.mapper.addMapping(self.lineEdit, 0)
        self.mapper.addMapping(self.dateTimeEdit, 1)
        self.mapper.addMapping(self.spinBox, 2)
        row = model.rowCount()
        model.insertRow(row)
        self.mapper.setCurrentIndex(row)

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        model = self.mapper.model()
        self.mapper.submit()
        model.select()


app = QtGui.QApplication(sys.argv)
view = View()
view.show()
sys.exit(app.exec())


