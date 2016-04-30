import os
from flask import Flask, send_from_directory, jsonify
from config import DB_URI, DB_USER, DB_PWD, ENV_NAME, BROKER_URL, DOC_LINK, DOC_EMAIL
from mongoengine import connect
from celery import Celery
from kombu import Queue

UPLOAD_FOLDER =  os.getcwd() + '/tmp'

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask('windopt', static_url_path = '', static_folder = os.getcwd() + '/gui/app')
CELERY_QUEUES = (
    Queue('default',routing_key='task.#'),
    Queue('train_wind_model',routing_key='train_wind_model'),
    Queue('calculate_expected_winddays',routing_key='calculate_expected_winddays'),
    Queue('calculate_windday_risks', routing_key = 'calculate_windday_risks'),
    Queue('unpack_layers', routing_key = 'unpack_layers'),
    Queue('calculate_tsp', routing_key='calculate_tsp')
)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC'] = os.getcwd() + '/app/static'
#TODO: Remove this from here and place it in an env var.
app.config['SECRET_KEY'] = 'die luft der freiheit weht'
app.config.update(
    CELERY_DEFAULT_QUEUE = 'default',
    CELERY_QUEUES=CELERY_QUEUES,
    CELERY_BROKER_URL=BROKER_URL,
    CELERY_RESULT_BACKEND=BROKER_URL,
    CELERY_ROUTES=({'train_wind_model':{'queue':'train_wind_model','routing_key': 'train_wind_model'}},),
    DB_URI = DB_URI,
    DB_USER = DB_USER,
    DB_PWD = DB_PWD,
    )

if ENV_NAME == 'local':
    # If local, assume that there is a local mongo instance
    conn = connect('windops', host = DB_URI, port = 27017)
else:
    # Otherwise, use env variables to connect
    conn = connect('windops', host='mongodb://'+ DB_USER + ':' + DB_PWD + '@' + DB_URI)

celery = make_celery(app)

#---Static Files--
@app.route('/')
def send_index():
	return app.send_static_file('index.html')
@app.route('/bower_components/<path:filename>')
def send_bower_components(filename):
	return send_from_directory(os.getcwd()+'/gui/bower_components/',filename)

#---Support ---
@app.route('/api/info')
def send_support_info():
    email = DOC_EMAIL
    link = DOC_LINK
    return jsonify(email = email, link = link, message = None)

from app import auth
from app import windday
from app import upload
from app import cranetest
from app import cranepath
from app import dbmodel
from app import costs
