from flask import Blueprint, request

from tracker_api.extensions import db
from tracker_api.models import *
from sqlalchemy.orm import aliased

main = Blueprint('main', __name__)

@main.route('/')
def index():
    wins = TeamGame.query.filter_by(placement=1).all()

    return {
        'num wins': len(wins)
        }

@main.route('/wins/<username>', methods=['GET'])
def player_wins(username):
    player = Player.query.filter_by(username=username).first()
    if player is None:
        return {
            'status': "Player not found!"
        }
    team_players = player.teams
    teams = [team_player.team for team_player in team_players]
    wins = 0
    for team in teams:
        wins += len(TeamGame.query.filter_by(id_team=team.id, placement=1).all())

    return {
        'status': 'Player found!',
        'num wins': wins
        }

@main.route('/teams', methods=['GET'])
def teams():
    teams = Team.query.all()

    return {
        'num teams': len(teams)
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

        team_game = TeamGame.query.filter_by(
            id_team=team.id, 
            id_game=game.id).first()
        if team_game is None:
            team_game = TeamGame(
                id_team=team.id, 
                id_game=game.id,
                placement=_team['placement']
            )
            db.session.add(team_game)
        else:
            pass
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
    q = db.session.query(TeamPlayer).filter_by(id_player=players[0].id)

    if len(players) > 1:
        subq = q.subquery()
        for player in players[1:]:
            q = db.session.query(TeamPlayer).filter( \
                (TeamPlayer.id_player==player.id) & \
                (TeamPlayer.id_team==subq.c.id_team))
            subq = q.subquery()
    
    print(q.all())
    record = q.first()
    team = None
    if record is None:
        # make new team
        team = make_team(players)
    else:
        team = Team.query.filter_by(id=record.id_team).first()
        if len(team.players) != len(players):
            team = make_team(players)
    for player in team.players:
        print(player.player.username)
    print('team id:',team.id)
    return team

def make_team(players):
    team = Team()
    db.session.add(team)
    for player in players:
        db.session.add(TeamPlayer(
            team=team,
            player=player
        ))
    db.session.commit()
    return team