from .. import db
from ..models import BaseballGame, BaseballTeam, Promo
from ..utility.database_helpers import deleteFromDb, saveToDb
from ..utility.datetime_helpers import ISO_FORMAT, YMD_FORMAT, dateToStr, strToDatetime
from ..utility.endpoint_constants import BASE_MLB_LOGO_URL
from ..utility.mlb_api import fetchRemainingSchedule, fetchThisYearsSchedule
from ..utility.utc_to_pt_converters import utcStrToPacificDatetime

from flask import current_app as app
from datetime import timedelta


#! Main CLI Command
def seedDB(updateMode = False):
    print("Running the Database Seeder")
    (totalGames, teamGameDates, startDate) = fetchRemainingSchedule() if updateMode \
        else fetchThisYearsSchedule()
    if totalGames is None or teamGameDates is None:
        return # Getting None means likely issue with MLB-Stats endpoint

    #? Query for all games in DB after `startDate` (today's date if in updateMode)
    startDateTime = utcStrToPacificDatetime(startDate, YMD_FORMAT)
    gamesInDb = db.session.scalars( # Checks if a save, update, or skip + print done later
        db.select(BaseballGame).where(BaseballGame.readableDateTime >= startDateTime) \
                                   .order_by(BaseballGame.date)
    ).all()

    startingDateStr = dateToStr(startDateTime, YMD_FORMAT) # In PDT
    print("Beginning to add Baseball Games to Schedule\n")
    seriesTotal, currentSeriesGame, seasonGameNum = 0, 0, 0
    for dayNum, gameDate in enumerate(teamGameDates):
        gameList = gameDate.get("games", [])
        if len(gameList) == 0:
            print("Date without any games found, skipping!")
            continue # Skip if date has no games (unsure if possible)
        print(f"Day #{dayNum+1} that {app.config.get('TEAM_FULL_NAME')}" \
            f" have played since {startingDateStr}")

        firstGameOfDay = gameList[0]
        currentSeriesGame = gameList[1]["seriesGameNumber"] if len(gameList) > 1 \
            else firstGameOfDay["seriesGameNumber"]

        gameStr = f"On {gameDate['date']} is "
        gameStr += "a double header " if len(gameList) > 1 \
            else f"game #{currentSeriesGame} "
        gameStr += "in a series "

        (seasonGameNum, gameStr) = createGamesOfTheDay(
            gameList, gamesInDb, seasonGameNum, gameStr
        )

        seriesTotal = firstGameOfDay["gamesInSeries"]
        if currentSeriesGame == seriesTotal: # This condition will group games by series
            gameStr += f"\n{('=' * 60)} SERIES END {('=' * 80)}\n\n"
            currentSeriesGame = 0
        else:
            gameStr += "\n"

        print(gameStr)

    from . import updateAllTeamRecords  #? Avoid initPromotions circular ref
    updateAllTeamRecords()

    print("Finishing seeding process. \n")

#! Model Creation Methods - GameDay, Team, and GameDayPromotions
def createGamesOfTheDay(todaysGames, gamesInDb, seasonGameNum, gameStr):
    # Perform this string manipulation ONCE, not twice if a double header
    awayTeam = createOrGrabTeam(todaysGames[0], "away")
    gameStr += f"where the visiting, {awayTeam.city_name} {awayTeam.team_name}, "
    homeTeam = createOrGrabTeam(todaysGames[0], "home")
    gameStr += f"will take on the {homeTeam.team_name} at home in {homeTeam.city_name}"

    for game in todaysGames: # In case of double headers
        gamePk, gameDate = game["gamePk"], game["gameDate"]
        gameSeriesNumber, gamesInSeries = game["seriesGameNumber"], game["gamesInSeries"]

        # Using a list sorted oldest to most recent date to get any game based on season #
        # based on what # game of the full season it is, i.e.
        # Ex: 10th game in season must = index 9 with all expected attributes
        gameExpectedFromDb: BaseballGame = gamesInDb[seasonGameNum] \
            if seasonGameNum < len(gamesInDb) else None

        # Create Game Model so promos can be associated later
        newGame = BaseballGame(gameKey=gamePk, date=strToDatetime(gameDate, ISO_FORMAT),
                               seriesGameNumber=gameSeriesNumber,
                               seriesGameCount=gamesInSeries,
                               home_team_id=homeTeam.id, away_team_id=awayTeam.id)

        # If `resumedFrom` key found, game was suspended from day before, & may be a copy
        originalDate = game.get("resumedFrom", "") # Default to '' to falsy check ternary
        originalPstDate = (strToDatetime(originalDate, ISO_FORMAT) - timedelta(hours=7)) \
            if originalDate else None # Avoids poorly formatted datetime
        # Games rarely added since 163rd tiebreakers can't happen with extended playoffs
        suspendedGame = originalPstDate and \
            originalPstDate.day + 1 == newGame.readableDateTime.day
        if seasonGameNum > 0 and suspendedGame: # Prevents copy from being saved into DB
            print("Found a suspended game so skipping!\n")
            continue

        # Check team abbreviation for when city has multiple teams, i.e. LA or NY
        newPromos = initPromotionsForGame(game.get("promotions", [])) \
            if homeTeam.abbreviation == "LAD" else []
        if gameExpectedFromDb is None: # Likely running seeder so save all as normal
            print("No game from the DB found so save the game and its promos!")
            createNewGame(newGame, newPromos)
            seasonGameNum += 1 # Increment to make sure to keep up with future checks
            continue

        # Compare datetime objs to get correct ordering, not string versions
        if newGame.date < gameExpectedFromDb.date:
            print("Seems a game moved up")
            if gameExpectedFromDb.seriesGameNumber == gameExpectedFromDb.seriesGameCount:
                print("Seems the game just made their start time earlier")
            # Away games track changes by comparing the API game to the current DB game
            # Home games track identity by promo set (so different than __eq__)
            #TODO: `gamePk` probably a better choice for both since it rarely changes
            if homeTeam.abbreviation == "LAD":
                findOriginalGameByPromos(
                    gamesInDb, seasonGameNum, newGame, newPromos, replaceOldGame
                )
        elif newGame.date > gameExpectedFromDb.date:
            print("Game likely suspended or postponed")
            if gameExpectedFromDb.seriesGameNumber == gameExpectedFromDb.seriesGameCount:
                print("Game likely later start time")
            if gameExpectedFromDb.seriesGameCount > newGame.seriesGameCount:
                print("Game likely full rescheduled, since total games in series reduced")
            if homeTeam.abbreviation == "LAD":
                findOriginalGameByPromos( # `replaceOldGame` helps keep db list ordered
                    gamesInDb, seasonGameNum, newGame, newPromos, replaceOldGame
                )

        print(f"Game from DB List = {gameExpectedFromDb}" \
            f" which is game #{gameExpectedFromDb.seriesGameNumber}" \
            f" in a series of {gameExpectedFromDb.seriesGameCount}"
        )
        print(f"Game from API = {newGame}" \
            f" which is game #{newGame.seriesGameNumber}" \
            f" in a series of {newGame.seriesGameCount}"
        )
        print(f"Game from DB List after changes = {gamesInDb[seasonGameNum]}" \
            f" which is game #{gamesInDb[seasonGameNum].seriesGameNumber}" \
            f" in a series of {gamesInDb[seasonGameNum].seriesGameCount}"
        )

        if gameExpectedFromDb == gamesInDb[seasonGameNum]:
            print("Game from DB List still still matches original in DB")
            if newGame == gameExpectedFromDb:
                if not comparePromoLists(gameExpectedFromDb.promos, newPromos):
                    print("Promo lists don't match, replacing old ones with new ones!")
                    replaceOldPromos(gameExpectedFromDb, newPromos)
            else:
                replaceOldGame(gamesInDb, seasonGameNum, newGame)
                print(f"API Game changed. Use {gamesInDb[seasonGameNum]} & delete other")
                createNewGame(newGame, newPromos)
            print("")
        elif newGame == gamesInDb[seasonGameNum]: # New game likely put into `gamesInDb`
            createNewGame(newGame, newPromos) # so save into actual DB now
            print("Game from DB list now matches API game\n")

        seasonGameNum += 1 # On to next game in the season so future checks work

    return (seasonGameNum, gameStr) #TODO: Get rid of OR consolidate `gameStr`

