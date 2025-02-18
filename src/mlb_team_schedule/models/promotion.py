from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .. import db


class Promo(db.Model):
    __tablename__ = 'promos'


    #* MLB API Json Parent Key = dates.games.promotions.
    id: Mapped[int] = mapped_column(primary_key=True)
    #* MLB API Json Key = name
    name: Mapped[str]
    #* MLB API Json Key = imageURL
    thumbnail_url: Mapped[str]
    #* MLB API Json Key = offerType
    offer_type: Mapped[str] #? MOSTLY = 'Day of Game Highlights', 'Giveaway' OR 'Ticket Offer'


    #? If there's only 1 path between 2 tables (e.g. game to promos), SQLAlchemy easily finds the foreign key linking the 2
    baseball_game_id: Mapped[int] = mapped_column(db.ForeignKey('baseball_games.id'))
    #? No matter if it's a 1-to-Many or a 1-to-1 relationship, just need to save a ForeignKey on the Child/BelongsTo side
    baseballGameMapName = 'BaseballGame'
    game: Mapped[baseballGameMapName] = relationship(back_populates='promos') #? SO this Promo BELONGS TO only 1 Game


    @hybrid_property
    def asDict(self):
        return { #* Not including game key to avoid recursive reference
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
