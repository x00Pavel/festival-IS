from flask_script import Manager, commands
from festival_is import app
from create_db import db
import psycopg2


manager = Manager(app)


@manager.command
def init_db():
    with app.test_request_context():

        db.engine.echo = True
        db.metadata.bind = db.engine
        db.metadata.create_all(checkfirst=True)
        # load_test_data()


@manager.command
def drop_db():
    with app.test_request_context():

        db.engine.echo = True
        db.metadata.bind = db.engine
        db.metadata.drop_all(checkfirst=True)


if __name__ == "__main__":
    manager.run()
