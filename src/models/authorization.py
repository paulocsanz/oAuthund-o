from . import DB

class Authorization:
    def __init__(self, client_id, username, id=None, app_name = None, app_description = None):
        self.id = id
        self.client_id = client_id
        self.username = username
        self.app_name = app_name
        self.app_description = app_description

    def save(self, db = None):
        with DB(db) as db:
            self.id = db.insert(
                    "INSERT INTO authorizations "
                    "(client_id, username) "
                    "VALUES (%s, %s);",
                    self.client_id,
                    self.username)

    def find_all(username):
        with DB() as db:
            return [Authorization(*auth) for auth in db.find_all(
                "SELECT auth.client_id, auth.username, auth.id, app.name, app.description "
                "FROM authorizations auth "
                "INNER JOIN applications app "
                "  ON app.client_id = auth.client_id "
                "WHERE auth.username = %s;",
                username)]

    def find(client_id, username):
        with DB() as db:
            return Authorization(*db.find(
                "SELECT client_id, username, id "
                "FROM authorizations "
                "WHERE client_id = %s"
                "      AND username = %s;",
                client_id, username))

    def delete(username, client_id):
        with DB() as db:
            db.exec("DELETE FROM authorizations "
                    "WHERE username = %s "
                    "      AND client_id = %s;",
                    username,
                    client_id)
