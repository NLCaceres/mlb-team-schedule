from .. import db

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Promo(db.Model):
    __tablename__ = "promos"


    #* MLB API Json Parent Key = dates.games.promotions.
    id: Mapped[int] = mapped_column(primary_key=True)
    #* MLB API Json Key = name
    name: Mapped[str]
    #* MLB API Json Key = imageURL
    thumbnail_url: Mapped[str]
    #* MLB API Json Key = offerType
    offer_type: Mapped[str] # MOSTLY 'Day of Game Highlights' 'Giveaway' OR 'Ticket Offer'


    #? SQLAlchemy easily finds model foreign keys if there's 1 quick path like game-promos
    baseball_game_id: Mapped[int] = mapped_column(db.ForeignKey("baseball_games.id"))
    #? ONLY need to save ForeignKey on Child/BelongsTo side of 1-Many or 1-1 relationship
    baseballGameMapName = "BaseballGame" #? SO a promo BELONGS TO ONLY 1 game
    game: Mapped[baseballGameMapName] = relationship(back_populates="promos")


    @hybrid_property
    def asDict(self):
        return { #* Not including game key to avoid recursive reference
            "id": self.id, "name": self.name, "thumbnailUrl": self.thumbnail_url
        }


    def __repr__(self): #? String representation on queries
        return f"<Promo id: {self.id} - {self.name}>"


    def __eq__(self, other):
        if isinstance(other, Promo):
            idCheck = self.id == other.id
            nameCheck = self.name == other.name
            return idCheck or nameCheck
        return False


    #? Equal objs MUST return the same hash BUT the same hash DOESN'T always mean equal
    def __hash__(self): #* SO, ONLY name is needed to compare Promos, especially for sets
        return hash(self.name) #* Also name rarely changes, while thumbnail COULD

