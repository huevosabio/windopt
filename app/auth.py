from mongoengine import *
import json
from passlib.apps import custom_app_context as pwd_context
from flask import Flask, abort, request, jsonify, g, url_for
from app import app, conn
from functools import wraps
import jwt
from datetime import timedelta, datetime
from errors import BadRequestException, UserException

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
        except jwt.DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except jwt.ExpiredSignature:
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

@app.route('/api/users', methods = ['POST'])
def create_user():
    '''
    Assumes a request with Content-Type: application/json.
    The json should be of the form:
    {
        "username":<username>,
        "password":<password>
    }
    '''
    user_data = request.json
    # check that the request is well formed.
    if 'username' not in user_data or 'password' not in user_data:
        raise BadRequestException('Malformed request.')

    # check that user does not exist
    if User.objects(username = user_data['username']).first():
        raise UserException('Username already exists.')

    else:
        user = User(username = user_data['username'])
        user.hash_password(user_data['password'])
        user.save()
        token = create_token(user)
        return jsonify(message = 'User created successfully.', user = user.to_json(), token = token)

@app.route('/api/users/<username>', methods = ['GET', 'PUT', 'DELETE'])
@login_required
def get_or_update_user(username):
    '''
    GET:
        Returns the user info (username)
    PUT:
        Updates user info (pwd)
    DELETE:
        Deletes user
    '''
    try:
        user = User.objects.get(username = username)
    except User.DoesNotExist:
        raise UserException('User does not exist.')
    if request.method == 'GET':
        return jsonify(username = user.username, message = 'User retrieved successfully')
    elif request.method == 'PUT' and g.user.username == username:
        # Method should be used only for changing password
        try:
            user.hash_password(request.json['password'])
            user.save()
            return jsonify(message = 'Password updated successfully.')
        except:
            raise BadRequestException('There was an error in the request.')
    elif request.method == 'DELETE' and auth.username == username:
        user.delete()
        return jsonify(message = 'User deleted.')
    else:
        raise BadRequestException('Your request was not understood by the server.')