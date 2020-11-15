from flask_script import Manager, commands
from datetime import datetime
from festival_is import app
from classes import db, RootAdmin
from werkzeug.security import generate_password_hash
import psycopg2
import os
import sys

manager = Manager(app)


@manager.command
def init_db():
    with app.test_request_context():

        db.engine.echo = True
        db.metadata.bind = db.engine
        db.metadata.create_all(checkfirst=True)
        root = RootAdmin(
            user_email=app.config["SECRET_USER"],
            name="Main",
            surname="Admin",
            avatar=None,
            passwd=generate_password_hash(app.config["SECRET_KEY"], method="sha256"),
            perms=0,
            address="Fests HQ",
        )
        db.session.add(root)
        db.session.commit()
        # load_test_data()


@manager.command
def drop_db():
    with app.test_request_context():
        db.engine.echo = True
        db.metadata.bind = db.engine
        db.metadata.drop_all(checkfirst=True)


@manager.command
def export_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    sql = """
    select table_name from information_schema.tables
    where table_schema not in ('information_schema', 'pg_catalog') and
    table_type = 'BASE TABLE'
    """
    cur.execute(sql)
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    os.mkdir("src/data/backup/" + date)
    for i in cur.fetchall():
        f = open("src/data/backup/" + date + "/" + i[0] + ".csv", "w")
        cur.copy_expert('COPY "' + i[0] + '" TO STDOUT WITH CSV HEADER', f)
        f.close()
    cur.close()


@manager.command
def import_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    for i in sorted(os.listdir("src/data")):
        if i.endswith(".csv"):
            table = i.split("-")[1].split(".")[0]
            print(f"From src/data/{i} - To table {table}")
            with open(f"src/data/{i}", "r") as f:
                header = f.readline()
                cur.copy_expert(
                    f'COPY "{table}" ({header}) FROM STDIN CSV', f,
                )
            conn.commit()
    cur.close()


@manager.command
def full_reset():
    drop_db()
    init_db()
    import_db()


if __name__ == "__main__":
    manager.run()
