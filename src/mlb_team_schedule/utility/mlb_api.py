from .api_helpers import fetch
from .datetime_helpers import YMD_FORMAT, dateToday, dateToStr
from .endpoint_constants import LEAGUE_STANDINGS_URL, SCHEDULE_ENDPOINT
from .team_map import getTeamID


def fetchTeamRecords():
    standingsJSON = fetch(LEAGUE_STANDINGS_URL)
    return standingsJSON.get("records", [])


def fetchThisYearsSchedule():
    (seasonStart, seasonEnd, thisYear) = scheduleDates()
    scheduleJSON = fetch(createEndpoint(seasonStart, seasonEnd, thisYear))

    # Since start date varies, include it w/ the schedule JSON tuple in a new tuple!
    return (*getScheduleTotals(scheduleJSON), seasonStart)


def fetchRemainingSchedule():
    (today, seasonEnd, thisYear) = scheduleDates(startingToday=True)
    scheduleJSON = fetch(createEndpoint(
        startDate=today, endDate=seasonEnd, seasonYear=thisYear
    ))

    return (*getScheduleTotals(scheduleJSON), today)


def getScheduleTotals(scheduleJSON):
    """Gets value data from endpoint's JSON response + Logs the values"""
    totalGames = scheduleJSON.get("totalGames", None)
    teamGameDates = scheduleJSON.get("dates", None)
    if totalGames is None or teamGameDates is None:
        return (None, None) # Unsuccessful response if totalGames or teamGameDates == NONE
    print(f"Total Games = {totalGames}", f"Number of Dates = {len(teamGameDates)}")

    return (totalGames, teamGameDates)


#! Schedule Endpoint Creation Methods
#? Return an unpackable tuple useful to create the schedule endpoint
def scheduleDates(startingToday = False):
    todaysDate = dateToday()
    thisYear = todaysDate.year # SeasonYear Format: YYYY -> e.g. 2021
    # StartDate & endDate Format: YYYY-MM-DD -> e.g. 2021-06-01
    startDate = dateToStr(todaysDate, YMD_FORMAT) if startingToday \
        else f"{thisYear}-03-01"
    endDate = f"{thisYear}-11-30"

    return (startDate, endDate, thisYear) # Most Pythonic way to pack data is a tuple!


def createEndpoint(startDate = None, endDate = None, seasonYear = None, teamId = None):
    if startDate is None or endDate is None or seasonYear is None:
        return None

    #? If teamId is falsy, THEN getTeamID() from Config. IF that's falsy, default to 119
    selectedTeamId = teamId or getTeamID() or 119
    return SCHEDULE_ENDPOINT.format(
        startDate=startDate, endDate=endDate, seasonYear=seasonYear, teamId=selectedTeamId
    )

