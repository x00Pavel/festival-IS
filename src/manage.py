from flask_script import Manager, commands
from festival_is import app

manager = Manager(app)


@manager.command
def init_db():
    with app.test_request_context():
        from create_db import db

        db.engine.echo = True
        db.metadata.bind = db.engine
        db.metadata.create_all(checkfirst=True)


@manager.command
def drop_db():
    with app.test_request_context():
        from create_db import db

        db.engine.echo = True
        db.metadata.bind = db.engine
        db.metadata.drop_all(checkfirst=True)


if __name__ == "__main__":
    manager.run()
