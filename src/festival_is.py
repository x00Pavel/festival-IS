import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

load_dotenv()
login_manager = LoginManager()

app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET_KEY"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
login_manager.init_app(app)

from views import *

if __name__ == "__main__":
    if "HEROKU" not in os.environ.keys():
        app.config["ENV"] = "development"
        app.config["DEBUG"] = True
        app.config["TESTING"] = True
    app.run()