def findOriginalGameByPromos(gamesInDb, seasonGameNum, newGame, newPromos, matchCallback):
    searchIndex = seasonGameNum + 1
    while searchIndex < len(gamesInDb) and gamesInDb[searchIndex].seriesGameNumber != 1:
        potentialGame: BaseballGame = gamesInDb[searchIndex]
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
    # Inserts `newGame` at expected date/index. Save to the DB later.
    gamesInDb.insert(seasonGameNum, newGame)

def createOrGrabTeam(game, teamKey=""):
    team = game["teams"][teamKey]["team"]

    teamInDb = None
    #? MUST return model so set fetched model var in walrus conditional OR create and save
    if (teamInDb := queryTeamByName(team["clubName"])) is not None:
        print(f"Found a matching team: {teamInDb} -> Won't double save. Set record later")
    else:
        teamRecord = game["teams"][teamKey]["leagueRecord"]

        # Easier to save `teamLogo` URL than save `svg+xml` & use safe `html.escape()`
        teamInDb = BaseballTeam(team_name=team["clubName"],
                                city_name=team["franchiseName"],
                                team_logo=BASE_MLB_LOGO_URL.format(espnID=team["id"]),
                                abbreviation=team["abbreviation"],
                                wins=teamRecord["wins"], losses=teamRecord["losses"])
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
        promoName = promo["name"]
        thumbnailUrl = promo.get("imageUrl", "undefined")
        offerType = promo.get("offerType", "")
        newPromo = Promo(name=promoName, thumbnail_url=thumbnailUrl, offer_type=offerType)
        newPromos.append(newPromo)
    return newPromos # Return the list of promos to save

def linkPromosToGame(newGame, newPromos):
    for newPromo in newPromos:
        newPromo.baseball_game_id = newGame.id
        saveToDb(newPromo)

def replaceOldPromos(oldGame, newPromos):
    [deleteFromDb(promo) for promo in oldGame.promos]
    linkPromosToGame(oldGame, newPromos)

#TODO: Could do `newPromoSet - dbPromoSet`, reliably leaving only new + changed promos
#TODO: THEN could iterate through the new promos, save and link them to the game
def comparePromoLists(dbPromos, newPromos):
    COMMON_SET = {
        Promo(name="Fireworks Show"),
        Promo(name="Taco Tuesdays"),
        Promo(name="Kids Run the Bases")
    }
    #? For sets obj hash & equals must BOTH = True so `dbPromoSet` drops all in COMMON_SET
    dbPromoSet = set(dbPromos) - COMMON_SET
    newPromoSet = set(newPromos) - COMMON_SET
    if len(dbPromoSet) != len(newPromoSet): # Easy quick guard check
        print("Promo length DOESN'T match")
        return False
    # If SAME HOME GAME, THEN promo set should match EXCEPT for date change
    if dbPromoSet != newPromoSet:
        print("Promo sets DON'T match")
        return False
    print("Promo sets match!")
    return True

