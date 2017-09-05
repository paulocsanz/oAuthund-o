#    Script copies 'dependencies/config.py.example' to 'config.py' if it
#    doesn't exist yet, reads it after the user modifies MYSQL_USER and
#    MYSQL_PASSWORD, drops the priviledge, creates folders to hold files
#    and its thumbs, create virtualenv, join it, install/update
#    dependencies with 'pip', creates DB if non existent.
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

from os import getcwd
from os.path import join, isfile, isdir
from subprocess import Popen, DEVNULL

# Copy config and restrict its access
if not isfile("config.py"):
    print("Copied 'dependencies/config.py.example' to 'config.py'")
    print("If in Production please change DEBUG to False, PORT to 80 and put the appropriate HOST/MYSQL_HOST\n")
    Popen(["cp",
           "dependencies/config.py.example",
           "config.py"],
           stderr=DEVNULL).wait()

    # Creates empty __init__.py to make folder a python package
    open("__init__.py", "a").close()

DB_USER, DB_PASSWORD = "", ""
def load_config():
    """Dynamically read config after editing MySQL's data"""
    global DB_USER, DB_PASSWORD
    with open("config.py", "r") as f:
        content = f.read()
        exec(content, globals())

    DB_USER, DB_PASSWORD = Config.MYSQL_USER, Config.MYSQL_PASSWORD
    return "" in [DB_USER, DB_PASSWORD]

while load_config():
    print("Please edit 'config.py' to include MySQL's user and password (MYSQL_USER, MYSQL_PASSWORD)")
    input("After doing that press enter to continue\n")

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

# Handle DB
print("Creating database if non-existent.")
with open(join(getcwd(), 'dependencies/create.sql')) as f:
    content = f.read().replace('\n','')

"""Spawns MySQL and fakes tty to pass password securely to process"""
p = spawn("mysql",
          ["-u",
           DB_USER,
           "-e",
           content,
           "-p"])
p.expect("Enter password:")
p.send(DB_PASSWORD + '\n')
p.wait()
print("Database created.\n")
