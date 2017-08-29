from random import SystemRandom
from string import ascii_letters, digits

def random_string(size, chars=ascii_letters+digits+'-_'):
    return ''.join(SystemRandom().choice(chars)
            for i in range(size))

def add_arg(uri, **kwargs)
    char = "&" if "?" in uri else "?"
    for key, value in kwargs.items():
        uri += "{}{}={}".format(char, key, value)
        char = "&"
    return uri
