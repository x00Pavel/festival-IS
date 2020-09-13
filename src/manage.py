from flask_script import Manager, commands
from datetime import datetime
from festival_is import app
from create_db import db
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
    for i in os.listdir("src/data"):
        if i.endswith(".csv"):
            print("From src/data/" + i + " - To table " + i[2:-4])
            f = open("src/data/" + i, "r")
            cur.copy_expert('COPY "' + i[2:-4] + '" FROM STDIN WITH CSV HEADER', f)
            f.close()
            conn.commit()
    cur.close()

if __name__ == "__main__":
    manager.run()
