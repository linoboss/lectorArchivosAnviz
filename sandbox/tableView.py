# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tableView.ui'
#
# Created: Sun Jul  3 12:33:11 2016
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(601, 458)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.b = QtGui.QDateTimeEdit(self.centralwidget)
        self.b.setObjectName(_fromUtf8("b"))
        self.gridLayout.addWidget(self.b, 2, 0, 1, 1)
        self.id = QtGui.QLabel(self.centralwidget)
        self.id.setMinimumSize(QtCore.QSize(100, 0))
        self.id.setObjectName(_fromUtf8("id"))
        self.gridLayout.addWidget(self.id, 1, 0, 1, 1)
        self.c = QtGui.QLineEdit(self.centralwidget)
        self.c.setObjectName(_fromUtf8("c"))
        self.gridLayout.addWidget(self.c, 2, 1, 1, 1)
        self.a = QtGui.QLineEdit(self.centralwidget)
        self.a.setObjectName(_fromUtf8("a"))
        self.gridLayout.addWidget(self.a, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.tableView = QtGui.QTableView(self.centralwidget)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout.addWidget(self.tableView)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 601, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.id.setText(_translate("MainWindow", "TextLabel", None))

