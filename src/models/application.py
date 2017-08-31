from ..common.utils import random_string
from .. import app

class Application:
    def __init__(self, name, description, redirect_uri, id=None, client_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.redirect_uri = redirect_uri
        self.client_id = client_id or random_string(app.config["CLIENT_ID_LENGTH")

    def save(self):
        with DB() as db:
            self.id = db.insert(
                    "INSERT INTO applications "
                    "(name, description, redirect_uri, client_id) "
                    "VALUES (%s, %s, %s, %s);",
                    self.name,
                    self.description,
                    self.redirect_uri,
                    self.client_id)

    def find(client_id):
        with DB() as db:
            return Application(db.find(
                "SELECT name, description, redirect_uri, id, client_id "
                "FROM applications "
                "WHERE client_id = %s",
                client_id)
