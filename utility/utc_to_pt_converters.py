from datetime import timedelta
from .datetime_helpers import dateToStr, strToDatetime, ISO_FORMAT, READABLE_FORMAT


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


#! UTC Datetime to Pacific Time converters
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
