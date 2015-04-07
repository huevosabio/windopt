import json
import os
import flask
from flask import Flask, request, redirect, url_for, render_template, jsonify
from app import app
from werkzeug.utils import secure_filename
from windscripts.costing import *
#from windscripts.geopy import *
from windscripts.tsp import *
from windscripts.features import *
import fiona
import pandas as pd
from app.dbmodel import *

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
    
@app.route('/layers',methods=['GET'])
def send_layer_file():
    return  app.send_static_file('layerlist.html')
    

@app.route('/api/cranepath/tsp',methods=['POST'])
@auth.login_required
def tsp_solsol_legacy():
    clear_uploads(RASTER_DIR)
    clear_uploads(PATHS_DIR)
    #Create Layer Dictionary and identify turbines
    print "we are at tsp_sol()"
    project = CraneProject()
    try:
        layerdict = request.json
    except Exception, e:
        print e
    print "we created the layerdict"
    for layer in layerdict:
        feature = GeoFeat()
        feature.read_shapefile(shp_DIR+'/'+layer+'.shp')
        feature.cost = float(layerdict[layer]['cost'])
        feature.name = layer
        print feature
        if layerdict[layer]['interpretation'] == 'turbines':
            project.turbines = feature
        elif layerdict[layer]['interpretation'] == 'boundary':
            project.set_boundary(feature)
        else:
            project.features.append(feature)
            
    #Create Cost Ratser
    print "cost raster"
    project.createCostRaster()
    
    #Create Complete NetworkX graph
    print 'graph'
    project.create_nx_graph()
    
    #Solve the graph
    print 'tsp'
    project.solve_tsp()
    project.expandPaths()
    
    #Save to GeoJSON
    print 'GeoJson'
    
    schedule = project.get_geojson()
    
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


@app.route('/api/cranepath/schedule',methods=['GET'])
@auth.login_required
def solved():
    result = {}
    with open(os.path.join(app.config['STATIC'], 'schedule.json'),'r') as j:
        result['schedule'] = json.load(j)
    return jsonify(result)
    
@app.route('/api/cranepath/schedule.csv',methods=['GET'])
@auth.login_required
def csv():
    return app.send_static_file('schedule.csv')