from flask import Flask, escape, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

socketio = SocketIO(app)

class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        
class Move:
    def __init__(self, player, board_id):
        self.player = player
        self.board_id = board_id

class Game:
    def __init__(self, game_id, player_blue='no user', player_red='no user'):
        self.game_id = game_id
        self.player_blue = player_blue
        self.player_red = player_red
        self.moves = []

class GameBoard:
    def __init__(self, game):
        self.game = game
        self.board = [['']*3 for i in range(3)]
        
        self._init_board()
        
    def _init_board(self):
        for move in self.game.moves:
            board_index = move.board_id - 1
            row = board_index // 3
            column = board_index % 3
            self.board[row][column] = move.player
        

users = [User(1,'Bertrand'), User(2, 'Diane')]

games = {}
if not games:
    games[1] = Game(1, users[0], users[1])


def find_game(game_id):
    return games[game_id]


@app.route('/game/<int:game_id>/', methods=['GET'])
def hello(game_id):
    print("show game")
    try:
        game = find_game(1)
    except:
        return f"Game {game_id} not found", 404

    game_board = GameBoard(game)

    return render_template('board.html', game_board=game_board)

@app.route('/games/', methods=['GET'])
def show_games():
    return render_template('games.html', games=games)

@app.route('/play/<int:game_id>/', methods=['POST'])
def play(game_id):
    request_data = request.get_json()
    player_id = request_data.get('playerId', 'unknown')
    board_id = request_data.get('boardId', 'unknown')
    print(f'played "{player_id}" "{board_id}""')
    try:
        game = find_game(1)
    except:
        return f"Game {game_id} not found", 404
    
    game.moves.append(Move(int(player_id), int(board_id)))
    
    return 'ok', 200

@socketio.on('played')
def on_played(game_id, board_id, user_id):
    print(f"played event {game_id}, {board_id}, {user_id}")
    
    game = find_game(game_id)
    
    color = 'red' if user_id == game.player_red.user_id else 'blue'
    
    print(color)
    
    emit('boardupdate', (board_id, color), broadcast=True)
    

@socketio.on('connect', namespace='/')
def connect():
    print ("We have connected to socketio")

if __name__ == '__main__':
    socketio.run(app)