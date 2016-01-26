import json
import os
import flask
from flask import Flask, request, redirect, url_for, render_template, jsonify, g
from app import app
from werkzeug.utils import secure_filename
from windscripts.costing import *
#from windscripts.geopy import *
from windscripts.tsp import *
import fiona
import pandas as pd
from app.dbmodel import *
import auth
from upload import allowed_file, ZIP
from zipfile import ZipFile
import shutil
from mongoengine import *
from mongoengine.dereference import DeReference
from cStringIO import StringIO
from errors import ProjectException
#NOTES:
#This implementation requires heavy use of a file system which in turns has all
#the nuances of permission management. Thus, in a more refined version, it would
#be obviously necessary to use a DB system instead of a local file system.
#Also, currently most GIS operations are handled by OGR/GDAL bindings. A proper
#solution would take advantage of Rasterio/Shapely/Fiona to avoid having to 
#make system calls and obfuscated code. Another reason, OGR/GDAL doesn't give
#warning when there is a failure to create a new file, instead it just returns
#a NoneType

SHP_DIR = app.config['UPLOAD_FOLDER']

def clear_uploads(DIR):
    shpdir = DIR
    if os.path.exists(shpdir):
        for the_file in os.listdir(shpdir):
            file_path = os.path.join(shpdir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e

def clear_shpfiles():
    shpdir = os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles')
    if os.path.exists(shpdir):
        for the_file in os.listdir(shpdir):
            file_path = os.path.join(shpdir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e

@app.route('/api/cranepath/zipupload',methods=['POST'])
@auth.login_required
def upload_ziplfile():
    print request.form
    print "At upload"
    if request.method == 'POST':
        fileobj = request.files['file']
        print "Got File"
        if fileobj and allowed_file(fileobj.filename,ZIP):
            print "File is allowed"

            #TODO: This still uses the file system
            clear_uploads(SHP_DIR)
            zip_contents = StringIO(fileobj.read())
            zipfile = SHP_DIR + '/' + str(os.getpid()) +'.zip'
            with open(zipfile, "wb") as f:
                f.write(zip_contents.getvalue())
            # create crane project
            user = User.objects.get(username = g.username)
            project = Project.objects.get(name =request.form['project'], user = user)

            crane_project = CraneProject()
            crane_project.status = "Crane Project created."
            crane_project.save()

            project.crane_project = crane_project
            project.save()

            #TODO: keep track of the data types.
            with fiona.drivers():
                messages = []
                crane_project.status = "Reading shapefiles."
                for i, layername in enumerate(
                fiona.listlayers(
                    '/',
                    vfs='zip://'+zipfile)):
                    feature = GeoFeat()
                    feature.read_shapefile(layername, zipfile)
                    feature.name = layername
                    #TODO: This just leaves shitty layers out of the project, you need to report this.
                    try:
                        feature.save()
                        crane_project.features.append(feature)
                    except:
                        messages.append(layername + ': not saved')
                        continue

            #TODO: These two calls might be redundant, check if its so.
            crane_project.status = "Shapefiles stored. User needs to enter Interpretations."
            crane_project.save()
            project.save()
                    
            return flask.jsonify(result={"status": 200}, messages = messages)
        else:
            raise ProjectException("Geographic files should be packed in a ZIP file")


@app.route('/api/cranepath/layerlist/<project>',methods=['GET'])
@auth.login_required
def list_layers(project):
    #TODO: Change this to our new layout with layerlists coming from features, turbines and boundary
    user = User.objects.get(username = g.username)
    project = Project.objects.get(name = project, user = user)
    result = {}
    layers = [feature.name for feature in project.crane_project.features]
    if project.crane_project.turbines:
        layers.append(project.crane_project.turbines.name)
    if project.crane_project.boundary:
        layers.append(project.crane_project.boundary.name)
    result["layers"] = layers
    return jsonify(result)
    

@app.route('/api/cranepath/tsp',methods=['POST'])
@auth.login_required
def tsp_sol_legacy():
    #Create Layer Dictionary and identify turbines
    print "we are at tsp_sol()"
    
    #Get the project
    user = User.objects.get(username = g.username)
    project = Project.objects.get(name = request.json['project'], user = user)
    project.crane_project.status = "Setting layer interpretations."
    project.crane_project.save()
    
    #TODO: Interpretations that don't match the existing location of the feature should change the location of the feature
    #TODO: example, a turbine misinterpreted originally as a feature should be  siwtched back to turbine
    #TODO: A layer assigned as a boundary, should be switched back to feature.

    try:
        layerdict = request.json['layerdict']
    except Exception, e:
        print e
    print "we created the layerdict"
    for feature in project.crane_project.features:
        feature.cost = float(layerdict[feature.name]['cost'])
        feature.interpretation = layerdict[feature.name]['interpretation']
        try:
            feature.save()
        except:
            print layer + ': not saved'
            continue
        if feature.interpretation == 'turbines':
            project.crane_project.turbines = feature
            'we got turbines'
        elif feature.interpretation == 'boundary':
            project.crane_project.set_boundary(feature)
            print 'we got a boundary'
        else:
            project.crane_project.features.append(feature)

    project.crane_project.save()
            
    #Create Cost Ratser
    print "cost raster"
    project.crane_project.status = "Creating the cost raster."
    project.crane_project.save()
    project.crane_project.createCostRaster()
    
    #Create Complete NetworkX graph
    print 'graph'

    project.crane_project.status = "Building the complete graph."
    project.crane_project.save()
    project.crane_project.create_nx_graph()
    
    #Solve the graph
    print 'tsp'
    project.crane_project.status = "Solving the Traveling Salesman Problem"
    project.crane_project.save()
    project.crane_project.solve_tsp()
    project.crane_project.status = "Getting detailed path costs."
    project.crane_project.save()
    project.crane_project.expandPaths()
    
    #Save to GeoJSON
    print 'GeoJson'
    
    schedule = project.crane_project.get_geojson()
    project.crane_project.geojson = schedule
    project.crane_project.status = "Solved."
    project.crane_project.save()
    project.save()
    

    #TODO: Remove the usage of the CSV from folder.
    if os.path.exists(os.path.join(app.config['STATIC'], 'schedule.json')):
        os.remove(os.path.join(app.config['STATIC'], 'schedule.json'))
    with open(os.path.join(app.config['STATIC'], 'schedule.json'),'w') as j:
        json.dump(schedule,j)
    
    #Save to CSV
    print 'csv'
    activities = []
    for part in schedule['features']: activities.append(part['properties'])
    
    pd.DataFrame(activities).to_csv(os.path.join(app.config['STATIC'], 'schedule.csv'))
    
    return jsonify({'result':'Success'})


@app.route('/api/cranepath/schedule/<project_name>',methods=['GET'])
@auth.login_required
def solved(project_name):
    user = User.objects.get(username = g.username)
    project = Project.objects.get(name = project_name, user = user).select_related(max_depth=10)
    result = {}
    result['schedule'] = project.crane_project.geojson
    result['features'] = [{"name":feature.name, "geojson":feature.geojson} for feature in project.crane_project.features]
    result['turbines'] = project.crane_project.turbines.geojson
    result['boundary'] = project.crane_project.boundary.geojson
    return jsonify(result)
    
@app.route('/api/cranepath/schedule.csv',methods=['GET'])
@auth.login_required
def csv():
    return app.send_static_file('schedule.csv')