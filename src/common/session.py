#    Creates abstraction to use an encrypted session, protecting the
#    token not only from tampering but from being read by unauthorized
#    entities. Creates an wrapper for the 'g' object, with a private
#    attribute.
#
#    Allows managing session during 'before_requests' and
#    'after_requests'.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
from hashlib import sha256
from base64 import urlsafe_b64encode as b64encode
from flask import request, g
from cryptography.fernet import Fernet, InvalidToken
from .utils import exists

log = None
fernet = None

class EncryptedSession(dict):
    def __init__(self, app, _log, debug_key=None):
        global fernet, log
        if app.config["DEBUG"]:
            key = debug_key
        else:
            # Since the SECRET_KEY must already be secure we can hash it
            # instead of using a key-stretching algorithm
            key = (b64encode(sha256(
                    bytes(app.config["SECRET_KEY"], "utf-8"))
                    .digest())
                    .decode('utf-8'))
            # sha256 outputs 32 bytes, the same size of Fernet keys (44 base64 encoded characters)
        fernet = Fernet(key)
        log = _log

        @app.before_request
        def decrypt():
            # Only decrypts if session wasn't used in a 'before_request'
            # that ran before this function
            EncryptedSession._decrypt_if_not()

        @app.after_request
        def encrypt(response):
            # Session is re-encrypted in this function, if it's used in a
            # 'after_request' that runs after this function it will be
            # re-encrypted after the change
            g._response = response
            EncryptedSession.encrypt_session()
            return response

    def decrypt_session(self=None):
        g._decrypted_session = {}
        if 'e' not in request.cookies.keys():
            return

        try:
            data = fernet.decrypt(bytes(request.cookies['e'], 'utf-8'))
            g._decrypted_session = json.loads(str(data, 'utf-8'))
        except InvalidToken as e:
            # Refreshing SECRET_KEY destroys all existent sessions, so ignore them
            # Logging doesn't hurt since you shouldn't refresh your SECRET_KEY that frequently
            # and it will catch any actual problem
            log.error(e, label="SESSION_DECRYPTION")

    def encrypt_session(self=None):
        g._response.delete_cookie('e')
        if g._decrypted_session == {}:
            return

        _bytes = bytes(json.dumps(g._decrypted_session), 'utf-8')
        g._response.set_cookie('e',
                               str(fernet.encrypt(_bytes), 'utf-8'),
                               httponly=True)

    def _decrypt_if_not(self=None):
        if not exists(getattr(g, '_decrypted_session', None)):
            # Session is being accessed before the EncryptedSession's
            # 'before_request'
            EncryptedSession.decrypt_session()

    def _reencrypt_if_changed(self=None):
        if exists(getattr(g, '_response', None)):
            # Session has already been encrypted by EncryptedSession's
            # 'after_request', but has been changed, re-encrypt it
            EncryptedSession.encrypt_session()

    # Dict wrapper taking into account the edge cases of the functions above
    def __len__(self):
        self._decrypt_if_not()
        return g._decrypted_session.__len__()

    def __getitem__(self, key):
        self._decrypt_if_not()
        return g._decrypted_session.__getitem__(key)

    def __setitem__(self, key, value):
        self._decrypt_if_not()
        g._decrypted_session.__setitem__(key, value)
        self._reencrypt_if_changed()

    def __hash__(self):
        self._decrypt_if_not()
        return g._decrypted_session.__hash__()

    def __delitem__(self, key):
        self._decrypt_if_not()
        g._decrypted_session.__delitem__(key)
        self._reencrypt_if_changed()

    def __repr__(self):
        self._decrypt_if_not()
        return g._decrypted_session.__repr__()

    def __str__(self):
        self._decrypt_if_not()
        return g._decrypted_session.__str__()

    def __dict__(self):
        self._decrypt_if_not()
        return g._decrypted_session

    def get(self, key, *default):
        self._decrypt_if_not()
        return g._decrypted_session.get(key, *default)

    def pop(self, key, *default):
        self._decrypt_if_not()
        ret = g._decrypted_session.pop(key, *default)
        self._reencrypt_if_changed()
        return ret

    def popitem(self):
        self._decrypt_if_not()
        ret = g._decrypted_session.popitem()
        self._reencrypt_if_changed()
        return ret

    def items(self):
        self._decrypt_if_not()
        return g._decrypted_session.items()

    def keys(self):
        self._decrypt_if_not()
        return g._decrypted_session.keys()

    def values(self):
        self._decrypt_if_not()
        return g._decrypted_session.values()

    def setdefault(self, key, *default):
        self._decrypt_if_not()
        ret = g._decrypted_session.setdefault(key, *default)
        self._reencrypt_if_changed()
        return ret

    def update(**other):
        self._decrypt_if_not()
        ret = g._decrypted_session.update(**other)
        self._reencrypt_if_changed()
        return ret
