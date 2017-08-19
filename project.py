from flask import Flask, render_template, url_for, request, redirect
# TODO , ,  flash, jsonify
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
    return render_template('main.html', genres = genres)


@app.route('/catalog/genres/<int:genre_id>/items')
def genreListings(genre_id):
    genres = session.query(Genre).all()

    genre = session.query(Genre).filter_by(id = genre_id).one()
    manga = session.query(Manga).filter_by(genre_id = genre_id)

    return render_template('genre.html', manga = manga, genres = genres, genre_id = genre_id)


@app.route('/catalog/genres/<int:genre_id>/new', methods=['GET', 'POST'])
def mangaCreate(genre_id):
    genre = session.query(Genre).filter_by(id = genre_id).one()
    if request.method == 'POST':
        newTitle = Manga(name = request.form['name'],
                        description = request.form['description'],
                        volumes = request.form['volumes'],
                        chapters = request.form['chapters'],
                        genre_id = genre_id)
        session.add(newTitle)
        session.commit()
        return redirect(url_for('genreListings', genre_id = genre_id))
    else:
        return render_template('mangaCreate.html', genre = genre)


@app.route('/catalog/titles/<int:manga_id>')
def mangaView(manga_id):
    manga = session.query(Manga).filter_by(id = manga_id).one()
    return render_template('manga.html', manga = manga)


@app.route('/catalog/titles/<int:manga_id>/edit')
def mangaEdit(manga_id):
    manga = session.query(Manga).filter_by(id = manga_id).one()
    return render_template('mangaEdit.html', manga = manga);


@app.route('/catalog/titles/<int:manga_id>/delete')
def mangaDelete(manga_id):
    manga = session.query(Manga).filter_by(id = manga_id).one()
    return render_template('mangaDelete.html', manga = manga);


@app.route('/catalog/json')
def catalogJSON():
    return 'THIS IS THE ROUTE FOR RETURING DB DATA IN JSON FORMAT'


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
