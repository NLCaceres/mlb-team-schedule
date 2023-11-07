from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from .. import db


#? With particularly small projects, this can be kept in the main app file
#? BUT when separating models into own file, you'd end up with a circular import and crash!
# db = SQLAlchemy()

#* Rename BaseballGame
class DodgerGame(db.Model):
    __tablename__ = 'dodger_games' #? Without override, tablename = 'dodger_game' -> #todo Rename to baseball_games


    #* MLB API Json Parent Key = dates.games.
    id: Mapped[int] = mapped_column(primary_key=True)
    #* MLB API Json Key = 'gamePk', seemingly the only consistent ID. Does 'Pk' = 'primary key'?
    gameKey: Mapped[int] = mapped_column(unique=True)
    #* MLB API Json Key = 'gameDate', format: 2021-07-05T22:40:00Z
    date: Mapped[datetime]
    #* MLB API Json Key = 'seriesGameNumber', e.g. Game # 2 of 3
    gameNumInSeries: Mapped[int] #todo Rename gameNumInSeries -> seriesGameNumber
    #* MLB API Json Key = 'gamesInSeries', e.g. 3 games in series
    gamesInSeries: Mapped[int] #todo Rename gamesInSeries -> seriesGameCount


    #? Use a ForeignKey so the DB can setup the 1-Team to Many-Games relationship -> Usage: ForeignKey('tablename.columnkey')
    home_team_id: Mapped[int] = mapped_column(db.ForeignKey('baseball_teams.id'))
    #? If there's 2+ paths between 2 tables, set foreign_keys in relationship() to set the specific key used in each path
    baseballTeamMapName = 'BaseballTeam'
    home_team: Mapped[baseballTeamMapName] = relationship(back_populates='homeGames', foreign_keys=[home_team_id])
    away_team_id: Mapped[int] = mapped_column(db.ForeignKey('baseball_teams.id'))
    away_team: Mapped[baseballTeamMapName] = relationship(back_populates='awayGames', foreign_keys=[away_team_id])


    #? Relationships now default to Lazy='select' which waits until 1st use to load in the relation
    promoMapName = 'Promo'
    promos: Mapped[List[promoMapName]] = relationship(back_populates='game')


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
