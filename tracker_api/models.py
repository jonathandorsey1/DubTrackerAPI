from .extensions import db
from datetime import datetime

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False)
    games = db.relationship('PlayerGame', backref='player', lazy=True)

class PlayerGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_player = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    id_game = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    kills = db.Column(db.Integer, nullable=False)
    damage = db.Column(db.Integer, nullable=False)
    deaths = db.Column(db.Integer, nullable=False)
    placement = db.Column(db.Integer, nullable=False)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dttm = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # TODO: implement grabbing gamemode squad size
    squad_size = db.Column(db.Integer)
    entries = db.relationship('PlayerGame', backref='game', lazy=True)
    
