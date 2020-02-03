from ..common.utils import random_string
from .. import app
from . import DB

class Application:
    def __init__(self, creator_username, name, description, redirect_uri,
                 id=None, client_id=None, client_secret = None):
        self.id = id
        self.name = name
        self.creator_username = creator_username
        self.description = description
        self.redirect_uri = redirect_uri
        self.client_id = client_id or random_string(app.config["TOKEN_SIZE"])
        self.client_secret = client_secret or random_string(app.config["TOKEN_SIZE"])

    def save(self):
        if self.id is None:
            with DB() as db:
                self.id = db.insert(
                        "INSERT INTO applications "
                        "(creator_username, name, description, redirect_uri, client_id, client_secret) "
                        "VALUES (%s, %s, %s, %s, %s, %s);",
                        self.creator_username,
                        self.name,
                        self.description,
                        self.redirect_uri,
                        self.client_id,
                        self.client_secret)
        else:
            with DB() as db:
                db.exec(
                        "UPDATE applications "
                        "SET name = %s, description = %s, redirect_uri = %s "
                        "WHERE client_id = %s;",
                        self.name,
                        self.description,
                        self.redirect_uri,
                        self.client_id)

    def delete(username, client_id):
        with DB() as db:
            db.exec("DELETE FROM applications "
                    "WHERE creator_username = %s "
                    "      AND client_id = %s;",
                    username,
                    client_id)

    def find_by_client(client_id):
        with DB() as db:
            return Application(*db.find(
                "SELECT creator_username, name, description, redirect_uri, id, client_id, client_secret "
                "FROM applications "
                "WHERE client_id = %s",
                client_id))

    def find_by_user(username):
        with DB() as db:
            return [Application(*app) for app in db.find_all(
                "SELECT creator_username, name, description, redirect_uri, id, client_id, client_secret "
                "FROM applications "
                "WHERE creator_username = %s",
                username)]
