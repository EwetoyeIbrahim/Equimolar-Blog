from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from . import utilities
from . import views

