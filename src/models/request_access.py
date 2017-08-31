from ..common.utils import random_string
from .. import app
from .authorization import Authorization

class RequestAccess:
    def __init__(self, client_id, code = None
                 access_token = None, valid = True):
        self.client_id = client_id
        self.code = code or random_string(app.config["AUTH_CODE_LENGTH"])
        self.access_token = access_token or random_string(app.config["ACCESS_TOKEN_LENGTH"])
        self.valid = valid

    def save(self):
        with DB() as db:
            self.id = db.insert(
                    "INSERT INTO access_requests "
                    "(client_id, code, valid) "
                    "VALUES (%s, %s, %s, %s, %s);",
                    self.client_id,
                    self.access_token,
                    self.code,
                    True)

    def grant(code, client_secret):
        with DB() as db:
            req_id, client_id, access_token = db.find(
                    "SELECT req.id, req.access_token, app.client_secret"
                    "FROM access_requests req "
                    "INNER JOIN applications app "
                    "  ON app.client_id = req.client_id "
                    "WHERE req.code = %s" 
                    "      AND app.client_secret = %s"
                    "      AND req.valid = %s;",
                    code,
                    client_secret,
                    True)
            db.exec("UPDATE access_requests "
                    "SET valid = %s "
                    "WHERE id = %s",
                    False,
                    req_id)
            auth = Authorization(client_id,
                                 user_id,
                                 code,
                                 app.config["AUTH_DURATION"])
            auth.save()
            return auth
