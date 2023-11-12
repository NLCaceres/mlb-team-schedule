from flask import current_app as app


#* A slightly more dynamic approach would be using the team's full name to query the DB
#* for a matching BaseballTeam obj, then returning the found Team's ID
#* BUT given only 30 baseball teams, a dictionary lookup is faster. 
#* If I was doing every pro league instead, then the DB query would be the better option
TEAM_TO_ID_MAP = {
    'los angeles angels': 108,
    'arizona diamondbacks': 109,
    'baltimore orioles': 110,
    'boston red sox': 111,
    'chicago cubs': 112,
    'cincinnati reds': 113,
    'cleveland guardians': 114,
    'colorado rockies': 115,
    'detroit tigers': 116,
    'houston astros': 117,
    'kansas city royals': 118,
    'los angeles dodgers': 119,
    'washington nationals': 120,
    'new york mets': 121,
    'oakland athletics': 133,
    'pittsburgh pirates': 134,
    'san diego padres': 135,
    'seattle mariners': 136,
    'san francisco giants': 137,
    'st. louis cardinals': 138,
    'tampa bay rays': 139,
    'texas rangers': 140,
    'toronto blue jays': 141,
    'minnesota twins': 142,
    'philadelphia phillies': 143,
    'atlanta braves': 144,
    'chicago white sox': 145,
    'miami marlins': 146,
    'new york yankees': 147,
    'milwaukee brewers': 158,
}


#* Using get() ensures None is returned if improper team set
#todo BUT maybe better to allow the KeyError to immediately be raised in case user misspells team?
#* SINCE alt issue of not setting team is handled by defaulting to Los Angeles Dodgers with guaranteed correct spelling
def getTeamIdFromName(name: str):
    return TEAM_TO_ID_MAP.get(name.lower())


#* get() the Flask Config's team full name env var, which defaults to 'Los Angeles Dodgers'
#* SO this return CAN fallback to 119 if no team full name env var provided 
#* OR return None in the case of a misspelled or unknown team name env var
def getTeamID():
    return getTeamIdFromName(app.config.get('TEAM_FULL_NAME'))
