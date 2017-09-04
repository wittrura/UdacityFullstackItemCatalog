# Dependencies
Flask - handles all frontend logic, routing, and rendering of template files
```pip install Flask
```

SQLAlchemy - ORM to support interaction between frontend and database
```pip install SQLAlchemy
```

SQLite - database

[Additional information can be found on the SQLite website](https://www.sqlite.org/download.html)

virtualenv - optional virtualization for easy workflow during development, allows for multiple installations of python
```sudo pip install virtualenv
```

# Creating the database
Set up the database by running `python database_setup_manga.py`

# Seeding the database
A seed file is provide to populate the initial database and get the app up and running

Data can be loaded by running `python seed_db_manga.py `

# Start the web server
Run `python project.py`

# Accessing the web app
By default, the app is set to run on port 5000

The app will be able to be accessed by navigating to http://localhost:5000/ in the browser
