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


def dateToStr(date: date, format_str: str):
    """ Accepts a simple date obj and uses the formatter to return a string """
    return date.strftime(format_str)


def strToDatetime(date_str: str, format_str: str):
    """ Accepts a date string of the given format and converts it into a datetime obj """
    return datetime.strptime(date_str, format_str)


#! UTC String to Pacific Time converters
def utcStrToPacificTimeStr(utc_string, daylight_savings = True):
    """ Converts a UTC formatted string into a Locale Readable Pacific Time string
    Params: 
        1: date string formatted to YYYY-mm-ddTHH:MM:SSZ (e.g. 1990-02-10T04:15:35Z) 
        2. daylight_savings flag to get a datetime offset of 7 if Daylight Savings is in place vs 8 for Standard time
    Returns: A datetime string formatted for Locale, e.g. Fri February 09 1990 at 09:15 PM
    """
    pst_datetime = utcStrToPacificDatetime(utc_string, daylight_savings)
    return dateToStr(pst_datetime, READABLE_FORMAT)


def utcStrToPacificDatetime(utc_string, daylight_savings = True):
    """ Converts a UTC formatted string into a Pacific Time datetime obj. See utcStrToPacificTimeStr for param details."""
    utc_datetime = strToDatetime(utc_string, ISO_FORMAT)
    return utcDatetimeToPacificDatetime(utc_datetime, daylight_savings)


#! UTC datetime to Pacific Time converters
def utcDatetimeToPacificDatetime(utc_datetime, daylight_savings = True):
    """ Converts a UTC datetime into a Pacific Time datetime obj """
    pacific_time_offset = 7 if daylight_savings else 8 #* PST is minus8, but PDT is minus7 from March to early Nov
    return (utc_datetime - timedelta(hours=pacific_time_offset)) #? And timedelta works exactly that way via Subtraction!


def utcDatetimeToPacificTimeStr(utc_datetime, format_str, daylight_savings = True):
    """ Converts a UTC datetime into a Pacific Time string formatted to your preference """
    pst_datetime = utcDatetimeToPacificDatetime(utc_datetime, daylight_savings)
    return dateToStr(pst_datetime, format_str)


def utcDatetimeToReadablePacificTimeStr(utc_datetime, daylight_savings = True):
    """ Converts a UTC datetime into a Locale Readable Pacific Time string """
    return utcDatetimeToPacificTimeStr(utc_datetime, READABLE_FORMAT, daylight_savings)
