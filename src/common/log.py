#    Handles logging with many labels and a output file, runs on another
#    process to avoid IO blocking.
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

import json as _json
from traceback import format_exception
from sys import exc_info
from multiprocessing import Process, Queue
from .utils import (format_date, now_timestamp, fix_whitespace, exists)

DEBUG = False
OUTPUT_FILE = None

# Access to 'messages' must be serialized
messages = Queue()

def _output(_type, msg, params=None):
    global messages
    _out = _build_str(_type, msg, params)
    messages.put(_out)

def _build_str(_type, msg, params):
    if isinstance(msg, list):
        msg = ', '.join(msg)
    date = format_date(now_timestamp())
    if exists(params):
        return "[{}] {}{}{}: {}".format(
                    date,
                    _type,
                    " - " if msg[0] != "\n" else "",
                    msg,
                    ", ".join(map(fix_whitespace, params)))
    else:
        return "[{}] {}{}{}".format(
                    date,
                    _type,
                    " - " if msg[0] != "\n" else "",
                    msg)

def debug(msg, *params):
    if DEBUG:
        _output("DEBUG", msg, params)

def message(msg, *params):
    _output("MESSAGE", msg, params)

def request(req):
    # Needed?
    pass

def error(err, label=None):
    try:
        raise err
    except Exception:
        lines = format_exception(*exc_info())
        padding = '-' * 30
        msg = "\n{0}\n{1}{0}\n".format(padding, ''.join(lines))

    if label is None:
        _type = str(type(err))
    else:
        _type = "({}) {}".format(label, type(err))

    _output(_type, msg)

def json(msg, _dict):
    _output("JSON", msg, _json.dumps(_dict))

def fatal(*msg):
    _output("FATAL", msg)

def loop(messages):
    def write(writer, messages):
        while True:
            # Since it keeps retrying and only this thread consumes from
            # Queue, Queue().empty() doesn't need to be thread safe
            if not messages.empty():
                msg = messages.get()

                # IO bound
                writer(msg)

    # Re-open log file if anything goes wrong
    while True:
        try:
            if exists(OUTPUT_FILE) and not DEBUG:
                with open(OUTPUT_FILE, "a") as _file:
                    write(_file.write, messages)
            else:
                write(print, messages)
        except Exception as e:
            error(e, label="LOG_PROCESS")

def ConfigLog(app):
    global DEBUG, OUTPUT_FILE
    DEBUG = app.config["DEBUG"]
    OUTPUT_FILE = app.config["LOG_FILE"] or None

    # Run log in another process
    p = Process(target=loop, args=(messages,))
    p.daemon = True
    p.start()

