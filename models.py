from datetime import timedelta
from sqlalchemy.ext.hybrid import hybrid_property
from . import db

#? With particularly small projects, this can be kept in the main app file
#? BUT when separating models into own file, you'd end up with a circular import and crash!
# db = SQLAlchemy()

#* Rename BaseballGame
class DodgerGame(db.Model):
    __tablename__ = 'dodger_games' #? Without override, tablename = 'dodger_game' -> #todo Rename to baseball_games

    #* MLB API Json parent key = dates.games.
    id = db.Column(db.Integer, primary_key=True)
    # gamePk = db.Column(db.Integer, nullable=False) #* MLB API Json Key = 'gamePk', seemingly its one consistent ID
    date = db.Column(db.DateTime, nullable=False) #* MLB API Json Key = 'gameDate', format: 2021-07-05T22:40:00Z
    #todo Update these two property names below
    #todo gameNumInSeries -> seriesGameNumber
    gameNumInSeries = db.Column(db.Integer, nullable=False) #* MLB API Json Key = 'seriesGameNumber', e.g. Game # 2 of 3
    #todo gamesInSeries -> seriesGameCount
    gamesInSeries = db.Column(db.Integer, nullable=False) #* MLB API Json Key = 'gamesInSeries', e.g. 3 games in series

    #? When setting foreign key, @param = 'tablename.columnkey'
    home_team_id = db.Column(db.Integer, db.ForeignKey('baseball_teams.id'), nullable=False)
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
        return {
            'id': self.id, 'date': self.readableDate, 'promos': [promotion.asDict for promotion in self.promos],
            'gameNumInSeries': self.gameNumInSeries, 'gamesInSeries': self.gamesInSeries,
            'homeTeam': self.home_team.asDict, 'awayTeam': self.away_team.asDict,
        }

    #? No Init needed (can be overridden if needed but otherwise allow sqlAlchemy to handle it)

    def __repr__(self): #? String representation on queries
        return '<DodgerGame id {} on {}>'.format(self.id, self.readableDate) #? A Python2-ish way to embed vars before f-strings

    def __eq__(self, other): #? Could also override __hash__ but only needed if expected to use sets
        if isinstance(other, DodgerGame):
            idCheck = self.id == other.id
            dateCheck = self.date == other.date and self.gameNumInSeries == other.gameNumInSeries and self.gamesInSeries == other.gamesInSeries
            teamsCheck = self.home_team_id == other.home_team_id and self.away_team_id == other.away_team_id
            return idCheck or (dateCheck and teamsCheck)
        return False

class BaseballTeam(db.Model):
    __tablename__ = 'baseball_teams'

    #* MLB API Json parent key = dates.games.teams.home.
    id = db.Column(db.Integer, primary_key=True)
    #* MLB API Json Key = team.id -> f"https://www.mlbstatic.com/team-logos/{espnID}.svg" -> DIFFERENT THAN above DB ID
    team_logo = db.Column(db.String(), unique=True, nullable=False)
    #* MLB API Json Key = team.clubName -> Dodgers which grabs the official name, not nicknames like D-Backs
    team_name = db.Column(db.String(), unique=True, nullable=False)
    #* MLB API Json Key = team.franchiseName -> Los Angeles which grabs official location, not necessarily city or state
    city_name = db.Column(db.String(), nullable=False) #* i.e. Colorado Rockies vs Denver Rockies
    #* MLB API Json key = team.abbreviation -> LAD
    abbreviation = db.Column(db.String(), unique=True, nullable=False)
    #* MLB API Json Key = leagueRecord.wins
    wins = db.Column(db.Integer, nullable=False)
    #* MLB API Json Key = leagueRecord.losses
    losses = db.Column(db.Integer, nullable=False)

    #? Relationship() defines a hasA/hasMany convenience property
    #? Backref creates the inverse relation to DodgerGame class. No back_populate needed - normally placed in both classes
    #? 'lazy' loads relationship on 1st request, synonym for setting it as 'select'
    #? Goal: Consolidate games BUT until then, this simplifies the table joins
    homeGames = db.relationship('DodgerGame', backref='home_team', lazy=True, foreign_keys='DodgerGame.home_team_id')
    awayGames = db.relationship('DodgerGame', backref='away_team', lazy=True, foreign_keys='DodgerGame.away_team_id')

    @hybrid_property #? Hybrid props are SqlAlchemy's equivalent of computed properties (or virtuals from mongo!)
    def fullName(self): #? MUST concatenate here, since f-strings are misinterpreted by SQLAlchemy
        return self.city_name + " " + self.team_name

    @hybrid_property
    def espnID(self): #* team_loglo starts as 'https://mlbstat.com/team-logos/123.svg'
        splitLogoUrl = self.team_logo.split('/')[4] #* so 4th index always grabs '123.svg'
        return splitLogoUrl.split('.')[0] #* Once split on the dot, take the 0-index from [123, svg] so '123'

    @hybrid_property
    def percentage(self):
        return self.wins / (self.wins + self.losses)

    @hybrid_property
    def asDict(self): #* No need to include homeGames/awayGames (which would just cause a large circular reference mess)
        return { 
            'id': self.id, 'teamLogo': self.team_logo,
            'teamName': self.team_name, 'cityName': self.city_name,
            'abbreviation': self.abbreviation, 'wins': self.wins, 'losses': self.losses
        }

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

    #* MLB API Json parent key = dates.games.promotions.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False) #* MLB API Json Key = name
    thumbnail_url = db.Column(db.String(), nullable=False) #* MLB API Json Key = imageURL
    dodger_game_id = db.Column(db.Integer, db.ForeignKey('dodger_games.id'), nullable=False)
    #todo Should also include 'offerType' to differentiate between Highlights like fireworks vs a Giveaway or Ticket Offer

    @hybrid_property
    def asDict(self):
        return { #* Not including game key to avoid circular reference
            'id': self.id, 'name': self.name, 'thumbnailUrl': self.thumbnail_url
        }

    def __repr__(self): #? String representation on queries
        return f"<Promo id: {self.id} - {self.name}>"

    def __eq__(self, other):
        if isinstance(other, Promo):
            idCheck = self.id == other.id
            nameCheck = self.name == other.name
            return idCheck or nameCheck
        return False

    #? Objs that are equal MUST return the same hash BUT Objs that return the same hash aren't necessarily equal
    def __hash__(self): #* SO, ONLY name is used as the identifying feature of Promo objs for better set comparison
        return hash(self.name) #* Though the thumbnail COULD, but is unlikely to change, while name is very consistent
