from datetime import timedelta
from .. import db
from ..models import DodgerGame, BaseballTeam, Promo
from ..utility.database_helpers import saveToDb, deleteFromDb
from ..utility.datetime_helpers import dateToStr, strToDatetime, ISO_FORMAT, YMD_FORMAT
from ..utility.utc_to_pt_converters import utcStrToPacificDatetime
from ..utility.endpoint_constants import BASE_MLB_LOGO_URL
from ..utility.mlb_api import fetchThisYearsSchedule, fetchRemainingSchedule


#! Main CLI Command
def seedDB(updateMode = False):
    print('Running the Database Seeder')
    (totalGames, teamGameDates, startDate) = fetchRemainingSchedule() if updateMode else fetchThisYearsSchedule()
    if totalGames is None or teamGameDates is None:
        return #* Getting None means likely issue with MLB-Stats endpoint

    #? Query for all games in DB after the startDate (which if in updateMode is today's date)
    startDateTime = utcStrToPacificDatetime(startDate, YMD_FORMAT) #? Take it as PDT since it's 7 hours earlier than UTC
    gamesInDb = db.session.scalars( #* gamesInDb used to check if a save, update, or skip + print done in createGamesOfTheDay
        db.select(DodgerGame).where(DodgerGame.readableDateTime >= startDateTime).order_by(DodgerGame.date)
    ).all()

    startingDateStr = dateToStr(startDateTime, YMD_FORMAT) #? StartDate with PDT accounted for!
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
        newGame = DodgerGame(gameKey=gamePk, date=strToDatetime(gameDate, ISO_FORMAT),
                             seriesGameNumber=gameSeriesNumber, seriesGameCount=gamesInSeries,
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
            if gameExpectedFromDb.seriesGameNumber == gameExpectedFromDb.seriesGameCount:
                print("Seems the game just made their start time earlier")
            #* Away games track changes by comparing the API game to the current DB game
            #* Home games can use promos to track game identity (which would be different than __eq__)
            #todo In the future, gamePk is all-around better option since it holds across major changes
            if homeTeam.abbreviation == 'LAD':
                findOriginalGameByPromos(gamesInDb, seasonGameNum, newGame, newPromos, replaceOldGame)
        elif newGame.date > gameExpectedFromDb.date:
            print('Seems a game was postponed OR suspended')
            if gameExpectedFromDb.seriesGameNumber == gameExpectedFromDb.seriesGameCount:
                print("Seems the game just made its start time later")
            if gameExpectedFromDb.seriesGameCount > newGame.seriesGameCount:
                print("Seems the game just rescheduled entirely since the total games in the series was reduced")
            #* replaceOldGame seems the best way all-around to keep the DB list ordered correctly
            if homeTeam.abbreviation == 'LAD':
                findOriginalGameByPromos(gamesInDb, seasonGameNum, newGame, newPromos, replaceOldGame)

        print(f"Game from DB List = {gameExpectedFromDb} which is game " \
              f"#{gameExpectedFromDb.seriesGameNumber} in a series of {gameExpectedFromDb.seriesGameCount}")
        print(f"Game from API = {newGame} which is game #{newGame.seriesGameNumber} in a series of {newGame.seriesGameCount}")
        print(f"Game from the DB List after changes = {gamesInDb[seasonGameNum]} which is game " \
              f"#{gamesInDb[seasonGameNum].seriesGameNumber} in a series of {gamesInDb[seasonGameNum].seriesGameCount}")

        if gameExpectedFromDb == gamesInDb[seasonGameNum]:
            print(f"Game from DB list still matches original DB game = {gameExpectedFromDb == gamesInDb[seasonGameNum]}")
            if newGame == gameExpectedFromDb:
                if not comparePromoLists(gameExpectedFromDb.promos, newPromos): #* Compare now since
                    print("Promo lists don't match, replacing old ones with new ones!") #* likely didn't run check earlier
                    replaceOldPromos(gameExpectedFromDb, newPromos)
            else:
                replaceOldGame(gamesInDb, seasonGameNum, newGame)
                print((f"API Game had an unnoticed minor change, so using {gamesInDb[seasonGameNum]}," #? Multi-line f-string
                       f"and deleting {gameExpectedFromDb}"))
                createNewGame(newGame, newPromos)
            print('')
        elif newGame == gamesInDb[seasonGameNum]: #* The new game was likely swapped into the DB list so save it now
            print(f"Game from DB list now matches API game = {newGame == gamesInDb[seasonGameNum]}\n")
            createNewGame(newGame, newPromos)

        seasonGameNum += 1 #* Increment to keep up with future checks

    return (seasonGameNum, gameStr) #* May one day get rid of gameStr or find way to consolidate string

def findOriginalGameByPromos(gamesInDb, seasonGameNum, newGame, newPromos, matchCallback):
    searchIndex = seasonGameNum + 1
    while searchIndex < len(gamesInDb) and gamesInDb[searchIndex].seriesGameNumber != 1:
        potentialGame: DodgerGame = gamesInDb[searchIndex]
        print(f"Potential game = {potentialGame} is #{potentialGame.seriesGameNumber}")
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
        offerType = promo.get('offerType', '')
        newPromo = Promo(name=promoName, thumbnail_url=thumbnailUrl, offer_type=offerType)
        newPromos.append(newPromo)
    return newPromos #* Return the list of promos to save

def linkPromosToGame(newGame, newPromos):
    for newPromo in newPromos:
        newPromo.dodger_game_id = newGame.id
        saveToDb(newPromo)

def replaceOldPromos(oldGame, newPromos):
    [deleteFromDb(promo) for promo in oldGame.promos]
    linkPromosToGame(oldGame, newPromos)

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
