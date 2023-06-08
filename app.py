from flask import Flask, request, abort
from datetime import date
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from os import environ
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from models.user import User, UserSchema
from models.card import Card, CardSchema
from init import db, ma, bcrypt, jwt
from blueprints.cli_bp import cli_bp
from blueprints.auth_bp import auth_bp

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


app.register_blueprint(cli_bp)
app.register_blueprint(auth_bp)


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
