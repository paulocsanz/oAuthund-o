from . import DB

class Authorization:
    def __init__(self, client_id, username, code, duration, id=None):
        self.id = id
        self.client_id = client_id
        self.username = username
        self.code = code
        self.duration = duration

    def save(self, db = None):
        def func(db):
            self.id = db.insert(
                    "INSERT INTO authorizations "
                    "(client_id, username, code, duration) "
                    "VALUES (%s, %s, %s, %s);",
                    self.client_id,
                    self.username,
                    self.code,
                    self.duration)

        if db is None:
            with DB() as db:
                func(db)
        else:
            func(db)

    def find(client_id, username):
        with DB() as db:
            return Authorization(client_id, username, *db.find(
                "SELECT code, duration "
                "FROM authorizations "
                "WHERE client_id = %s"
                "      AND username = %s;",
                client_id, username))
