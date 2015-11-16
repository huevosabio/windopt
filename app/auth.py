from mongoengine import *
import json
from passlib.apps import custom_app_context as pwd_context
from flask import Flask, abort, request, jsonify, g, url_for
from app import app, conn
from functools import wraps
import jwt
from datetime import timedelta, datetime

class User(Document):
    username = StringField(unique=True)
    password = StringField()
    
    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

class Role(Document):
    name = StringField(unique = True)
    description = StringField()

# Create admin account
@app.before_first_request
def create_admin():
    try:
        User.objects.get(username = 'admin')
    except User.DoesNotExist:
        admin = User(username = 'admin')
        admin.hash_password('admin')
        admin.save()
    return
def create_token(user):
    payload = {
        'sub': user.username,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=14)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'])
    return token.decode('unicode_escape')

def parse_token(request):
    token = request.headers.get('Authorization').split()[1]
    return jwt.decode(token, app.config['SECRET_KEY'])


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        g.username = payload['sub']

        return f(*args, **kwargs)

    return decorated_function

@app.route('/api/auth/login', methods=['POST'])
def login():
    user = User.objects(username = request.json['username'])[0]
    if not user or not user.verify_password(request.json['password']):
        response = jsonify(message='Wrong Email or Password')
        response.status_code = 401
        return response
    token = create_token(user)
    return jsonify(token=token)