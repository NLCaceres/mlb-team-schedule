from datetime import date, datetime, timedelta

#! Common Format constants
YMD_FORMAT = '%Y-%m-%d' #? YYYY-MM-DD
ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ' #? YYYY-mm-ddTHH:MM:SSZ (T starts the time in ISO, Z indicates UTC time zone)

#! Quick convenience methods
def dateToday():
    return date.today()

#* Not sure if the 'is' prefix is common in Python
def isDatetime(obj):
    return type(obj) is datetime

#* Takes a simple date object and uses the formatter to return a string
def dateToStr(date: date, formatStr: str):
    return date.strftime(formatStr)

#* Takes a date string of this particular format and converts it into a 'datetime' obj
def strToDatetime(dateStr: str, formatStr: str):
    return datetime.strptime(dateStr, formatStr)

#! More specific use helper methods
#* Takes a datetime string formatted to YYYY-mm-ddTHH:MM:SSZ (e.g. 1990-02-10T04:15:35Z)
#* Returns a datetime string formatted for Locale (e.g. Sun February 10 1990 at 04:15 AM) 
def utcStrToPacificTime(utcString, daylightSavings = True):
    utcDateTime = datetime.strptime(utcString, '%Y-%m-%dT%H:%M:%SZ')
    return utcDateTimeToPacificTimeStr(utcDateTime, '%a %B %d %Y at %I:%M %p', daylightSavings)

#? Provide a readable datetime string converted from UTC to PST/PDT through subtraction
def utcDateTimeToPacificTimeStr(utcDateTime, formatStr, daylightSavings = True):
    pacificTimeOffset = 7 if daylightSavings else 8 #* PST is minus8, but PDT is minus7 in March to early Nov
    return (utcDateTime - timedelta(hours=pacificTimeOffset)).strftime(formatStr)
