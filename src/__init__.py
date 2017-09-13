from flask import Flask
app = Flask(__name__)

from .common import InitializeLib
from .common.db import DB
from ..config import Config

for key, value in Config.__dict__.items():
    if not (key.startswith("__") and key.endswith("__")):
        app.config[key] = value

InitializeLib(app)
from .common import session

from . import views
app.run(host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"])
