from flask import Flask, render_template, url_for, request, redirect, jsonify
# backend
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# database setup for sqlite
# from database_setup_manga import Base, Genre, Manga, User
# database setup for postgres
from database_setup_postgres import Base, Genre, Manga, User

# authorization
from flask import session as login_session
from key import secret_key
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
# support, http requests, parsing
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# engine for sqlite
# engine = create_engine('sqlite:///manga.db')
# engine for postgresq
engine = create_engine('postgresql://catalog:udacity@localhost:5432/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def showAllGenres():
    genres = session.query(Genre).all()
    latest_titles = session.query(Manga).order_by(Manga.id.desc()).limit(3)
    return render_template('main.html',
                           genres=genres,
                           latest_titles=latest_titles)


@app.route('/catalog/genres/<int:genre_id>/items')
def genreListings(genre_id):
    genres = session.query(Genre).all()

    genre = session.query(Genre).filter_by(id=genre_id).one()
    manga = session.query(Manga).filter_by(genre_id=genre_id)

    return render_template('genre.html',
                           manga=manga,
                           genres=genres,
                           genre_id=genre_id)


@app.route('/catalog/genres/<int:genre_id>/new', methods=['GET', 'POST'])
def mangaCreate(genre_id):
    if 'username' not in login_session:
        return redirect('/login')

    genre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        newTitle = Manga(name=request.form['name'],
                         description=request.form['description'],
                         volumes=request.form['volumes'],
                         chapters=request.form['chapters'],
                         authors=request.form['authors'],
                         genre_id=genre_id,
                         user_id=login_session['user_id'])
        session.add(newTitle)
        session.commit()
        return redirect(url_for('genreListings', genre_id=genre_id))
    else:
        return render_template('mangaCreate.html', genre=genre)


@app.route('/catalog/titles/<int:manga_id>')
def mangaView(manga_id):
    manga = session.query(Manga).filter_by(id=manga_id).one()
    creator = getUserInfo(manga.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('mangaPublic.html', manga=manga)
    else:
        return render_template('manga.html', manga=manga)


@app.route('/catalog/titles/<int:manga_id>/edit', methods=['GET', 'POST'])
def mangaUpdate(manga_id):
    if 'username' not in login_session:
        return redirect('/login')

    mangaToUpdate = session.query(Manga).filter_by(id=manga_id).one()

    if mangaToUpdate.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized" +\
        " to edit this restaurant. Please create your own restaurant in " +\
        "order to edit.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            mangaToUpdate.name = request.form['name']
            mangaToUpdate.description = request.form['description']
            mangaToUpdate.volumes = request.form['volumes']
            mangaToUpdate.chapters = request.form['chapters']
            mangaToUpdate.authors = request.form['authors']
            session.add(mangaToUpdate)
            session.commit()
            return redirect(url_for('mangaView', manga_id=mangaToUpdate.id))
        return render_template('mangaUpdate.html', manga=mangaToUpdate)
    else:
        return render_template('mangaUpdate.html', manga=mangaToUpdate)


@app.route('/catalog/titles/<int:manga_id>/delete', methods=['GET', 'POST'])
def mangaDelete(manga_id):
    if 'username' not in login_session:
        return redirect('/login')

    mangaToDelete = session.query(Manga).filter_by(id=manga_id).one()
    genre_id = mangaToDelete.genre_id

    if mangaToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized" +\
        " to delete this restaurant. Please create your own restaurant in " +\
        "order to delete.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(mangaToDelete)
        session.commit()
        return redirect(url_for('genreListings', genre_id=genre_id))
    else:
        return render_template('mangaDelete.html', manga=mangaToDelete)


@app.route('/catalog/genres/json')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(Genres=[g.serialize for g in genres])


@app.route('/catalog/genres/<int:genre_id>/json')
def mangaJSON(genre_id):
    manga = session.query(Manga).filter_by(genre_id=genre_id).all()
    return jsonify(Manga=[m.serialize for m in manga])


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px;
              height: 300px;
              border-radius: 150px;
              -webkit-border-radius: 150px;
              -moz-border-radius: 150px;
              "> '''
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state paramter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    # exchange client token for long-lived server-side token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = '''https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s''' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = '''https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200''' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "
              width: 300px;
              height: 300px;
              border-radius: 150px;
              -webkit-border-radius: 150px;
              -moz-border-radius: 150px;
              "> '''

    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('showAllGenres'))
    else:
        return redirect(url_for('showAllGenres'))


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = secret_key
    app.debug = True
    # app.run(host='0.0.0.0', port=8080)
    app.run(host='52.1.134.59', port=80)
