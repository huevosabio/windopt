from mongoengine import *
import json
from flask import Flask, abort, request, jsonify, g, url_for
from app import app, conn, auth
import cPickle
from app.auth import User
import windscripts.features as wind_features

@app.route('/api/costs', methods = ['POST', 'GET'])
@auth.login_required
def create_or_list_cost():
    '''
    Assumes a request with Content-Type: application/json.
    The json should be of the form:
    {
        "name":<cost_name>
    }
    '''
    if request.method == 'POST':
        cost_data = request.json
        # check that the request is well formed.
        if 'name' not in cost_data:
            raise BadRequestException('Malformed request.')

        # check that name does not exist
        if Cost.objects(
            name = cost_data['name']).first():
            raise CostException('Cost name already exists.')

        else:
            user = User.objects.get(username = g.username)
            cost = Cost(name = cost_data['name'],
            interpretation = cost_data['interpretation'],
            cost = cost_data['cost'],
             user = user)
            cost.save()
            return jsonify(
                message = 'Cost created successfully.',
                cost = cost.to_mongo()
                )

    elif request.method == 'GET':
        user = User.objects.get(username = g.username)
        costs = [cost.to_mongo() for cost in Cost.objects(user = user).all()]
        return jsonify(message = 'Queried costs', costs = costs)


@app.route('/api/costs/<name>', methods = ['GET'])
@auth.login_required
def get_or_update_cost(name):
    '''
    GET:
        Returns the cost info (name)
    PUT:
        NOT IMPLEMENTED
        Updates cost info (name)
    DELETE:
        NOT IMPLEMENTED
        Deletes cost
    '''
    try:
        user = User.objects.get(username = g.username)
        cost = Cost.objects.get(name = name, user = user)
    except Cost.DoesNotExist:
        raise CostException('Cost does not exist.')
    if request.method == 'GET':
        return jsonify(cost.to_mongo())
    else:
        raise BadRequestException('Your request was not understood by the server.')

class CraneCost(Document):
    user = ReferenceField(User)
    name = StringField()
    interpretation = StringField()
    cost= FloatField()