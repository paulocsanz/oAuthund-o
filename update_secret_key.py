from string import ascii_letters, digits
from random import SystemRandom
from re import sub

KEY_SIZE = 30
def random_string(size, chars=ascii_letters+digits+'-_'):
    return ''.join(SystemRandom().choice(chars)
            for i in range(size))

with open("src/config.py", "r") as f:
    content = f.read()

key = random_string(KEY_SIZE)
content = sub(r"SECRET_KEY = \"[\w_\-<>]*\"",
              "SECRET_KEY = \"{}\"".format(key),
              content)
with open("config.py", "w") as f:
    f.write(content)
