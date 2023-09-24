from flask import Flask
from flask import jsonify

from flask_cors import CORS
from config import BUCKET


app = Flask(__name__)
CORS(app)


@app.route("/")
def get_app_version():
    app_data = {
        "service": "Berylitics API",
        "version": 1.0
    }
    return jsonify(app_data)
