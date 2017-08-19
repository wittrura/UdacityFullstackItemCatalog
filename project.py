from flask import Flask
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_manga import Base, Genre, Manga

engine = create_engine('sqlite:///manga.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def showAllGenres():
    genres = session.query(Genre).all()
    output = ''
    for g in genres:
        output += g.name
        output += '<br><br>'
    return output

# to delete
@app.route('/catalog/<int:genre_id>/')
def genreListings(genre_id):
    genre = session.query(Genre).filter_by(id = genre_id).one()
    manga = session.query(Manga).filter_by(genre_id = genre_id)
    output = ''
    for m in manga:
        output += m.name
        output += '<br>'
        output += str(m.volumes)
        output += '<br>'
        output += str(m.chapters)
        output += '<br>'
        output += m.authors
        output += '<br>'
        output += m.description
        output += '<br><br>'
    return output
#

@app.route('/catalog/Snowboarding/items')
@app.route('/catalog/Snowboarding/Snowboard')
@app.route('/catalog/Snowboard/edit')
@app.route('/catalog/Snowboard/delete')
@app.route('/catalog.json')

def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    output = ''
    for i in items:
        output += i.name
        output += '<br>'
        output += i.price
        output += '<br>'
        output += i.description
        output += '<br><br>'
    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
