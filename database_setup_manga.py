import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    name = Column(String(50), nullable = False)
    email = Column(String(50), nullable = False)
    picture = Column(String(80))
    id = Column(Integer, primary_key = True)


class Genre(Base):
    __tablename__ = 'genre'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

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

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
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
