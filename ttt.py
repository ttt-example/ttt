import flask

app = flask.Flask(__name__)

@app.route('/ttt')
def move():
    return "Hello world"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
