from .database_seed import comparePromoLists, initPromotionsForGame, replaceOldPromos
from .. import db
from ..models import BaseballGame
from ..utility.datetime_helpers import ISO_FORMAT, strToDatetime
from ..utility.mlb_api import fetchRemainingSchedule

from flask import current_app as app  #? Main method of accessing App's Config.py env vars
from sqlalchemy.exc import NoResultFound


def updateAllPromotions():
    print("Going to update all promotions")

    # Get `gameDates`, not `gameTotal` or `todaysDate`
    gameDateList = fetchRemainingSchedule()[1] or []
    for gameDate in gameDateList:
        gameList = gameDate.get("games", [])
        #? If a date has no games, the list comprehension won't run and for loop continues
        [updateEachGamesPromotions(game) for game in gameList]


def updateEachGamesPromotions(game):
    #? Since `homeTeamName` is deeply nested, catching the KeyError if it's `None`
    #? helps so the comprehension finishes the rest of the games and dates lists
    try:
        # Running `lower()` on these names helps with comparison
        homeTeamName = game["teams"]["home"]["team"].get("name", "").lower()
        expectedTeamName = app.config.get("TEAM_FULL_NAME").lower()
        if (homeTeamName == expectedTeamName): # ONLY add promos if it's a home game
            dateForGame = strToDatetime(game["gameDate"], ISO_FORMAT)
            gameInDb = db.session.scalars(
                db.select(BaseballGame).filter_by(date=dateForGame)
            ).one()
            newPromos = initPromotionsForGame(game.get("promotions", []))
            if not comparePromoLists(gameInDb.promos, newPromos):
                replaceOldPromos(gameInDb, newPromos)
    except KeyError:
        print("When updating Game Promotions: No game home team or date found in JSON")
    except NoResultFound:
        print(f"When updating Game Promotions: No game with UTC date: {game['gameDate']}")
    except Exception as exception:
        print(f"When updating Game Promotions: Encountered {type(exception)} encountered")

