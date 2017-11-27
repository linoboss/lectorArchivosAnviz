import sys
from PyQt4 import uic
from PyQt4 import QtGui, QtSql, QtCore
import assets.sql as sql

# Uic Loader
qtCreatorFile = "ui\\schedulesview.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


(TIMEID, TIMENAME, INTIME, OUTTIME,
 BINTIME, EINTIME, BOUTTIME, EOUTTIME) = range(8)


class Schedulesview_Controller(Ui_MainWindow, QtBaseClass):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent

        listmodel = QtSql.QSqlTableModel(self)
        listmodel.setTable("Schedule")
        listmodel.setEditStrategy(listmodel.OnFieldChange)
        listmodel.select()
        # QtGui.QListView().setColum
        self.listView.setModel(listmodel)
        self.listView.setModelColumn(1)

        self.mapper = QtGui.QDataWidgetMapper(self)
        self.mapper.setModel(listmodel)
        self.mapper.addMapping(self.qisOvernight, 5)
        self.mapper.setSubmitPolicy(QtGui.QDataWidgetMapper.AutoSubmit)
        self.mapper.setCurrentIndex(0)

        model = QtSql.QSqlRelationalTableModel(self)
        model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        model.setTable('TimeTable')
        model.select()
        model.setHeaderData(TIMENAME, QtCore.Qt.Horizontal, "Turno")
        model.setHeaderData(INTIME, QtCore.Qt.Horizontal, "Entrada")
        model.setHeaderData(OUTTIME, QtCore.Qt.Horizontal, "Salida")
        model.setHeaderData(BINTIME, QtCore.Qt.Horizontal, "Inicio de\nEntrada")
        model.setHeaderData(EINTIME, QtCore.Qt.Horizontal, "Fin de la\nEntrada")
        model.setHeaderData(BOUTTIME, QtCore.Qt.Horizontal, "Inicio de\nSalida")
        model.setHeaderData(EOUTTIME, QtCore.Qt.Horizontal, "Fin de la\nSalida")

        proxymodel = ProxyModel(self)
        proxymodel.setSourceModel(model)
        proxymodel.setFilterKeyColumn(0)
        proxymodel.setFilterRegExp(
            self.filter_arg(
                str(listmodel.index(0, 0).data())
            )
        )

        # self.tableView = QtGui.QTableView()
        self.tableView.setModel(proxymodel)
        self.tableView.setItemDelegate(CustomDelegate(self))
        for hc in (0, 8, 9, 10, 11, 12, 13, 14, 15):
            self.tableView.hideColumn(hc)
        self.tableView.setSelectionMode(QtGui.QTableView.SingleSelection)
        self.tableView.setSelectionBehavior(QtGui.QTableView.SelectItems)

    @QtCore.pyqtSlot("QModelIndex")
    def on_listView_clicked(self, index):
        self.mapper.setCurrentModelIndex(index)
        model = self.listView.model()
        schid = model.index(index.row(), 0).data()

        regex_filter = self.filter_arg(schid)

        proxymodel = self.tableView.model()
        proxymodel.setFilterRegExp(regex_filter)

    @staticmethod
    def filter_arg(schid):
        schtime_table = QtSql.QSqlTableModel()
        schtime_table.setTable("SchTime")
        schtime_table.select()
        proxy_schtime_table = QtGui.QSortFilterProxyModel()
        proxy_schtime_table.setSourceModel(schtime_table)
        proxy_schtime_table.setFilterKeyColumn(0)
        proxy_schtime_table.setFilterRegExp(str(schid))
        list_ = []
        for row in range(proxy_schtime_table.rowCount()):
            list_.append((
                proxy_schtime_table.index(row, 0).data(),
                proxy_schtime_table.index(row, 2).data()
            ))
        options = list(set(list_))
        items = list(map(lambda x: str(x[1]), options))
        regex_filter = '|'.join(items)
        return regex_filter


class ProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def setData(self, index, item, int_role=None):
        sIndex = self.mapToSource(index)
        smodel = self.sourceModel()
        smodel.setData(sIndex, item)


class CustomDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent = None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        column = index.column()
        item = index.data()
        if column == TIMENAME:
            painter.save()
            if option.state & QtGui.QStyle.State_Selected:
                painter.setPen(QtCore.Qt.white)
                painter.setBrush(option.palette.highlightedText())
                painter.fillRect(option.rect, option.palette.highlight())
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, item.capitalize())
            painter.restore()
        else:
            QtSql.QSqlRelationalDelegate().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        column = index.column()
        if column == TIMENAME:
            editor = None  # QtGui.QTextEdit(parent)
        else:
            editor = QtGui.QTimeEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        column = index.column()
        item = index.data()
        if column == TIMENAME:
            editor.setText(item)
        else:
            # editor = QtGui.QTimeEdit()
            time = QtCore.QTime().fromString(item, "h:m")
            editor.setTime(time)

    def commitAndCloseEditor(self):
        pass

    def setModelData(self, editor, model, index):
        # model = QtSql.QSqlRelationalTableModel()
        if isinstance(editor, QtGui.QTextEdit):
            text = editor.toPlainText()
        else:
            text = editor.time().toString("hh:mm")
        model.setData(index, text)

    def sizeHint(self, option, index):
        return QtCore.QSize(100, 20)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    sql.AnvizRegisters()

    checkioview = Schedulesview_Controller()
    checkioview.show()

    sys.exit(app.exec())
