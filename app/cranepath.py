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
import zipfile
import shutil
from mongoengine import *
from mongoengine.dereference import DeReference
#NOTES:
#This implementation requires heavy use of a file system which in turns has all
#the nuances of permission management. Thus, in a more refined version, it would
#be obviously necessary to use a DB system instead of a local file system.
#Also, currently most GIS operations are handled by OGR/GDAL bindings. A proper
#solution would take advantage of Rasterio/Shapely/Fiona to avoid having to 
#make system calls and obfuscated code. Another reason, OGR/GDAL doesn't give
#warning when there is a failure to create a new file, instead it just returns
#a NoneType

SHP_DIR = os.path.join(app.config['UPLOAD_FOLDER'],'shapefiles')
RASTER_DIR = os.path.join(app.config['UPLOAD_FOLDER'],'rasters')
PATHS_DIR = os.path.join(app.config['UPLOAD_FOLDER'],'paths')

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
    clear_shpfiles()
    print "At upload"
    if request.method == 'POST':
        fileobj = request.files['file']
        print "Got File"
        if fileobj and allowed_file(fileobj.filename,ZIP):
            print "File is allowed"
            #filename = secure_filename(file.filename)
            fileobj.save(os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles.zip'))
            path = os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles')
            with zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles.zip'), "r") as z:
                for member in z.namelist():
                    filename = os.path.basename(member)
                    if not filename: continue
                    # copy file (taken from zipfile's extract)
                    source = z.open(member)
                    target = file(os.path.join(path, filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
                    
            return flask.jsonify(result={"status": 200})


@app.route('/api/cranepath/layerlist',methods=['GET'])
@auth.login_required
def list_layers():
    result = {}
    layers = []
    for f in os.listdir(SHP_DIR):
        if f.endswith(".shp"):
            layers.append(f[:f.index('.')])
    result["layers"] = layers
    return jsonify(result)
    

@app.route('/api/cranepath/tsp',methods=['POST'])
@auth.login_required
def tsp_sol_legacy():
    clear_uploads(RASTER_DIR)
    clear_uploads(PATHS_DIR)
    #Create Layer Dictionary and identify turbines
    print "we are at tsp_sol()"
    
    #Get the project
    user = User.objects.get(username = g.username)
    project = Project.objects.get(name = request.json['project'], user = user)

    crane_project = CraneProject()
    crane_project.save()

    project.crane_project = crane_project

    project.save()

    try:
        layerdict = request.json['layerdict']
    except Exception, e:
        print e
    print "we created the layerdict"
    for layer in layerdict:
        feature = GeoFeat()
        feature.read_shapefile(SHP_DIR+'/'+layer+'.shp')
        feature.cost = float(layerdict[layer]['cost'])
        feature.name = layer
        feature.interpretation = layerdict[layer]['interpretation']
        try:
            feature.save()
        except:
            print layer + ': not saved'
            continue
        if feature.interpretation == 'turbines':
            crane_project.turbines = feature
        elif feature.interpretation == 'boundary':
            crane_project.set_boundary(feature)
        else:
            crane_project.features.append(feature)

    crane_project.save()
            
    #Create Cost Ratser
    print "cost raster"
    crane_project.createCostRaster()
    
    #Create Complete NetworkX graph
    print 'graph'
    crane_project.create_nx_graph()
    
    #Solve the graph
    print 'tsp'
    crane_project.solve_tsp()
    crane_project.expandPaths()
    
    #Save to GeoJSON
    print 'GeoJson'
    
    schedule = crane_project.get_geojson()
    crane_project.geojson = schedule

    crane_project.save()
    project.save()
    
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