import pytest
from datetime import date, datetime, timedelta
from DodgersPromo.utility.datetime_helpers import (dateToday, isDatetime, dateToStr, strToDatetime, ISO_FORMAT,
                                                   utcStrToPacificTimeStr, utcStrToPacificDatetime,
                                                   utcDatetimeToPacificDatetime,
                                                   utcDatetimeToPacificTimeStr, utcDatetimeToReadablePacificTimeStr)


def test_dateToday():
    #* WHEN using dateToday()
    todays_date = dateToday()
    also_today = date.today()
    #* THEN it acts as a simple alias for date.today()
    assert todays_date.year == also_today.year
    assert todays_date.month == also_today.month
    assert todays_date.day == also_today.day


def test_isDatetime():
    #* WHEN directly requesting a datetime via utcnow()
    todays_datetime = datetime.utcnow()
    #* THEN isDatetime, of course, returns True
    assert isDatetime(todays_datetime) is True
    
    #* WHEN using my dateToday() alias to request the current datetime
    todays_date = dateToday()
    #* THEN isDatetime returns False since a date is NOT a datetime, just similar
    assert isDatetime(todays_date) is False

    #* WHEN using a string
    #* THEN isDatetime returns False
    assert isDatetime('not a date') is False
    #* THEN isDatetime returns False EVEN IF a string that could be formatted into a date
    assert isDatetime('2021-03-01') is False
    
    #* WHEN using an int
    #* THEN isDatetime returns False
    assert isDatetime(123) is False


def test_dateToStr():
    #* WHEN converting any date into a string using a specific format
    todays_date = dateToday()
    todays_date_str = dateToStr(todays_date, '%Y-%m-%d')
    [year_str, month_str, day_str] = todays_date_str.split('-')
    #* THEN the date values will predictably appear in that format (allowing for easy splitting to grab for these tests)
    assert int(year_str) == todays_date.year
    assert int(month_str) == todays_date.month
    assert int(day_str) == todays_date.day
    #? This would work in Javascript, BUT in Python, not all types are subscriptable, like lists or dicts
    # date_elems = ['year', 'month', 'day']
    # for elem, prop in zip(date_str_elems, date_elems):
    #     assert elem == todays_date[prop]


def test_strToDatetime():
    #* WHEN converting a string using a known format
    date_str = '12/25/2010'
    some_datetime = strToDatetime(date_str, '%m/%d/%Y')
    #* THEN the string is converted into a datetime properly
    assert some_datetime.year == 2010
    assert some_datetime.month == 12
    assert some_datetime.day == 25

    #* WHEN converting a string using an incorrect/unknown format
    with pytest.raises(ValueError):
        strToDatetime(date_str, '%Y/%m/%d')
        #* THEN the string is NOT converted into a datetime properly and throws a ValueError due to unmatched format
        #* BECAUSE strToDatetime functionally is an alias for datetime.strptime(some_date_str, format_str)


#! UTC string to Pacific Time converters
def test_utcStrToPacificTimeStr():
    #* WHEN the UTC string is converted into a PDT string
    utc_str = '1990-02-10T04:15:35Z'
    pdt_str = utcStrToPacificTimeStr(utc_str)
    #* THEN it shifts back 7 hours from Feb 10 to Feb 9 9:15 PM, 7 hours earlier
    assert pdt_str == 'Fri February 09 1990 at 09:15 PM' #? PDT is -7 hours from UTC, i.e. Daylight Savings

    #* WHEN the UTC string is converted into a PST string
    pst_str = utcStrToPacificTimeStr(utc_str, daylight_savings = False) #? PST is -8 hours from UTC
    #* THEN it shifts back 8 hours from Feb 10 to Feb 9 8:15 PM, 8 hours earlier
    assert pst_str == 'Fri February 09 1990 at 08:15 PM'

    #* WHEN an improperly formatted UTC string is used
    with pytest.raises(ValueError):
        #* THEN a ValueError is raised
        utcStrToPacificTimeStr('1990-02-10T04:15Z')


def test_utcStrToPacificDatetime():
    #* WHEN a properly formatted UTC string is used
    utc_str = '2011-05-22T06:32:35Z' #* May 22nd 2011 at 6:32 AM
    pdt_datetime = utcStrToPacificDatetime(utc_str)
    #* THEN its converted to a datetime, and shifted back 7 hours
    assert pdt_datetime.year == 2011
    assert pdt_datetime.month == 5
    #? Since the UTC date is the 22nd at 6 AM, and PDT is -7 hours from UTC, the time is 11:32PM/21:32 on the 21st instead
    assert pdt_datetime.day == 21
    assert pdt_datetime.hour == 23
    assert pdt_datetime.minute == 32

    #* WHEN a properly formatted UTC string used w/out daylight_savings
    pst_datetime = utcStrToPacificDatetime(utc_str, daylight_savings = False) #? PST is -8 hours from UTC
    #* THEN its converted to a datetime, and shifted back 8 hours
    assert pst_datetime.year == 2011
    assert pst_datetime.month == 5
    #? PST is -8 from UTC, so it's 10:32PM on the 21st here
    assert pst_datetime.day == 21
    assert pst_datetime.hour == 22
    assert pst_datetime.minute == 32

    #* WHEN a UTC string is used that is not in the expected ISO format
    with pytest.raises(ValueError):
        #* THEN a Value Error is raised
        utcStrToPacificDatetime('2011-05-22')


