import flask
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

x_win_states = (re.compile(board.replace("o", "x")) for board in o_win_states)
o_win_states = (re.compile(board) for board in o_win_states)

def wins(board, player="o"):
    goals = o_win_states if player == "o" else x_win_states
    return any(g.match(board) for g in goals)

def invalidity_reason(board):
    if len(board) != 9:
        return "Board needs to be of length 9"

    unacceptable = re.sub("[xo ]", "", board)
    if unacceptable:
        return "Characters {0} are unacceptable".format(unacceptable)

    num_os = len(list(c for c in board if c == "o"))
    num_xs = len(list(c for c in board if c == "x"))
    # Either player can start, but a player can never make two more moves than
    # the other
    if abs(num_os - num_xs) > 1:
        return "Imbalanced number of moves"

    return None

@app.route('/ttt')
def move():
    board = flask.request.args["board"]
    if board is None:
        return "No board in request!", 400
    invalid = invalidity_reason(board)
    if invalid:
        return invalid, 400
    out = "Checking board {0}...\n".format(board)
    if wins(board):
        out += "o wins"
    elif wins(board, player="x"):
        out += "x wins"
    else:
        out += "No winner"
    return out

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
