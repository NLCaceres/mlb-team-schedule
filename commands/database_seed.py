from datetime import timedelta
import requests
from .. import db
from ..models import DodgerGame, BaseballTeam, Promo
from ..utility.database_helpers import saveToDb, deleteFromDb
from ..utility.datetime_helpers import (dateToday, dateToStr, strToDatetime, utcDateTimeToPacificTimeStr, YMD_FORMAT, ISO_FORMAT)
from ..utility.endpoint_helpers import BASE_MLB_LOGO_URL, SCHEDULE_ENDPOINT


#! Endpoint generation methods
#? Return an unpackable tuple useful to create the schedule endpoint
def scheduleDates(updateMode = False):
    todaysDate = dateToday()
    thisYear = todaysDate.year #* SeasonYear Format: YYYY -> e.g. 2021
    #* StartDate & endDate Format: YYYY-MM-DD -> e.g. 2021-06-01
    startDate = dateToStr(todaysDate, YMD_FORMAT) if updateMode else f"{thisYear}-03-01"
    endDate = f"{thisYear}-11-30"

    return (startDate, endDate, thisYear) #* Most Python solution to quickly pack related data! Return a tuple!

def createEndpoint(startDate = None, endDate = None, seasonYear = None, teamId = None):
    if startDate is None or endDate is None or seasonYear is None:
        return None

    selectedTeamId = teamId or 119 #* The Dodgers ID acts as the default if None is found
    return SCHEDULE_ENDPOINT.format(startDate=startDate, endDate=endDate, seasonYear=seasonYear, teamId=selectedTeamId)

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
    startDateTime = strToDatetime(startDate, YMD_FORMAT) #todo Might be able to convert to PST HERE since it's EARLIER than UTC
    gamesInDb = db.session.scalars(
        db.select(DodgerGame).where(DodgerGame.readableDateTime >= startDateTime).order_by(DodgerGame.date)
    ).all()
    #* gamesInDb used to check if a save, update, or skip + print done in createGamesOfTheDay

    startingDateStr = utcDateTimeToPacificTimeStr(startDateTime, YMD_FORMAT) #? StartDate with PST accounted for!
    print('Beginning to add Dodger Games to Schedule\n')
    seriesTotal, currentSeriesGame, seasonGameNum = 0, 0, 0 #* SeasonGameNum tracks total num of games read so far
    for dayNum, gameDate in enumerate(teamGameDates):
        gameList = gameDate.get('games', [])
        if len(gameList) == 0:
            print('Date without any games found, skipping!')
            continue #? In case a date without any games is returned for some reason, skip it! (Not sure if possible)
        print(f"Day #{dayNum+1} that Dodgers have played since {startingDateStr}")

        firstGameOfDay = gameList[0]
        currentSeriesGame = gameList[1]['seriesGameNumber'] if len(gameList) > 1 else firstGameOfDay['seriesGameNumber']
        #* Next line checks for double headers BUT the above line just grabs the 1st of the 2 games (See next todo)
        gameStr = f"On {gameDate['date']} is "
        gameStr += "a double header " if len(gameList) > 1 else f"game #{currentSeriesGame} "
        gameStr += 'in a series '

        (seasonGameNum, gameStr) = createGamesOfTheDay(gameList, gamesInDb, seasonGameNum, gameStr)

        seriesTotal = firstGameOfDay['gamesInSeries']
        if currentSeriesGame == seriesTotal: #* This condition will group games by series
            gameStr += f"\n{('=' * 60)} SERIES END {('=' * 80)}\n\n"
            currentSeriesGame = 0
        else:
            gameStr += '\n'

        print(gameStr)

    from . import updateAllTeamRecords #? Avoid initPromotions circular ref
    updateAllTeamRecords()

    print('Finishing seeding process. \n')

