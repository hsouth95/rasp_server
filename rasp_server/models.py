import sqlite3

class User:
    """A basic User class."""
    def __init__(self, nickname):
        self.user_key = None
        self.nickname = nickname
        self.permissions = None
        self.picture = None
        self.home = 1

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
    @staticmethod
    def get(key, db):
        cursor = db.cursor()
        rotation = cursor.execute("select * from rotation where rotation_key = ?", [key]).fetchone()
        return dict(rotation)
    
    @staticmethod
    def set_next(key, db):
        # get current order
        # get next rot_user
        cursor = db.cursor()
        rotation = dict(cursor.execute("select * from rotation where rotation_key = ?", [key]).fetchone())
        if rotation:
            previous_person = rotation["next"]
            if previous_person:
                cursor.execute("update rotation set next = ?", [Rotation_User.get_next_user_key(previous_person, key, db)])
                db.commit()


class Rotation_User:
    def create(self, user_key, rotation_key, db):
        cursor = db.cursor()
        try:
            cursor.execute("insert into rotationuser (rotation, user) values (?, ?)", [rotation_key, user_key])
            db.commit()
        except sqlite3.Error as err:
            raise err
    
    @staticmethod
    def get_by_rotation(rotation_key, db):
        cursor = db.cursor()
        return map(dict, cursor.execute("select * from rotationuser where rotation = ?", [rotation_key]).fetchall())
    
    @staticmethod
    def get_by_user(user_key, db):
        cursor = db.cursor()
        return map(dict, cursor.execute("select * from rotationuser where user = ?", [user_key]).fetchall())

    @staticmethod
    def get_next_user_key(previous_user, rotation_key, db):
        cursor = db.cursor()
        next_user = cursor.execute("select user from rotationuser where rotation = %s and sort_order = (select MAX(sort_order) from rotationuser where user = ?) + 1" % rotation_key, [previous_user]).fetchone()
        if next_user:
            return dict(next_user)["user"]
        return 1