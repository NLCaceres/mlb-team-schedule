import pytest
import requests
#? An alt option w/ built-in collections like lists, dicts and sets is their constructor BUT they return shallow copies
import copy #? So deep copy is super useful to avoid changes propagating in nested values across new copies
from MockHttpResponse import MockHttpResponse
from sqlalchemy import exc
from DodgersPromo import db
from DodgersPromo.commands.database_update import (updateTeamRecord, updateAllTeamRecords,
                                                   updateEachDivision, updateAllPromotions, updateEachGamesPromotions)
from DodgersPromo.models import BaseballTeam, DodgerGame
from DodgersPromo.utility.datetime_helpers import strToDatetime, ISO_FORMAT
from DodgersPromo.utility.database_helpers import saveToDb


#! Fixtures
#! Update Team Records Fixtures
@pytest.fixture(autouse=True)
def teamDbSetup(app):
    team1 = BaseballTeam(team_name='Dodgers', city_name='Los Angeles', team_logo='Foo', abbreviation='LAD', wins=2, losses=1)
    team2 = BaseballTeam(team_name='Yankees', city_name='New York', team_logo='Bar', abbreviation='NYY', wins=1, losses=2)

    with app.app_context():
        saveToDb(team1)
        saveToDb(team2)
        assert len(db.session.scalars(db.select(BaseballTeam)).all()) == 2

@pytest.fixture
def standingsJSON(divisionJSON):
    return { 'records': [divisionJSON] } #? Python seems to hoist so using a fixture declared later works!

@pytest.fixture
def divisionJSON(teamJSON):
    return { 'division': { 'id': 123 }, 'teamRecords': [teamJSON] }

@pytest.fixture
def teamJSON():
    return { 'team': { 'id': 123, 'name': 'Los Angeles Dodgers' }, 'wins': 123, 'losses': 321 }


#! Update Promotions Fixtures
@pytest.fixture
def gameDbSetup(app):
    with app.app_context():
        teams = db.session.scalars(db.select(BaseballTeam)).all()
        dodgers = teams[0] if teams[0].fullName == 'Los Angeles Dodgers' else teams[1]
        yankees = teams[0] if teams[0].fullName == 'New York Yankees' else teams[1]
        #* Game 1 = Dodgers facing Yankees at home while Game 2 = Dodgers facing Yankees at New York
        date1 = strToDatetime('2021-05-10T02:10:35Z', ISO_FORMAT) #* May 09 2021 7:10PM
        game1 = DodgerGame(date=date1, gameNumInSeries=1, gamesInSeries=3, home_team_id=dodgers.id, away_team_id=yankees.id)
        date2 = strToDatetime('2021-08-02T23:15:35Z', ISO_FORMAT) #* Aug 02 2021 4:15PM
        game2 = DodgerGame(date=date2, gameNumInSeries=1, gamesInSeries=3, home_team_id=yankees.id, away_team_id=dodgers.id)
        saveToDb(game1)
        saveToDb(game2)
        assert len(db.session.scalars(db.select(BaseballTeam)).all()) == 2
        assert len(db.session.scalars(db.select(DodgerGame)).all()) == 2

@pytest.fixture
def gameDatesJSON(gameJSON):
    return { 'dates': [{ 'games': [gameJSON] }] }

@pytest.fixture
def gameJSON(promoJSON):
    return {
        'teams': { 'home': { 'team': { 'name': 'Los Angeles Dodgers' } } },
        'gameDate': '2021-05-10T02:10:35Z', 'promotions': [promoJSON]
    }
@pytest.fixture
def promoJSON():
    return { 'name': 'Hat', 'imageUrl': 'https://mktg.mlbstatic.com/clubName/images/promotions/year/example-300x300.jpg' }

