import os
import sqlite3
import json
import models

from flask import Flask, g, request
from functools import wraps
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

def get_home():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("select * from home limit 1")
        house = cursor.fetchone()

        if house:
            return dict(house)
        return None
    except sqlite3.Error as err:
        raise err

def authorise(permissions):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            auth = request.authorization
            if not auth.username or is_authorised(permissions, auth.username):
                return "Auth failed", 401
            return func(*args, **kwargs)
        return wrapper
    return real_decorator

def is_authorised(permission_required, user_key):
    user = User.get(user_key, get_db())
    if user:
        permission = user["permissions"]
        if permission == permission_required or permission == "su" or (permission == "w" and permission_required == "r"):
            return True
    return False

class User:
    """A basic User class."""
    def __init__(self, nickname):
        self.user_key = None
        self.nickname = nickname
        self.permissions = None
        self.picture = None
        self.home = get_home()["id"]

    def create(self, db):
        """Create the User in the given database.

            Args:
                db: Database object used to execute the command
            Note:
                Any operations stay within a transaction, therefore
                the given Database object will need to be committed.
                This operation will create the User as having all
                permissions if it is the first User to be created.
        """
        # Check if this is the first User being created
        if User.get(1, db) == None:
            self.permissions = "su"
        else:
            self.permissions = "r"
        cursor = db.cursor()
        try:
            cursor.execute("insert into users (nickname, picture, permissions, home) values (?, ?, ?, ?)", [self.nickname, self.picture, self.permissions, self.home])
            db.commit()
            self.user_key = cursor.lastrowid
            return self.user_key
        except sqlite3.Error as er:
            raise er

    def update(self, db):
        """Updates the User in the given database

            Args:
                db: Database object used to execute the command
        """
        cursor = db.cursor()
        try:
            cursor.execute("update users set nickname = ? where user_key = ?", [self.nickname, self.user_key])
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

    @staticmethod
    def list(db):
        """Retrieves the nicknames of all the User's

            Args:
                db: Database object used to execute the command
        """
        cursor = db.cursor()
        try:
            cursor.execute("select nickname from users")
            users = cursor.fetchall()

            if users:
                return map(dict, users)
            return None
        except sqlite3.Error as er:
            raise er

class Rotation:
    def __init__(self, name):
        self.name = name
        self.rotation_key = None
    
    def create(self, db):
        # Check if this is the first User being created
        cursor = db.cursor()
        try:
            cursor.execute("insert into rotation (name) values (?)", [self.name])
            db.commit()
            self.rotation_key = cursor.lastrowid
            return self.rotation_key
        except sqlite3.Error as er:
            raise er

class Rotation_User:
    def create(self, user_key, rotation_key, db):
        cursor = db.cursor()
        try:
            cursor.execute("insert into rotationuser (rotation_key, user_key) values (?, ?)", [rotation_key, user_key])
            db.commit()
        except sqlite3.Error as err:
            raise err
            
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


@app.route('/hello')
def hello():
    """Handler for API discovery"""
    return "hello"


@app.route('/user', methods=["POST"])
def create_user():
    """Handler for retrieving a new User key"""
    user_nickname = request.values.get("nickname")
    if user_nickname:
        user = User(user_nickname)
        db = get_db()
        try:
            user_id = user.create(db)
        except sqlite3.Error as err:
            return err.message, 500
        db.commit()
        return str(user_id)
    else:
        return "Nickname must be provided", 400


@app.route('/user', methods=["GET"])
def list_users():
    """Handler for retrieving all Users"""
    try:
        users = User.list(get_db())

        if users:
            return json.dumps(users)
        return json.dumps([])
    except sqlite3.Error as er:
        return er.message, 500


@app.route('/user/<key>')
def get_user(key):
    """Handler for retrieving User information"""
    user = User.get(key, get_db())

    if user:
        return json.dumps(user)
    return "Cannot find User", 404


@app.route('/user/<key>', methods=["PUT"])
def update_user(key):
    user_nickname = request.values.get("nickname")

    if user_nickname:
        user = User(user_nickname)
        user.user_key = key

        try:
            user.update(get_db())

            return "Successful", 200
        except sqlite3 as er:
            return er.message, 500
    return "Nickname must be provided", 400

@app.route('/user/<key>', methods=["DELETE"])
@authorise("su")
def delete_user(key):
    # The first User can never be deleted
    if key != 1:
        return str(key)

@app.route('/home', methods=["GET"])
def list_home():
    return json.dumps(get_home())

if __name__ == '__main__':
    app.run()
