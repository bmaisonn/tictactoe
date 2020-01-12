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
    def __init__(self, game_id, playerBlue='no user', playerRed='no user'):
        self.game_id = game_id
        self.playerBlue = playerBlue
        self.playerRed = playerRed
        self.moves = []

class GameBoard:
    def __init__(self):
        self.board = [['']*3 for i in range(3)]
        

games = {}
if not games:
    games[1] = Game(1, User(1, 'Bertrand'), User(0, 'Unknown'))

def find_game(game_id):
    return games[game_id]

@app.route('/game/<int:game_id>/', methods=['GET'])
def hello(game_id):
    try:
        game = find_game(1)
    except:
        return f"Game {game_id} not found", 404

    game_board = GameBoard()
    for move in game.moves:
        board_index = move.board_id - 1
        row = board_index // 3
        column = board_index % 3
        
        print(row)
        print(column)
        game_board.board[row][column] = move.player

    return render_template('board.html', game_board=game_board)

@app.route('/games/', methods=['GET'])
def show_games():
    return render_template('games.html', games=games)

@app.route('/play/<int:game_id>/', methods=['POST'])
def play(game_id):
    request_data = request.get_json()
    player = request_data.get('player', 'unknown')
    board_id = request_data.get('boardId', 'unknown')
    
    try:
        game = find_game(1)
    except:
        return f"Game {game_id} not found", 404
    
    game.moves.append(Move(player, int(board_id)))
    
    return 'ok', 200

@socketio.on('played')
def on_played(board_id):
    emit('played', board_id, broadcast=True)
    

@socketio.on('connect', namespace='/')
def connect():
    print ("We have connected to socketio")

if __name__ == '__main__':
    socketio.run(app)