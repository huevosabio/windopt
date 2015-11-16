import os
from flask import Flask, send_from_directory
from config import DB_URI, DB_USER, DB_PWD, ENV_NAME
from mongoengine import connect

UPLOAD_FOLDER =  os.getcwd() + '/tmp'

app = Flask('windopt', static_url_path = '', static_folder = os.getcwd() + '/gui/app')
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['STATIC'] = '/var/www/windDayApp/app/static'
#TODO: Remove this from here and place it in an env var.
app.config['SECRET_KEY'] = 'die luft der freiheit weht'

if ENV_NAME == 'local':
    # If local, assume that there is a local mongo instance
    conn = connect('windops', host = 'localhost', port = 27017)
else:
    # Otherwise, use env variables to connect
    conn = connect('windops', host='mongodb://'+ DB_USER + ':' + DB_PWD + '@' + DB_URI)

#---Static Files--
@app.route('/')
def send_index():
	return app.send_static_file('index.html')
@app.route('/bower_components/<path:filename>')
def send_bower_components(filename):
	return send_from_directory(os.getcwd()+'/gui/bower_components/',filename)

from app import auth
from app import upload
from app import windday
from app import visualization
from app import lostshifts
from app import cranetest
from app import cranepath
from app import dbmodel
from app import useradmin