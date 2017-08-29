from .common import InitializeLib, session
from flask import Flask

app = Flask()
InitializeLib(app)

app.run(DEBUG=app.config["DEBUG"])
