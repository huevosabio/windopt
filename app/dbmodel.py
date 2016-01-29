from mongoengine import *
import json
from flask import Flask, abort, request, jsonify, g, url_for
from app import app, conn, auth
import cPickle
from app.auth import User
import windscripts.features as wind_features

@app.route('/api/projects', methods = ['POST', 'GET'])
@auth.login_required
def create_or_list_project():
    '''
    Assumes a request with Content-Type: application/json.
    The json should be of the form:
    {
        "name":<project_name>
    }
    '''
    if request.method == 'POST':
        project_data = request.json
        # check that the request is well formed.
        if 'name' not in project_data:
            raise BadRequestException('Malformed request.')

        # check that name does not exist
        if Project.objects(name = project_data['name']).first():
            raise ProjectException('Project name already exists.')

        else:
            user = User.objects.get(username = g.username)
            project = Project(name = project_data['name'], user = user)
            project.save()
            return jsonify(
                message = 'Project created successfully.',
                project = project.get_summary()
                )

    elif request.method == 'GET':
        user = User.objects.get(username = g.username)
        projects = [project.get_summary() for project in Project.objects(user = user).all()]
        return jsonify(message = 'Queried projects', projects = projects)


@app.route('/api/projects/<name>', methods = ['GET'])
@auth.login_required
def get_or_update_project(name):
    '''
    GET:
        Returns the project info (name)
    PUT:
        NOT IMPLEMENTED
        Updates project info (name)
    DELETE:
        NOT IMPLEMENTED
        Deletes project
    '''
    try:
        user = User.objects.get(username = g.username)
        project = Project.objects.get(name = name, user = user)
    except Project.DoesNotExist:
        raise ProjectException('Project does not exist.')
    if request.method == 'GET':
        return jsonify(project.get_summary())
    else:
        raise BadRequestException('Your request was not understood by the server.')

class GeoFeat(wind_features.GeoFeat, Document):
    interpretation = StringField()
    geometry_type = StringField()
    cost = FloatField()
    name = StringField()
    geojson = DictField()
    bounds = ListField(FloatField())

class CraneProject(wind_features.CraneProject, Document):
    boundary = ReferenceField(GeoFeat)
    turbines = ReferenceField(GeoFeat)
    features = ListField(ReferenceField(GeoFeat))
    psize = FloatField(default=50.0)
    walkCost = FloatField()
    crs = DictField()
    bounds = ListField(FloatField())
    geojson = DictField()
    status = StringField()


class Project(Document):
    name = StringField(unique=True)
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    raw_wind_data = FileField()
    wind_status = StringField(default = "Empty project.")
    windday_conditions = DictField()
    windHeight = IntField()
    windTMatrix = BinaryField()
    windSeasonality = BinaryField()
    crane_project = ReferenceField(CraneProject)
    
    def save_TMatrix(self,tmat):
        #convert transition matrix to binary and assign
        self.windTMatrix = cPickle.dumps(tmat, protocol=2)
    
    def get_TMatrix(self):
        if self.windTMatrix:
            return cPickle.loads(self.windTMatrix)
        else: return None

    def save_Seasonality(self,matrix):
        #convert transition matrix to binary and assign
        self.windSeasonality = cPickle.dumps(matrix, protocol=2)
    
    def get_Seasonality(self):
        if self.windSeasonality:
            return cPickle.loads(self.windSeasonality)
        else: return None
        
    def save_Stationary(self,matrix):
        #convert transition matrix to binary and assign
        self.windStationary = cPickle.dumps(matrix, protocol=2)
    
    def get_Stationary(self):
        if self.windStationary:
            return cPickle.loads(self.windStationary)
        else: return None

    def get_summary(self):
        return {
            'name': self.name,
            'hasWindFile': bool(self.windTMatrix)
        }
        
        
        
    
    
    
