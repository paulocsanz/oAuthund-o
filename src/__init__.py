from flask import Flask
app = Flask(__name__)

from .common import InitializeLib
from .config import Config

# Pass config values to Flask config
for key, value in Config.__dict__.items():
    if not (key.startswith("__") and key.endswith("__")):
        app.config[key] = value

InitializeLib(app)
from .common import session

from . import views

if __name__ == "__main__":
    app.run(host=app.config["HOST"],
            port=app.config["PORT"],
            debug=app.config["DEBUG"])
