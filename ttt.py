import flask
import random
import re

app = flask.Flask(__name__)

# Store game states as strings; this is a pretty efficient Pythonic solution,
# not as compact as encoding things as bits of integers, but saves from having
# to convert between binary and ternary.
o_win_states = (
    "ooo......",
    "...ooo...",
    "......ooo",
    "o..o..o..",
    ".o..o..o.",
    "..o..o..o",
    "o...o...o",
    "..o.o.o..")

x_win_states = [re.compile(board.replace("o", "x")) for board in o_win_states]
o_win_states = [re.compile(board) for board in o_win_states]

def wins(board, player="o"):
    goals = o_win_states if player == "o" else x_win_states
    return any(g.match(board) for g in goals)

def available_moves(board, player="o"):
    return [board[:i] + player + board[i+1:]
            for i, place in enumerate(board)
            if place == " "]

def other(player):
    return "x" if player == "o" else "o"

cache = {}

def choose_move(board, player="o", depth = 0):
    if (board, player) in cache:
        return cache[(board, player)]

    available = list(available_moves(board, player))
    best = []
    best_move_score = -1.0
    avg = 0
    examined = 0

    # If we can win, don't recurse on other paths
    for move in available:
        if wins(move, player):
            cache[(board,player)] = move, 1.0
            return move, 1.0

    for move in available:
        #:print "Examining", move, depth
        if wins(move, other(player)):
            score = 0
        elif " " not in move:
            # This is a draw
            score = 0.5
        else:
            reply, other_score = choose_move(move, other(player), depth + 1)
            score = 1 - other_score

        avg += score
        examined += 1
        if score > best_move_score:
            if depth == 0:
                print "Move", move, score
            best_move_score = score
            best = [move]
        elif score == best_move_score:
            best.append(move)
    # If our best move is a draw, we score as 0.5 * fraction of our moves that are draws
    avg /= examined

    cache[(board,player)] = best[0], avg
    return best[0], avg


def invalidity_reason(board):
    "Return a string describing a problem with the board, or None if things are fine."
    if len(board) != 9:
        return "Board needs to be of length 9"

    unacceptable = re.sub("[xo ]", "", board)
    if unacceptable:
        return "Characters {0} are unacceptable".format(unacceptable)

    num_os = len(list(c for c in board if c == "o"))
    num_xs = len(list(c for c in board if c == "x"))
    # Either player can start, but a player can never make two more moves than
    # the other
    if num_os > num_xs:
        return "It can't be O's move"
    if num_xs > num_os + 1:
        return "Too many Xs on the board"

    if wins(board):
        return "O already won"
    if wins(board, "x"):
        return "X already won"

    return None

@app.route('/ttt')
def move():
    board = flask.request.args["board"]
    if board is None:
        return "No board in request!", 400

    out = "Checking board {0}...\n".format(board)
    invalid = invalidity_reason(board)
    if invalid:
        return invalid, 400

    move, score =  choose_move(board)
    desc = ""
    if score >= 1:
        print "wins"
    elif score <= 0:
        print "loses"
    return move

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
