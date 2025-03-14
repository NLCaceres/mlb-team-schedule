from mlb_team_schedule.utility.datetime_helpers import (
    dateToday, dateToStr, isDatetime, strToDatetime,
)

import pytest
from datetime import UTC, date, datetime


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
    todays_datetime = datetime.now(UTC)
    #* THEN isDatetime, of course, returns True
    assert isDatetime(todays_datetime) is True

    #* WHEN using my dateToday() alias to request the current datetime
    todays_date = dateToday()
    #* THEN isDatetime returns False since a date is NOT a datetime, just similar
    assert isDatetime(todays_date) is False

    #* WHEN using a string
    #* THEN isDatetime returns False
    assert isDatetime("not a date") is False
    #* THEN isDatetime returns False EVEN IF a string that could be formatted into a date
    assert isDatetime("2021-03-01") is False

    #* WHEN using an int
    #* THEN isDatetime returns False
    assert isDatetime(123) is False


def test_dateToStr():
    #* WHEN converting any date into a string using a specific format
    todays_date = dateToday()
    todays_date_str = dateToStr(todays_date, "%Y-%m-%d")
    [year_str, month_str, day_str] = todays_date_str.split("-")
    #* THEN date values predictably appear in format
    assert int(year_str) == todays_date.year # Also makes for easier assertions!
    assert int(month_str) == todays_date.month
    assert int(day_str) == todays_date.day
    #? Not all Python types are subscriptable like list/dict or Javascript
    # date_elems = ['year', 'month', 'day']
    # for elem, prop in zip(date_str_elems, date_elems):
    #     assert elem == todays_date[prop]


def test_strToDatetime():
    #* WHEN converting a string using a known format
    date_str = "12/25/2010"
    some_datetime = strToDatetime(date_str, "%m/%d/%Y")
    #* THEN the string is converted into a datetime properly
    assert some_datetime.year == 2010
    assert some_datetime.month == 12
    assert some_datetime.day == 25

    #* WHEN converting a string using an incorrect/unknown format
    with pytest.raises(ValueError):
        strToDatetime(date_str, "%Y/%m/%d")
        #* THEN the string ISN'T converted into datetime, throwing ValueError
        #* SINCE strToDateTime is basically a `datetime.strptime` alias
