from .. import app
from . import DB
from ..common.utils import fernet_key, encrypt, decrypt, InvalidToken, hash

class Authentication:
    def __init__(self, username, password, cookie, id = None, access_token = None, refresh_token = None, is_encrypted=False):
        self.id = id
        self.access_token = access_token or fernet_key()
        self.refresh_token = refresh_token or fernet_key()
        self.username = username
        if is_encrypted:
            self.encrypted_cookie = cookie
            self.encrypted_password = password
        else:
            self.encrypted_cookie = encrypt(self.access_token, cookie)
            self.encrypted_password = encrypt(self.refresh_token, password)

    def save(self):
        with DB() as db:
            self.id = db.insert(
                    "INSERT INTO authentications "
                    "(username, access_token_hash, encrypted_cookie, refresh_token_hash, encrypted_password) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    self.username,
                    hash(self.access_token),
                    self.encrypted_cookie,
                    self.encrypted_password,
                    hash(self.refresh_token))

    def retrieve_password(refresh_token):
        _hash = hash(refresh_token)
        with DB() as db:
            encrypted_password = db.find_all(
                    "SELECT encrypted_password "
                    "FROM authentications "
                    "WHERE refresh_token_hash = %s;",
                    _hash)
        return decrypt(refresh_token, encrypted_password)

    def retrieve_cookie(access_token):
        with DB() as db:
            encrypted_cookie = db.find(
                    "SELECT encrypted_cookie "
                    "FROM authentications "
                    "WHERE access_token_hash = %s;",
                    hash(access_token))
        return decrypt(access_token, encrypted_cookie)

    def get_username(access_token):
        with DB() as db:
            return db.find(
                    "SELECT username "
                    "FROM authentications "
                    "WHERE access_token_hash = %s;",
                    hash(access_token))
