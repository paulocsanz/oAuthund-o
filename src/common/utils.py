from datetime import datetime
from json import dumps as json_dumps
from random import SystemRandom
from string import ascii_letters, digits
from cryptography.fernet import Fernet, InvalidToken
from .errors import NoDateFormat
from hashlib import sha256
import re

def ConfigUtils(app):
    global DATE_FORMAT
    DATE_FORMAT = app.config["DATE_FORMAT"]

    app.jinja_env.filters['length'] = len
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['exists'] = exists
    app.jinja_env.filters['is_empty'] = is_empty
    app.jinja_env.filters['int'] = int_or_zero
    app.jinja_env.filters['str'] = str_or_empty
    app.jinja_env.filters['optional'] = optional

def optional(txt):
    return txt if txt is not None else ""

def hash(content):
    sha = sha256()
    if not isinstance(content, bytes):
        content = bytes(str(content), 'utf-8')
    sha.update(content)
    return sha.hexdigest()

def fernet_key():
    return str(Fernet.generate_key(), 'utf-8')

def encrypt(key, value):
    if not isinstance(key, bytes):
        key = bytes(str(key), 'utf-8')
    if not isinstance(value, bytes):
        value = bytes(str(value), 'utf-8')
    fernet = Fernet(key)
    return str(fernet.encrypt(value), 'utf-8')

def decrypt(key, value):
    if not isinstance(key, bytes):
        key = bytes(str(key), 'utf-8')
    if not isinstance(value, bytes):
        value = bytes(str(value), 'utf-8')
    fernet = Fernet(key)
    return str(fernet.decrypt(value), 'utf-8')

DATE_FORMAT = None

def format_title(txt):
    words = []
    for w in txt.split(" "):
        if len(w) > 1:
            words += [w[0].upper() + w[1:].lower()]
        else:
            words += [w.lower()]
    return " ".join(words)

def str_or_empty(txt):
    return convert_or_default(str, txt, '')

def int_or_zero(num):
    return convert_or_default(int, num, 0)

def convert_or_default(func, arg, default):
    try:
        return func(arg) or default
    except Exception:
        return default

def fix_whitespace(txt):
    return re.sub(r'[\t\n]*[\ ]+', ' ', str_or_empty(txt))

def exists(var):
    return var is not None

def is_empty(var):
    return not exists(var) or len(var) == 0

def format_date(timestamp):
    if not exists(DATE_FORMAT):
        raise NoDateFormat()
    return (datetime.fromtimestamp(timestamp)
                    .strftime(DATE_FORMAT))

def now_timestamp():
    return datetime.now().timestamp()

def random_string(size, chars=ascii_letters+digits+'-_'):
    return ''.join(SystemRandom().choice(chars)
            for i in range(size))

def add_arg(uri, **kwargs):
    char = "&" if "?" in uri else "?"
    for key, value in kwargs.items():
        uri += "{}{}={}".format(char, key, value)
        char = "&"
    return uri

def object_json(obj):
    # Only public non-function attributes
    attrs = {k:v for k, v in obj.__dict__.items()
                if not (k.startswith("_")
                        or callable(k))}
    return json_dumps(attrs)

def _photo_uri(photo_id):
    return "https://sigadocker.ufrj.br:8090/{}".format(photo_id)
