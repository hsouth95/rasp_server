import os
import sqlite3
from models import User

from flask import Flask, g, request
app = Flask(__name__)

# Load config from this file
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'rasp_server.db'),
    SECRET_KEY="DEVKEY",
    USERNAME='rasp_server_user',
    PASSWORD='default'
))

app.config.from_envvar('RASP_SERVER_SETTINGS', silent=True)

def connect_db():
    """Connects to the rasp_server database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the 
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database at the end of a request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initialises the database."""
    init_db()
    print("Initialised the database.")

connections = []

@app.route('/hello')
def hello():
	"""Handler for API discovery"""
	#user = User("batman")
	return "apple"

@app.route('/user', methods=["POST"])
def get_user_key():
	"""Handler for retrieving a new User key"""

	user_nickname = request.values.get("nickname")
	if user_nickname:
		db = get_db()
		cursor = db.cursor()
		cursor.execute("insert into users (nickname) values (?)", [user_nickname])
		db.commit()

		return str(cursor.lastrowid)
	else:
		return "You must provide a nickname", 400

@app.route('/user/<key>')
def get_user(key):
    connections.append(key)

    return get_file_contents()

@app.route('/connections')
def get_connections():
    return ", ".join(map(str, connections))

def get_file_contents():
	f = open("rasp_server/values.txt", "r")
	return f.read()

if __name__ == '__main__':
    app.run()
