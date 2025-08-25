# Contains all 3rd-party API endpoints used by this Flask backend
#! Main MLB-Stats API Constants
#? https://github.com/toddrob99/MLB-StatsAPI/wiki - For info on the MLB-Stats API

#? The following URL = regular season schedule for a given team via injected team_ID
SCHEDULE_ENDPOINT = ("https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team"
                    ",game(promotions)&season={seasonYear}&startDate={startDate}&endDate={endDate}"
                    "&teamId={teamId}&gameType=R&scheduleTypes=games")
#? The following URL grabs latest game (useful to grab a team's win-loss record)
LATEST_GAME_URL = "https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&teamId={espnID}"
#? Above URL grabs the most recent game up until 6-8AM PST the next day
#? BUT on off-days, by 8AM the last game will disappear, and no games will be returned


#? Helpful URL to grab info on known meta/key/urlParam types - https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-meta
GAME_TYPE_META_KEYS_URL = "https://statsapi.mlb.com/api/v1/gameTypes"
# Meta Tag Definition: 'S' = 'Spring Training Game'
SPRING_TRAINING_URL = "https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&season={seasonYear}&teamId={teamId}&gameType=S"
# Meta Tag Definition: 'A' = 'All Star Game'
ALL_STAR_GAME_URL = "https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&season={seasonYear}&gameType=A"
# Meta Tag Definitions: 'F' = 'Wild Card', 'D' = 'Division Series', 'L' = 'League Series'
# 'W' = 'World Series', 'P' = 'Playoff' BUT possible a legacy/unused meta-tag
#? As of 2025, Playoff dates aren't available until the 2nd half of the season
#? With the playoffs POSSIBLY lasting until a November 4th (in 2023) World Series Game 7
PLAYOFFS_URL = "https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&season={seasonYear}&gameType=F,D,L,W"


#! More useful endpoints constants
#? Insert the team's ID into this URL to grab their logo as an SVG
BASE_MLB_LOGO_URL = "https://www.mlbstatic.com/team-logos/{espnID}.svg"
#? Grabs all games of the day
ALL_GAMES_OF_THE_DAY_URL = "https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1"
#? Grabs all teams
ALL_MLB_TEAMS_URL = "https://statsapi.mlb.com/api/v1/teams?lang=en&sportId=1"
#? Grabs all National League teams -> 203 - 205 NL West, East, Central with Records
NL_TEAMS_URL = "https://statsapi.mlb.com/api/v1/standings?leagueId=104"
#? Grabs all American League teams -> 200 - 202 AL West, East, Central with Records
AL_TEAMS_URL = "https://statsapi.mlb.com/api/v1/standings?leagueId=103"
#? Grabs BOTH the NL + AL in a group of 6 items (0-5) listing off teams in Standings Order
LEAGUE_STANDINGS_URL = "https://statsapi.mlb.com/api/v1/standings?leagueId=103&leagueId=104"


#? Following is a concrete example that grabs all Dodgers games in 2023
# https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team,game(promotions)&season=2023&startDate=2023-03-01&endDate=2023-10-31&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games
DODGER_GAMES_2023_URL = ("https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&hydrate=team"
                        ",game(promotions)&season=2023&startDate=2023-03-01&endDate=2023-10-31"
                        "&teamId=119&gameType=R,F,D,L,W&scheduleTypes=games")

