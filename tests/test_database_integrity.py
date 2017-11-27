import sys, os

import pytest
from assets.anviz_reader import AnvizReader
from PyQt4 import QtSql

anvReader = AnvizReader()


def test_critical_tables_exist():
    tables = QtSql.QSqlDatabase().tables()
    assert "WorDays" in tables
