from flask import Flask, jsonify
from flask_cors import CORS

from message import Message

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    msg = Message().get_one("1")
    return jsonify(msg)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
