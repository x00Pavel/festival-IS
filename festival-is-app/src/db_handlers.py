import flask
import json
import psycopg2

conn = None

def listBlog():
    global conn
    if not conn:
        conn = DBManager()
    rec = conn.query_titles()
    result = []
    for c in rec:
        result.append(c)
    return flask.jsonify({"response": result})

class DBManager:
    def __init__(self):
        self.connection = psycopg2.connect( user = "admin",
                                            password = "admin",
                                            host = "festival-is-db",
                                            port = "5432",
                                            database = "festival")
        self.cursor = self.connection.cursor()

   
    def query_titles(self):
        self.cursor.execute('SELECT title FROM blog')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec