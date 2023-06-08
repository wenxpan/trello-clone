from flask import Blueprint
from models.card import Card, CardSchema
from init import db
from flask_jwt_extended import jwt_required
from blueprints.auth_bp import admin_required


cards_bp = Blueprint('cards', __name__)


@cards_bp.route('/cards')
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
