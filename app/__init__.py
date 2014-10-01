import os
from flask import Flask

UPLOAD_FOLDER = '/home/ubuntu/windDayApp/tmp'

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC'] = '/home/ubuntu/windDayApp/app/static'

from app import upload
from app import windday
from app import visualization
from app import lostshifts
from app import cranetest
