#    Loads configs for each 'lib' here to make it easier to use in
#    different flask projects.
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

from .session import EncryptedSession
from .headers import SecureHeader
from .db import ConfigDB

session = None
def InitializeLib(app):
    global session
    SecureHeader(app)
    session = EncryptedSession(
        app,
        log,
        debug_key=b'4444444444444444444444444444444444444444444=')
    ConfigDB(app, log)
