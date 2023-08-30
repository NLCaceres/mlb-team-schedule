import requests
from .database_seed import createEndpoint, scheduleDates, initPromotionsForGame
from .. import db
from ..utility.database_helpers import finalizeDbUpdate
from ..utility.datetime_helpers import strToDatetime, ISO_FORMAT
from ..utility.endpoint_helpers import LEAGUE_STANDINGS_URL
from ..models import BaseballTeam, DodgerGame

def updateAllPromotions():
    print("Going to update all promotions")
    dodgersSchedule = requests.get(createEndpoint(*scheduleDates(True)))
    if (dodgersSchedule.status_code != 200):
        return #? In case of broken link
    scheduleJson = dodgersSchedule.json()

    teamGameDates = scheduleJson.get('dates', 0)
    if not teamGameDates or len(teamGameDates) == 0:
        return #? In case json structure changes

    for gameDate in teamGameDates:
        gameList = gameDate.get('games', 0)
        if not gameList or len(gameList) == 0:
            continue #? In case a date without any games is returned for some reason, skip it!

        for game in gameList: #* In case of double headers
            homeTeamName = game['teams']['home']['team']['name'].split()
            #? Example of expected split: ['Texas', 'Rangers', 'vs', 'Los', 'Angeles', 'Dodgers']
            #* Add promos ONLY if it's a home game, i.e. the first two indices are 'Los' and 'Angeles'
            if (homeTeamName[0] + ' ' + homeTeamName[1] == 'Los Angeles'):
                dateForGame = strToDatetime(game['gameDate'], ISO_FORMAT) #* Convert typical UTC string to datetime obj
                gameInDb = DodgerGame.query.filter_by(date=dateForGame).first()
                initPromotionsForGame(game['promotions'] if ('promotions' in game) else [], gameInDb)


def updateAllTeamRecords():
    print("Updating all team records in Db")
    request = requests.get(LEAGUE_STANDINGS_URL)
    if (request.status_code != 200):
        print(f"Error Code: {request.status_code}")
        return #? In case of broken link

    #* Request should only receive single most recent game (or two in case of double header days)
    divisions = request.json().get('records', []) #? If key exists, get val, else provide an empty [] for early return
    if len(divisions) == 0:
        print("No team records found")
        return #? In case api ever changes

    [updateByDivision(division) for division in divisions]

MLB_DIVISIONS = {
    200: 'American League West', 201: 'American League East', 202: 'American League Central',
    203: 'National League West', 204: 'National League East', 205: 'National League Central',
}
def updateByDivision(division):
    divisionInfo = division.get('division', None)
    if divisionInfo is None:
        print("No matching division found")
        return

    divisionID = divisionInfo.get('id', None)
    if divisionID is None:
        print("No division ID found. Not possible to update standings")
        return

    print(f"Updating the {MLB_DIVISIONS[divisionID]} division")
    teamRecords = division.get('teamRecords', [])
    [updateTeamRecord(team) for team in teamRecords]
    print('DIVISION DONE\n\n')

def updateTeamRecord(team):
    teamInfo = team.get('team', None)
    if teamInfo is None:
        print('No team found. Unable to update standings')
        return

    teamName, teamID = teamInfo.get('name', ''), teamInfo.get('id', 0)
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
