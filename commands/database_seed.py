import requests
from ..utility.database_helpers import saveToDb, finalizeDbUpdate
from ..utility.datetime_helpers import (dateToday, dateToStr, strToDatetime, utcStrToPacificTime, 
                             utcDateTimeToPacificTimeStr, YMD_FORMAT, ISO_FORMAT)
from ..utility.endpoint_helpers import BASE_MLB_LOGO_URL, SCHEDULE_ENDPOINT
from ..models import DodgerGame, BaseballTeam, Promo

#! Endpoint generation methods
#? Return an unpackable tuple useful to create the schedule endpoint
def scheduleDates(updateMode = False):
    todaysDate = dateToday()
    thisYear = todaysDate.year #* SeasonYear Format: YYYY -> e.g. 2021
    #* StartDate & endDate Format: YYYY-MM-DD -> e.g. 2021-06-01
    startDate = dateToStr(todaysDate, YMD_FORMAT) if updateMode else f"{thisYear}-03-01"
    endDate = f"{thisYear}-11-30"

    return (startDate, endDate, thisYear) #* Most Python solution to quickly pack related data! Return a tuple!

def createEndpoint(startDate = None, endDate = None, seasonYear = None):
    if startDate is None or endDate is None or seasonYear is None:
        return None

    return SCHEDULE_ENDPOINT.format(startDate=startDate, endDate=endDate, seasonYear=seasonYear)

def fetchGames(endpointStr): #* Returns false OR a tuple.
    if endpointStr is None:
        return None #* Ensure the endpoint string isn't None due to bad formatting
    dodgersSchedule = requests.get(endpointStr)

    if (dodgersSchedule.status_code != 200):
        return None #? In case of broken link
    scheduleJson = dodgersSchedule.json()
    print('Beginning seeding process')

    totalGames = scheduleJson.get('totalGames', 0)
    print(f"Games expected: {totalGames}")
    teamGameDates = scheduleJson.get('dates', 0)
    print(f"Dates found: {len(teamGameDates)}\n")
    if not teamGameDates or len(teamGameDates) == 0:
        return False #? In case json structure changes

    return (totalGames, teamGameDates)

#! Main CLI Command
def seedDB(updateMode = False):
    print('Running the Database Seeder')
    (startDate, endDate, seasonYear) = scheduleDates(updateMode)
    gamesTuple = fetchGames(createEndpoint(startDate, endDate, seasonYear))
    if gamesTuple is None:
        return #* Getting None means likely issue with stats endpoint
    (totalGames, teamGameDates) = gamesTuple #* Tuples can unpack just like Javascript destructures!

    #? Query for all games in DB after the startDate (which if in updateMode is today's date)
    startDateTime = strToDatetime(startDate, YMD_FORMAT)
    gamesInDb = DodgerGame.query.filter(DodgerGame.readableDateTime >= startDateTime).order_by(DodgerGame.date).all()
    #* gamesInDb used to check if a save, update, or skip + print done in createTodaysGames

    startingDateStr = utcDateTimeToPacificTimeStr(startDateTime, YMD_FORMAT) #? StartDate with PST accounted for!
    print('Beginning to add Dodger Games to Schedule\n')
    seriesTotal, currentSeriesGame, seasonGameNum = 0, 0, 0 #* SeasonGameNum tracks total num of games read so far
    for dayNum, gameDate in enumerate(teamGameDates):
        gameList = gameDate.get('games', 0)
        if not gameList or len(gameList) == 0:
            continue #? In case a date without any games is returned for some reason, skip it! (Not sure if possible)
        print(f"Day #{dayNum+1} that Dodgers have played since {startingDateStr}")

        currentSeriesGame = gameList[0]['seriesGameNumber']
        #* Next line checks for double headers BUT the above line just grabs the 1st of the 2 games (See next todo)
        gameStr = "Today's a double header! " if len(gameList) > 1  \
            else f"On {gameDate['date']} is game #{currentSeriesGame} in a series "

        (seasonGameNum, gameStr) = createTodaysGames(gameList, gamesInDb, seasonGameNum, gameStr)

        seriesTotal = gameList[0]['gamesInSeries'] #todo Using the 1st game MIGHT cause next line to fail
        if currentSeriesGame == seriesTotal: #* This condition will group games by series
            gameStr += '\n'
            gameStr += ('=' * 60)
            gameStr += ' SERIES END '
            gameStr += ('=' * 80)
            gameStr += '\n\n'
            currentSeriesGame = 0
        else:
            gameStr += '\n'

        print(gameStr)

    from . import updateAllTeamRecords #? Avoid createPromotions circular ref
    updateAllTeamRecords()

    print('Finishing seeding process. \n')

