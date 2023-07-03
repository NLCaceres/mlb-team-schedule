from datetime import date, datetime, timedelta
from DodgersPromo.utility.datetime_helpers import (dateToday, isDatetime, dateToStr, 
                                                   strToDatetime, utcStrToPacificTime, utcDateTimeToPacificTimeStr)

def test_dateToday():
    todays_date = dateToday()
    also_today = date.today()

    assert todays_date.year == also_today.year
    assert todays_date.month == also_today.month
    assert todays_date.day == also_today.day

def test_isDatetime():
    todays_date = dateToday()
    todays_datetime = datetime.utcnow()

    date_is_datetime = isDatetime(todays_date)
    str_is_datetime = isDatetime('not a date')
    datetime_is_datetime = isDatetime(todays_datetime)

    assert date_is_datetime is False
    assert str_is_datetime is False
    assert datetime_is_datetime is True

def test_dateToStr():
    todays_date = dateToday()
    todays_date_str = dateToStr(todays_date, '%Y-%m-%d')
    [year_str, month_str, day_str] = todays_date_str.split('-')

    #? While this'll work in Javascript, not all Python types are subscriptable (like lists or dicts)
    # date_elems = ['year', 'month', 'day']
    # for elem, prop in zip(date_str_elems, date_elems):
    #     assert elem == todays_date[prop]

    assert int(year_str) == todays_date.year
    assert int(month_str) == todays_date.month
    assert int(day_str) == todays_date.day

def test_strToDatetime():
    date_str = '12/25/2010'
    some_datetime = strToDatetime(date_str, '%m/%d/%Y')

    assert some_datetime.year == 2010
    assert some_datetime.month == 12
    assert some_datetime.day == 25

def test_utcStrToPacificTime():
    utc_str = '1990-02-10T04:15:35Z'
    pdt_str = utcStrToPacificTime(utc_str)
    assert pdt_str == 'Fri February 09 1990 at 09:15 PM' #? PDT is -7 hours from UTC, i.e. Daylight Savings

    pst_str = utcStrToPacificTime(utc_str, False) #? PST is -8 hours from UTC
    assert pst_str == 'Fri February 09 1990 at 08:15 PM'

def test_utcDateTimeToPacificTimeStr():
    utc_datetime = datetime.utcnow()
    pdt_str = utcDateTimeToPacificTimeStr(utc_datetime, '%a %B %d %Y at %I:%M %p')
    day_index = 2
    year_index = 3
    time_index = 5
    pdt_str_elems = pdt_str.split()

    pdt_datetime = utc_datetime - timedelta(hours=7)
    assert pdt_datetime.day == int(pdt_str_elems[day_index])
    assert pdt_datetime.year == int(pdt_str_elems[year_index])

    pdt_time = pdt_str_elems[time_index].split(':')
    pdt_datetime_hour = pdt_datetime.hour
    #* Need to adjust for military 0-23 time
    pdt_datetime_correct_hour = pdt_datetime_hour + 12 if pdt_datetime_hour == 0 else (
        (pdt_datetime_hour - 12) if pdt_datetime_hour > 12 else pdt_datetime_hour
    )
    assert pdt_datetime_correct_hour == int(pdt_time[0])
    assert pdt_datetime.minute == int(pdt_time[1])

    #! PST Version
    pst_str = utcDateTimeToPacificTimeStr(utc_datetime, '%a %B %d %Y at %I:%M %p', False)
    pst_str_elems = pst_str.split()
    pst_datetime = utc_datetime - timedelta(hours=8)
    assert pst_datetime.day == int(pst_str_elems[day_index])
    assert pst_datetime.year == int(pst_str_elems[year_index])

    pst_time = pst_str_elems[time_index].split(':')
    pst_datetime_hour = pst_datetime.hour
    #* Need to adjust for military 0-23 time
    pst_datetime_correct_hour = pst_datetime_hour + 12 if pst_datetime_hour == 0 else (
        (pst_datetime_hour - 12) if pst_datetime_hour > 12 else pst_datetime_hour
    )
    assert pst_datetime_correct_hour == int(pst_time[0])
    #? Since PST == -8 BUT PDT == -7, so it must subtract 1 extra hour
    adjusted_pdt_time = 12 if pdt_datetime_correct_hour == 1 else pdt_datetime_correct_hour - 1
    assert int(pst_time[0]) ==  adjusted_pdt_time
    assert pst_datetime.minute == int(pst_time[1])
    assert int(pst_time[1]) == int(pdt_time[1])

def test_utcDateTimeToPacificTimeStr_withOtherFormat():
    utc_datetime = datetime.utcnow()
    pdt_str = utcDateTimeToPacificTimeStr(utc_datetime, '%d %Y')
    [day, year] = pdt_str.split()

    pdt_datetime = utc_datetime - timedelta(hours=7)
    assert pdt_datetime.day == int(day)
    assert pdt_datetime.year == int(year)
    