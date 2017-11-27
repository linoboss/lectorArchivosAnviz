import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from assets.sql import AnvizRegisters
from assets.dates_tricks import MyDates as md
import datetime as dt
from pprint import pprint
app = QtGui.QApplication(sys.argv)

avzRgs = AnvizRegisters()

workers = avzRgs.getWorkers("names")
pprint(workers)

from_date = avzRgs.min_date_of("Checkinout")
to_date = avzRgs.max_date_of("Checkinout")

dates_range = md.dates_range(from_date, to_date)
time1 = dt.datetime.now()

for d in dates_range:
    avzRgs.query.prepare("SELECT Logid, Userid, CheckTime "
                         "FROM Checkinout "
                         "WHERE FORMAT(CheckTime, 'yyyy-mm-dd') = FORMAT(:from_date, 'yyyy-mm-dd')")
    avzRgs.query.bindValue(":from_date", QtCore.QDate(d))
    avzRgs.query.exec_()
    avzRgs.next()
    print(avzRgs.value(2), d)

time2 = dt.datetime.now()

print("total operation time:", time2 - time1)
time1 = dt.datetime.now()

avzRgs.query.exec("SELECT Logid, Userid, CheckTime "
                  "FROM Checkinout "
                  "ORDER BY CheckTime ASC")
while avzRgs.next():
    avzRgs.next()
    print(avzRgs.value(0), avzRgs.value(1), avzRgs.value(2))

time2 = dt.datetime.now()

print("total operation time:", time2 - time1)

sys.exit()
