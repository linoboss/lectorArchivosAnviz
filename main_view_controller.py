__author__ = 'SG_LAURA'


import sys
from PyQt4 import uic
from PyQt4 import QtCore, QtGui
import assets.helpers as helpers
from assistence_table_controller import AssistenceTableController
from configview_controller import ConfigViewController
from workersviewcontroller import WorkersViewController
from checkinoutviewcontroller import CheckinoutViewController
from daysoffviewcontroller import DaysoffViewController

qtCreatorFile = "ui\\MainView.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainViewController(Ui_MainWindow, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.widgets_map = {}

        self.assistence_table = AssistenceTableController()
        self.add_interface("assistence", self.assistence_table)

        self.config_view = ConfigViewController()
        self.add_interface("config_view", self.config_view)

        self.workers_view = WorkersViewController()
        self.add_interface("workers_view", self.workers_view)

        self.registers_view = CheckinoutViewController()
        self.add_interface("registers", self.registers_view)

        self.daysoff_view = DaysoffViewController()
        self.add_interface("daysoff", self.daysoff_view)

        self.select_interface("assistence")

    def add_interface(self, name, widget):
        self.widgets_map[name] = \
            self.stackedWidget.addWidget(widget)

    def select_interface(self, name):
        self.stackedWidget.setCurrentIndex(self.widgets_map[name])

    @QtCore.pyqtSlot("QAction*")
    def on_menubar_triggered(self, action):
        # TODO add security here
        if action is self.action_assistence:
            self.assistence_table.updateModel()
            self.select_interface("assistence")
        elif action is self.action_database:
            self.select_interface("config_view")
            # TODO ask user to reopen program
            """
            self.connect(configview, QtCore.SIGNAL('dbChanged()'), self.ask_user_to_reopen_program)
            self.connect(configview, QtCore.SIGNAL('registersErased()'), self.ask_user_to_reopen_program)
            """
        elif action is self.action_workers:
            self.select_interface("workers_view")
        elif action is self.action_registers:
            self.select_interface("registers")
        elif action is self.action_daysoff:
            self.select_interface("daysoff")
        """
        elif action is self.action_registers:
            from checkinoutview_controller import Checkinoutview_Controller
            checkioview = Checkinoutview_Controller(self)
            checkioview.exec()
        elif action is self.action_schedules:
            from schedulesview_controller import Schedulesview_Controller
            schview = Schedulesview_Controller(self)
            schview.exec()
        elif action is self.action_workers:
            from workersview_controller import Workersview_controller
            checkioview = Workersview_controller(self)
            checkioview.exec()
        elif action is self.action_daysoff:
            from daysoffview_controller import Daysoffview_controller
            daysoff_view = Daysoffview_controller(self)
            daysoff_view.exec()
        else:
            helpers.PopUps.inform_user("not implemented!")

        """
        #self.assistence_table.updateModel()

    @staticmethod
    def closeProgram():
        app = QtGui.QApplication.instance()
        app.closeAllWindows()
        sys.exit()

    def ask_user_to_reopen_program(self):
        helpers.PopUps.inform_user("El programa cerrara automaticamente.\n"
                                   "Por favor, abralo nuevamente")
        QtGui.QApplication.instance().closeAllWindows()
        sys.exit()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mvc = MainViewController()
    mvc.show()
    sys.exit(app.exec_())
