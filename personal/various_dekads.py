import os
from datetime import date, datetime
import calendar
import pandas as pd
import math
import time

"""
This module provides functions for date manipulation on a dekadal basis.
"""

def testaggi():

    print "Time in seconds since the epoch: %s" % time.time ()
    print "Current date and time: " , datetime.now ()
    print "Or like this: " , datetime.now ().strftime ( "%y-%m-%d-%H-%M" )
    print "Current year: " , date.today ().strftime ( "%Y" )
    print "Month of year: " , date.today ().strftime ( "%B" )
    print "Week number of the year: " , date.today ().strftime ( "%W" )
    print "Weekday of the week: " , date.today ().strftime ( "%w" )
    print "Day of year: " , date.today ().strftime ( "%j" )
    print "Day of the month : " , date.today ().strftime ( "%d" )
    print "Day of week: " , date.today ().strftime ( "%A" )

def dekad_index(begin, end=None):
    """Creates a pandas datetime index on a decadal basis.

    Parameters
    ----------
    begin : datetime
        Datetime index start date.
    end : datetime, optional
        Datetime index end date, set to current date if None.

    Returns
    -------
    dtindex : pandas.DatetimeIndex
        Dekadal datetime index.
    """

    if end is None:
        end = datetime.now()

    mon_begin = datetime(begin.year, begin.month, 1)
    mon_end = datetime(end.year, end.month, 1)

    daterange = pd.date_range(mon_begin, mon_end, freq='MS')

    dates = []

    for i, dat in enumerate(daterange):
        lday = calendar.monthrange(dat.year, dat.month)[1]
        if i == 0 and begin.day > 1:
            if begin.day < 11:
                if daterange.size == 1:
                    if end.day < 11:
                        dekads = [10]
                    elif end.day >= 11 and end.day < 21:
                        dekads = [10, 20]
                    else:
                        dekads = [10, 20, lday]
                else:
                    dekads = [10, 20, lday]
            elif begin.day >= 11 and begin.day < 21:
                if daterange.size == 1:
                    if end.day < 21:
                        dekads = [20]
                    else:
                        dekads = [20, lday]
                else:
                    dekads = [20, lday]
            else:
                dekads = [lday]
        elif i == (len(daterange) - 1) and end.day < 21:
            if end.day < 11:
                dekads = [10]
            else:
                dekads = [10, 20]
        else:
            dekads = [10, 20, lday]

        for j in dekads:
            dates.append(pd.datetime(dat.year, dat.month, j))

    dtindex = pd.DatetimeIndex(dates)

    return dtindex

def check_dekad(date):
    """Checks the dekad of a date and returns the dekad date.

    Parameters
    ----------
    date : datetime
        Date to check.

    Returns
    -------
    new_date : datetime
        Date of the dekad.
    """
    if date.day < 11:
        dekad = 10
    elif date.day > 10 and date.day < 21:
        dekad = 20
    else:
        dekad = calendar.monthrange(date.year, date.month)[1]

    new_date = datetime(date.year, date.month, dekad)

    return new_date

def dekad2day(year, month, dekad):
    """Gets the day of a dekad.

    Parameters
    ----------
    year : int
        Year of the date.
    month : int
        Month of the date.
    dekad : int
        Dekad of the date.

    Returns
    -------
    day : int
        Day value for the dekad.
    """

    if dekad == 1:
        day = 10
    elif dekad == 2:
        day = 20
    elif dekad == 3:
        day = calendar.monthrange(year, month)[1]

    return day

def runningdekad2date(year, rdekad):
    """Gets the date of the running dekad of a spacifc year.

    Parameters
    ----------
    year : int
        Year of the date.
    rdekad : int
        Running dekad of the date.

    Returns
    -------
    datetime.datetime
        Date value for the running dekad.
    """

    month = int(math.ceil(rdekad / 3.))
    dekad = rdekad - month * 3 + 3
    day = dekad2day(year, month, dekad)

    return datetime(year, month, day)

def day2dekad(day):
    """Returns the dekad of a day.

    Parameters
    ----------
    day : int
        Day of the date.

    Returns
    -------
    dekad : int
        Number of the dekad in a month.
    """

    if day < 11:
        dekad = 1
    elif day > 10 and day < 21:
        dekad = 2
    else:
        dekad = 3

    return dekad

def get_dekad_period(dates):
    """Checks number of the dekad in the current year for dates given as list.

    Parameters
    ----------
    dates : list of datetime
        Dates to check.

    Returns
    -------
    period : list of int
        List of dekad periods.
    """

    period = []

    for dat in dates:
        d = check_dekad(dat)
        dekad = day2dekad(d.day)
        per = dekad + ((d.month - 1) * 3)
        period.append(per)

    return period

oggi = datetime.now()
data_test = datetime(2017,5,5)

prima = datetime(2013,5,2)
seconda = datetime(2011,2,5)
terza = datetime(2015,6,15)
quarta = datetime(2016,12,31)
#testaggi()
print dekad_index(data_test)
print check_dekad(data_test)
print dekad2day(2012,2,1)
print runningdekad2date(2014,23)
print day2dekad(3)
#print get_dekad_period([prima,seconda,terza,quarta])
print get_dekad_period([quarta])