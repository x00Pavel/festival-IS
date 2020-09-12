import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

from views import *

if __name__ == "__main__":
    if "HEROKU" not in os.environ.keys():
        app.config["ENV"] = "development"
        app.config["DEBUG"] = True
        app.config["TESTING"] = True
    app.run()
