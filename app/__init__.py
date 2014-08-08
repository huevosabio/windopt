import os
from flask import Flask

UPLOAD_FOLDER = 'tmp'

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC'] = 'app/static'

from app import upload
from app import windday
from app import visualization
