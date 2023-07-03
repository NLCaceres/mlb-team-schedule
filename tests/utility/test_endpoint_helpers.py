import pytest
from DodgersPromo.utility.endpoint_helpers import SCHEDULE_ENDPOINT, LATEST_GAME_URL, BASE_MLB_LOGO_URL

def test_format_schedule_endpoint():
    #? If the endpoint is used without a format() call, then the string KEEPS the placeholders
    assert SCHEDULE_ENDPOINT == ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                                 ',game(promotions)&season={seasonYear}&startDate={startDate}&endDate={endDate}'
                                 '&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games')
    
    #* Using format() without the keyname (i.e. seasonYear) throws an Exception
    with pytest.raises(KeyError):
        SCHEDULE_ENDPOINT.format(123)

    #* Omitting any of the other keynames also causes an Exception
    with pytest.raises(KeyError):
        SCHEDULE_ENDPOINT.format(seasonYear = 123)

    filled_schedule_endpoint = SCHEDULE_ENDPOINT.format(seasonYear = 123, startDate = 'Y-M-D', endDate = 'y-m-d')
    assert filled_schedule_endpoint == ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                                             ',game(promotions)&season=123&startDate=Y-M-D&endDate=y-m-d'
                                             '&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games')

def test_format_latest_game_url():
    assert LATEST_GAME_URL == 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&teamId={espnID}'

    filled_latest_game_url = LATEST_GAME_URL.format(espnID = '123')
    assert filled_latest_game_url == 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&teamId=123'

def test_format_base_mlb_logo_url():
    assert BASE_MLB_LOGO_URL == 'https://www.mlbstatic.com/team-logos/{espnID}.svg'

    filled_mlb_logo_url = BASE_MLB_LOGO_URL.format(espnID = '456')
    assert filled_mlb_logo_url == 'https://www.mlbstatic.com/team-logos/456.svg'
