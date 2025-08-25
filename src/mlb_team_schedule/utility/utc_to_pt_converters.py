from .datetime_helpers import ISO_FORMAT, READABLE_FORMAT, dateToStr, strToDatetime

from datetime import timedelta


#! UTC String to Pacific Time converters
def utcStrToPacificTimeStr(utc_string, daylight_savings = True):
    """Converts a UTC formatted string into a Locale Readable Pacific Time string
    Params:
        date : string - Formatted to YYYY-mm-ddTHH:MM:SSZ (e.g. 1990-02-10T04:15:35Z)
        daylight_savings : bool - Flag to use a -7 Daylight Savings offset vs -8 for PST
    Returns: A datetime string formatted for Locale, e.g. Fri February 09 1990 at 09:15 PM
    """
    pst_datetime = utcStrToPacificDatetime(utc_string, daylight_savings)
    return dateToStr(pst_datetime, READABLE_FORMAT)


def utcStrToPacificDatetime(utc_string, daylight_savings = True):
    """Converts a UTC formatted string into a Pacific Time datetime obj.
    Params:
        date : string - Formatted to YYYY-mm-ddTHH:MM:SSZ (e.g. 1990-02-10T04:15:35Z)
        daylight_savings : bool - Flag to use a -7 Daylight Savings offset vs -8 for PST
    Returns: A datetime offset by either -7 or -8 depending on the daylight_savings flag
    """
    utc_datetime = strToDatetime(utc_string, ISO_FORMAT)
    return utcDatetimeToPacificDatetime(utc_datetime, daylight_savings)


#! UTC Datetime to Pacific Time converters
def utcDatetimeToPacificDatetime(utc_datetime, daylight_savings = True):
    """Converts a UTC datetime into a Pacific Time datetime obj"""
    pacific_time_offset = 7 if daylight_savings else 8 # PST is -8. PDT is -7 Mar to Nov
    #? AND `timedelta` works exactly like a -7 or -8 via subtraction as shown below
    return (utc_datetime - timedelta(hours=pacific_time_offset))


def utcDatetimeToPacificTimeStr(utc_datetime, format_str, daylight_savings = True):
    """Converts a UTC datetime into a Pacific Time string formatted to your preference"""
    pst_datetime = utcDatetimeToPacificDatetime(utc_datetime, daylight_savings)
    return dateToStr(pst_datetime, format_str)


def utcDatetimeToReadablePacificTimeStr(utc_datetime, daylight_savings = True):
    """Converts a UTC datetime into a Locale Readable Pacific Time string"""
    return utcDatetimeToPacificTimeStr(utc_datetime, READABLE_FORMAT, daylight_savings)

