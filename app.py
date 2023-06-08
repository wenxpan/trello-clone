from flask import Flask, request, abort
from datetime import date
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from os import environ
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from models.user import User, UserSchema
from models.card import Card, CardSchema
from init import db, ma, bcrypt, jwt

load_dotenv()

app = Flask(__name__)


app.config['JWT_SECRET_KEY'] = environ.get('JWT_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URI')

db.init_app(app)
ma.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)


def admin_required():
    user_email = get_jwt_identity()
    stmt = db.select(User).filter_by(email=user_email)
    user = db.session.scalar(stmt)
    # check that user is truthy and admin
    if not (user and user.is_admin):
        abort(401)


@app.errorhandler(401)
def unauthorized(err):
    return {'error': 'You must be an admin'}, 401


@app.cli.command('create')
def create_db():
    db.drop_all()
    db.create_all()
    print('Tables created successfully')


@app.cli.command('seed')
def seed_db():

    users = [
        User(email='admin@spam.com',
             password=bcrypt.generate_password_hash(
                 'spinynorman').decode('utf-8'),
             is_admin=True
             ),
        User(
            name='John Cleese',
            email='cleese@spam.com',
            password=bcrypt.generate_password_hash(
                'tisbutascratch').decode('utf-8')
        )
    ]
    # create an instance of the Card model in memory
    cards = [Card(
        title='Start the project',
        description='Stage 1 - Create an ERD',
        status="Done",
        date_created=date.today()
    ),
        Card(
        title='ORM queries',
        description='Stage 2 - Implement several queries',
        status='In Progress',
        date_created=date.today()
    ),
        Card(
        title='Marshmellow',
        description='Stage 3 - Implement jsonify of models',
        status='In Progress',
        date_created=date.today()
    ),]

    # truncate table; delete all rows in the table
    db.session.query(Card).delete()
    db.session.query(User).delete()

    # add the card to the session (transaction)
    db.session.add_all(cards)
    db.session.add_all(users)

    # commit the transaction to the database
    db.session.commit()
    print('Models seeded')


@app.route('/register', methods=['POST'])
def register():
    try:
        # parse, sanitize and validate the incoming JSON data
        # via the schema
        user_info = UserSchema().load(request.json)
        # create a new User model instance with the schema data
        user = User(email=user_info['email'],
                    password=bcrypt.generate_password_hash(
                        user_info['password']).decode('utf-8'),
                    name=user_info['name'])

        # add and commit the new user
        db.session.add(user)
        db.session.commit()

        # return new user, excluding the password, 201: created
        return UserSchema(exclude=['password']).dump(user), 201
    except IntegrityError:
        # return conflict
        return {'error': 'Email address already in use'}, 409


@app.route('/login', methods=['POST'])
def login():
    try:
        stmt = db.select(User).filter_by(email=request.json['email'])
        user = db.session.scalar(stmt)
        if user and bcrypt.check_password_hash(user.password, request.json['password']):
            token = create_access_token(
                identity=user.email, expires_delta=timedelta(days=1))
            return {'token': token, 'user': UserSchema(exclude=['password']).dump(user)}
        else:
            return {'error': 'Invalid email address or password'}, 401
    except KeyError:
        return {'error': 'Email and password are required'}, 400


@app.route('/cards')
@jwt_required()
def all_cards():
    # check if the user is admin
    admin_required()

    # stmt = db.select(Card).order_by(Card.status.desc())
    stmt = db.select(Card)
    # returns a list of objects?
    cards = db.session.scalars(stmt).all()
    print(cards[0].__dict__)
    return CardSchema(many=True).dump(cards)


@app.cli.command('cards')
def show_cards():
    stmt = db.select(Card)
    cards = db.session.scalars(stmt).all()

    print(CardSchema(many=True).dump(cards))


@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
