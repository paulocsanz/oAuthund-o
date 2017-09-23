#    Script copies 'dependencies/config.py.example' to 'config.py' if it
#    doesn't exist yet (add MySQL info and SECRET_KEY automatically),
#    creates MySQL user and password reads it, creates virtualenv, join
#    it, install/update dependencies with 'pip', creates DB if non existent.
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

#!/usr/bin/env python3

from re import sub
from os import getcwd
from getpass import getpass
from random import SystemRandom
from subprocess import Popen, DEVNULL
from os.path import join, isfile, isdir
from string import ascii_letters, digits

def random_string(size, chars=ascii_letters+digits+'-_'):
    return ''.join(SystemRandom().choice(chars)
            for i in range(size))

KEY_SIZE = 30

db_username = "sigalogado"
db_password = random_string(KEY_SIZE)

if not isfile("config.py"):
    print("Copied 'dependencies/config.py.example' to 'config.py'")
    print("If in Production please change DEBUG to False, PORT to 80\n")
    with open("dependencies/config.py.example", "r") as fd:
        with open("config.py", "w+") as f:
            f.write(fd.read()
                      .replace("<MYSQL_USER>", db_username)
                      .replace("<MYSQL_PASSWORD>", db_password)
                      .replace("<SECRET_KEY>", random_string(KEY_SIZE)))

# Creates empty __init__.py to make folder a python package
open("__init__.py", "a").close()

# Handle virtualenv (make dependencies local instead of global)
if not isdir(".env"):
    print("Creating virtualenv")
    Popen(["virtualenv",
           "-p",
           "python3",
           ".env"],
           stderr=DEVNULL).wait()
    print("Virtualenv created")

print("Joining virtualenv\n")
__file__ = join(".env", "bin", "activate_this.py")
with open(__file__, "r") as f:
    exec(f.read())

print("Installing/updating requirements inside virtualenv")
Popen([".env/bin/pip",
       "install",
       "-Ur",
       "dependencies/requirements.txt"]).wait()
print("Requirements installed\n")

# Import after installing dependencies
from pexpect import spawn

def run_mysql_command(DB_USER, DB_PASSWORD, command):
    """Spawns MySQL and fakes tty to pass password securely to process"""
    p = spawn("mysql",
              ["-u",
               DB_USER,
               "-e",
               command.replace("\n", " "),
               "-p"])
    p.expect("Enter password:")
    p.send(DB_PASSWORD + '\n')
    p.wait()

# Handle DB
print("Please provide the MySQL information to setup the environment (empty to end installation)")
DB_USER = input("Username: ")
DB_PASSWORD = getpass(prompt="Password: ").replace("")
if "" in [DB_USER, DB_PASSWORD]:
    exit()

# Just, like, don't be an asshole, your admin info created with
# 'install.py' shouldn't try to inject SQL, thanks
def pseudo_filter(txt):
    txt = txt.replace("'", "''")
    txt = txt.replace('"', '""')
    return txt.replace("\\", "\\\\")

run_mysql_command(DB_USER, DB_PASSWORD, ("CREATE USER '{0}'@'localhost' IDENTIFIED BY '{1}';"
                                         "GRANT SELECT INSERT UPDATE DELETE ON sigalogado.* TO '{0}'@'localhost';"
                                        ).format(pseudo_filter(db_username),
                                                 pseudo_filter(db_password)))

print("Creating database if non-existent.")
with open(join(getcwd(), 'dependencies/create.sql')) as f:
    run_mysql_command(DB_USER, DB_PASSWORD, f.read())
    print("Database created.\n")
