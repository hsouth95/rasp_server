import os
import sqlite3
import json

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

from models import *

def get_home():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("select * from home")
        house = cursor.fetchall()

        if house:
            return dict(house)
        return None
    except sqlite3.Error as err:
        raise err

def authorise(permissions):
    def real_decorator(func):
        @wraps(func)
        def auth_wrapper(*args, **kwargs):
            auth = request.authorization
            if not auth.username or is_authorised(permissions, auth.username):
                return "Auth failed", 401
            return func(*args, **kwargs)
        return auth_wrapper
    return real_decorator

def is_authorised(permission_required, user_key):
    user = User.get(user_key, get_db())
    if user:
        permission = user["permissions"]
        if permission == permission_required or permission == "su" or (permission == "w" and permission_required == "r"):
            return True
    return False
       
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
        user = User(nickname=user_nickname)
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
        return json.dumps(user.to_dict())
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
        except sqlite3.Error as er:
            return er.message, 500
    return "Nickname must be provided", 400

@app.route('/user/<key>/sethome', methods=["PUT"])
def set_user_home(key):
    password = request.values.get("password")
    home = request.values.get("home_id")

    user = User.get(key, get_db())
    if user.add_to_home(home, password, get_db()):
        return "Success", 200
    return "Password did not match", 400

@app.route('/user/<key>', methods=["DELETE"])
#@authorise("su")
def delete_user(key):
    # The first User can never be deleted
    if key != 1:
        return str(key)

@app.route('/home', methods=["GET"])
def list_home():
    return json.dumps(Home.list(get_db()))

@app.route('/home/<key>', methods=["GET"])
def home_get(key):
    return json.dumps(Home.get(key, get_db()))

@app.route('/home', methods=["POST"])
#@authorise("su")
def create_home():
    name = request.values.get("name")
    password = request.values.get("password")
    home = Home(name, password)
    id = home.create(get_db())

    return str(id)

@app.route("/rotation/<key>", methods=["GET"])
def get_rotation(key):
    rotation = Rotation.get(key, get_db())
    return json.dumps(rotation)

@app.route("/rotation/<key>/setnext", methods=["POST"])
def set_next_rotation(key):
    Rotation.set_next(key, get_db())
    return "Success!", 200

if __name__ == '__main__':
    app.run()
