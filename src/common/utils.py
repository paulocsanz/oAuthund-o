from datetime import datetime
from random import SystemRandom
from string import ascii_letters, digits
from .errors import NoDateFormat
import re

DATE_FORMAT = None

def ConfigUtils(app):
    global DATE_FORMAT
    DATE_FORMAT = app.config["DATE_FORMAT"]

    app.jinja_env.filters['length'] = len
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['exists'] = exists
    app.jinja_env.filters['is_empty'] = is_empty
    app.jinja_env.filters['int'] = int_or_zero
    app.jinja_env.filters['str'] = str_or_empty

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
