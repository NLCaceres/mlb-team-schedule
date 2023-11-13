from ...utility.mlb_api import (fetchThisYearsSchedule, fetchRemainingSchedule,
                                getScheduleTotals, scheduleDates, createEndpoint)
from ..common_assertions import assertIsNone
from ...utility.datetime_helpers import dateToday, dateToStr, YMD_FORMAT


def test_fetchThisYearsSchedule(app, monkeypatch):
    mockResponse = { }
    def mock_JSON(*args, **kwargs):
        return mockResponse
    #? Need to monkeypatch the imported fetch() func, NOT the api_helper module's original export
    monkeypatch.setattr("DodgersPromo.utility.mlb_api.fetch", mock_JSON)
    with app.app_context():
        #* WHEN the response is empty
        totalGames, teamGameDates, seasonStart = fetchThisYearsSchedule()
        #* THEN the totalGames and teamGameDates will be None
        assertIsNone(totalGames)
        assertIsNone(teamGameDates)
        #* BUT the start date will still be set to March 1st of THIS year
        expectedDate = f'{dateToday().year}-03-01'
        assert seasonStart == expectedDate

    with app.app_context():
        #* WHEN the response is filled
        mockResponse = { 'totalGames': 123, 'dates': [] }
        filledTotalGames, filledTeamGameDates, newSeasonStart = fetchThisYearsSchedule()
        #* THEN all values are properly assigned in a tuple
        assert filledTotalGames == 123
        assert filledTeamGameDates == []
        assert newSeasonStart == expectedDate #* This date won't change


def test_fetchRemainingSchedule(app, monkeypatch):
    mockResponse = { } #? Can use a lambda to inject this value via monkeypatch!
    #? Python Lambda's are just 1-line expressions, so placing a var in a lambda acts as an implicit return
    monkeypatch.setattr("DodgersPromo.utility.mlb_api.fetch", lambda x: mockResponse) #? `x` is required even though unused
    with app.app_context():
        #* WHEN the response is empty
        totalGames, teamGameDates, scheduleStartPoint = fetchRemainingSchedule()
        #* THEN the totalGames and teamGameDates will be None
        assertIsNone(totalGames)
        assertIsNone(teamGameDates)
        #* BUT the scheduleStartPoint will still be filled properly to today's date, i.e. YYYY-MM-DD
        expectedDate = dateToStr(dateToday(), YMD_FORMAT)
        assert scheduleStartPoint == expectedDate

    with app.app_context():
        #* WHEN the response is filled
        mockResponse = { 'totalGames': 123, 'dates': [] }
        filledTotalGames, filledTeamGameDates, newScheduleStartPoint = fetchRemainingSchedule()
        #* THEN all values are properly assigned in a tuple
        assert filledTotalGames == 123
        assert filledTeamGameDates == []
        assert newScheduleStartPoint == expectedDate #* This date won't change


def test_getScheduleTotals():
    #* WHEN the schedule JSON is empty
    totalGames, teamGameDates = getScheduleTotals({ })
    assertIsNone(totalGames) #* THEN the tuple returned is filled with 2 None values
    assertIsNone(teamGameDates)

    #* WHEN the schedule JSON is missing the game dates
    nextTotalGames, nextTeamGameDates = getScheduleTotals({ 'totalGames': 123 })
    assertIsNone(nextTotalGames) #* THEN the tuple returned is filled with 2 None values
    assertIsNone(nextTeamGameDates) #* It needs both the game dates and total game count to be filled

    #* WHEN the schedule JSON is missing the total game count
    thirdTotalGames, thirdTeamGameDates = getScheduleTotals({ 'dates': [] })
    assertIsNone(thirdTotalGames) #* THEN the tuple returned is filled with 2 None values
    assertIsNone(thirdTeamGameDates) #* It needs both the game dates and total game count to be filled

    #* WHEN the schedule JSON has both the total game count and list of game dates (even if empty)
    filledTotalGames, filledTeamGameDates = getScheduleTotals({ 'totalGames': 123, 'dates': [] })
    assert filledTotalGames == 123 #* THEN the tuple returned is filled with their respective key's values
    assert filledTeamGameDates == []


def test_scheduleDates():
    #* WHEN requesting this year's schedule dates w/out args to use their default values
    defaultStartDate, defaultEndDate, defaultThisYear = scheduleDates()
    todaysDate = dateToday()
    expectedYear = todaysDate.year
    expectedStart = f'{expectedYear}-03-01'
    expectedEnd = f'{expectedYear}-11-30'
    #* THEN the start date is March 1st of THIS year and end date is November 30 of the same year
    assert defaultStartDate == expectedStart
    assert defaultEndDate == expectedEnd
    assert defaultThisYear == expectedYear
    
    #* WHEN requesting this year's schedule dates by explicitly setting startingToday to False
    startDate, endDate, thisYear = scheduleDates(startingToday = False)
    #* THEN the start date is STILL March 1st of THIS year and end date is November 30 of the same year
    assert startDate == expectedStart
    assert endDate == expectedEnd
    assert thisYear == expectedYear

    #* WHEN requesting this year's schedule dates setting startingToday to True
    startingTodayDate, updatedEndDate, updatedThisYear = scheduleDates(startingToday = True)
    #* THEN the start date is today's date in YYYY-MM-DD format AND the end date is STILL November 30th of this year
    assert startingTodayDate == dateToStr(dateToday(), YMD_FORMAT)
    assert updatedEndDate == expectedEnd
    assert updatedThisYear == expectedYear


