import flask

app = flask.Flask(__name__)

@app.route('/')
def move():
    flask.abort(404)
    return "Moved"
