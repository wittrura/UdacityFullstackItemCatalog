from flask import Flask, render_template
# TODO request, redirect, url_for, flash, jsonify
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
    # output = ''
    # for g in genres:
    #     output += g.name
    #     output += '<br><br>'
    # return output
    return render_template('main.html', genres = genres)

@app.route('/catalog/genres/<int:genre_id>/items')
def genreListings(genre_id):
    genre = session.query(Genre).filter_by(id = genre_id).one()
    manga = session.query(Manga).filter_by(genre_id = genre_id)
    output = ''
    for m in manga:
        output += m.name
        output += '<br><br>'
    return output

@app.route('/catalog/titles/<int:manga_id>')
def mangaView(manga_id):
    # genre = session.query(Genre).filter_by(id = genre_id).one()
    manga = session.query(Manga).filter_by(id = manga_id).one()
    output = ''
    output += manga.name
    output += '<br><br>'
    output += manga.description
    output += '<br><br>'
    output += str(manga.volumes)
    output += '<br><br>'
    output += str(manga.chapters)
    output += '<br><br>'
    output += manga.authors
    output += '<br><br>'
    return output

@app.route('/catalog/titles/<int:manga_id>/edit')
def mangaEdit(manga_id):
    output = 'THIS IS THE ROUTE FOR EDITING TITLES'
    return output

@app.route('/catalog/titles/<int:manga_id>/delete')
def mangaDelete(manga_id):
    output = 'THIS IS THE ROUTE FOR DELETING TITLES'
    return output

@app.route('/catalog/json')
def catalogJSON():
    return 'THIS IS THE ROUTE FOR RETURING DB DATA IN JSON FORMAT'

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
