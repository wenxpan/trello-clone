from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:spameggs123@127.0.0.1:5432/trello'

db = SQLAlchemy(app)

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    date_created = db.Column(db.Date())


@app.cli.command('create')
def create_db():
    db.drop_all()
    db.create_all()
    print('Tables created successfully')


@app.cli.command('seed')
def seed_db():
    # create an instance of the Card model in memory
    card = Card(
        title = 'Start the project',
        description = 'Stage 1 - Create an ERD',
        date_created = date.today()
    )

    # truncate table
    db.session.query(Card).delete()

    # add the card to the session (transaction)
    db.session.add(card)

    # commit the transaction to the database
    db.session.commit()
    print('Models seeded')

@app.route('/')
def index():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)