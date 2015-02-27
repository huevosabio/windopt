import json
import os
import flask
from flask import Flask, request, redirect, url_for, render_template, jsonify
from app import app
from werkzeug.utils import secure_filename
from windscripts.costing import *
from windscripts.geopy import *
from windscripts.tsp import *
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
def tsp_sol():
    clear_uploads(RASTER_DIR)
    clear_uploads(PATHS_DIR)
    #Create Layer Dictionary and identify turbines
    print "we are at tsp_sol()"
    turbines = {}
    try:
        layerdict = request.json
    except Exception, e:
        print e
    print "we created the layerdict"
    for layer in layerdict:
        print layer
        if layerdict[layer]['interpretation'] == 'turbines':
            turbines['file'] =SHP_DIR+'/'+layer+'.shp'
            turbines['cost'] = float(layerdict[layer]['cost'])
            turbines['name'] = layer
        elif layerdict[layer]['interpretation'] == 'boundary':
            layerdict[layer]['logic'] = 'boundary'
            layerdict[layer]['cd'] = float(layerdict[layer]['cost'])
            layerdict[layer]['cc'] = 0.0
            layerdict[layer]['file'] =SHP_DIR+'/'+layer+'.shp'
            boundary = layerdict[layer]['file']
            walkCost = float(layerdict[layer]['cost'])
        else:
            layerdict[layer]['cc'] = float(layerdict[layer]['cost'])
            layerdict[layer]['cd'] = 0.0
            layerdict[layer]['file'] =SHP_DIR+'/'+layer+'.shp'
    
    
    del layerdict[turbines['name']]
            
    #Create Cost Ratser
    print "cost raster"
    rasterfn = RASTER_DIR+'/costraster.tif'
    create_cost_raster(rasterfn,layerdict,50.0)
    
    #Create Complete NetworkX graph
    print 'graph'
    
    complete = create_nx_graph(turbines['file'],rasterfn,PATHS_DIR+'/',layerdict)
    graph = complete[0]
    pos = complete[1]
    
    #Solve the graph
    print 'tsp'
    solved = tsp_ca(graph)
    #Detailed Path Structure
    cost, solved = get_total_cost(solved,pos, layerdict,PATHS_DIR+'/',rasterfn,walkCost)
    
    #Save to GeoJSON
    print 'GeoJson'
    goodpos = {}
    with fiona.open(turbines['file']) as s:
        for d in s:
            goodpos[d['id']] = transform_to_wgs84(s.crs,d['geometry'])['coordinates']
    
    schedule = get_geojson(solved,turbines['cost'],goodpos)
    properties={'activity':'boundary'}
    boundary = shp2geojson(boundary,properties=properties)
    schedule['features']+= boundary['features']
    
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