from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from .. import db


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
    baseball_game_mapping_name = 'DodgerGame'
    homeGames: Mapped[List[baseball_game_mapping_name]] = relationship(back_populates='home_team',
                                                                       foreign_keys='DodgerGame.home_team_id')
    #? Put home+away games in 1 column THEN filter via hybrid_prop?.. FOR NOW, these 2 relationships provide easy table joins
    awayGames: Mapped[List[baseball_game_mapping_name]] = relationship(back_populates='away_team',
                                                                       foreign_keys='DodgerGame.away_team_id')


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
    def asDict(self): #* No need to include homeGames/awayGames (which would just cause a large recursive reference mess)
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
