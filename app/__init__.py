import os
from flask import Flask

UPLOAD_FOLDER = 'tmp'

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import upload

