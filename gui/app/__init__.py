import os
from flask import Flask, request, Response, redirect
from flask import send_file, make_response, abort
from flask.ext.mongoengine import MongoEngine
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource, Api
from bson.json_util import dumps

app = Flask(__name__,static_url_path='/dist')
api = Api(app)

app.config["MONGODB_SETTINGS"] = {'DB': "windops"}
app.config["SECRET_KEY"] = "titimania"

#extensions
db = MongoEngine(app)
auth = HTTPBasicAuth()

#return our AngularJS app
@app.route('/')
def index():
	return redirect('/index.html')

from app import schemas

from app.resources.auth import *
api.add_resource(Register,'/api/register')
api.add_resource(Login,'/api/login')


if __name__ == '__main__':
	app.run()