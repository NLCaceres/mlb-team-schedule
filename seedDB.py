from datetime import date, datetime, timedelta
import requests 
from app import db
from models import * #DodgerGame, BaseballTeam, Promo 

#? Changing teamId in following url can change homeTeam to desired one
upcomingSchedule = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team' #? Concatenated at compile time
                    ',game(promotions)&season={seasonYear}&startDate={startDate}&endDate={endDate}' 
                    '&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games') #* See below for formatting
baseMlbLogoUrl = 'https://www.mlbstatic.com/team-logos/{espnID}.svg'
latestGameUrl = 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&teamId={espnID}' #? Grabs latest game so best for grabbing record
#https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1 #? Grabs all games of the day
#https://statsapi.mlb.com/api/v1/teams?lang=en&sportId=1 #? Grabs all teams
#https://statsapi.mlb.com/api/v1/standings?leagueId=104 #? Grabs all national league -> 203 - 205 NL West,East,Central
#https://statsapi.mlb.com/api/v1/standings?leagueId=103 #? Grabs all american league -> 200 - 202 AL West,East,Central

def createScheduleEndpoint(startDate = None, endDate = None, seasonYear = None):
    #* StartDate & endDate Format: YYYY-MM-DD -> e.g. 2021-06-01 #* SeasonYear Format: YYYY -> e.g. 2021
    todaysDateTime = date.today()
    todaysDate = todaysDateTime.strftime("%Y-%m-%d")
    thisYear = todaysDateTime.year
    expectedSeasonEnd = f"{thisYear}-10-30" #? Should always be some variant of 2021-10-30, 2022-10-30, etc.

    finalStartDate = startDate if startDate is not None else todaysDate
    finalEndDate = endDate if endDate is not None else expectedSeasonEnd
    finalSeasonYear = seasonYear if seasonYear is not None else thisYear
    
    return upcomingSchedule.format(startDate=finalStartDate, endDate=finalEndDate, seasonYear=finalSeasonYear)

def prelimEndpointCheck(endpointStr): #* Returns false OR a tuple. 
    dodgersSchedule = requests.get(endpointStr)
    if (dodgersSchedule.status_code != 200): return False #? In case of broken link
    scheduleJson = dodgersSchedule.json()
    print("Beginning seeding process")

    totalGames = scheduleJson.get('totalGames', 0)
    print(f"Games expected: {totalGames}")
    teamGameDates = scheduleJson.get('dates', 0)
    print(f"Dates found: {len(teamGameDates)}")
    if not teamGameDates or len(teamGameDates) == 0: return False #? In case json structure changes

    return (totalGames, teamGameDates)

def seedDB(updateMode = False):
    print("Running the Database Seeder")
    gamesTuple = prelimEndpointCheck(createScheduleEndpoint()) if updateMode else prelimEndpointCheck(createScheduleEndpoint('2021-06-01'))
    if not gamesTuple: return #* Getting false means likely issue with stats endpoint
    (totalGames, teamGameDates) = gamesTuple #* Above is very repeatable, so best pythonic solution = return a tuple! Very JS unpacking too!

    futureDates = date.today() if updateMode else datetime.strptime('2021-06-01', '%Y-%m-%d')
    startingDateStr = (futureDates - timedelta(hours=7)).strftime('%Y-%m-%d')
    gamesInDb = DodgerGame.query.filter(DodgerGame.readableDateTime >= futureDates).order_by(DodgerGame.date).all()

    print("Beginning to add Dodger Games to Schedule")
    seriesTotal, currentSeriesGame, seasonGameNum = 0, 0, 0 #* SeasonGameNum tracks total num of games read so far
    for dayNum, gameDate in enumerate(teamGameDates):
        if not gameDate.get('games', 0) or len(gameDate['games']) == 0: continue #? In case of offday returned for some reason, skip date (not sure if possible)
        print(f"Day #{dayNum+1} that Dodgers have played since {startingDateStr}")

        seriesTotal, currentSeriesGame = gameDate['games'][0]['gamesInSeries'], gameDate['games'][0]['seriesGameNumber']
        #* Double headers considered below but above line doesn't entirely (currentSeriesGame may need to be set elsewhere)
        gameStr = f"Today's a double header! " if len(gameDate['games']) > 1  \
            else f"On {gameDate['date']} is game #{currentSeriesGame} in a series "

        (seasonGameNum, gameStr) = createTodaysGames(gameDate['games'], gamesInDb, seasonGameNum, gameStr)

        if currentSeriesGame == seriesTotal: #*  Logic to group games in same series together
            gameStr += ' \n\n '
            currentSeriesGame = 0
        else: gameStr += ' \n '
            
        print(gameStr)

    updateAllTeamRecords()

    print("Finishing seeding process. \n")

