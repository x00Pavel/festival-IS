import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
import boto3

load_dotenv()
login_manager = LoginManager()

app = Flask(__name__)

app.config["SECRET_USER"] = os.getenv("ROOT_EMAIL")
app.config["SECRET_KEY"] = os.getenv("ROOT_PSSWD")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")

login_manager.init_app(app)

from views import *

if __name__ == "__main__":
    if "HEROKU" not in os.environ.keys():
        app.config["ENV"] = "development"
        app.config["TEMPLATES_AUTO_RELOAD"] = True
        app.config["DEBUG"] = True
        app.config["TESTING"] = True
    app.run()
