import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Genre(Base):
    __tablename__ = 'genre'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

    @property
    def serialize(self):
        return {
        'name': self.name,
        'id': self.id
        }

class Manga(Base):
    __tablename__ = 'manga'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    volumes = Column(Integer)
    chapters = Column(Integer)
    description = Column(String(1000))
    authors = Column(String(250))

    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)

    @property
    def serialize(self):
        #returns object data in serializeable format
        return {
        'name': self.name,
        'id': self.id,
        'volumes': self.volumes,
        'chapters': self.chapters,
        'description': self.description,
        'authors': self.authors
        }


engine = create_engine('sqlite:///manga.db')

Base.metadata.create_all(engine)
