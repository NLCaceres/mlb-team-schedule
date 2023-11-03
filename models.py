from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from . import db


#? With particularly small projects, this can be kept in the main app file
#? BUT when separating models into own file, you'd end up with a circular import and crash!
# db = SQLAlchemy()

#* Rename BaseballGame
class DodgerGame(db.Model):
    __tablename__ = 'dodger_games' #? Without override, tablename = 'dodger_game' -> #todo Rename to baseball_games

    #* MLB API Json Parent Key = dates.games.
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    #* MLB API Json Key = 'gamePk', seemingly the only consistent ID, 'Pk' = 'primary key'?
    # gameKey = db.Column(db.Integer, nullable=False)
    #* MLB API Json Key = 'gameDate', format: 2021-07-05T22:40:00Z
    date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    #* MLB API Json Key = 'seriesGameNumber', e.g. Game # 2 of 3
    gameNumInSeries: Mapped[int] = mapped_column(db.Integer, nullable=False) #todo Rename gameNumInSeries -> seriesGameNumber
    #* MLB API Json Key = 'gamesInSeries', e.g. 3 games in series
    gamesInSeries: Mapped[int] = mapped_column(db.Integer, nullable=False) #todo Rename gamesInSeries -> seriesGameCount

    #? Use a ForeignKey so the DB can setup the 1-Team to Many-Games relationship -> Usage: ForeignKey('tablename.columnkey')
    home_team_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('baseball_teams.id'), nullable=False)
    #? If there's 2+ paths between 2 tables, set foreign_keys in relationship() to set the specific key used in each path
    home_team: Mapped['BaseballTeam'] = relationship(back_populates='homeGames', foreign_keys=[home_team_id])
    away_team_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('baseball_teams.id'), nullable=False)
    away_team: Mapped['BaseballTeam'] = relationship(back_populates='awayGames', foreign_keys=[away_team_id])

    #? Relationships now default to Lazy='select' which waits until 1st use to load in the relation
    promos: Mapped[List['Promo']] = relationship(back_populates='game')

    @hybrid_property
    def readableDateTime(self): #* Used to query/filter specific rows by date
        return self.date - timedelta(hours=7)

    @hybrid_property
    def readableDate(self): #* timedelta hours = 7 since that's PDT offset from utc
        return (self.date - timedelta(hours=7)).strftime('%a %B %d %Y at %I:%M %p')

    @hybrid_property
    def asDict(self):
        return {
            'id': self.id, 'date': self.readableDate, 'promos': [promotion.asDict for promotion in self.promos],
            'gameNumInSeries': self.gameNumInSeries, 'gamesInSeries': self.gamesInSeries,
            'homeTeam': self.home_team.asDict, 'awayTeam': self.away_team.asDict,
        }

    #? No Init needed (CAN override the default if needed but otherwise let SQLAlchemy handle it)

    def __repr__(self): #? String representation on queries
        return '<DodgerGame id {} on {}>'.format(self.id, self.readableDate) #? Python2.6 way to embed vars w/out f-strings

    def __eq__(self, other): #? Could also override __hash__ but only needed if expected to use sets
        if isinstance(other, DodgerGame):
            idCheck = self.id == other.id
            gameNumberCheck = self.gameNumInSeries == other.gameNumInSeries
            gameCountCheck = self.gamesInSeries == other.gamesInSeries
            dateCheck = (self.date == other.date and gameNumberCheck and gameCountCheck)
            teamsCheck = self.home_team_id == other.home_team_id and self.away_team_id == other.away_team_id
            return idCheck or (dateCheck and teamsCheck)
        return False

class BaseballTeam(db.Model):
    __tablename__ = 'baseball_teams'

    #* MLB API Json Parent Key = dates.games.teams.home.
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    #* MLB API Json Key = team.id -> f"https://www.mlbstatic.com/team-logos/{espnID}.svg" -> DIFFERENT THAN above DB ID
    team_logo: Mapped[str] = mapped_column(db.String(), unique=True, nullable=False)
    #* MLB API Json Key = team.clubName -> Dodgers which grabs the official name, not nicknames like D-Backs
    team_name: Mapped[str] = mapped_column(db.String(), unique=True, nullable=False)
    #* MLB API Json Key = team.franchiseName -> Los Angeles which grabs official location, not necessarily city or state
    city_name: Mapped[str] = mapped_column(db.String(), nullable=False) #* i.e. Colorado Rockies vs Denver Rockies
    #* MLB API Json Key = team.abbreviation -> LAD
    abbreviation: Mapped[str] = mapped_column(db.String(), unique=True, nullable=False)
    #* MLB API Json Key = leagueRecord.wins
    wins: Mapped[int] = mapped_column(db.Integer, nullable=False)
    #* MLB API Json Key = leagueRecord.losses
    losses: Mapped[int] = mapped_column(db.Integer, nullable=False)

    #? Being on the Many-side, BaseballGame uses foreign_keys to pair ITS OWN foreign keys' w/ their relationships
    #? BUT on the 1-side, BaseballTeam uses foreign_keys to help SQLAlchemy find those ForeignKeys in BASEBALL_GAMES table
    homeGames: Mapped[List['DodgerGame']] = relationship(back_populates='home_team', foreign_keys='DodgerGame.home_team_id')
    #? Put home+away games in 1 column THEN filter via hybrid_prop?.. FOR NOW, these 2 relationships provide easy table joins
    awayGames: Mapped[List['DodgerGame']] = relationship(back_populates='away_team', foreign_keys='DodgerGame.away_team_id')

    @hybrid_property #? Hybrid props are SQLAlchemy's equivalent of computed properties (or virtuals from mongo!)
    def fullName(self): #? MUST concatenate here, since f-strings are misinterpreted by SQLAlchemy
        return self.city_name + " " + self.team_name

    @hybrid_property
    def espnID(self): #* team_logo starts as 'https://mlbstat.com/team-logos/123.svg'
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

    #* MLB API Json Parent Key = dates.games.promotions.
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    #* MLB API Json Key = name
    name: Mapped[str] = mapped_column(db.String(), nullable=False)
    #* MLB API Json Key = imageURL
    thumbnail_url: Mapped[str] = mapped_column(db.String(), nullable=False)
    #* MLB API Json Key = offerType
    # offer_type = db.Column(db.String(), nullable=False) #? MOSTLY = 'Day of Game Highlights', 'Giveaway' OR 'Ticket Offer'

    #? If there's only 1 path between 2 tables (e.g. game to promos), SQLAlchemy easily finds the foreign key linking the 2
    dodger_game_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('dodger_games.id'), nullable=False)
    #? No matter if it's a 1-to-Many or a 1-to-1 relationship, just need to save a ForeignKey on the Child/BelongsTo side
    game: Mapped['DodgerGame'] = relationship(back_populates='promos') #? i.e. This Promo BELONGS TO only 1 Game

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
