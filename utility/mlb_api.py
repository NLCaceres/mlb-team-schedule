from .api_helpers import fetch
from .datetime_helpers import dateToday, dateToStr, YMD_FORMAT
from .endpoint_constants import SCHEDULE_ENDPOINT


def fetchThisYearsSchedule():
    (seasonStart, seasonEnd, thisYear) = scheduleDates()
    scheduleJSON = fetch(createEndpoint(seasonStart, seasonEnd, thisYear))

    #* Since the start date can vary, include it w/ the schedule JSON data tuple in a whole new tuple!
    return (*getScheduleTotals(scheduleJSON), seasonStart)


def fetchRemainingSchedule():
    (today, seasonEnd, thisYear) = scheduleDates(startingToday=True)
    scheduleJSON = fetch(createEndpoint(startDate=today, endDate=seasonEnd, seasonYear=thisYear))

    return (*getScheduleTotals(scheduleJSON), today)


def getScheduleTotals(scheduleJSON):
    """Grabs the most important data from the endpoint's JSON response AND ALSO logs those values"""
    totalGames = scheduleJSON.get('totalGames', None)
    teamGameDates = scheduleJSON.get('dates', None)
    if totalGames is None or teamGameDates is None: #* BOTH values must be found for the response to be considered a success
        return (None, None)
    print(f"Total Games = {totalGames}", f"Number of Dates = {len(teamGameDates)}")

    return (totalGames, teamGameDates)


#! Schedule Endpoint Creation Methods
#? Return an unpackable tuple useful to create the schedule endpoint
def scheduleDates(startingToday = False):
    todaysDate = dateToday()
    thisYear = todaysDate.year #* SeasonYear Format: YYYY -> e.g. 2021
    #* StartDate & endDate Format: YYYY-MM-DD -> e.g. 2021-06-01
    startDate = dateToStr(todaysDate, YMD_FORMAT) if startingToday else f"{thisYear}-03-01"
    endDate = f"{thisYear}-11-30"

    return (startDate, endDate, thisYear) #* Most Pythonic solution to quickly pack related data: Return a tuple!


def createEndpoint(startDate = None, endDate = None, seasonYear = None, teamId = None):
    if startDate is None or endDate is None or seasonYear is None:
        return None

    selectedTeamId = teamId or 119 #* The Dodgers ID acts as the default if None is found
    return SCHEDULE_ENDPOINT.format(startDate=startDate, endDate=endDate, seasonYear=seasonYear, teamId=selectedTeamId)
