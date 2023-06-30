
#! Constants
#? https://bit.ly/2XbrNVn - URL to Github MLB-stats python-based wrapper
#? Changing teamId in this URL changes homeTeam to desired one
SCHEDULE_ENDPOINT = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team' #? Concatenated on compile
                    ',game(promotions)&season={seasonYear}&startDate={startDate}&endDate={endDate}' 
                    '&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games')
#? This URL grabs the latest game so it can be useful for grabbing a Team's win-loss record
LATEST_GAME_URL = 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&teamId={espnID}'

#? More examples of various endpoints
ALL_GAMES_OF_THE_DAY_URL = 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1' #? Grabs all games of the day
ALL_MLB_TEAMS_URL = 'https://statsapi.mlb.com/api/v1/teams?lang=en&sportId=1' #? Grabs all teams
#? Grabs all National League teams -> 203 - 205 NL West, East, Central
NL_TEAMS_URL = 'https://statsapi.mlb.com/api/v1/standings?leagueId=104'
#? Grabs all American League teams -> 200 - 202 AL West, East, Central
AL_TEAMS_URL = 'https://statsapi.mlb.com/api/v1/standings?leagueId=103'
#? This URL helps for grabbing info on certain meta/key/urlParam types - https://bit.ly/3CLOyjl known types
META_KEYS_URL = 'https://statsapi.mlb.com/api/v1/gameTypes'

#? Following is a concrete example that grabs all Dodgers games in 2023
DODGER_GAMES_2023_URL = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                        ',game(promotions)&season=2023&startDate=2023-03-01&endDate=2023-10-31'
                        '&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games')

BASE_MLB_LOGO_URL = 'https://www.mlbstatic.com/team-logos/{espnID}.svg'