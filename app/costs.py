from mongoengine import *
import json
from flask import Flask, abort, request, jsonify, g, url_for
from app import app, conn, auth
import cPickle
from app.auth import User
import windscripts.features as wind_features
from errors import CostException

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

        if 'cost' not in cost_data or \
        type(cost_data['cost']) not in [float, int]:
            raise CostException('Please assign proper cost.')

        if 'interpretation' not in cost_data or \
        cost_data['interpretation'] not in ['boundary','turbines','crossing']:
            raise CostException('Invalid interpretation.')

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
                cost = cost.to_dict()
                )

    elif request.method == 'GET':
        user = User.objects.get(username = g.username)
        costs = [cost.to_dict() for cost in Cost.objects(user = user).all()]
        return jsonify(message = 'Queried costs', costs = costs)


@app.route('/api/costs/<id>', methods = ['GET', 'DELETE', 'PUT'])
@auth.login_required
def get_or_update_cost(id):
    '''
    GET:
        Returns the cost info (name)
    PUT:
        Updates cost info (name)
    DELETE:
        NOT IMPLEMENTED
        Deletes cost
    '''
    try:
        user = User.objects.get(username = g.username)
        cost = Cost.objects.get(id = id, user = user)
    except Cost.DoesNotExist:
        raise CostException('Cost does not exist.')
    if request.method == 'GET':
        return jsonify(cost.to_dict())
    if request.method == 'PUT':
        print request.json
        cost.name = request.json['name']
        cost.interpretation = request.json['interpretation']
        cost.cost = request.json['cost']
        cost.save()
        return jsonify(message = 'Cost updated.')
    if request.method == 'DELETE':
        cost.delete()
        return jsonify(message = 'Cost deleted.')
    else:
        raise BadRequestException('Your request was not understood by the server.')

class Cost(Document):
    user = ReferenceField(User)
    name = StringField(unique = True)
    interpretation = StringField()
    cost= FloatField()

    def to_dict(self):
        if self.interpretation == 'turbines':
            units = 'USD/EA'
        elif self.interpretation == 'boundary':
            units = 'USD/m'
        elif self.interpretation == 'crossing':
            units = 'USD/crossing'
        else:
            units = ''

        def xstr(s):
            if s is None:
                return ''
            else:
                return str(s)
        return {
        'name': self.name,
        'interpretation': self.interpretation,
        'cost': self.cost,
        'id': str(self.id),
        'verbose': xstr(self.name) + ', interpretation: ' + xstr(self.interpretation) + \
         ',  cost: $' + \
         xstr(self.cost) + ' ' +\
          units,
         'units': units
        }


@app.before_first_request
def create_fake_costs():
    user = User.objects.get(username = 'admin')
    try:
        cost_t = Cost(user = user, name = 'Fake Turbine Cost', interpretation = 'turbines', cost = 1000)
        cost_t.save()
        cost_b = Cost(user = user, name = 'Fake Boundary Cost', interpretation = 'boundary', cost = 1.5)
        cost_b.save()
        cost_c = Cost(user = user, name = 'Fake Crossing Cost', interpretation = 'crossing', cost = 5000)
        cost_c.save()
    except NotUniqueError:
        pass
    return
