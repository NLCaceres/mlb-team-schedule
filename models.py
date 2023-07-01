from datetime import timedelta
from sqlalchemy.ext.hybrid import hybrid_property
from . import db

#? With particularly small projects, this can be kept in the main app file
#? BUT when separating models into own file, you'd end up with a circular import and crash!
# db = SQLAlchemy()

class DodgerGame(db.Model):
    __tablename__ = 'dodger_games' #? Without override, tablename = 'dodger_game'

    #* JsonKeyBase = dates.games.
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False) #* Json key = 'gameDate', format: 2021-07-05T22:40:00Z
    gameNumInSeries = db.Column(db.Integer, nullable=False) #* Json key = 'seriesGameNumber', e.g. Game # 2 of 3
    gamesInSeries = db.Column(db.Integer, nullable=False) #* Json key = 'gamesInSeries', e.g. 3 games in series

    #? When setting foreign key, @param = 'tablename.columnkey'
    home_team_id = db.Column(db.Integer, db.ForeignKey('baseball_teams.id'), nullable=False) #* Always dodgers?
    away_team_id = db.Column(db.Integer, db.ForeignKey('baseball_teams.id'), nullable=False)

    #? 1 to 1 relationship, uselist = False prevents unnecessary list usage/creation
    promos = db.relationship('Promo', backref="game", lazy=True)

    @hybrid_property
    def readableDateTime(self): #* Used to query/filter specific rows by date
        return self.date - timedelta(hours=7) 

    @hybrid_property
    def readableDate(self): #* timedelta hours = 7 since that's PDT offset from utc
        return (self.date - timedelta(hours=7)).strftime("%a %B %d %Y at %I:%M %p")

    @hybrid_property
    def asDict(self):
        return { 'id': self.id, 'date': self.readableDate, 'gameNumInSeries': self.gameNumInSeries, 'gamesInSeries': self.gamesInSeries,
            'homeTeam': self.home_team.asDict, 'awayTeam': self.away_team.asDict,
            'promos': [promotion.asDict for promotion in self.promos]}
        

    #? No Init needed (can be overridden if needed but otherwise allow sqlAlchemy to handle it)

    def __repr__(self): #? String representation on queries
        return '<DodgerGame id {} on {}>'.format(self.id, self.readableDate) #? Bit of an older way to embed vars before f-strings

    def __eq__(self, other): #? Could also override __hash__ but only needed if expected to use sets
        if isinstance(other, DodgerGame):
            idCheck = self.id == other.id 
            dateTeamsCheck = self.date == other.date and self.home_team_id == other.home_team_id and self.away_team_id == other.away_team_id
            return idCheck or dateTeamsCheck
        return False

class BaseballTeam(db.Model):
    __tablename__ = 'baseball_teams'

    #* JsonKeyBase = dates.games.teams.home.    
    id = db.Column(db.Integer, primary_key=True)
    team_logo = db.Column(db.String(), unique=True, nullable=False) #* JsonKey = team.id -> f"https://www.mlbstatic.com/team-logos/{espnID}.svg" #* NOT this db's ID
    #* JsonKey = team.clubName -> Dodgers #? ClubName gives full name instead of teamName 
    team_name = db.Column(db.String(), unique=True, nullable=False) #* -> Diamondbacks vs D-Backs
    #* JsonKey = team.franchiseName -> Los Angeles #? FranchiseName gives proper location rather than actual city
    city_name = db.Column(db.String(), nullable=False) #* -> Colorado Rockies vs Denver Rockies
    abbreviation = db.Column(db.String(), unique=True, nullable=False) #* JsonKey = team.abbreviation -> LAD
    wins = db.Column(db.Integer, nullable=False) #* JsonKey = leagueRecord.wins
    losses = db.Column(db.Integer, nullable=False) #* JsonKey = leagueRecord.losses

    #? Relationship() defines a hasA/hasMany convenience property.
    #? Backref creates the inverse prop/relation in DodgerGame class (no back_populate needed - normally placed in both classes)
    homeGames = db.relationship('DodgerGame', backref='home_team', lazy=True, foreign_keys='DodgerGame.home_team_id') #? 'lazy' loads relationship on 1st request, synonym for setting it as 'select'
    awayGames = db.relationship('DodgerGame', backref='away_team', lazy=True, foreign_keys='DodgerGame.away_team_id') #? Goal: Consolidate games BUT until then, this simplifies the table joins

    @hybrid_property #? Hybrid props are SqlAlchemy's equivalent of computed properties (or virtuals from mongo!)
    def fullName(self):
        return f'{self.city_name} {self.team_name}'

    @hybrid_property
    def espnID(self):
        splitLogoUrl = self.team_logo.split('/')[4] #? NonNull so 4th index always: https://mlbstat.com/team-logos/123.svg -> 123.svg
        return splitLogoUrl.split('.')[0] #* Once split on the dot, [123, svg] so 0-index!

    @hybrid_property 
    def percentage(self):
        return self.wins / (self.wins + self.losses)

    @hybrid_property
    def asDict(self): #* No need to include homeGames/awayGames (which would just cause a large circular reference mess)
        return { 'id': self.id, 'teamLogo': self.team_logo, 
            'teamName': self.team_name, 'cityName': self.city_name,
            'abbreviation': self.abbreviation, 'wins': self.wins, 'losses': self.losses}

    def __repr__(self): #? String representation on queries
        return f'<BaseballTeam {self.id} - The {self.city_name} {self.team_name}>'

    def __eq__(self, other): #? Could also override __hash__ but only needed if expected to use sets
        if isinstance(other, BaseballTeam):
            idCheck = self.id == other.id 
            teamCheck = self.city_name == other.city_name and self.team_name == other.team_name
            return idCheck or teamCheck
        return False

class Promo(db.Model): 
    __tablename__ = 'promos'

    #* JsonKeyBase = dates.games.promotions.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False) #* JsonKey = name
    thumbnail_url = db.Column(db.String(), nullable=False) #* JsonKey = imageURL
    dodger_game_id = db.Column(db.Integer, db.ForeignKey('dodger_games.id'), nullable=False)

    @hybrid_property
    def asDict(self): #* timedelta hours = 7 since that's PDT offset from utc
        return { 'id': self.id, 'name': self.name, 
            'thumbnailUrl': self.thumbnail_url } #* Not including game key to avoid circular reference

    def __repr__(self): #? String representation on queries
        return f'<Promo {self.id} - {self.name}>'

    def __eq__(self, other): #? Could also override __hash__ but only needed if expected to use sets
        if isinstance(other, Promo):
            idCheck = self.id == other.id
            nameGameCheck = self.name == other.name and self.dodger_game_id == other.dodger_game_id 
            return idCheck or nameGameCheck
        return False