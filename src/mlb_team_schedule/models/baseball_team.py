from .. import db

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


class BaseballTeam(db.Model):
    __tablename__ = "baseball_teams"


    # MLB API Json Parent Key = dates.games.teams.home.
    id: Mapped[int] = mapped_column(primary_key=True)
    # MLB API Json Key = team.id -> f"https://www.mlbstatic.com/team-logos/{espnID}.svg"
    team_logo: Mapped[str] = mapped_column(unique=True) # Uses different ID than above ID
    # MLB API Json Key = team.clubName -> Dodgers - Grabs official name, not nicknames
    team_name: Mapped[str] = mapped_column(unique=True)
    # MLB API Json Key = team.franchiseName -> Los Angeles - Grabs official location
    city_name: Mapped[str] # Might not be city or state i.e. Colorado Rockies vs Denver
    # MLB API Json Key = team.abbreviation -> LAD
    abbreviation: Mapped[str] = mapped_column(unique=True) #? Need unique in mapped_column
    # MLB API Json Key = leagueRecord.wins
    wins: Mapped[int] #? Don't need mapped_column since nullable = false based on type!
    # MLB API Json Key = leagueRecord.losses
    losses: Mapped[int] #? IF nullable must be true, set the type to Mapped[Optional[int]]


    #? BaseballGame sets `foreign_keys` from ITS OWN table to pair the BaseballTeam FK
    #? BaseballTeam as parent sets `foreign_keys` to help SQLAlchemy find those FKs
    baseballGameMapName = "BaseballGame"
    homeGames: Mapped[List[baseballGameMapName]] = relationship(
        back_populates="home_team", foreign_keys="BaseballGame.home_team_id"
    )
    #TODO: Home+Away games in 1 column THEN filter as hybrid_prop? Delim "Ws-Ls" by "-"
    awayGames: Mapped[List[baseballGameMapName]] = relationship(
        back_populates="away_team", foreign_keys="BaseballGame.away_team_id"
    )


    @hybrid_property #? SQLAlchemy hybrid props act like computed props or Mongo virtuals
    def fullName(self): #? MUST concat here, since SQLAlchemy misinterprets f-strings
        return self.city_name + " " + self.team_name


    @hybrid_property
    def espnID(self): # team_logo starts as 'https://mlbstat.com/team-logos/123.svg'
        splitLogoUrl = self.team_logo.split("/")[4] # so 4th index SHOULD grab '123.svg'
        return splitLogoUrl.split(".")[0] # Split on "." to get '123' from [123, svg]


    @hybrid_property
    def percentage(self):
        return self.wins / (self.wins + self.losses)


    @hybrid_property
    def asDict(self): # Don't need homeGames/awayGames, and cause a big recursive mess
        return {
            "id": self.id, "teamLogo": self.team_logo,
            "teamName": self.team_name, "cityName": self.city_name,
            "abbreviation": self.abbreviation, "wins": self.wins, "losses": self.losses
        }


    def __repr__(self): #? String representation on queries
        return f"<BaseballTeam {self.id} - The {self.city_name} {self.team_name}>"


    def __eq__(self, other): #? CAN override `__hash__` but only needed if using sets
        if isinstance(other, BaseballTeam):
            idCheck = self.id == other.id
            sameCity = self.city_name == other.city_name
            sameTeamName = self.team_name and other.team_name
            return idCheck or (sameCity and sameTeamName)
        return False

