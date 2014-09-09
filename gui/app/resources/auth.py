from app import db, auth
from app.schemas import User
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.restful import Resource, Api
from mongoengine.queryset import DoesNotExist

@auth.verify_password
def verify_password(username_or_token, password):
	user = User.verify_auth_token(username_or_token)
	if not user:
		#try to auntheticate with username/passworduser
		try:
			user = User.objects.with_id(username_or_token)
			if not user.verify_password(password):
				return False
			else:
				#not sure if necessary
				g.user = user
				return True
		except DoesNotExist:
			return False



class Register(Resource):
	def post(self):
		email = request.json.get('email')
		password = request.json.get('password')
		if email is None or password is None:
			return jsonify(request)
			abort(400) #missing arguments
		if User.objects.with_id(email) is not None:
			abort(400) #existing user
		user = User(email=email)
		user.hash_password(password)
		user.save()
		return jsonify({'message':'Welcome!'})

class Login(Resource):
	@auth.login_required
	def post(self):
		token = g.user.generate_auth_token()
		return jsonify({'token':token.decode('ascii')})
