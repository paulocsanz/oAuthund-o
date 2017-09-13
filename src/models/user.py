from . import DB

class User:
    def __init__(self, username, name, photo_uri):
        self.username = username
        self.name = name
        self.photo_uri = photo_uri
