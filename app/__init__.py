import os
from flask import Flask, send_from_directory

UPLOAD_FOLDER =  os.getcwd() + '/tmp'

app = Flask('windopt', static_url_path = '', static_folder = os.getcwd() + '/gui/app')
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['STATIC'] = '/var/www/windDayApp/app/static'

#---Static Files--
@app.route('/')
def send_index():
	return app.send_static_file('index.html')
@app.route('/bower_components/<path:filename>')
def send_bower_components(filename):
	return send_from_directory(os.getcwd()+'/gui/bower_components/',filename)

from app import upload
from app import windday
from app import visualization
from app import lostshifts
from app import cranetest
from app import cranepath
from app import dbmodel
from app import useradmin