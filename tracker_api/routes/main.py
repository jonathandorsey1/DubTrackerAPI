from flask import Blueprint, request

from tracker_api.extensions import db
from tracker_api.models import *
from sqlalchemy.orm import aliased

main = Blueprint('main', __name__)
NUM_PLAYERS = 4

@main.route('/')
def index():
    wins = TeamGame.query.filter_by(placement=1).all()

    return {
        'num wins': len(wins)
        }

@main.route('/team')
def team_wins():
    players = []
    for i in range(4):
        player = request.args.get('p' + str(i), None)
        if player:
            _p = Player.query.filter_by(username=player).first()
            if _p:
                players.append(_p)
            else:
                return {
                    'status': 'Team not found!'
                }
    team = get_team(players)
    if team is None:
        return {
            'status': 'Team not found!'
        }
    agg_stats = {player.username:get_player_win_stats(player, [team]) for player in players}
    return {
        'status': 'Team found!',
        'stats': agg_stats
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
    stats = get_player_win_stats(player, teams)
    return {
        'status': 'Player found!',
        'stats': stats
        }

# helper function that gets aggregate stats for player player
# on games played by the teams teams
def get_player_win_stats(player, teams): 
    stats = {'wins': 0,
                'kills': [],
                'deaths': [],
                'damages': []
                }

    for team in teams:
        wins = TeamGame.query.filter_by(id_team=team.id, placement=1).subquery()
        games = PlayerGame.query.filter_by(id_player=player.id).subquery()
        player_games = db.session.query(games).join(wins, wins.c.id_game==games.c.id_game).all()
        for game in player_games:
            stats['wins'] += 1
            stats['kills'] += [game.kills]
            stats['damages'] += [game.damage]
            stats['deaths'] += [game.deaths]
    return stats

@main.route('/wins/gamemode/<int:id>', methods=['GET'])
def gamemode_wins(id):
    if id not in [1, 2, 3, 4]:
        id = -1
    games = Game.query.filter_by(gamemode=id).all()
    if games is None:
        return {
            'status': "Gamemode not found!"
        }
    wins = len(games)

    return {
        'status': 'Gamemode found!',
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

def get_team(players, make=True):
    # TODO: check if the following queries work
    q = db.session.query(TeamPlayer).filter_by(id_player=players[0].id)
    subq = q.subquery()
    if len(players) > 1:
        for player in players[1:]:
            subq2 = db.session.query(TeamPlayer).filter_by(id_player=player.id).subquery()
            q = db.session.query(subq2).join(subq, subq2.c.id_team==subq.c.id_team)
            # q = db.session.query(TeamPlayer).filter( \
            #     (TeamPlayer.id_player==player.id) & \
            #     (TeamPlayer.id_team==subq.c.id_team))
            subq = q.subquery()

    team = db.session.query(Team).filter((Team.id==subq.c.id_team) & (Team.num_players==len(players)))
    team = team.first()
    if team is None and make:
        # make new team
        team = make_team(players)
    if team:
        print('team id:',team.id)
    return team

def make_team(players):
    team = Team(
        num_players=len(players)
    )
    db.session.add(team)
    for player in players:
        db.session.add(TeamPlayer(
            team=team,
            player=player
        ))
    db.session.commit()
    return team