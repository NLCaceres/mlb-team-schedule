from .. import db
from ..models import BaseballTeam
from ..utility.database_helpers import finalizeDbUpdate
from ..utility.mlb_api import fetchTeamRecords

#! DIVISION NAME CONSTANT
MLB_DIVISIONS = {
    200: "American League West",
    201: "American League East",
    202: "American League Central",
    203: "National League West",
    204: "National League East",
    205: "National League Central"
}


#! Main Standings Update Function
def updateAllTeamRecords():
    print("Updating all team records in Db")

    standings = fetchTeamRecords()
    if len(standings) == 0:
        print("No team records found")

    [updateEachDivision(division) for division in standings]


def updateEachDivision(division):
    divisionInfo = division.get("division", None)
    if divisionInfo is None:
        print("No division info found")
        return

    divisionID = divisionInfo.get("id", None)
    if divisionID is None:
        print("No division ID found. Not possible to update standings")
        return

    divisionName = MLB_DIVISIONS.get(divisionID, "")
    print(f"Updating the {divisionName} division" if bool(divisionName) \
          else "Unknown division being updated")

    teamRecords = division.get("teamRecords", [])
    [updateTeamRecord(team) for team in teamRecords] #? Comprehension won't run if empty
    print("DIVISION DONE\n\n")


def updateTeamRecord(team):
    teamInfo = team.get("team", None)
    if teamInfo is None:
        print("No team found. Unable to update standings")
        return

    teamName = teamInfo.get("name", "")
    if not teamName: #? Pep8 treats empty strings, lists + tuples as falsy via `not`
        print("No team name found. Unable to update record in database")
        return

    print(f"Looking for latest league record for the following team: {teamName}")

    teamWins, teamLosses = team.get("wins", None), team.get("losses", None)
    if teamWins is None or teamLosses is None:
        print("API returned JSON missing wins or losses. Must update later")
        return

    #? first() returns None if no Game is found whereas one() raises an exception
    thisTeam = db.session.scalars(
        db.select(BaseballTeam).filter_by(fullName=teamName)
    ).first()
    if thisTeam is None:
        print(f"No team found in the DB with the name: {teamName}")
        return
    print(f"Found team = {thisTeam} with record = {thisTeam.wins}-{thisTeam.losses}")
    print(f"Updating to a win-loss of {teamWins}-{teamLosses}\n")

    thisTeam.wins, thisTeam.losses = teamWins, teamLosses
    finalizeDbUpdate()

