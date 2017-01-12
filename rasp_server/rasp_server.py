import os
import sqlite3
import json

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


class User:
    """A basic User class."""
    def __init__(self, nickname):
        self.nickname = nickname

    def create(self, db):
        """Create the User in the given database.

            Args:
                db: Database object used to execute the command
            Note:
                Any operations stay within a transaction, therefore
                the given Database object will need to be committed
        """
        cursor = db.cursor()
        try:
            cursor.execute("insert into users (nickname) values (?)", [self.nickname])
            return cursor.lastrowid
        except sqlite3.Error as er:
            raise er

    @staticmethod
    def get(key, db):
        """Retrieves a User record with a given user_key.

            Args:
                key: The ID of the User record to retrieve
                db: Database object used to execute the command
        """
        cursor = db.cursor()
        try:
            cursor.execute("select * from users where user_key = ?", [key])
            user = cursor.fetchone()

            if user:
                return dict(user)
            return None
        except sqlite3.Error as er:
            raise er


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
    """Creates a Database."""
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
    return "hello"


@app.route('/user', methods=["POST"])
def get_user_key():
    """Handler for retrieving a new User key"""
    user_nickname = request.values.get("nickname")
    if user_nickname:
        user = User(user_nickname)
        db = get_db()
        try:
            user_id = user.create(db)
        except:
            return "Error creating User", 500
        db.commit()
        return str(user_id)
    else:
        return "Nickname must be provided", 400


@app.route('/user/<key>')
def get_user(key):
    """Handler for retrieving User information"""
    connections.append(key)
    user = User.get(key, get_db())

    if user:
        return json.dumps(user)
    return "Cannot find User", 404


if __name__ == '__main__':
    app.run()
