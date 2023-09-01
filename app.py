from flask import Flask, jsonify
from flask_cors import CORS

from models.author import Author
from models.blog import Blog
from models.message import Message
from models.world import World

app = Flask(__name__)
CORS(app)

for model in [Message, World, Author, Blog]:
    model.add_routes(app)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