#? Example of a fixture that monkeypatches/mocks the `requests` library get() fetch func
@pytest.fixture
def mock_404_response(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockHttpResponse(404)

    monkeypatch.setattr(requests, "get", mock_get)


#! Tests
#! Update Team Records funcs
def test_updateAllTeamRecords(app, monkeypatch, mock_404_response, standingsJSON):
    updateAllTeamRecords() #? mock_404_response monkeypatched in by fixture
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to the DB happen

    #? Inline way of monkeypatch/mocking, 1. Setup the mock 2. Inject mock into a callable
    #? 3. Set the object's attribute that we want mocked via monkeypatch w/ a callable that returns the mock
    mockResponse = MockHttpResponse(200)
    def mock_JSON(*args, **kwargs):
        return mockResponse
    monkeypatch.setattr(requests, "get", mock_JSON)
    updateAllTeamRecords() #* WHEN 200 status code BUT empty JSON dict used
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes

    mockResponse.jsonResponse = { 'records': [] }
    updateAllTeamRecords() #* WHEN 200 status code BUT empty records
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes

    with app.app_context():
        originalTeam, originalWins, originalLosses = checkTeamDefaultVals()
        #* WHEN a filled records list is used
        mockResponse.jsonResponse = standingsJSON
        updateAllTeamRecords()
        #* THEN any matching teams found will update their win-loss to the values in the JSON
        checkUpdatedWinLossRecord(originalTeam, originalWins, originalLosses)

def checkTeamDefaultVals():
    teams = db.session.scalars(db.select(BaseballTeam)).all()
    originalTeam = teams[0] if teams[0].fullName == 'Los Angeles Dodgers' else teams[1]
    wins, losses = originalTeam.wins, originalTeam.losses
    assert wins == 2
    assert losses == 1
    return (originalTeam, wins, losses)

def checkUpdatedWinLossRecord(originalTeam, originalWins, originalLosses):
    #* This `originalTeam` obj should have received the updated values
    updatedWins, updatedLosses = originalTeam.wins, originalTeam.losses
    assert originalWins != updatedWins #* Old values held onto their original values
    assert updatedWins == 123
    assert originalLosses != updatedLosses
    assert updatedLosses == 321

def test_updateEachDivision(app, divisionJSON):
    missingDivisionInfo = { } #* WHEN ALL division info is empty
    updateEachDivision(missingDivisionInfo)
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to DB

    missingDivisionID = { 'division': { } } #* WHEN the division info is empty
    updateEachDivision(missingDivisionID)
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to DB

    divisionWithoutTeams = { 'division': { 'id': 123 } }
    updateEachDivision(divisionWithoutTeams) #* WHEN the team record list isn't present
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to DB

    divisionEmptyTeamRecords = copy.deepcopy(divisionJSON)
    divisionEmptyTeamRecords['teamRecords'] = [] #* WHEN the team record list is empty
    updateEachDivision(divisionEmptyTeamRecords)
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to DB can occur

    with app.app_context():
        originalTeam, originalWins, originalLosses = checkTeamDefaultVals()
        #* WHEN divisions have filled team records
        updateEachDivision(divisionJSON)
        #* THEN any matching teams found will change to match the JSON win-loss
        checkUpdatedWinLossRecord(originalTeam, originalWins, originalLosses)

def test_updateTeamRecord(app, teamJSON):
    teamMissingInfo = { } #* WHEN team info is missing
    updateTeamRecord(teamMissingInfo)
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes

    teamMissingID = { 'team': { } } #* WHEN team info is missing the ID
    updateTeamRecord(teamMissingID)
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes

    #* WHEN team is missing info on wins or losses
    teamMissingWins = copy.deepcopy(teamJSON)
    teamMissingWins.pop('wins')
    teamMissingWins.pop('losses')
    updateTeamRecord(teamMissingWins)
    with app.app_context():
        checkTeamDefaultVals() #* THEN NO update to its win-loss record will happen
    #* WHEN team is missing info on losses
    teamMissingLosses = copy.deepcopy(teamJSON)
    teamMissingLosses.pop('losses')
    updateTeamRecord(teamMissingLosses)
    with app.app_context():
        checkTeamDefaultVals() #* THEN NO update to its win-loss record will happen

    with app.app_context():
        #* WHEN no team matching the name found in JSON found
        teamNotFoundByName = copy.deepcopy(teamJSON)
        teamNotFoundByName['team']['name'] = 'Foobar'
        with pytest.raises(exc.NoResultFound): #* THEN NoResultFound exception raised preventing any updates
            updateTeamRecord(teamNotFoundByName)

        originalTeam, originalWins, originalLosses = checkTeamDefaultVals()
        #* WHEN team with matching name found AND the JSON contains a win-loss record
        updateTeamRecord(teamJSON)
        #* THEN team found will update its win-loss columns in DB
        checkUpdatedWinLossRecord(originalTeam, originalWins, originalLosses)


#! Update Promotions funcs
def test_updateAllPromotions(app, monkeypatch, gameDbSetup, gameDatesJSON):
    #* WHEN http response returns 404 status code
    mockResponse = MockHttpResponse(404)
    def mock_JSON(*args, **kwargs):
        return mockResponse
    monkeypatch.setattr(requests, "get", mock_JSON)
    updateAllPromotions()
    with app.app_context(): #* THEN no changes to the promotions in the DB
        checkDefaultPromotions()

    #* WHEN status code is now 200 BUT JSON received is empty
    mockResponse.status_code = 200
    mockResponse.jsonResponse = { }
    updateAllPromotions()
    with app.app_context(): #* THEN no changes to the promotions in the DB
        checkDefaultPromotions()
        
    #* WHEN the dates received are empty
    mockResponse.jsonResponse = { 'dates': [] }
    updateAllPromotions()
    with app.app_context(): #* THEN no changes to the promotions in the DB
        checkDefaultPromotions()

    #* WHEN the gameDates contain no game info
    gamesDatesMissingGames = copy.deepcopy(gameDatesJSON)
    gamesDatesMissingGames['dates'] = [{}]
    mockResponse.jsonResponse = gamesDatesMissingGames
    updateAllPromotions()
    with app.app_context(): #* THEN no changes to the promotions in the DB
        checkDefaultPromotions()
    #* WHEN the games list on any given date is empty
    gameDatesWithEmptyGamesList = copy.deepcopy(gameDatesJSON)
    gameDatesWithEmptyGamesList['dates'][0]['games'] = []
    mockResponse.jsonResponse = gameDatesWithEmptyGamesList
    updateAllPromotions()
    with app.app_context(): #* THEN no changes to the promotions in the DB
        checkDefaultPromotions()

    #* WHEN the gameDatesJSON is correctly formatted and filled
    mockResponse.jsonResponse = gameDatesJSON
    with app.app_context():
        updateAllPromotions() #* THEN the game will receive an updated list of promotions
        checkUpdatedPromotions()

def test_updateEachGamesPromotions(app, gameDbSetup, gameJSON):
    #* WHEN the game JSON on any given date contains no info on the home team
    gameMissingTeamsInfo = { 'teams': { } }
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameMissingTeamsInfo)
        checkDefaultPromotions()
    #* WHEN the game JSON on any given date contains empty home team info
    gameMissingHomeTeamInfo = { 'teams': { 'home': { } } }
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameMissingHomeTeamInfo)
        checkDefaultPromotions()
    #* WHEN the game JSON on any given date is missing the team name
    gameMissingHomeTeamName = copy.deepcopy(gameJSON)
    gameMissingHomeTeamName['teams']['home']['team'] = { }
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameMissingHomeTeamName)
        checkDefaultPromotions()

    #* WHEN the game JSON being checked has a different home team then expected
    gameUnexpectedHomeTeam = copy.deepcopy(gameJSON)
    gameUnexpectedHomeTeam['teams']['home']['team']['name'] = 'Foobar Fizzes'
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameUnexpectedHomeTeam)
        checkDefaultPromotions()

    #* WHEN the game JSON being checked is missing the game date
    gameMissingDate = copy.deepcopy(gameJSON)
    gameMissingDate.pop('gameDate')
    with app.app_context(): #* THEN no changes to the promotions in the DB
        updateEachGamesPromotions(gameMissingDate)
        checkDefaultPromotions()

    #* WHEN game JSON's date DOESN'T match any game in the DB
    gameUnexpectedDate = copy.deepcopy(gameJSON)
    gameUnexpectedDate.pop('promotions')
    #* Technically promos can accidentally find the wrong game if the date was incorrect BUT seems unlikely w/ real data
    gameUnexpectedDate['gameDate'] = '2021-06-10T02:10:35Z'
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
        checkUpdatedPromotions() #* THEN promotions will remain exactly as they are (in this case as updated values)

    #* WHEN promotions in JSON are empty BUT the game's promotions in DB are filled
    with app.app_context():
        gameJSON['promotions'] = []
        updateEachGamesPromotions(gameJSON) #* THEN promotions will be deleted to match the JSON
        checkDefaultPromotions() #* SO the empty list in promos acts as a reset back to the default values of the Game

def checkDefaultPromotions():
    games = db.session.scalars(db.select(DodgerGame)).all()
    [assertEmpty(game.promos) for game in games]

def checkUpdatedPromotions():
    games = db.session.scalars(db.select(DodgerGame)).all()
    updatedGame = games[0] if games[0].home_team.fullName == 'Los Angeles Dodgers' else games[1]
    unchangedGame = games[1] if games[1].home_team.fullName == 'New York Yankees' else games[0]
    assert len(updatedGame.promos) == 1
    assert len(unchangedGame.promos) == 0
    assert updatedGame.promos[0].name == 'Hat'

def assertEmpty(someList):
    assert len(someList) == 0
