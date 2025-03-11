from ..common_assertions import assertIsNone
from mlb_team_schedule.utility.datetime_helpers import YMD_FORMAT, dateToday, dateToStr
from mlb_team_schedule.utility.mlb_api import (
    createEndpoint, fetchRemainingSchedule, fetchThisYearsSchedule,
    getScheduleTotals, scheduleDates,
)


def test_fetchThisYearsSchedule(app, monkeypatch):
    mockResponse = { }
    def mock_JSON(*args, **kwargs):
        return mockResponse
    #? MUST monkeypatch imported `fetch()`, NOT the api_helper module's original export
    monkeypatch.setattr("mlb_team_schedule.utility.mlb_api.fetch", mock_JSON)
    with app.app_context():
        #* WHEN the response is empty
        totalGames, teamGameDates, seasonStart = fetchThisYearsSchedule()
        #* THEN the totalGames and teamGameDates will be None
        assertIsNone(totalGames)
        assertIsNone(teamGameDates)
        #* BUT the start date will still be set to March 1st of THIS year
        expectedDate = f"{dateToday().year}-03-01"
        assert seasonStart == expectedDate

    with app.app_context():
        #* WHEN the response is filled
        mockResponse = { "totalGames": 123, "dates": [] }
        totalGames, teamGameDates, seasonStart = fetchThisYearsSchedule()
        #* THEN all values are properly assigned in a tuple
        assert totalGames == 123
        assert teamGameDates == []
        assert seasonStart == expectedDate #* This date won't change


def test_fetchRemainingSchedule(app, monkeypatch):
    mockResponse = { } #? Can use a lambda to inject this value via monkeypatch!
    #? Python Lambdas are 1-line expressions that can implicitly return referenced vars
    #? Lambdas also typically accepts args, and the following one NEEDS it to pass test
    monkeypatch.setattr("mlb_team_schedule.utility.mlb_api.fetch", lambda _: mockResponse)
    with app.app_context():
        #* WHEN the response is empty
        totalGames, teamGameDates, scheduleStartPoint = fetchRemainingSchedule()
        #* THEN the totalGames and teamGameDates will be None
        assertIsNone(totalGames)
        assertIsNone(teamGameDates)
        #* BUT scheduleStartPoint still is filled correctly to today's date as YYYY-MM-DD
        expectedDate = dateToStr(dateToday(), YMD_FORMAT)
        assert scheduleStartPoint == expectedDate

    with app.app_context():
        #* WHEN the response is filled
        mockResponse = { "totalGames": 123, "dates": [] }
        totalGames, teamGameDates, scheduleStartPoint = fetchRemainingSchedule()
        #* THEN all values are properly assigned in a tuple
        assert totalGames == 123
        assert teamGameDates == []
        assert scheduleStartPoint == expectedDate #* This date won't change


def test_getScheduleTotals():
    #* WHEN the schedule JSON is empty
    totalGames, teamGameDates = getScheduleTotals({ })
    assertIsNone(totalGames) #* THEN the tuple returned is filled with 2 None values
    assertIsNone(teamGameDates)

    #* WHEN the schedule JSON is missing the game dates
    nextTotalGames, nextTeamGameDates = getScheduleTotals({ "totalGames": 123 })
    assertIsNone(nextTotalGames) #* THEN the tuple returned is filled with 2 None values
    assertIsNone(nextTeamGameDates) #* MUST fill both game dates & total game count

    #* WHEN the schedule JSON is missing the total game count
    thirdTotalGames, thirdTeamGameDates = getScheduleTotals({ "dates": [] })
    assertIsNone(thirdTotalGames) #* THEN the tuple returned is filled with 2 None values
    assertIsNone(thirdTeamGameDates) #* MUST fill both game dates & total game count

    #* WHEN the schedule JSON has BOTH total game count & game date list (even if empty)
    totalGames, teamGameDates = getScheduleTotals({ "totalGames": 123, "dates": [] })
    assert totalGames == 123 #* THEN fills returned tuple with respective k-v pairs
    assert teamGameDates == []


def test_scheduleDates():
    #* WHEN requesting this year's schedule dates w/out args to use their default values
    defaultStartDate, defaultEndDate, defaultThisYear = scheduleDates()
    todaysDate = dateToday()
    expectedYear = todaysDate.year
    expectedStart = f"{expectedYear}-03-01"
    expectedEnd = f"{expectedYear}-11-30"
    #* THEN start date is March 1st THIS year & end date is Nov 30 THIS year
    assert defaultStartDate == expectedStart
    assert defaultEndDate == expectedEnd
    assert defaultThisYear == expectedYear

    #* WHEN requesting this year's dates by setting startingToday to False
    startDate, endDate, thisYear = scheduleDates(startingToday = False)
    #* THEN start date is STILL March 1st THIS year & end date is Nov 30 THIS year
    assert startDate == expectedStart
    assert endDate == expectedEnd
    assert thisYear == expectedYear

    #* WHEN requesting this year's schedule dates setting startingToday to True
    startingTodayDate, setEndDate, setThisYear = scheduleDates(startingToday = True)
    #* THEN start date is today's date as YYYY-MM-DD & end date is STILL Nov 30 THIS year
    assert startingTodayDate == dateToStr(dateToday(), YMD_FORMAT)
    assert setEndDate == expectedEnd
    assert setThisYear == expectedYear


