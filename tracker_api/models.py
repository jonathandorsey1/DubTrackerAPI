from .extensions import db
from datetime import datetime

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    games = db.relationship('PlayerGame', backref='player', lazy=True)
    teams = db.relationship('TeamPlayer', backref='player', lazy=True)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dttm = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # TODO: implement grabbing gamemode squad size
    gamemode = db.Column(db.Integer, nullable=False)
    entries = db.relationship('PlayerGame', backref='game', lazy=True)
    teams = db.relationship('TeamGame', backref='game', lazy=True)
    
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    players = db.relationship('TeamPlayer', backref='team', lazy=True)
    games = db.relationship('TeamGame', backref='team', lazy=True)

class PlayerGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_player = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    id_game = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    kills = db.Column(db.Integer, nullable=False)
    damage = db.Column(db.Integer, nullable=False)
    deaths = db.Column(db.Integer, nullable=False)

class TeamGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_team = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    id_game = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    placement = db.Column(db.Integer, nullable=False)

class TeamPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_team = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    id_player = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
