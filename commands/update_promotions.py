from flask import current_app as app #? Main method of accessing App's Config.py env vars
import requests
from sqlalchemy.exc import NoResultFound
from .. import db
from .database_seed import createEndpoint, scheduleDates, initPromotionsForGame, comparePromoLists, replaceOldPromos
from ..models import DodgerGame
from ..utility.datetime_helpers import strToDatetime, ISO_FORMAT


def updateAllPromotions():
    print("Going to update all promotions")
    #? '*' unpacks the tuple returned by scheduleDates() into the args of createEndpoint()
    response = requests.get(createEndpoint(*scheduleDates(True)))
    if (response.status_code != 200):
        return #? In case of broken link
    dodgersSchedule = response.json()

    gameDateList = dodgersSchedule.get('dates', [])
    for gameDate in gameDateList:
        gameList = gameDate.get('games', [])
        #? If a date is found w/out any games, then this list comprehension ends immediately, moving on to next date
        [updateEachGamesPromotions(game) for game in gameList]


def updateEachGamesPromotions(game):
    #? Since the homeTeamName is deeply nested, it's easiest in Python to catch the KeyError if the name is missing, so the
    #? comprehension keeps processing remaining games AND all remaining game dates by halting error propagation
    try:
        homeTeamName = game['teams']['home']['team'].get('name', '').lower() #* Ensure using lower() on a string via default
        expectedTeamName = app.config.get('TEAM_FULL_NAME').lower()
        if (homeTeamName == expectedTeamName): #* ONLY add promos if it's a home game
            dateForGame = strToDatetime(game['gameDate'], ISO_FORMAT) #* Convert typical UTC string to datetime obj
            gameInDb = db.session.scalars(db.select(DodgerGame).filter_by(date=dateForGame)).one()
            newPromos = initPromotionsForGame(game.get('promotions', []))
            if not comparePromoLists(gameInDb.promos, newPromos):
                replaceOldPromos(gameInDb, newPromos)
    except KeyError:
        print("While updating Game Promotions: Unable to find the game's home team or date in JSON")
    except NoResultFound:
        print(f"While updating Game Promotions: Unable to find Dodger game with the following UTC date: {game['gameDate']}")
    except Exception as exception:
        print(f"While updating Game Promotions: Unexpected exception of {type(exception)} encountered")