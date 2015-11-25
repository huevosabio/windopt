from mongoengine import *
import json
from flask import Flask, abort, request, jsonify, g, url_for
from app import app, conn, auth
import cPickle
from app.auth import User

@app.route('/api/project', methods = ['POST', 'GET'])
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
            project_dict = project.to_mongo()
            print project_dict
            project_dict.pop('_id')
            project_dict.pop('user')
            return jsonify(message = 'Project created successfully.', project = project_dict)

    elif request.method == 'GET':
        user = User.objects.get(username = g.username)
        projects = [{'name':project.name} for project in Project.objects(user = user).only('name').all()]
        return jsonify(message = 'Queried projects', projects = projects)


@app.route('/api/projects/<name>', methods = ['GET', 'PUT', 'DELETE'])
@auth.login_required
def get_or_update_project(projectname):
    '''
    GET:
        Returns the project info (name)
    PUT:
        Updates project info (name)
    DELETE:
        Deletes project
    '''
    try:
        user = User.objects.get(username = g.username)
        project = Project.objects.get(name = name, user = user)
    except Project.DoesNotExist:
        raise ProjectException('Project does not exist.')
    if request.method == 'GET':
        return jsonify(projectname = project.projectname, message = 'Project retrieved successfully')
    elif request.method == 'PUT' and g.project.projectname == projectname:
        # Method should be used only for changing password
        try:
            project.hash_password(request.json['password'])
            project.save()
            return jsonify(message = 'Password updated successfully.')
        except:
            raise BadRequestException('There was an error in the request.')
    elif request.method == 'DELETE' and auth.projectname == projectname:
        project.delete()
        return jsonify(message = 'Project deleted.')
    else:
        raise BadRequestException('Your request was not understood by the server.')


class Project(Document):
    name = StringField(unique=True)
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    windHeight = IntField()
    windTMatrix = BinaryField()
    windSeasonality = BinaryField()
    
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
    
    
        
        
        
        
        
        
    
    
    
