from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# DB CONNECTION AREA
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://tomato:admin123@127.0.0.1:5432/ripe_tomatoes_db'

db = SQLAlchemy(app)
ma = Marshmallow(app)

# CLI COMMANDS AREA


@app.cli.command('create')
def create_db():
    db.drop_all()
    db.create_all()
    print('Tables created successfully')


@app.cli.command('seed')
def seed_db():
    movies = [Movie(title='Spider-Man', genre='Action', length=148, year=2021),
              Movie(title='Dune', genre='Sci-fi', length=155, year=2021),]
    actors = [Actor(first_name='Tom', last_name='Holland', gender='male', country='UK', dob='1998-05-15'),
              Actor(first_name='Marisa', last_name='Tomer',
                    gender='female', country='USA', dob='1999-04-05'),
              Actor(first_name='John', last_name='Doe', gender='male',
                    country='Australia', dob='1998-04-20'),
              Actor(first_name='Sam', last_name='Smith', gender='male', country='UK', dob='1980-02-24'),]

    db.session.query(Movie).delete()
    db.session.query(Actor).delete()

    db.session.add_all(movies)
    db.session.add_all(actors)

    db.session.commit()
    print('Models seeded')

# MODELS AREA


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100))
    length = db.Column(db.Integer)
    year = db.Column(db.Integer)


class Actor(db.Model):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    gender = db.Column(db.String())
    country = db.Column(db.String())
    dob = db.Column(db.Date())

# SCHEMAS AREA


class MovieSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'genre', 'length', 'year')


class ActorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'gender', 'country', 'dob')


# ROUTING AREA
# @app.cli.command('movies')
@app.route('/movies')
def all_movies():
    stmt = db.select(Movie)
    movies = db.session.scalars(stmt).all()
    # movies = db.session.execute(stmt).all()
    # print(MovieSchema(many=True).dumps(movies))
    return MovieSchema(many=True).dump(movies)


@app.route('/actors')
def all_actors():
    stmt = db.select(Actor)
    actors = db.session.scalars(stmt).all()
    return ActorSchema(many=True).dump(actors)


@app.route("/")
def hello():
    return "Welcome to Ripe Tomatoes API"


# if __name__ == '__main__':
#     app.run(debug=True)
