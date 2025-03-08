from mlb_team_schedule.utility.datetime_helpers import ISO_FORMAT, strToDatetime
from mlb_team_schedule.utility.utc_to_pt_converters import (
    utcDatetimeToPacificDatetime, utcDatetimeToPacificTimeStr,
    utcDatetimeToReadablePacificTimeStr, utcStrToPacificDatetime, utcStrToPacificTimeStr,
)

import pytest
from datetime import UTC, datetime, timedelta


#! UTC String to PT Converters
def test_utcStrToPacificTimeStr():
    #* WHEN the UTC string is converted into a PDT Daylight Savings time string
    utc_str = "1990-02-10T04:15:35Z"
    pdt_str = utcStrToPacificTimeStr(utc_str)
    #* THEN it shifts back 7 hours from Feb 10 to Feb 9 9:15 PM, 7 hours earlier
    assert pdt_str == "Fri February 09 1990 at 09:15 PM" #? PDT is -7 hours from UTC

    #* WHEN the UTC string is converted into a PST string (-8 hours from UTC)
    pst_str = utcStrToPacificTimeStr(utc_str, daylight_savings = False)
    #* THEN it shifts back 8 hours from Feb 10 to Feb 9 8:15 PM, 8 hours earlier
    assert pst_str == "Fri February 09 1990 at 08:15 PM"

    #* WHEN an improperly formatted UTC string is used
    with pytest.raises(ValueError):
        #* THEN a ValueError is raised
        utcStrToPacificTimeStr("1990-02-10T04:15Z")


def test_utcStrToPacificDatetime():
    #* WHEN a properly formatted UTC string is used
    utc_str = "2011-05-22T06:32:35Z" #* May 22nd 2011 at 6:32 AM
    pdt_datetime = utcStrToPacificDatetime(utc_str)
    #* THEN its converted to a datetime, and shifted back 7 hours
    assert pdt_datetime.year == 2011
    assert pdt_datetime.month == 5
    #? UTC date is 6am 22nd, PDT is -7utc, THEN time == 11:32pm (21:32) 21st!
    assert pdt_datetime.day == 21
    assert pdt_datetime.hour == 23
    assert pdt_datetime.minute == 32

    #* WHEN a properly formatted UTC string used w/out daylight_savings
    pst_datetime = utcStrToPacificDatetime(utc_str, daylight_savings = False)
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
        utcStrToPacificDatetime("2011-05-22")


#! UTC Datetime to PT Converters
def test_utcDatetimeToPacificDatetime():
    utc_str = "2005-06-02T01:15:35Z"
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
    utc_datetime = datetime.now(UTC)
    pdt_str = utcDatetimeToPacificTimeStr(utc_datetime, "%a %B %d %Y at %I:%M %p")
    pdt_datetime = utc_datetime - timedelta(hours=7)
    pdt_datetime_hour = pdt_datetime.hour #* MUST change the hours into military 0-23 time
    expected_pdt_datetime_hour = pdt_datetime_hour + 12 if pdt_datetime_hour == 0 else (
        (pdt_datetime_hour - 12) if pdt_datetime_hour > 12 else pdt_datetime_hour
    )
    pdt_date_vals = pdt_str.split()
    time_index = 5 #* Time is %I:%M in the format string
    pdt_time_vals = pdt_date_vals[time_index].split(":")
    day_index = 2 #* Day is %d in the format string
    year_index = 3 #* Year is %Y in the format string
    #* THEN can be split into its date values, 7 hours earlier than UTC time
    assert pdt_datetime.day == int(pdt_date_vals[day_index])
    assert pdt_datetime.year == int(pdt_date_vals[year_index])
    assert expected_pdt_datetime_hour == int(pdt_time_vals[0])
    assert pdt_datetime.minute == int(pdt_time_vals[1])

    #* WHEN a UTC datetime is converted into a PST string of a specific format
    pst_str = utcDatetimeToPacificTimeStr(utc_datetime, "%a %B %d %Y at %I:%M %p", False)
    pst_datetime = utc_datetime - timedelta(hours=8)
    pst_datetime_hour = pst_datetime.hour #* MUST change the hours into military 0-23 time
    expected_pst_datetime_hour = pst_datetime_hour + 12 if pst_datetime_hour == 0 else (
        (pst_datetime_hour - 12) if pst_datetime_hour > 12 else pst_datetime_hour
    ) #? Since PST == -8 BUT PDT == -7, so it must subtract 1 extra hour
    adjusted_pdt_time = 12 if expected_pdt_datetime_hour == 1 \
        else expected_pdt_datetime_hour - 1
    pst_date_vals = pst_str.split()
    pst_time = pst_date_vals[time_index].split(":")
    #* THEN date values stay the same as PDT version, even minutes
    assert pst_datetime.day == int(pst_date_vals[day_index])
    assert pst_datetime.year == int(pst_date_vals[year_index])
    assert int(pst_time[1]) == int(pdt_time_vals[1])
    #* EXCEPT now 1 hour earlier from -8utc offset vs -7utc PDT offset
    assert expected_pst_datetime_hour == int(pst_time[0])
    assert int(pst_time[0]) ==  adjusted_pdt_time
    assert pst_datetime.minute == int(pst_time[1])

    #* WHEN the format changes
    pdt_str = utcDatetimeToPacificTimeStr(utc_datetime, "%d %Y")
    [day, year] = pdt_str.split()
    #* THEN the returned string still has matching day/year values
    pdt_datetime = utc_datetime - timedelta(hours=7)
    assert pdt_datetime.day == int(day)
    assert pdt_datetime.year == int(year)


def test_utcDatetimeToReadablePacificTimeStr():
    utc_str = "2013-11-27T07:12:25Z"
    utc_datetime = strToDatetime(utc_str, ISO_FORMAT)
    #* WHEN a UTC datetime is converted into a Locale readable PDT date string
    pdt_date_str = utcDatetimeToReadablePacificTimeStr(utc_datetime)
    #* THEN the time is -7utc, i.e. 7:12AM to 12:12AM same day
    assert pdt_date_str == "Wed November 27 2013 at 12:12 AM"

    #* WHEN a UTC datetime is converted into a Locale readable PST date string
    pst_date_str = utcDatetimeToReadablePacificTimeStr(utc_datetime, False)
    #* THEN the time is -7utc, i.e. 7:12AM to 11:12AM the night before
    assert pst_date_str == "Tue November 26 2013 at 11:12 PM"
