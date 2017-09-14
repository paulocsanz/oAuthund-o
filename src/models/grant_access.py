from .. import app
from ..common.utils import decrypt, encrypt, fernet_key, hash
from . import DB
from .authorization import Authorization

class GrantAccess:
    def __init__(self, client_id, access_token = None, refresh_token = None,
                 valid = True, encrypted=False, code=None):
        self.client_id = client_id
        if encrypted:
            self.code = code
            self.access_token = decrypt(self.code, access_token)
            self.refresh_token = decrypt(self.code, refresh_token)
        else:
            self.code = fernet_key()
            self.access_token = encrypt(self.code, access_token)
            self.refresh_token = encrypt(self.code, refresh_token)
        self.valid = valid

    def save(self):
        with DB() as db:
            self.id = db.insert(
                    "INSERT INTO granted_accesses "
                    "(client_id, code_hash, access_token, refresh_token, valid) "
                    "VALUES (%s, %s, %s, %s, %s);",
                    self.client_id,
                    hash(self.code),
                    self.access_token,
                    self.refresh_token,
                    True)

    def grant(code, client_id, client_secret):
        with DB() as db:
            req_id, access_token, refresh_token = db.find(
                    "SELECT ga.id, ga.access_token, ga.refresh_token "
                    "FROM granted_accesses ga "
                    "INNER JOIN applications app "
                    "  ON app.client_id = ga.client_id "
                    "WHERE code_hash = %s" 
                    "      AND app.client_id = %s"
                    "      AND app.client_secret = %s"
                    "      AND ga.valid = %s;",
                    hash(code),
                    client_id,
                    client_secret,
                    True)
            db.exec("UPDATE granted_accesses "
                    "SET valid = %s "
                    "WHERE id = %s",
                    False,
                    req_id)
            return decrypt(code, access_token), decrypt(code, refresh_token)