#! Model Creation Methods - GameDay, Team, and GameDayPromotions
def createGamesOfTheDay(todaysGames, gamesInDb, seasonGameNum, gameStr):
    #* Perform this string manipulation ONCE, not twice if a double header
    awayTeam = createOrGrabTeam(todaysGames[0], 'away') #* Always needed so promos can check for updates later
    gameStr += f"where the visiting, {awayTeam.city_name} {awayTeam.team_name}, "
    homeTeam = createOrGrabTeam(todaysGames[0], 'home')
    gameStr += f"will take on the {homeTeam.team_name} at home in {homeTeam.city_name}"

    for game in todaysGames: #* In case of double headers
        gamePk, gameDate = game['gamePk'], game['gameDate']
        gameSeriesNumber, gamesInSeries = game['seriesGameNumber'], game['gamesInSeries']

        #* Should be able to grab any game in the DB from a oldest to most recent date sorted list 
        #* based on what # game of the full season it is, i.e.
        #* The tenth game of the year should be at index 9 with the expected time, promotions, etc
        gameExpectedFromDb: DodgerGame = gamesInDb[seasonGameNum] if seasonGameNum < len(gamesInDb) else None

        #* Create Game Model so promos can be associated later
        newGame = DodgerGame(date=strToDatetime(gameDate, ISO_FORMAT),
                             gameNumInSeries=gameSeriesNumber, gamesInSeries=gamesInSeries,
                             home_team_id=homeTeam.id, away_team_id=awayTeam.id)

        #* If resumedFrom key found, then found a Suspended game, which is most likely a copy of the previous game
        originalDate = game.get('resumedFrom', '') #* Use default '' to falsy check ternary to avoid datetime format errors
        originalPstDate = (strToDatetime(originalDate, ISO_FORMAT) - timedelta(hours=7)) if originalDate else None
        #? Games aren't really added anymore, since 163rd tiebreaker games no longer happen due to extended playoffs
        if seasonGameNum > 0 and originalPstDate and originalPstDate.day + 1 == newGame.readableDateTime.day:
            print('Found a suspended game so skipping!\n') #* So that way, no 2nd copy is made
            continue

        #* Using abbreviation to mark homeTeams handles edge case where a city has multiple teams, i.e. LA & NY
        newPromos = initPromotionsForGame(game.get('promotions', [])) if homeTeam.abbreviation == 'LAD' else []
        if gameExpectedFromDb is None: #* Likely running initial seed so just save everything as normal
            print("No game from the DB found so save the game and its promos!")
            createNewGame(newGame, newPromos)
            seasonGameNum += 1 #* Increment to make sure to keep up with future checks
            continue

        #* Comparing datetime objs to get correct date ordering, not the strings which would get lexicographic sorting
        if newGame.date < gameExpectedFromDb.date:
            print('Seems a game moved up')
            if gameExpectedFromDb.gameNumInSeries == gameExpectedFromDb.gamesInSeries:
                print("Seems the game just made their start time earlier")
            #* Away games track changes by comparing the API game to the current DB game
            #* Home games can use promos to track game identity (which would be different than __eq__)
            #todo In the future, gamePk is all-around better option since it holds across major changes
            if homeTeam.abbreviation == 'LAD':
                findOriginalGameByPromos(gamesInDb, seasonGameNum, newGame, newPromos, replaceOldGame)
        elif newGame.date > gameExpectedFromDb.date:
            print('Seems a game was postponed OR suspended')
            if gameExpectedFromDb.gameNumInSeries == gameExpectedFromDb.gamesInSeries:
                print("Seems the game just made its start time later")
            if gameExpectedFromDb.gamesInSeries > newGame.gamesInSeries:
                print("Seems the game just rescheduled entirely since the total games in the series was reduced")
            #* replaceOldGame seems the best way all-around to keep the DB list ordered correctly
            if homeTeam.abbreviation == 'LAD':
                findOriginalGameByPromos(gamesInDb, seasonGameNum, newGame, newPromos, replaceOldGame)

        print(f"Game from DB List = {gameExpectedFromDb} which is game " \
              f"#{gameExpectedFromDb.gameNumInSeries} in a series of {gameExpectedFromDb.gamesInSeries}")
        print(f"Game from API = {newGame} which is game #{newGame.gameNumInSeries} in a series of {newGame.gamesInSeries}")
        print(f"Game from the DB List after changes = {gamesInDb[seasonGameNum]} which is game " \
              f"#{gamesInDb[seasonGameNum].gameNumInSeries} in a series of {gamesInDb[seasonGameNum].gamesInSeries}")

        if gameExpectedFromDb == gamesInDb[seasonGameNum]:
            print(f"Game from DB list still matches original DB game = {gameExpectedFromDb == gamesInDb[seasonGameNum]}")
            if newGame == gameExpectedFromDb:
                if not comparePromoLists(gameExpectedFromDb.promos, newPromos): #* Compare now since likely didn't run check earlier
                    print("Promo lists don't match, replacing old ones with new ones!")
                    replaceOldPromos(gameExpectedFromDb, newPromos)
            else:
                replaceOldGame(gamesInDb, seasonGameNum, newGame)
                print(f"API Game had an unnoticed minor change, so using {gamesInDb[seasonGameNum]}, and deleting {gameExpectedFromDb}")
                createNewGame(newGame, newPromos)
            print('')
        elif newGame == gamesInDb[seasonGameNum]: #* The new game was likely swapped into the DB list so save it now
            print(f"Game from DB list now matches API game = {newGame == gamesInDb[seasonGameNum]}\n")
            createNewGame(newGame, newPromos)

        seasonGameNum += 1 #* Increment to keep up with future checks

    return (seasonGameNum, gameStr) #* May one day get rid of gameStr or find way to consolidate string

