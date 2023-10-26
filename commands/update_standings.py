import requests
from .. import db
from ..models import BaseballTeam
from ..utility.database_helpers import finalizeDbUpdate
from ..utility.endpoint_helpers import LEAGUE_STANDINGS_URL


#! DIVISION NAME CONSTANT
MLB_DIVISIONS = {
    200: 'American League West', 201: 'American League East', 202: 'American League Central',
    203: 'National League West', 204: 'National League East', 205: 'National League Central'
}


#! Main Standings Update Function
def updateAllTeamRecords():
    print("Updating all team records in Db")
    response = requests.get(LEAGUE_STANDINGS_URL)
    if (response.status_code != 200):
        print(f"Error Code: {response.status_code}")
        return #? In case of broken link

    standings = response.json().get('records', [])
    if len(standings) == 0:
        print("No team records found")

    [updateEachDivision(division) for division in standings]


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

    teamName = teamInfo.get('name', '')
    if not teamName: #? Perfectly cool w/ Pep 8 to treat empty strings, lists or tuples as falsy using `not someVar`
        print('No team name found. Unable to update record in database')
        return

    print(f"Looking for latest league record for the following team: {teamName}")

    teamWins, teamLosses = team.get('wins', None), team.get('losses', None)
    if teamWins is None or teamLosses is None:
        print('The API returned JSON missing the wins or losses. Will have to update later')
        return

    #? first() returns None if no Game is found whereas one() raises an exception
    thisTeam = db.session.scalars(db.select(BaseballTeam).filter_by(fullName=teamName)).first()
    if thisTeam is None:
        print(f'No team found in the DB with the name: {teamName}')
        return
    print(f"Found the following team = {thisTeam} with a win-loss record of {thisTeam.wins}-{thisTeam.losses}")
    print(f"Updating to a win-loss of {teamWins}-{teamLosses}\n")

    thisTeam.wins, thisTeam.losses = teamWins, teamLosses
    finalizeDbUpdate()
