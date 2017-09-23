from ..common.utils import _photo_uri
from . import DB

class User:
    def __init__(self, username, name, photo_id, id=None):
        self.id = id
        self.username = username
        self.name = name
        self.photo_id = photo_id
        self._photo_uri = _photo_uri(photo_id)

    def save(self):
        with DB() as db:
            self.id = db.insert(
                    "INSERT INTO users "
                    "(username, name, photo_id) "
                    "VALUES (%s, %s, %s);",
                    self.username,
                    self.name,
                    self.photo_id)
