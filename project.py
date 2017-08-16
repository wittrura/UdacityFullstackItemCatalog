from flask import Flask
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/Snowboarding/items')
@app.route('/catalog/Snowboarding/Snowboard')
@app.route('/catalog/Snowboard/edit')
@app.route('/catalog/Snowboard/delete')
@app.route('/catalog.json')

def HelloWorld():
    restaurant = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    output = ''
    for i in items:
        output += i.name
        output += '<br>'
    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
