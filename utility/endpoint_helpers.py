
#! Constants
#? https://bit.ly/2XbrNVn - URL to Github MLB-stats python-based wrapper
#? Changing teamId in this URL changes homeTeam to desired one
SCHEDULE_ENDPOINT = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team' #? Concatenated on compile
                    ',game(promotions)&season={seasonYear}&startDate={startDate}&endDate={endDate}' 
                    '&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games')
#? This URL grabs the latest game so it can be useful for grabbing a Team's win-loss record
LATEST_GAME_URL = 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&teamId={espnID}'
#TODO Double check above seemingly grabs latest game even if day has past, and even if actual current day is an off day

#? More examples of various endpoints
ALL_GAMES_OF_THE_DAY_URL = 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1' #? Grabs all games of the day
ALL_MLB_TEAMS_URL = 'https://statsapi.mlb.com/api/v1/teams?lang=en&sportId=1' #? Grabs all teams
#? Grabs all National League teams -> 203 - 205 NL West, East, Central with Records
NL_TEAMS_URL = 'https://statsapi.mlb.com/api/v1/standings?leagueId=104'
#? Grabs all American League teams -> 200 - 202 AL West, East, Central with Records
AL_TEAMS_URL = 'https://statsapi.mlb.com/api/v1/standings?leagueId=103'
#? Grabs BOTH the NL and AL in a group of 6 items (0-5) listing off teams in Standings Order
LEAGUE_STANDINGS_URL = 'https://statsapi.mlb.com/api/v1/standings?leagueId=103&leagueId=104'
#? This URL helps for grabbing info on certain meta/key/urlParam types - https://bit.ly/3CLOyjl known types
META_KEYS_URL = 'https://statsapi.mlb.com/api/v1/gameTypes'
#* This particular meta_key url grabs info on gameTypes, notably:
  #* 'F' = 'Wild Card', 'D' = 'Division Series', 'L' = 'League Series', 'W' = 'World Series', and 'A' = 'All Star Game'
ALL_STAR_GAME_URL = 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&season=2023&gameType=A'
#? Seems as of 2023, there isn't any way of getting Playoff dates until the teams are finalized in late September
#? Additionally, as of 2023, the World Series Game 7 CAN possibly occur as late as November 4th
#* A good possible URL for the playoffs would be 'https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&season=2023&gameType=P'

#? Following is a concrete example that grabs all Dodgers games in 2023
# https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team,game(promotions)&season=2023&startDate=2023-03-01&endDate=2023-10-31&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games
DODGER_GAMES_2023_URL = ('https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team'
                        ',game(promotions)&season=2023&startDate=2023-03-01&endDate=2023-10-31'
                        '&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games')

BASE_MLB_LOGO_URL = 'https://www.mlbstatic.com/team-logos/{espnID}.svg'