def findOriginalGameByPromos(gamesInDb, seasonGameNum, newGame, newPromos, matchCallback):
    searchIndex = seasonGameNum + 1
    while searchIndex < len(gamesInDb) and gamesInDb[searchIndex].gameNumInSeries != 1:
        potentialGame: DodgerGame = gamesInDb[searchIndex]
        print(f"Potential game = {potentialGame} is #{potentialGame.gameNumInSeries}")
        matchingPromos = comparePromoLists(potentialGame.promos, newPromos)
        if matchingPromos:
            matchCallback(gamesInDb, seasonGameNum, newGame, searchIndex)
            break
        searchIndex += 1

def replaceOldGame(gamesInDb, seasonGameNum, newGame, searchIndex=None):
    deleteIndex = searchIndex or seasonGameNum
    print(f"Deleting a matching outdated game at index = {deleteIndex}")
    originalGame = gamesInDb.pop(deleteIndex)
    [deleteFromDb(promo) for promo in originalGame.promos]
    deleteFromDb(originalGame)
    gamesInDb.insert(seasonGameNum, newGame) #* Insert the newGame at expected date index. Save the changes to the DB later

def createOrGrabTeam(game, teamKey=''): #* If able to fetch team, great! Otherwise let's add it!
    team = game['teams'][teamKey]['team']

    teamInDb = None
    #? Will always return model, so declare a var, check if in DB w/ walrus in conditional, or Create+Save, then return
    if (teamInDb := queryTeamByName(team['clubName'])) is not None:
        print(f"Found a matching team! {teamInDb} -> No need to double save") #* Finalize team record later
    else:
        teamRecord = game['teams'][teamKey]['leagueRecord']

        #* Easiest to directly save teamLogo URL below rather than save svg+xml & use html.escape() for safety
        teamInDb = BaseballTeam(team_name=team['clubName'], city_name=team['franchiseName'],
                                team_logo=BASE_MLB_LOGO_URL.format(espnID=team['id']),
                                abbreviation=team['abbreviation'], wins=teamRecord['wins'], losses=teamRecord['losses'])
        saveToDb(teamInDb)

    return teamInDb

def queryTeamByName(name):
    return db.session.scalars(db.select(BaseballTeam).filter_by(team_name=name)).first()

def createNewGame(newGame, newPromos):
    saveToDb(newGame)
    linkPromosToGame(newGame, newPromos)

def initPromotionsForGame(promotions):
    newPromos = []
    for promo in promotions:
        promoName = promo['name']
        thumbnailUrl = promo.get('imageUrl', 'undefined')
        newPromo = Promo(name=promoName, thumbnail_url=thumbnailUrl)
        newPromos.append(newPromo)
    return newPromos #* Return the list of promos to save

def linkPromosToGame(newGame, newPromos):
    for newPromo in newPromos:
        newPromo.dodger_game_id = newGame.id
        saveToDb(newPromo)

def replaceOldPromos(oldGame, newPromos):
    [deleteFromDb(promo) for promo in oldGame.promos]
    linkPromosToGame(oldGame, newPromos)

#todo Likely no longer need this updatePromo func
def updatePromotionsForGame(promotions, thisGame):
    newPromos = []
    for promo in promotions:
        promoName = promo['name']
        print(f"\t********** {promoName} **********")
        thumbnailUrl = promo.get('imageUrl', 'undefined')

        if len(thisGame.promos) > 0: #* THEN update the promotions list for this game
            matchingPromo = next((gamePromo for gamePromo in thisGame.promos if (gamePromo.name == promoName)), None)
            if matchingPromo is not None and matchingPromo.thumbnail_url != thumbnailUrl:
                # matchingPromo.thumbnail_url = thumbnailUrl
                # finalizeDbUpdate()
                print('\tMatch found but image url changed, so updating!')
                continue
            elif matchingPromo is not None:
                print('\tMatch found but image url remained the same, so skip!')
                continue

        newPromo = Promo(name=promoName, thumbnail_url=thumbnailUrl)
        newPromos.append(newPromo)
    return newPromos #* Return the list of promos to save

#todo Could use also do (newPromoSet - dbPromoSet), and it should reliably leave ONLY the new/changed promos
#todo from there, could iterate thru the new promos, save and link them
def comparePromoLists(dbPromos, newPromos):
    commonSet = { Promo(name='Fireworks Show'), Promo(name='Taco Tuesdays'), Promo(name='Kids Run the Bases') }
    dbPromoSet = set(dbPromos) - commonSet #? Important that obj hashes match AND equals return True
    #? so that dbPromoSet drops anything from the commonSet
    newPromoSet = set(newPromos) - commonSet
    if len(dbPromoSet) != len(newPromoSet): #* First prelim check if matching length
        print("Promo length DOESN'T match")
        return False
    #* If SAME HOME game, then should be the same set of promo names despite date moving a day forward or back
    if dbPromoSet != newPromoSet:
        print("Promo sets DON'T match")
        return False
    print('Promo sets match!')
    return True
