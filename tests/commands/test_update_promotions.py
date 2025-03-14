from ..common_assertions import assertHasLengthOf, assertIsEmpty
from ..MockHttpResponse import MockHttpResponse
from mlb_team_schedule import db
from mlb_team_schedule.commands.update_promotions import (
    updateAllPromotions,
    updateEachGamesPromotions,
)
from mlb_team_schedule.models import BaseballGame, BaseballTeam
from mlb_team_schedule.utility.api_helpers import ClientErrorStatusCodeException
from mlb_team_schedule.utility.database_helpers import saveToDb
from mlb_team_schedule.utility.datetime_helpers import ISO_FORMAT, strToDatetime

import pytest
import requests
#? Std-Lib Lists/Dicts/Sets create shallow copies via their constructors
import copy #? So this deep copies them to avoid propagating changes by ref to new copies

#! Fixtures
@pytest.fixture(autouse=True)
def gameDbSetup(app):
    #? MUST init the Config to the expected/desired home team
    app.config["TEAM_FULL_NAME"] = "Los Angeles Dodgers"
    dodgers = BaseballTeam(team_name="Dodgers", city_name="Los Angeles", team_logo="A",
                           abbreviation="LAD", wins=2, losses=1)
    yankees = BaseballTeam(team_name="Yankees", city_name="New York", team_logo="B",
                           abbreviation="NYY", wins=1, losses=2)

    with app.app_context():
        saveToDb(dodgers)
        saveToDb(yankees)
        assert len(db.session.scalars(db.select(BaseballTeam)).all()) == 2

        #* Game 1 = Dodgers vs Yankees at home BUT Game 2 = Dodgers vs Yankees at New York
        date1 = strToDatetime("2021-05-10T02:10:35Z", ISO_FORMAT) #* May 09 2021 7:10PM
        game1 = BaseballGame(gameKey=1, date=date1, seriesGameNumber=1,
                             seriesGameCount=3, home_team_id=dodgers.id,
                             away_team_id=yankees.id)
        date2 = strToDatetime("2021-08-02T23:15:35Z", ISO_FORMAT) #* Aug 02 2021 4:15PM
        game2 = BaseballGame(gameKey=2, date=date2, seriesGameNumber=1,
                             seriesGameCount=3, home_team_id=yankees.id,
                             away_team_id=dodgers.id)
        saveToDb(game1)
        saveToDb(game2)
        assert len(db.session.scalars(db.select(BaseballGame)).all()) == 2

@pytest.fixture
def gameDatesJSON(gameJSON): #? MUST set 'totalGames' or fetchSchedule fails in updater
    return { "dates": [{ "games": [gameJSON] }], "totalGames": 123 }

@pytest.fixture
def gameJSON(promoJSON):
    return {
        "teams": { "home": { "team": { "name": "Los Angeles Dodgers" } } },
        "gameDate": "2021-05-10T02:10:35Z", "promotions": [promoJSON]
    }
@pytest.fixture
def promoJSON():
    return {
        "name": "Hat",
        "imageUrl": "https://mktg.mlbstatic.com/clubName/images/promotions/year/example-300x300.jpg"
    }


#! Tests
def test_updateAllPromotions(app, monkeypatch, gameDatesJSON):
    #* WHEN http response returns 404 status code
    mockResponse = MockHttpResponse(404)
    def mock_JSON(*args, **kwargs):
        return mockResponse
    monkeypatch.setattr(requests, "get", mock_JSON)
    with app.app_context(): #* THEN no changes to the promotions in the DB
        with pytest.raises(ClientErrorStatusCodeException): #* Due to ClientError raised
            updateAllPromotions()
        checkDefaultPromotions()

    #* WHEN status code is now 200 BUT JSON received is empty
    mockResponse.status_code = 200
    mockResponse.jsonResponse = { }
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateAllPromotions()
        checkDefaultPromotions()

    #* WHEN the dates received are empty
    mockResponse.jsonResponse = { "dates": [] }
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateAllPromotions()
        checkDefaultPromotions()

    #* WHEN the gameDates contain no game info
    gamesDatesMissingGames = copy.deepcopy(gameDatesJSON)
    gamesDatesMissingGames["dates"] = [{ }]
    mockResponse.jsonResponse = gamesDatesMissingGames
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateAllPromotions()
        checkDefaultPromotions()
    #* WHEN the games list on any given date is empty
    gameDatesWithEmptyGamesList = copy.deepcopy(gameDatesJSON)
    gameDatesWithEmptyGamesList["dates"][0]["games"] = []
    mockResponse.jsonResponse = gameDatesWithEmptyGamesList
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateAllPromotions()
        checkDefaultPromotions()

    #* WHEN the gameDatesJSON is correctly formatted and filled
    mockResponse.jsonResponse = gameDatesJSON
    with app.app_context():
        updateAllPromotions() #* THEN the game will receive an updated list of promotions
        checkUpdatedPromotions()


