import sys, os
from PyQt4 import QtGui, QtSql, QtCore, uic
from main_view_controller import MainViewController
import assets.sql as sql
import assets.helpers as helpers
from assets.anviz_reader import AnvizReader

YES = QtGui.QMessageBox.Yes
NO = QtGui.QMessageBox.No

qtCreatorFile = "ui\\startDlg.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class StartDlg(Ui_MainWindow, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setImg("images/1965243.jpg")

    def setText(self, text):
        self.info.setText(text)

    def setImg(self, path):
        self.image.setPixmap(QtGui.QPixmap(path))


class Start:
    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)
        self.startDlg = StartDlg()
        self.startDlg.show()

    def __call__(self):
        sys.exit(self.app.exec())

    def tests(self):
        """
        Revision de elementos críticos para el funcionamiento
        del programa
        """

        # Buscar archivo shelve de configuracion
        if sql.ConfigFile.exist():
            text = "Archivo de configuracion encontrado"
        else:
            text = "Archivo de configuracion creado"
            sql.ConfigFile.create()
        self.startDlg.setText(text)

        # buscar archivo de la base de datos
        if os.path.exists(
                sql.ConfigFile.get("database_path")):
            text = "Base de datos encontrada"
        else:
            if self.ask_user_to("search db") == YES:
                self.search_db_file()
            else:
                self.close()
            text = "Base de datos seleccionada"
        self.startDlg.setText(text)

        # conectar con la base de datos
        try:
            anvRgs = sql.AnvizRegisters()
        except ConnectionError:
            if self.ask_user_to('search db', 'invalid') == YES:
                self.search_db_file()
            else:
                self.close()

        # Si no existe, crear tabla para tipos de dias libre
        if anvRgs.tableExists("WorkerPassTypes"):
            text = "Tabla WorkerPassTypes existente"
        else:
            anvRgs.createTable("WorkerPassTypes")
            if anvRgs.query_failed():
                helpers.PopUps.error_message("Error creando la tabla\nWorkerPassTypes",
                                             detailedtext=anvRgs.howthequerydid())
                self.close()
            text = "Tabla WorkerPassTypes creada"
        self.startDlg.setText(text)

        # Si no existe, crear la tabla de dias libre
        if anvRgs.tableExists("WorkerPass"):
            text = "Tabla WorkerPass existente"
        else:
            anvRgs.createTable("WorkerPass")
            if anvRgs.query_failed():
                helpers.PopUps.error_message("Error creando la tabla\nWorkerPass",
                                             detailedtext=anvRgs.howthequerydid())
                self.close()
            text = "Tabla WorkerPass creada"
        self.startDlg.setText(text)

        # revisar la existencia de la tabla WorkDays
        if anvRgs.tableExists("WorkDays"):
            text = "Tabla WorkDays existente"
        else:
            anvRgs.createTable("WorkDays")
            if anvRgs.query_failed():
                helpers.PopUps.error_message("Error creando la tabla\nWorkDays",
                                             detailedtext=anvRgs.howthequerydid())
                self.close()
            text = "Tabla WorkDays creada"
        self.startDlg.setText(text)

        # revisar que existan elementos en la tabla Checkinout
        model = QtSql.QSqlTableModel()
        model.setTable("Checkinout")
        model.select()
        if model.rowCount() == 0:
            helpers.PopUps.inform_user("No hay registros en la base de datos!")

        # Agregar campos requeridos por el programa
        if 'isActive' not in helpers.Db.tableHeader('Userinfo'):
            anvRgs.addColumn('Userinfo', 'isActive', bool)
        if 'isOvernight' not in helpers.Db.tableHeader('Schedule'):
            anvRgs.addColumn('Schedule', 'isOvernight', bool)

        anvRgs.disconnect()

    def updates(self):
        anvizReader = AnvizReader()
        for d in anvizReader.updateTable():
            print(d)
        anvizReader.close_conection()

    def mainview(self):
        mainview = MainViewController()
        mainview.show()
        return mainview

    @staticmethod
    def ask_user_to(option, sub=None):
        messageBox = QtGui.QMessageBox()
        messageBox.setStandardButtons(QtGui.QMessageBox.Yes |
                                      QtGui.QMessageBox.No)
        messageBox.setIcon(QtGui.QMessageBox.Question)

        if option == "search db":
            if sub is None:
                messageBox.setText("La base de datos no fue encontrada...")
            elif sub == "invalid":
                messageBox.setText("La base de datos encontrada es invalida...")

            messageBox.setInformativeText("Desea buscarla?")
            messageBox.setDetailedText("Probablemente se encuentre en"
                                       " la direccion:\n C:\\standard")
        elif option == "reselect":
            messageBox.setText("Desea intentar de nuevo?")

        return messageBox.exec()

    def close(self):
        self.app.closeAllWindows()
        sys.exit()

    def search_db_file(self):
        file_name = ''
        while True:
            file_name = QtGui.QFileDialog.getOpenFileName(
                None, "Seleccionar archivo Access", "C:\\", "Access db (*.mdb)")
            file_name = file_name.replace('/', '\\')
            if file_name:
                sql.ConfigFile.set("database_path", file_name)
                break
            if self.ask_user_to("reselect") == NO:
                self.close()
        return file_name

if __name__ == "__main__":
    start = Start()
    """
    from assets.sql import AnvizRegisters
    AnvizRegisters().deleteRegistersFrom('WorkDays')
    """
    QtGui.QApplication.processEvents()
    start.tests()
    QtGui.QApplication.processEvents()
    start.updates()
    QtGui.QApplication.processEvents()
    start.startDlg.close()
    QtGui.QApplication.processEvents()
    mainview = start.mainview()

    start()