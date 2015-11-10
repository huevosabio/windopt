from flask import Flask, abort, request, jsonify, g, url_for
from app import app
from errors import BadRequestException, UserException
from dbmodel import User, auth
import cPickle


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
	if 'username' not in user_data and 'password' not in user_data:
		raise BadRequestException('Malformed request.')

	# check that user does not exist
	if User.objects(username = user_data['username']).first():
		raise UserException('Username already exists.')

	else:
		user = User(username = user_data['username'])
		user.hash_password(user_data['password'])
		user.save()
	return jsonify(message = 'User created successfully.', user = user.to_json())

@app.route('/api/users/<username>', methods = ['GET', 'PUT', 'DELETE'])
@auth.login_required
def get_or_update_user(username):
	try:
		user = User.objects.get(username = username)
	except User.DoesNotExist:
		raise UserException('User does not exist.')
	if request.method == 'GET':
		return jsonify(username = user.username, message = 'User retrieved successfully')
	elif request.method == 'PUT':
		user.