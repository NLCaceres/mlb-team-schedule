from datetime import date, datetime, timedelta

#! Common Format constants
YMD_FORMAT = '%Y-%m-%d' #? YYYY-MM-DD
ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ' #? YYYY-mm-ddTHH:MM:SSZ (T starts the time in ISO, Z indicates UTC time zone)
READABLE_FORMAT = '%a %B %d %Y at %I:%M %p' #? i.e. Fri February 09 1990 at 09:15 PM

#! Quick convenience methods
def dateToday():
    return date.today()

#* Not sure if the 'is' prefix is common in Python
def isDatetime(obj):
    return type(obj) is datetime

#* Accepts a simple date object and uses the formatter to return a string
def dateToStr(date: date, format_str: str):
    return date.strftime(format_str)

#* Accepts a date string of this particular format and converts it into a 'datetime' obj
def strToDatetime(date_str: str, format_str: str):
    return datetime.strptime(date_str, format_str)

#! More specific use helper methods
#* Accepts a datetime string formatted to YYYY-mm-ddTHH:MM:SSZ (e.g. 1990-02-10T04:15:35Z)
#* Returns a datetime string formatted for Locale (e.g. Fri February 09 1990 at 09:15 PM) 
def utcStrToPacificTime(utc_string, daylight_savings = True):
    utc_datetime = datetime.strptime(utc_string, ISO_FORMAT)
    return utcDateTimeToPacificTimeStr(utc_datetime, READABLE_FORMAT, daylight_savings)

#? Returns a readable datetime string converted from UTC to PST/PDT through subtraction
def utcDateTimeToPacificTimeStr(utc_datetime, format_str, daylight_savings = True):
    pacific_time_offset = 7 if daylight_savings else 8 #* PST is minus8, but PDT is minus7 in March to early Nov
    return (utc_datetime - timedelta(hours=pacific_time_offset)).strftime(format_str)