def test_createEndpoint(app):
    with app.app_context():
        #* WHEN any of the date values are missing
        endpointMissingAllValues = createEndpoint(startDate = None, endDate = None,
                                                  seasonYear = None, teamId = None)
        #* THEN None is returned
        assertIsNone(endpointMissingAllValues)
        endpointFromStartDate = createEndpoint(startDate = "2021-03-01", endDate = None,
                                               seasonYear = None, teamId = None)
        assertIsNone(endpointFromStartDate)
        endpointFromEndDate = createEndpoint(startDate = None, endDate = "2021-11-01",
                                             seasonYear = None, teamId = None)
        assertIsNone(endpointFromEndDate)
        endpointFromYear = createEndpoint(startDate = None, endDate = None,
                                          seasonYear = "2021", teamId = None)
        assertIsNone(endpointFromYear)

        #* WHEN no date values are provided
        endpointMissingDateValues = createEndpoint(teamId = None)
        #* THEN the default None value is used for each, resulting in None being returned
        assertIsNone(endpointMissingDateValues)

        #* WHEN the date values are filled
        endpointWithDefaultTeam = createEndpoint("2021-03-01", "2021-11-30", "2021")
        #* THEN the endpoint will be filled with those values AND a default team ID of 119
        expectedEndpointWithDefaultTeam = ("https://statsapi.mlb.com/api/v1/schedule?lang=en"
                                           "&sportId=1&hydrate=team,game(promotions)"
                                           "&season=2021&startDate=2021-03-01&endDate=2021-11-30"
                                           "&teamId=119&gameType=R&scheduleTypes=games")
        assert endpointWithDefaultTeam == expectedEndpointWithDefaultTeam

        #* WHEN the teamID env var is filled incorrectly
        app.config["TEAM_FULL_NAME"] = "chiicagoo Cubs"
        endpointWithMisspelledTeam = createEndpoint("2021-03-01", "2021-11-30", "2021")
        #* THEN the endpoint will be filled with those values AND a default team ID of 119
        expectedEndpointStillWithDefaultTeam = ("https://statsapi.mlb.com/api/v1/schedule"
                                                "?lang=en&sportId=1&hydrate=team"
                                                ",game(promotions)&season=2021"
                                                "&startDate=2021-03-01&endDate=2021-11-30"
                                                "&teamId=119&gameType=R&scheduleTypes=games")
        assert endpointWithMisspelledTeam == expectedEndpointStillWithDefaultTeam

        #* WHEN the teamID env var is filled properly
        app.config["TEAM_FULL_NAME"] = "Chicago Cubs"
        endpointWithOtherTeam = createEndpoint("2021-03-01", "2021-11-30", "2021")
        #* THEN the endpoint will be filled with those values AND the team's expected ID
        expectedEndpointWithOtherTeam = ("https://statsapi.mlb.com/api/v1/schedule?lang=en"
                                         "&sportId=1&hydrate=team,game(promotions)&season=2021"
                                         "&startDate=2021-03-01&endDate=2021-11-30"
                                         "&teamId=112&gameType=R&scheduleTypes=games")
        assert endpointWithOtherTeam == expectedEndpointWithOtherTeam

        #* WHEN all args are filled
        normalEndpointWithID = createEndpoint("2021-03-01", "2021-11-30", "2021", 123)
        #* THEN endpoint filled using ALL arg values, even if TEAM_ID env var filled
        normalExpectedEndpointWithID = ("https://statsapi.mlb.com/api/v1/schedule?lang=en"
                                        "&sportId=1&hydrate=team,game(promotions)&season=2021"
                                        "&startDate=2021-03-01&endDate=2021-11-30"
                                        "&teamId=123&gameType=R&scheduleTypes=games")
        assert normalEndpointWithID == normalExpectedEndpointWithID

        #* WHEN the dates are input BUT poorly formatted
        app.config["TEAM_FULL_NAME"] = "Los Angeles Dodgers" #* Reset to default
        endpointWithUnformattedDateVals = createEndpoint(startDate = "03-01-2021",
                                                         endDate = "11-30-2020",
                                                         seasonYear = 1234, teamId = None)
        #* THEN the poorly formatted values will be injected regardless
        poorlyFormattedEndpoint = ("https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1"
                                   "&hydrate=team,game(promotions)&season=1234"
                                   "&startDate=03-01-2021&endDate=11-30-2020"
                                   "&teamId=119&gameType=R&scheduleTypes=games")
        assert endpointWithUnformattedDateVals == poorlyFormattedEndpoint

        #* WHEN all values are input BUT poorly formatted
        endpointWithUnformattedVals = createEndpoint(startDate = "03-01-2021",
                                                     endDate = "11-30-2020",
                                                     seasonYear = 1234, teamId = "someId")
        #* THEN the poorly formatted values will be injected regardless
        completelyPoorlyFormattedEndpoint = ("https://statsapi.mlb.com/api/v1/schedule?lang=en"
                                             "&sportId=1&hydrate=team,game(promotions)"
                                             "&season=1234&startDate=03-01-2021&endDate=11-30-2020"
                                             "&teamId=someId&gameType=R&scheduleTypes=games")
        assert endpointWithUnformattedVals == completelyPoorlyFormattedEndpoint
