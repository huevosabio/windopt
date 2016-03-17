from app import app
from flask import jsonify

class BaseException(Exception):
	status_code = 469

	def __init__(self, message, status_code=None, payload=None):
		Exception.__init__(self)
		self.message = message
		if status_code is not None:
			self.status_code = status_code
		self.payload = payload

	def to_dict(self):
		rv = dict(self.payload or {'message':'Default Error Message'})
		rv['message'] = self.message
		return rv

def handler_function(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response


class BadRequestException(BaseException):
	status_code = 400
	pass

@app.errorhandler(BadRequestException)
def rerrun_lease_exception_handler(error):
	return handler_function(error)

class UserException(BaseException):
	status_code = 469
	pass

@app.errorhandler(UserException)
def user_exception_handler(error):
	return handler_function(error)

class ProjectException(BaseException):
	status_code = 469
	pass

@app.errorhandler(ProjectException)
def user_exception_handler(error):
	return handler_function(error)

class CostException(BaseException):
	status_code = 469
	pass

@app.errorhandler(CostException)
def cost_exception_handler(error):
	return handler_function(error)
