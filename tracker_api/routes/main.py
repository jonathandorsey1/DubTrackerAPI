from flask import Blueprint, request

from tracker_api.extensions import db
from tracker_api.models import *

main = Blueprint('main', __name__)

@main.route('/')
def index():
    wins = TeamGame.query.filter_by(placement=1).all()

    return {
        'num wins': len(wins)
        }

@main.route('/track', methods=['POST'])
def track():
    """
    Expecting data in json format:
    {
        "game": {
            "game_id": int,
            "gamemode": int
        },
        "teams": [
            {
                "placement": int,
                "members":
                [
                    
                    {
                        "username": string,
                        "kills": int,
                        "damage": int,
                        "deaths": int
                    },
                ]
            },
        ]
    }
    """
    payload = request.json
    if 'game' not in payload or 'teams' not in payload:
        return {
            'status': 'Invalid payload!'
        }

    # get game from payload
    game = get_game(payload)

    # get players from teams
    for _team in payload['teams']:
        players = get_players(_team['members'], game)
        # check if team record already exists
        team = get_team(players)
        team_game = TeamGame(
            team=team,
            game=game,
            placement=_team['placement']
        )
        db.session.add(team_game)
    db.session.commit()

    return 'Game tracked!'

def get_game(payload):
    game = Game.query.filter_by(id=payload['game']['game_id']).first()
    if game is None:
        game = Game(
            id=payload['game']['game_id'],
            gamemode=payload['game']['gamemode']
        )
        db.session.add(game)
    return game

def get_players(team, game):
    players = []
    for _player in team:
            # get player associated w/ game
            player = Player.query.filter_by(username=_player['username']).first()
            if player is None:
                player = Player(
                    username=_player['username'],
                )
                db.session.add(player)
            players.append(player)
    db.session.commit()
    for player, _player in zip(players, team):
        # add each PlayerGame record
        player_game = PlayerGame.query.filter_by(id_player=player.id, id_game=game.id).first()
        if player_game is None:
            player_game = PlayerGame(
                player=player,
                game=game,
                kills=_player['kills'],
                damage=_player['damage'],
                deaths=_player['deaths']
            )
            db.session.add(player_game)
        # else:
        #     # entry already exists, update
        #     player_game['kills']=_player['kills'],
        #     player_game['damage']=_player['damage'],
        #     player_game['deaths']=_player['deaths']
    db.session.commit()
    return players

def get_team(players):
    # TODO: check if the following queries work
    query = db.session.query(TeamPlayer).filter_by(id_player=players[0].id)

    for player in players[1:]:
        query = db.session.query(TeamPlayer).filter_by(id_player=player.id).join(query.subquery())
    
    record = query.first()
    team = None
    if record is None:
        # make new team
        team = Team()
        db.session.add(team)
        for player in players:
            db.session.add(TeamPlayer(
                team=team,
                player=player
            ))
        db.session.commit()
    else:
        team = Team.query.filter(id=record.id_team)
    
    return team