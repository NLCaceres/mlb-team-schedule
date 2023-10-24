import requests
from flask import current_app as app #? Main method of accessing App's Config.py env vars
from .database_seed import createEndpoint, scheduleDates, initPromotionsForGame, comparePromoLists, replaceOldPromos
from .. import db
from ..utility.database_helpers import finalizeDbUpdate
from ..utility.datetime_helpers import strToDatetime, ISO_FORMAT
from ..utility.endpoint_helpers import LEAGUE_STANDINGS_URL
from ..models import BaseballTeam, DodgerGame

def updateAllPromotions():
    print("Going to update all promotions")
    #? '*' unpacks the tuple returned by scheduleDates() into the args of createEndpoint()
    response = requests.get(createEndpoint(*scheduleDates(True)))
    if (response.status_code != 200):
        return #? In case of broken link
    dodgersSchedule = response.json()

    gameDateList = dodgersSchedule.get('dates', [])
    for gameDate in gameDateList:
        gameList = gameDate.get('games', [])
        #? If a date is found w/out any games, then this list comprehension ends immediately, moving on to next date
        [updateEachGamesPromotions(game) for game in gameList]

def updateEachGamesPromotions(game):
    #? Since the homeTeamName is deeply nested, it's easiest in Python to catch the KeyError if the name is missing, so the
    #? comprehension keeps processing remaining games AND all remaining game dates by halting error propagation
    try:
        homeTeamName = game['teams']['home']['team'].get('name', '').lower() #* Ensure using lower() on a string via default
        expectedTeamName = app.config.get('TEAM_FULL_NAME').lower()
        if (homeTeamName == expectedTeamName): #* ONLY add promos if it's a home game
            dateForGame = strToDatetime(game['gameDate'], ISO_FORMAT) #* Convert typical UTC string to datetime obj
            #? first() returns None if no Game is found whereas one() raises an exception
            gameInDb = db.session.scalars(db.select(DodgerGame).filter_by(date=dateForGame)).first()
            if gameInDb is None:
                return
            newPromos = initPromotionsForGame(game.get('promotions', []))
            if not comparePromoLists(gameInDb.promos, newPromos):
                replaceOldPromos(gameInDb, newPromos)
    except Exception:
        print("Exception raised while trying to find home team or game's date in JSON")


def updateAllTeamRecords():
    print("Updating all team records in Db")
    response = requests.get(LEAGUE_STANDINGS_URL)
    if (response.status_code != 200):
        print(f"Error Code: {response.status_code}")
        return #? In case of broken link

    divisions = response.json().get('records', []) #? If key exists, get val, else provide an empty [] for early return
    if len(divisions) == 0:
        print("No team records found")
        return #? In case api ever changes

    [updateEachDivision(division) for division in divisions]

MLB_DIVISIONS = {
    200: 'American League West', 201: 'American League East', 202: 'American League Central',
    203: 'National League West', 204: 'National League East', 205: 'National League Central',
}
def updateEachDivision(division):
    divisionInfo = division.get('division', None)
    if divisionInfo is None:
        print("No division info found")
        return

    divisionID = divisionInfo.get('id', None)
    if divisionID is None:
        print("No division ID found. Not possible to update standings")
        return

    divisionName = MLB_DIVISIONS.get(divisionID, '')
    print(f"Updating the {divisionName} division" if bool(divisionName) else "Unknown division being updated")

    teamRecords = division.get('teamRecords', [])
    [updateTeamRecord(team) for team in teamRecords] #? If comprehension finds empty [], then nothing happens
    print('DIVISION DONE\n\n')

def updateTeamRecord(team):
    teamInfo = team.get('team', None)
    if teamInfo is None:
        print('No team found. Unable to update standings')
        return

    teamID, teamName = teamInfo.get('id', 0), teamInfo.get('name', '')
    if not teamID:
        print('No team ID found. Unable to update record in database')
        return

    print(f"Looking for latest league record for the following team: {teamName}")

    teamWins, teamLosses = team.get('wins', 0), team.get('losses', 0)
    if not teamWins or not teamLosses:
        print('The API returned JSON missing the wins or losses. Will have to update later')
        return

    thisTeam = db.session.scalars(db.select(BaseballTeam).filter_by(fullName=teamName)).one()
    print(f"Found the following team = {thisTeam} with a win-loss record of {thisTeam.wins}-{thisTeam.losses}")
    print(f"Updating to a win-loss of {teamWins}-{teamLosses}\n")

    thisTeam.wins, thisTeam.losses = teamWins, teamLosses
    finalizeDbUpdate()
