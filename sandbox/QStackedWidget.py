import sys
import time
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui, QtSql
from assets.anviz_reader import AnvizReader


qtCreatorFile = "QStackedWidget.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainView(Ui_MainWindow, QtBaseClass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.anvRgs = AnvizReader()
        # self.qworkers = QtGui.QComboBox()
        self.qworkers.addItems(
            ["Todos"] + self.anvRgs.workers_names)
        self.qdatesfilter.setCurrentIndex(0)

    @QtCore.pyqtSlot("QString")
    def on_qworkers_currentIndexChanged(self, text):
        print(text)

    @QtCore.pyqtSlot()
    def on_qprint_clicked(self):
        self.qprint.setDisabled(True)
        print("imprimir")

        time.sleep(1)
        QtGui.QApplication.processEvents()  # flushes the signal queue and prevents multiple clicks

        self.qprint.setDisabled(False)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainView()
    window.show()
    sys.exit(app.exec())
