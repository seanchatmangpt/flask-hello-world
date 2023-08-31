from flask import Flask, jsonify
from flask_cors import CORS

from strapi_model_mixin import *

app = Flask(__name__)
CORS(app)

for model in [Message, World, Author, Blog]:
    model.add_routes(app)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
