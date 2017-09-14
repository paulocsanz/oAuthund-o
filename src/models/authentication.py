from .. import app
from . import DB
from ..common.utils import fernet_key, encrypt, decrypt, InvalidToken, hash

class Authentication:
    def __init__(self, username, password, cookie, id = None, code = None, refresh_token = None, is_encrypted=False):
        self.id = id
        self.code = code or fernet_key()
        self.refresh_token = refresh_token or fernet_key()
        self.username = username
        if is_encrypted:
            self.encrypted_cookie = cookie
            self.encrypted_password = password
        else:
            self.encrypted_cookie = encrypt(self.code, cookie)
            self.encrypted_password = encrypt(self.refresh_token, password)

    def save(self):
        with DB() as db:
            self.id = db.insert(
                    "INSERT INTO authentications "
                    "(username, code_hash, encrypted_cookie, refresh_token_hash, encrypted_password) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    self.username,
                    hash(self.code),
                    self.encrypted_cookie,
                    self.encrypted_password,
                    hash(self.refresh_token))

    def retrieve_password(username, refresh_token):
        _hash = hash(refresh_token)
        with DB() as db:
            encrypted_password = db.find_all(
                    "SELECT encrypted_password "
                    "FROM authentications "
                    "WHERE username = %s "
                    "      AND refresh_token_hash = %s;",
                    username,
                    _hash)
        return decrypt(refresh_token, encrypted_password)

    def retrieve_cookie(username, code):
        _hash = hash(code)
        with DB() as db:
            encrypted_cookie = db.find(
                    "SELECT encrypted_cookie "
                    "FROM authentications "
                    "WHERE username = %s "
                    "      AND code_hash = %s;",
                    username,
                    _hash)
        return decrypt(code, encrypted_cookie)
