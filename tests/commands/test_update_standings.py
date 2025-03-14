from ..MockHttpResponse import MockHttpResponse
from mlb_team_schedule import db
from mlb_team_schedule.commands.update_standings import (
    updateAllTeamRecords,
    updateEachDivision,
    updateTeamRecord,
)
from mlb_team_schedule.models import BaseballTeam
from mlb_team_schedule.utility.api_helpers import ClientErrorStatusCodeException
from mlb_team_schedule.utility.database_helpers import saveToDb

import pytest
import requests
import copy


#! Fixtures
@pytest.fixture(autouse=True)
def teamDbSetup(app):
    team1 = BaseballTeam(team_name="Dodgers", city_name="Los Angeles", team_logo="Foo",
                         abbreviation="LAD", wins=2, losses=1)
    team2 = BaseballTeam(team_name="Yankees", city_name="New York", team_logo="Bar",
                         abbreviation="NYY", wins=1, losses=2)

    with app.app_context():
        saveToDb(team1)
        saveToDb(team2)
        assert len(db.session.scalars(db.select(BaseballTeam)).all()) == 2

@pytest.fixture
def standingsJSON(divisionJSON):
    #? Python seems to hoist so this `divisionJSON` fixture CAN be declared later
    return { "records": [divisionJSON] }

@pytest.fixture
def divisionJSON(teamJSON):
    return { "division": { "id": 123 }, "teamRecords": [teamJSON] }

@pytest.fixture
def teamJSON():
    return {
        "team": { "id": 123, "name": "Los Angeles Dodgers" },
        "wins": 123, "losses": 321
    }


#! Tests
def test_updateAllTeamRecords(app, monkeypatch, mock_404_response, standingsJSON):
    with pytest.raises(ClientErrorStatusCodeException):
        updateAllTeamRecords() #? mock_404_response monkeypatched in by fixture
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to the DB happen

    #? Inline way of monkeypatch/mocking, 1. Setup mock 2. Inject mock into a callable
    #? 3. Set obj attribute that needs mocking via monkeypatch callable returning the mock
    mockResponse = MockHttpResponse(200)
    def mock_JSON(*args, **kwargs):
        return mockResponse
    monkeypatch.setattr(requests, "get", mock_JSON)
    updateAllTeamRecords() #* WHEN 200 status code BUT empty JSON dict used
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes

    mockResponse.jsonResponse = { "records": [] }
    updateAllTeamRecords() #* WHEN 200 status code BUT empty records
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes

    with app.app_context():
        originalTeam, originalWins, originalLosses = checkTeamDefaultVals()
        #* WHEN a filled records list is used
        mockResponse.jsonResponse = standingsJSON
        updateAllTeamRecords()
        #* THEN matching teams found update their win-loss to the JSON values
        checkUpdatedWinLossRecord(originalTeam, originalWins, originalLosses)


def test_updateEachDivision(app, divisionJSON):
    missingDivisionInfo = { } #* WHEN ALL division info is empty
    updateEachDivision(missingDivisionInfo)
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to DB

    missingDivisionID = { "division": { } } #* WHEN the division info is empty
    updateEachDivision(missingDivisionID)
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to DB

    divisionWithoutTeams = { "division": { "id": 123 } }
    updateEachDivision(divisionWithoutTeams) #* WHEN the team record list isn't present
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes to DB

    divisionEmptyTeamRecords = copy.deepcopy(divisionJSON)
    divisionEmptyTeamRecords["teamRecords"] = [] #* WHEN the team record list is empty
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

    teamMissingName = { "team": { } } #* WHEN team info is missing its name
    updateTeamRecord(teamMissingName)
    with app.app_context():
        checkTeamDefaultVals() #* THEN no changes

    #* WHEN team is missing info on wins or losses
    teamMissingWins = copy.deepcopy(teamJSON)
    teamMissingWins.pop("wins")
    teamMissingWins.pop("losses")
    updateTeamRecord(teamMissingWins)
    with app.app_context():
        checkTeamDefaultVals() #* THEN NO update to its win-loss record will happen
    #* WHEN team is missing info on losses
    teamMissingLosses = copy.deepcopy(teamJSON)
    teamMissingLosses.pop("losses")
    updateTeamRecord(teamMissingLosses)
    with app.app_context():
        checkTeamDefaultVals() #* THEN NO update to its win-loss record will happen

    with app.app_context():
        #* WHEN no team matching the name found in JSON found
        teamNotFoundByName = copy.deepcopy(teamJSON)
        teamNotFoundByName["team"]["name"] = "Foobar"
        #* THEN no DB changes, so the upcoming checkTeamDefaultValues() works fine
        updateTeamRecord(teamNotFoundByName)

        originalTeam, originalWins, originalLosses = checkTeamDefaultVals()
        #* WHEN team with matching name found AND the JSON contains a win-loss record
        updateTeamRecord(teamJSON)
        #* THEN team found will update its win-loss columns in DB
        checkUpdatedWinLossRecord(originalTeam, originalWins, originalLosses)

        #* Interesting edge case if wins & losses == 0 (like in the beginning of a season)
        teamJSON["wins"], teamJSON["losses"] = 0, 0
        updateTeamRecord(teamJSON)
        #* BEFORE: No wins or losses key found, so default val of 0 causes early return
        #* NOW Default is None, so team CAN begin season with expected 0-0 win-loss record
        assert originalTeam.wins == 0
        assert originalTeam.losses == 0


#! Assertion Methods
def checkTeamDefaultVals():
    teams = db.session.scalars(db.select(BaseballTeam)).all()
    originalTeam = teams[0] if teams[0].fullName == "Los Angeles Dodgers" else teams[1]
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