#! Model Creation Methods - GameDay, Team, and GameDayPromotions
def createTodaysGames(todaysGames, gamesInDb, seasonGameNum, gameStr): #* Make games for particular date
    #* Perform this string manipulation ONCE, not twice if a double header
    awayTeam = createOrGrabTeam(todaysGames[0], 'away') #* Always needed so promos can check for updates later
    gameStr += f"where the visiting, {awayTeam.city_name} {awayTeam.team_name}, "
    homeTeam = createOrGrabTeam(todaysGames[0], 'home')
    gameStr += f"will take on the {homeTeam.team_name} at home in {homeTeam.city_name}"

    for game in todaysGames: #* In case of double headers
        gameDate, gameSeriesNumber, gamesInSeries = game['gameDate'], game['seriesGameNumber'], game['gamesInSeries']

        currentGameInDb = gamesInDb[seasonGameNum] if seasonGameNum < len(gamesInDb) else None
        gameNotInDB = currentGameInDb is None

        if gameNotInDB: #* If no record found, let's make one and set it!
            print('No game previously on this date so adding it to the DB')
            #* Create Game Model so promos can be associated
            currentGameInDb = DodgerGame(date=strToDatetime(gameDate, ISO_FORMAT),
                                         gameNumInSeries=gameSeriesNumber, gamesInSeries=gamesInSeries,
                                         home_team_id=homeTeam.id, away_team_id=awayTeam.id)
            saveToDb(currentGameInDb)

        #* Add promos ONLY if it's a home game
        if homeTeam.city_name == 'Los Angeles':
            createPromotionsForGame(game['promotions'] if ('promotions' in game) else [], currentGameInDb)
        seasonGameNum += 1 #* Keep incrementing regardless of conditional case above

        if gameNotInDB or currentGameInDb.gameNumInSeries != gameSeriesNumber or currentGameInDb.gamesInSeries != gamesInSeries:
            continue

        print(f"Game #{seasonGameNum + 1} currently in db is at {currentGameInDb}")
        print(f"Game #{seasonGameNum + 1} in endpoint is at {utcStrToPacificTime(gameDate)}")
        if currentGameInDb.readableDate != utcStrToPacificTime(gameDate):
            print('No match! Update the game!')
            currentGameInDb.date = gameDate #* Date might not be the only prop that needs updating!
            finalizeDbUpdate() #todo BUT need to look for other changes that might happen
        else:
            print('Game time matches! All fine, move on!')

    return (seasonGameNum, gameStr) #* May one day get rid of gameStr or find way to consolidate string

def createOrGrabTeam(game, teamKey=''): #* If able to fetch team, great! Otherwise let's add it!
    team = game['teams'][teamKey]['team']

    teamInDb = None
    #? Will always return model, so declare a var, check if in DB w/ walrus in conditional, or Create+Save, then return
    if (teamInDb := BaseballTeam.query.filter_by(team_name=team['clubName']).first()) is not None:
        print(f"Found a matching team! {teamInDb}. No need to double save") #* Finalize team record later
    else:
        teamRecord = game['teams'][teamKey]['leagueRecord']

        #* Easiest to directly save teamLogo URL below rather than save svg+xml & use html.escape() for safety
        teamInDb = BaseballTeam(team_name=team['clubName'], city_name=team['franchiseName'],
                                team_logo=BASE_MLB_LOGO_URL.format(espnID=team['id']),
                                abbreviation=team['abbreviation'], wins=teamRecord['wins'], losses=teamRecord['losses'])
        saveToDb(teamInDb)

    return teamInDb

def createPromotionsForGame(promotions, thisGame):
    print(f"Today's Game, {thisGame}, has {len(promotions)} promotions")
    if thisGame is None:
        return #? In case game doesn't exist (which would cause linking below to fail)
    for promo in promotions:
        promoName = promo['name']
        print(f"\t********** {promoName} **********")
        thumbnailUrl = promo['imageUrl'] if ('imageUrl' in promo) else 'undefined'

        if len(thisGame.promos) > 0: #* THEN update the promotions list for this game
            matchingPromo = next((gamePromo for gamePromo in thisGame.promos if (gamePromo.name == promoName)), None)
            if matchingPromo is not None and matchingPromo.thumbnail_url != thumbnailUrl:
                matchingPromo.thumbnail_url = thumbnailUrl
                finalizeDbUpdate()
                print('\tMatch found but image url changed, so updating!')
                continue
            elif matchingPromo is not None:
                print('\tMatch found but image url remained the same, so skip!')
                continue

        saveToDb(Promo(name=promoName, thumbnail_url=thumbnailUrl, dodger_game_id=thisGame.id))