def test_updateEachGamesPromotions(app, gameJSON):
    #* WHEN the game JSON on any given date contains no info on the home team
    gameMissingTeamsInfo = { "teams": { } }
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameMissingTeamsInfo)
        checkDefaultPromotions()
    #* WHEN the game JSON on any given date contains empty home team info
    gameMissingHomeTeamInfo = { "teams": { "home": { } } }
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameMissingHomeTeamInfo)
        checkDefaultPromotions()
    #* WHEN the game JSON on any given date is missing the team name
    gameMissingHomeTeamName = copy.deepcopy(gameJSON)
    gameMissingHomeTeamName["teams"]["home"]["team"] = { }
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameMissingHomeTeamName)
        checkDefaultPromotions()

    #* WHEN the game JSON being checked has a different home team then expected
    gameUnexpectedHomeTeam = copy.deepcopy(gameJSON)
    gameUnexpectedHomeTeam["teams"]["home"]["team"]["name"] = "Foobar Fizzes"
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameUnexpectedHomeTeam)
        checkDefaultPromotions()

    #* WHEN the game JSON being checked is missing the game date
    gameMissingDate = copy.deepcopy(gameJSON)
    gameMissingDate.pop("gameDate")
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameMissingDate)
        checkDefaultPromotions()

    #* WHEN game JSON's date DOESN'T match any game in the DB
    gameUnexpectedDate = copy.deepcopy(gameJSON)
    gameUnexpectedDate.pop("promotions")
    #* Promos CAN find the wrong game if date is incorrect BUT not likely in real data
    gameUnexpectedDate["gameDate"] = "2021-06-10T02:10:35Z"
    with app.app_context(): #* THEN promotions remain the same in the DB
        updateEachGamesPromotions(gameUnexpectedDate)
        checkDefaultPromotions()

    #* WHEN promotions don't match
    with app.app_context():
        updateEachGamesPromotions(gameJSON)
        checkUpdatedPromotions() #* THEN promotions will be updated to match the JSON

    #* WHEN promotions match
    with app.app_context():
        updateEachGamesPromotions(gameJSON)
        checkUpdatedPromotions() #* THEN promos remain exactly as is with updated values

    #* WHEN promotions in JSON are empty BUT the game's promotions in DB are filled
    with app.app_context():
        gameJSON["promotions"] = []
        updateEachGamesPromotions(gameJSON) #* THEN delete promos to match the JSON
        checkDefaultPromotions() #* SO empty promos list resets Game to default value


#! Assertion Methods
def checkDefaultPromotions():
    games = db.session.scalars(db.select(BaseballGame)).all()
    [assertIsEmpty(game.promos) for game in games]

def checkUpdatedPromotions():
    games = db.session.scalars(db.select(BaseballGame)).all()
    updatedGame = games[0] if games[0].home_team.fullName == "Los Angeles Dodgers" \
        else games[1]
    unchangedGame = games[1] if games[1].home_team.fullName == "New York Yankees" \
        else games[0]
    assertHasLengthOf(updatedGame.promos, 1)
    assertIsEmpty(unchangedGame.promos)
    assert updatedGame.promos[0].name == "Hat"
