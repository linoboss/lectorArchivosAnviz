import datetime as dt
import calendar
from dateutil.relativedelta import relativedelta

DIAS_SEMANA = ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo')
MESES = ('', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre',
         'Diciembre')

class MyDates:
    @staticmethod
    def monthFirstDate(year, month):
        return dt.date(year, month, 1)

    @staticmethod
    def monthLastDate(year, month):
        cal = calendar.Calendar()
        to_date_last = max(list(cal.itermonthdays(year, month)))
        return dt.date(year, month, to_date_last)

    @staticmethod
    def monthName(m):
        return MESES[m]

    @staticmethod
    def dayName(y=1, m=1, d=1):
        if isinstance(y, dt.date):
            date = y
            return DIAS_SEMANA[calendar.weekday(date.year, date.month, date.day)]
        return DIAS_SEMANA[calendar.weekday(y, m, d)]

    @staticmethod
    def dayNumber(y=1, m=1, d=1):
        return calendar.weekday(y, m, d)

    @staticmethod
    def fechaActual():
        return dt.datetime.now().date()

    @staticmethod
    def ahora():
        return dt.datetime.now()

    @staticmethod
    def mesSiguiente(date):
        return date + relativedelta(months=1)

    @staticmethod
    def mesAnterior(date):
        return date - relativedelta(months=1)

    @staticmethod
    def getWeek(date):
        week = None
        weeks = calendar.monthcalendar(date.year, date.month)
        for week in weeks:
            if date.day in week:
                break
        return week

    @staticmethod
    def oneDay():
        return dt.timedelta(days=1)

    @staticmethod
    def add_months(sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return dt.date(year, month, day)

    @staticmethod
    def dates_range(from_date, to_date):
        dates_range_ = []
        d = from_date
        while d <= to_date:
            dates_range_.append(d)
            d += relativedelta(days=1)
        return dates_range_

    @staticmethod
    def next_day(d):
        return d + relativedelta(days=1)

    @staticmethod
    def dateToString(d, option='default'):
        if option == 'default':
            return '{} {} de {} de {}'.format(
                MyDates.dayName(d),
                d.day, MyDates.monthName(d.month),
                d.year
            )

    @staticmethod
    def isValid(d):
        if dt.MINYEAR < d.year < dt.MAXYEAR:
            return True
        else:
            return False


# **TESTS**


def dates_range():
    d1 = dt.date(2015, 5, 5)
    d2 = dt.date(2015, 5, 10)
    pprint(MyDates.dates_range(d1, d2))


if __name__ == "__main__":
    from pprint import pprint

    print(MyDates.dateToString(dt.datetime.now().date()))
