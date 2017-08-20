from flask import Flask, render_template, url_for, request, redirect, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_manga import Base, Genre, Manga, User

# authorization
from flask import session as login_session
from key import secret_key
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


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


# TODO - route for creating a new category


@app.route('/catalog/genres/<int:genre_id>/new', methods=['GET', 'POST'])
def mangaCreate(genre_id):
    genre = session.query(Genre).filter_by(id = genre_id).one()
    if request.method == 'POST':
        newTitle = Manga(name = request.form['name'],
                        description = request.form['description'],
                        volumes = request.form['volumes'],
                        chapters = request.form['chapters'],
                        authors = request.form['authors'],
                        genre_id = genre_id,
                        user_id = login_session['user_id'])
        session.add(newTitle)
        session.commit()
        return redirect(url_for('genreListings', genre_id = genre_id))
    else:
        return render_template('mangaCreate.html', genre = genre)


@app.route('/catalog/titles/<int:manga_id>')
def mangaView(manga_id):
    manga = session.query(Manga).filter_by(id = manga_id).one()
    return render_template('manga.html', manga = manga)


@app.route('/catalog/titles/<int:manga_id>/edit', methods=['GET', 'POST'])
def mangaUpdate(manga_id):
    mangaToUpdate = session.query(Manga).filter_by(id = manga_id).one()
    if request.method == 'POST':
        if request.form['name']:
            mangaToUpdate.name = request.form['name']
            mangaToUpdate.description = request.form['description']
            mangaToUpdate.volumes = request.form['volumes']
            mangaToUpdate.chapters = request.form['chapters']
            mangaToUpdate.authors = request.form['authors']
            session.add(mangaToUpdate)
            session.commit()
            return redirect(url_for('mangaView', manga_id = mangaToUpdate.id))
        return render_template('mangaUpdate.html', manga = mangaToUpdate)
    else:
        return render_template('mangaUpdate.html', manga = mangaToUpdate);


@app.route('/catalog/titles/<int:manga_id>/delete', methods=['GET', 'POST'])
def mangaDelete(manga_id):
    mangaToDelete = session.query(Manga).filter_by(id = manga_id).one()
    genre_id = mangaToDelete.genre_id
    if request.method == 'POST':
        session.delete(mangaToDelete)
        session.commit()
        return redirect(url_for('genreListings', genre_id = genre_id))
    else:
        return render_template('mangaDelete.html', manga = mangaToDelete);


@app.route('/catalog/genres/json')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(Genres = [g.serialize for g in genres])

@app.route('/catalog/genres/<int:genre_id>/json')
def mangaJSON(genre_id):
    manga = session.query(Manga).filter_by(genre_id = genre_id).all()
    return jsonify(Manga = [m.serialize for m in manga])


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html')

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # upgrade auth code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # abort if there is an error in the acces token info
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is valid for this specific app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match application."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check to see if a user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token in the session for later user
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params = params)
    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    return output



def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = secret_key
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
