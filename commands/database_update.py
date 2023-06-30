import requests
from .database_seed import createEndpoint, scheduleDates, createPromotionsForGame
from ..utility.database_helpers import finalizeDbUpdate
from ..utility.datetime_helpers import strToDatetime, ISO_FORMAT
from ..utility.endpoint_helpers import LATEST_GAME_URL
from ..models import BaseballTeam

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
        if not gameDate.get('games', 0) or len(gameDate['games']) == 0: 
            continue #? In case a date without any games is returned for some reason, skip it!

        for game in gameDate['games']: #* In case of double headers
            homeTeamName = game['teams']['home']['team']['name'].split()
            #? Example of expected split: ['Texas', 'Rangers', 'vs', 'Los', 'Angeles', 'Dodgers']
            #* Add promos ONLY if it's a home game, i.e. the first two indices are 'Los' and 'Angeles'
            if (homeTeamName[0] + ' ' + homeTeamName[1] == 'Los Angeles'):
                dateForGame = strToDatetime(game['gameDate'], ISO_FORMAT) #* Convert typical UTC string to datetime obj
                createPromotionsForGame(game['promotions'] if ('promotions' in game) else [], dateForGame)


def updateAllTeamRecords():
    print("Updating each team's record in Db")
    for team in BaseballTeam.query.all():
        updateTeamRecord(team)

def updateTeamRecord(team):
    print(f"Looking for latest league record for the following team: {team.team_name}")
    request = requests.get(LATEST_GAME_URL.format(espnID=team.espnID))
    if (request.status_code != 200): 
        return #? In case of broken link

    datesWithGames = request.json().get('dates', 0) #? If key exists, get val, else set it to 0 so next line fails on issue
    if (not datesWithGames or len(datesWithGames) == 0): 
        return #? In case api ever changes

    if (datesWithGames[0] and datesWithGames[0]['games'] and len(datesWithGames[0]['games']) > 0):
        todaysGame = datesWithGames[0]['games'][0]
        thisTeam = todaysGame['teams']['home'] if (todaysGame['teams']['home']['team']['name'] == team.fullName) \
            else todaysGame['teams']['away'] #* Grab home or away team based on a matching name
        team.wins, team.losses = thisTeam['leagueRecord']['wins'], thisTeam['leagueRecord']['losses']
        #? The above '\' trick doesn't work with strings! Format issues occur
        print(f"Json says wins: {thisTeam['leagueRecord']['wins']} & losses: {thisTeam['leagueRecord']['losses']}")
        print(f"so saving team's record as {team.wins} - {team.losses}")
        finalizeDbUpdate()
