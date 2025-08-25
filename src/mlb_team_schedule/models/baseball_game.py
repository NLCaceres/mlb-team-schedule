from .. import db

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from typing import List

#? With particularly small projects, this can be kept in the main app file
#? BUT when splitting models into own file, you'd end up with a circular import and crash
# db = SQLAlchemy()

class BaseballGame(db.Model):
    __tablename__ = "baseball_games" #? Without override, tablename = 'baseball_game'


    # MLB API Json Parent Key = dates.games.
    id: Mapped[int] = mapped_column(primary_key=True)
    # MLB API Json Key = 'gamePk', seemingly only consistent ID. Is 'Pk' = 'primary key'?
    gameKey: Mapped[int] = mapped_column(unique=True)
    # MLB API Json Key = 'gameDate', format: 2021-07-05T22:40:00Z
    date: Mapped[datetime]
    # MLB API Json Key = 'seriesGameNumber', e.g. Game # 2 of 3
    seriesGameNumber: Mapped[int]
    # MLB API Json Key = 'gamesInSeries', e.g. 3 games in series
    seriesGameCount: Mapped[int]


    #? `ForeignKey` sets up 1 Team to Many Games relationship via "tablename.columnkey"
    home_team_id: Mapped[int] = mapped_column(db.ForeignKey("baseball_teams.id"))
    #? If 2 tables can be reached through multiple paths/attributes,
    #? Set `foreign_keys` in `relationship()` using the specific key path
    baseballTeamMapName = "BaseballTeam"
    home_team: Mapped[baseballTeamMapName] = relationship(
        back_populates="homeGames", foreign_keys=[home_team_id]
    )
    away_team_id: Mapped[int] = mapped_column(db.ForeignKey("baseball_teams.id"))
    away_team: Mapped[baseballTeamMapName] = relationship(
        back_populates="awayGames", foreign_keys=[away_team_id]
    )

    #? Relationships default to `lazy='select'`, waiting until 1st use before loading
    promoMapName = "Promo"
    promos: Mapped[List[promoMapName]] = relationship(back_populates="game")


    @hybrid_property
    def readableDateTime(self): # Used to query/filter specific rows by date
        return self.date - timedelta(hours=7)


    @hybrid_property
    def readableDate(self): # timedelta hours = 7 since that's PDT offset from UTC
        return (self.date - timedelta(hours=7)).strftime("%a %B %d %Y at %I:%M %p")


    @hybrid_property
    def asDict(self):
        return {
            "id": self.id, "date": self.readableDate,
            "promos": [promotion.asDict for promotion in self.promos],
            "seriesGameNumber": self.seriesGameNumber,
            "seriesGameCount": self.seriesGameCount,
            "homeTeam": self.home_team.asDict, "awayTeam": self.away_team.asDict,
        }


    #? No init needed. CAN override the default BUT SQLAlchemy can handle it fine


    def __repr__(self): #? String representation on queries
        #? Python 2.6 (SQLAlchemy-compatible) way of embedding vars w/out f-strings
        return "<BaseballGame id {} on {}>".format(self.id, self.readableDate)


    def __eq__(self, other): #? Could override `__hash__` but only if expected to use sets
        if isinstance(other, BaseballGame):
            idCheck = self.id == other.id
            gameNumberCheck = self.seriesGameNumber == other.seriesGameNumber
            gameCountCheck = self.seriesGameCount == other.seriesGameCount
            dateCheck = (self.date == other.date and gameNumberCheck and gameCountCheck)
            sameHomeTeam = self.home_team_id == other.home_team_id
            sameAwayTeam = self.away_team_id == other.away_team_id
            return idCheck or (dateCheck and (sameHomeTeam and sameAwayTeam))
        return False

