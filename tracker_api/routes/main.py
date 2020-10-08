from flask import Blueprint, request

from tracker_api.extensions import db
from tracker_api.models import Player, PlayerGame, Game

main = Blueprint('main', __name__)

@main.route('/')
def index():
    wins = PlayerGame.query.filter_by(placement=1).group_by(id_game).all()

    return {
        'num wins': len(wins)
        }