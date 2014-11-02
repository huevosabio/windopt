from mongoengine import *
import json
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from flask.ext.httpauth import HTTPBasicAuth
from flask import Flask, abort, request, jsonify, g, url_for
from app import app

with open('/home/ubuntu/windDayApp/config.json') as f:
    dbdata = json.loads(f.read())

conn = connect('', host='mongodb://'+dbdata['DB_USER']+':'+dbdata['DB_PWD']+'@ds049180.mongolab.com:49180/windops')
auth = HTTPBasicAuth()

app.config['SECRET_KEY'] = 'die luft der freiheit weht'
class User(Document):
    email = StringField(unique=True)
    password = StringField()
    
    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)
    
    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'email': self.email })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.objects(email=data['email'])[0]
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        try:
            user = User.objects(email=username_or_token)[0]
            if not user.verify_password(password): return False
        except User.DoesNotExist:
            return False
    g.user = user
    return True
