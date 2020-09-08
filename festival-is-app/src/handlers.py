import flask
import json

def hello():
    return flask.jsonify({"response": "Hello from Docker!"})