def createTodaysGames(todaysGames, gamesInDb, seasonGameNum, gameStr): #* Make games for particular date
    for game in todaysGames: #* In case of double headers
        currentGameInDb = gamesInDb[seasonGameNum] if seasonGameNum < len(gamesInDb) else None

        awayTeam = createOrGrabTeam(game, 'away') #* Always needed so promos can check for updates later
        gameStr += f"where the visiting: {awayTeam.city_name} {awayTeam.team_name} "
        homeTeam = createOrGrabTeam(game, 'home')
        gameStr += f"will take on the home: {homeTeam.city_name} {homeTeam.team_name}"

        if currentGameInDb is None: #* If no record found, let's make one and set it!
            print("Initial seed db so simple create")
            #* Create Game Model so promos can be associated
            currentGameInDb = DodgerGame(date=datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ'), 
                gameNumInSeries=game['seriesGameNumber'], gamesInSeries=game['gamesInSeries'],
                home_team_id=homeTeam.id, away_team_id=awayTeam.id)
            saveToDb(currentGameInDb)

        elif currentGameInDb.gameNumInSeries == game['seriesGameNumber'] and currentGameInDb.gamesInSeries == game['gamesInSeries'] \
        and currentGameInDb.readableDate == utcStrToPacificTime(game['gameDate']):
            print(f"Game #{seasonGameNum + 1} currently in db is at {currentGameInDb}")
            print(f"Game #{seasonGameNum + 1} in endpoint is at {utcStrToPacificTime(game['gameDate'])}")
            print(f"Game time matches! All fine, move on!")

        elif currentGameInDb.gameNumInSeries == game['seriesGameNumber'] and currentGameInDb.gamesInSeries == game['gamesInSeries']:
            print(f"Game #{seasonGameNum + 1} currently in db is at {currentGameInDb}")
            print(f"Game #{seasonGameNum + 1} in endpoint is at {utcStrToPacificTime(game['gameDate'])}")
            print("No match! Update the game!")
            currentGameInDb.date = game['gameDate'] #todo May need to update more than just date, but not sure yet of other common changes
            db.session.commit()

        else: #* Currently unsure if this will ever fire but above elif makes certain that gameInDb is the exact same and need to change date
            print(f"Game #{currentGameInDb.gameNumInSeries} in a series of {currentGameInDb.gamesInSeries} against ... seems to have been canceled?")
  
        #* Add promos ONLY if it's a home game
        if homeTeam.city_name == 'Los Angeles': createPromotionsForGame(game['promotions'] if ('promotions' in game) else [], currentGameInDb)
        seasonGameNum += 1 #* Keep incrementing regardless of conditional case above
    
    return (seasonGameNum, gameStr) #* May one day get rid of gameStr or find way to consolidate string

def createOrGrabTeam(game, teamKey=''): #* If able to fetch team, great! Otherwise let's add it!
    team = game['teams'][teamKey]['team']
    
    teamInDb = None 
    #? Since always returning a model, declare above, check for existing record w/ walrus in conditional or create+save, & return
    if (teamInDb := BaseballTeam.query.filter_by(team_name=team['clubName']).first()) is not None:
        print(f"Found a matching team! {teamInDb}. No need to double save") #* Finalize team record later        
    else:
        teamRecord = game['teams'][teamKey]['leagueRecord']
    
        #* Easiest to directly save teamLogo URL below rather than save svg+xml & use html.escape() for safety
        teamInDb = BaseballTeam(team_name=team['clubName'], city_name=team['franchiseName'], 
            team_logo=baseMlbLogoUrl.format(espnID=team['id']), abbreviation=team['abbreviation'], 
            wins=teamRecord['wins'], losses=teamRecord['losses'])
        saveToDb(teamInDb)

    return teamInDb

