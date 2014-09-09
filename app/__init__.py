import os
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource, Api
from bson.json_util import dumps

app = Flask(__name__)
api = Api(app)

app.config["MONGODB_SETTINGS"] = {'DB': "windops"}
app.config["SECRET_KEY"] = "titimania"

#extensions
db = MongoEngine(app)
auth = HTTPBasicAuth()

from app import schemas

from app.resources.auth import *
api.add_resource(Register,'/api/register')
api.add_resource(Login,'/api/login')


if __name__ == '__main__':
	app.run()