def test_utcDatetimeToPacificDatetime():
    utc_str = '2005-06-02T01:15:35Z'
    #* WHEN a UTC datetime is converted into a PDT datetime
    utc_datetime = strToDatetime(utc_str, ISO_FORMAT)
    pdt_datetime = utcDatetimeToPacificDatetime(utc_datetime)
    #* THEN the time is shifted 7 hours as expected
    assert utc_datetime.day == 2 #? Since the UTC datetime is set to June 2 1:15AM
    assert pdt_datetime.day == 1 #? Converting it to PDT makes the date June 1 6:15PM
    assert pdt_datetime.hour == 18 #? So it's 18:15 military time

    #* WHEN a UTC datetime is converted into a PST datetime
    pst_datetime = utcDatetimeToPacificDatetime(utc_datetime, daylight_savings = False)
    #* THEN the time is shifted 8 hours as expected
    assert pst_datetime.day == 1
    assert pst_datetime.hour == 17 #? During PST, it's 17:15 military time


def test_utcDateTimeToPacificTimeStr():
    #* WHEN a UTC datetime is converted into a PDT string of a specific format
    utc_datetime = datetime.utcnow()
    pdt_str = utcDatetimeToPacificTimeStr(utc_datetime, '%a %B %d %Y at %I:%M %p')
    pdt_datetime = utc_datetime - timedelta(hours=7)
    pdt_datetime_hour = pdt_datetime.hour #* Need to change the hours into military 0-23 time
    expected_pdt_datetime_hour = pdt_datetime_hour + 12 if pdt_datetime_hour == 0 else (
        (pdt_datetime_hour - 12) if pdt_datetime_hour > 12 else pdt_datetime_hour
    )
    pdt_date_vals = pdt_str.split()
    time_index = 5 #* Time is %I:%M in the format string
    pdt_time_vals = pdt_date_vals[time_index].split(':')
    day_index = 2 #* Day is %d in the format string
    year_index = 3 #* Year is %Y in the format string
    #* THEN it can be reliably split into its date values and predicted to be 7 hours earlier than its UTC version
    assert pdt_datetime.day == int(pdt_date_vals[day_index])
    assert pdt_datetime.year == int(pdt_date_vals[year_index])
    assert expected_pdt_datetime_hour == int(pdt_time_vals[0])
    assert pdt_datetime.minute == int(pdt_time_vals[1])

    #* WHEN a UTC datetime is converted into a PST string of a specific format
    pst_str = utcDatetimeToPacificTimeStr(utc_datetime, '%a %B %d %Y at %I:%M %p', False)
    pst_datetime = utc_datetime - timedelta(hours=8)
    pst_datetime_hour = pst_datetime.hour #* Need to change the hours into military 0-23 time
    expected_pst_datetime_hour = pst_datetime_hour + 12 if pst_datetime_hour == 0 else (
        (pst_datetime_hour - 12) if pst_datetime_hour > 12 else pst_datetime_hour
    ) #? Since PST == -8 BUT PDT == -7, so it must subtract 1 extra hour
    adjusted_pdt_time = 12 if expected_pdt_datetime_hour == 1 else expected_pdt_datetime_hour - 1
    pst_date_vals = pst_str.split()
    pst_time = pst_date_vals[time_index].split(':')
    #* THEN the date values remain the same as the PDT version (day, year and even minutes)
    assert pst_datetime.day == int(pst_date_vals[day_index])
    assert pst_datetime.year == int(pst_date_vals[year_index])
    assert int(pst_time[1]) == int(pdt_time_vals[1])
    #* EXCEPT for the hour which is reduced by 1 due to the 8 hour offset of PST vs 7 of PDT
    assert expected_pst_datetime_hour == int(pst_time[0])
    assert int(pst_time[0]) ==  adjusted_pdt_time
    assert pst_datetime.minute == int(pst_time[1])

    #* WHEN the format changes
    pdt_str = utcDatetimeToPacificTimeStr(utc_datetime, '%d %Y')
    [day, year] = pdt_str.split()
    #* THEN regardless of formatting, the returned string has matching date values (day and year here)
    pdt_datetime = utc_datetime - timedelta(hours=7)
    assert pdt_datetime.day == int(day)
    assert pdt_datetime.year == int(year)


def test_utcDatetimeToReadablePacificTimeStr():
    utc_str = '2013-11-27T07:12:25Z'
    utc_datetime = strToDatetime(utc_str, ISO_FORMAT)
    #* WHEN a UTC datetime is converted into a Locale readable PDT date string
    pdt_date_str = utcDatetimeToReadablePacificTimeStr(utc_datetime)
    #* THEN the time is shifted 7 hours back as expected
    assert pdt_date_str == 'Wed November 27 2013 at 12:12 AM' #* from 7:12AM to 12:12AM same day

    #* WHEN a UTC datetime is converted into a Locale readable PST date string
    pst_date_str = utcDatetimeToReadablePacificTimeStr(utc_datetime, daylight_savings = False)
    #* THEN the time is shifted 8 hours back as expected
    assert pst_date_str == 'Tue November 26 2013 at 11:12 PM' #* from 7:12AM to 11:12PM the night before!
