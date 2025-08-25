from datetime import date, datetime

#! Common Format constants
YMD_FORMAT = "%Y-%m-%d" #? YYYY-MM-DD
ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ" #? YYYY-mm-ddTHH:MM:SSZ - T marks time, Z = UTC timezone
READABLE_FORMAT = "%a %B %d %Y at %I:%M %p" #? i.e. Fri February 09 1990 at 09:15 PM


#! Quick convenience methods
def dateToday():
    return date.today()


# Not sure if the 'is' prefix is common in Python
def isDatetime(obj):
    return type(obj) is datetime


def dateToStr(date: date, format_str: str):
    """Accepts a simple date obj and uses the formatter to return a string"""
    return date.strftime(format_str)


def strToDatetime(date_str: str, format_str: str):
    """Accepts a date string of the given format and converts it into a datetime obj"""
    return datetime.strptime(date_str, format_str)