def createPromotionsForGame(promotions, thisGame):
    thisDaysGame = thisGame if type(thisGame) is not datetime else DodgerGame.query.filter_by(date=thisGame).first()
    print(f"Today's Game = {thisDaysGame}")
    if thisDaysGame is None: return #? In case game doesn't exist (which would cause linking below to fail)
    for promo in promotions:
        print(f"Latest Promo in endpoint for {thisDaysGame.readableDate}: {promo['name']}")
        thumbnailUrl = promo['imageUrl'] if ('imageUrl' in promo) else 'undefined'

        if thisDaysGame is not None and len(thisDaysGame.promos) > 0:
            matchFound = any(promo['name'] == gamePromo.name for gamePromo in thisDaysGame.promos)
            if matchFound: 
                print("Match found. Skip promo!")
                continue
        
        promoModel = Promo(name=promo['name'], thumbnail_url=thumbnailUrl, dodger_game_id=thisDaysGame.id)
        saveToDb(promoModel)

def updateAllPromotions():
    print("Going to update all promotions")
    dodgersSchedule = requests.get(createScheduleEndpoint())
    if (dodgersSchedule.status_code != 200): return #? In case of broken link
    scheduleJson = dodgersSchedule.json()

    teamGameDates = scheduleJson.get('dates', 0) 
    if not teamGameDates or len(teamGameDates) == 0: return #? In case json structure changes

    for gameDate in teamGameDates:
        if not gameDate.get('games', 0) or len(gameDate['games']) == 0: continue #? In case of offday returned for some reason, skip date (not sure if possible)

        for game in gameDate['games']: #* In case of double headers
            homeTeamName = game['teams']['home']['team']['name'].split()
            #* Add promos ONLY if it's a home game
            if (homeTeamName[0] + ' ' + homeTeamName[1] == 'Los Angeles'): #? All teams have at least 2 indexes (e.g. Arizona Diamondbacks vs Los Angeles Dodgers)
                dateForGame = datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ') #* Convert typical UTC string to datetime obj
                createPromotionsForGame(game['promotions'] if ('promotions' in game) else [], dateForGame)


def updateTeamRecord(team):
    print(f"Looking for latest league record for the following team: {team.team_name}")
    request = requests.get(latestGameUrl.format(espnID=team.espnID))
    if (request.status_code != 200): return #? In case of broken link

    datesWithGames = request.json().get('dates', 0) #? If key exists, get val, else set it to 0 so next line fails on issue
    if (not datesWithGames or len(datesWithGames) == 0): return #? In case api ever changes

    if (datesWithGames[0] and datesWithGames[0]['games'] and len(datesWithGames[0]['games']) > 0):
        todaysGame = datesWithGames[0]['games'][0]
        thisTeam = todaysGame['teams']['home'] if (todaysGame['teams']['home']['team']['name'] == team.fullName) \
            else todaysGame['teams']['away'] #* Grab home or away team based on a matching name
        team.wins, team.losses = thisTeam['leagueRecord']['wins'], thisTeam['leagueRecord']['losses']
        print(f"Json says wins: {thisTeam['leagueRecord']['wins']} & losses: {thisTeam['leagueRecord']['losses']}")
        print(f"so saving team's record to {team.wins} - {team.losses}") #? The above '\' trick doesn't work with strings! (will get formatting issues)
        db.session.commit()

def updateAllTeamRecords():
    print("Updating the standings for teams in Db")
    for team in BaseballTeam.query.all():
        updateTeamRecord(team)


#* Utility Functions

#? Just a slightly simpler db save method (delete could and does look similar)
def saveToDb(newModel):
    print(f"Saving {newModel} to the database")
    db.session.add(newModel) #? This saves a new model
    db.session.commit() 
    #? To update, query using a column like 'name', using returned model row.name = 'newName' (or row.wins = row.wins + 1), and still commit commit!
    #? Could also just use Model.query.filter_by(name='oldName').update({name='newName'}) which helps for mass updates
    print(f"Successfully saved {newModel}!")

def utcStrToPacificTime(utcString, daylightSavings = True):
    utcDateTime = datetime.strptime(utcString, '%Y-%m-%dT%H:%M:%SZ')
    pacificTimeOffset = 7 if daylightSavings else 8 #* PST is minus8 but PDT is minus7 (daylight savings versus none)
    #* PDT usually starts early March and ends early November
    return (utcDateTime - timedelta(hours=pacificTimeOffset)).strftime("%a %B %d %Y at %I:%M %p")