def test_createEndpoint(app):
    with app.app_context():
        #* WHEN any of the date values are missing
        endpointMissingAllValues = createEndpoint(startDate = None, endDate = None, seasonYear = None, teamId = None)
        #* THEN None is returned
        assertIsNone(endpointMissingAllValues)
        endpointWithOnlyStartDate = createEndpoint(startDate = '2021-03-01', endDate = None, seasonYear = None, teamId = None)
        assertIsNone(endpointWithOnlyStartDate)
        endpointWithOnlyEndDate = createEndpoint(startDate = None, endDate = '2021-11-01', seasonYear = None, teamId = None)
        assertIsNone(endpointWithOnlyEndDate)
        endpointWithOnlyYear = createEndpoint(startDate = None, endDate = None, seasonYear = '2021', teamId = None)
        assertIsNone(endpointWithOnlyYear)

        #* WHEN no date values are provided
        endpointMissingDateValues = createEndpoint(teamId = None)
        #* THEN the default None value is used for each, resulting in None being returned
        assertIsNone(endpointMissingDateValues)

        #* WHEN the date values are filled
        endpointWithDefaultTeam = createEndpoint('2021-03-01', '2021-11-30', '2021')
        #* THEN the endpoint will be filled with those values AND a default team ID of 119
        expectedEndpointWithDefaultTeam = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                                           ',game(promotions)&season=2021&startDate=2021-03-01&endDate=2021-11-30'
                                           '&teamId=119&gameType=R&scheduleTypes=games')
        assert endpointWithDefaultTeam == expectedEndpointWithDefaultTeam

        #* WHEN the teamID env var is filled incorrectly
        app.config['TEAM_FULL_NAME'] = 'chiicagoo Cubs'
        endpointWithMisspelledTeam = createEndpoint('2021-03-01', '2021-11-30', '2021')
        #* THEN the endpoint will be filled with those values AND a default team ID of 119
        expectedEndpointStillWithDefaultTeam = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                                                ',game(promotions)&season=2021&startDate=2021-03-01&endDate=2021-11-30'
                                                '&teamId=119&gameType=R&scheduleTypes=games')
        assert endpointWithMisspelledTeam == expectedEndpointStillWithDefaultTeam

        #* WHEN the teamID env var is filled properly
        app.config['TEAM_FULL_NAME'] = 'Chicago Cubs'
        endpointWithOtherTeam = createEndpoint('2021-03-01', '2021-11-30', '2021')
        #* THEN the endpoint will be filled with those values AND the team's expected ID
        expectedEndpointWithOtherTeam = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                                         ',game(promotions)&season=2021&startDate=2021-03-01&endDate=2021-11-30'
                                         '&teamId=112&gameType=R&scheduleTypes=games')
        assert endpointWithOtherTeam == expectedEndpointWithOtherTeam

        #* WHEN all args are filled
        normalEndpointWithID = createEndpoint('2021-03-01', '2021-11-30', '2021', 123)
        #* THEN the endpoint will be filled using ALL input arg values, even if team ID env var is filled
        normalExpectedEndpointWithID = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                                        ',game(promotions)&season=2021&startDate=2021-03-01&endDate=2021-11-30'
                                        '&teamId=123&gameType=R&scheduleTypes=games')
        assert normalEndpointWithID == normalExpectedEndpointWithID

        #* WHEN the dates are input BUT poorly formatted
        app.config['TEAM_FULL_NAME'] = 'Los Angeles Dodgers' #* Reset to default for simplicity sake
        endpointWithUnformattedDateVals = createEndpoint(startDate = '03-01-2021', endDate = '11-30-2020', 
                                                        seasonYear = 1234, teamId = None)
        #* THEN the poorly formatted values will be injected regardless
        poorlyFormattedEndpoint = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                                ',game(promotions)&season=1234&startDate=03-01-2021&endDate=11-30-2020'
                                '&teamId=119&gameType=R&scheduleTypes=games')
        assert endpointWithUnformattedDateVals == poorlyFormattedEndpoint

        #* WHEN all values are input BUT poorly formatted
        endpointWithUnformattedVals = createEndpoint(startDate = '03-01-2021', endDate = '11-30-2020', 
                                                    seasonYear = 1234, teamId = 'some_id')
        #* THEN the poorly formatted values will be injected regardless
        completelyPoorlyFormattedEndpoint = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                                            ',game(promotions)&season=1234&startDate=03-01-2021&endDate=11-30-2020'
                                            '&teamId=some_id&gameType=R&scheduleTypes=games')
        assert endpointWithUnformattedVals == completelyPoorlyFormattedEndpoint
