#    Handles DB abstraction, interfacing with MySQL (flask_mysqlqdb)
#    while raising appropriate errors in a nice wrapper.
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

from flask_mysqldb import MySQL, MySQLdb
from .utils import exists, is_empty
from .errors import NoResult, UnexpectedError, InsertFailed, NoDBConfig
from codecs import register, lookup

# Make MySQL's utf8mb4 an alias for utf-8 in python, since MySQL's utf-8 is broken
# utf-8 uses 3 bytes in MySQL, when it regularly uses up to 4 bytes (basically excludes emojis)
register(lambda name: lookup("utf8") if name == 'utf8mb4' else None)

app = None
log = None
mysql = None

def ConfigDB(_app, _log):
    global app, log, mysql
    _app.config["MYSQL_CHARSET"] = "utf8mb4"
    app = _app
    log = _log
    mysql = MySQL(app)

class DB:
    def __init__(self, db = None):
        global app, log, mysql
        if None in [app, log, mysql]:
            raise NoDBConfig

        if db is None:
            self._app = app
            self.log = log
            self.connection = mysql.connection
        else:
            self = db

    def __enter__(self):
        try:
            self.cursor = self.connection.cursor()
        except AttributeError as ex:
            self.log.error(ex)
            raise UnexpectedError
        return self

    def __exit__(self, *args):
        """
        flask_mysqldb handles closing the connection, context is here to
        prevent the creation of N cursors (with independent connections)
        for N requests

        We should think about moving to raw MySQLdb lib and handle the
        closing while closing context, or use connections Pools
        """
        pass

    def __backend(self, command, parameters, many=False, _return=False,
                  return_id=False):
        self.log.debug("SQL query", command)
        if not is_empty(parameters):
            self.log.debug("Parameters", *parameters)

        exec_func = {True: self.cursor.executemany,
                     False: self.cursor.execute}
        try:
            exec_func[many](command, parameters)

            if not _return or return_id:
                self.connection.commit()

            if return_id:
                command = "SELECT LAST_INSERT_ID();"
                self.log.debug("SQL query", command)
                self.cursor.execute(command)

            if _return or return_id:
                response = self.cursor.fetchall()
                _empty = (exists(response)
                          and (is_empty(response)
                               or is_empty(response[0])))
                if _empty or not exists(response):
                    raise NoResult
                self.log.debug("Response", str(response))
                return response
        except (MySQLdb.Warning, MySQLdb.DataError, MySQLdb.IntegrityError) as ex:
            self.log.error(ex)
            self.connection.rollback()
            if self._app.config['DEBUG']:
                raise
            if _return or return_id:
                raise NoResult
            raise InsertFailed
        except (MySQLdb.InterfaceError, MySQLdb.OperationalError, MySQLdb.InternalError) as ex:
            self.log.error(ex)
            if self._app.config['DEBUG']:
                raise
            raise UnexpectedError

    def exec(self, command, *parameters, _return=False):
        return self.__backend(command, parameters, _return=_return)

    def exec_many(self, command, *parameters):
        return self.__backend(command, parameters, _many=True)

    def insert(self, command, *parameters, return_id=False):
        try:
            response = self.__backend(command, parameters, return_id=return_id)
        except NoResult as ex:
            if return_id:
                raise InsertFailed
            else:
                raise

        return DB._value(response)

    def __return(self, command, parameters):
        return self.__backend(command, parameters, _return=True)

    def find_all(self, command, *parameters):
        return self.__return(command, parameters)

    def find(self, command, *parameters):
        response = self.__return(command, parameters)
        return DB.tuple(response)

    def find_value(self, command, *parameters):
        response = self.__return(command, parameters)
        return DB._value(response)

    def tuple(response):
        if len(response) > 0:
            return response[0]

    def _value(response):
        if not is_empty(response) and not is_empty(response[0]):
            return response[0][0]
