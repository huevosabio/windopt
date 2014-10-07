import json
import os
import flask
from flask import Flask, request, redirect, url_for, render_template, jsonify
from app import app
from werkzeug.utils import secure_filename
from windscripts import *
import fiona
import pandas as pd

SHP_DIR = os.path.join(app.config['UPLOAD_FOLDER'],'shapefiles')
RASTER_DIR = os.path.join(app.config['UPLOAD_FOLDER'],'rasters')
PATHS_DIR = os.path.join(app.config['UPLOAD_FOLDER'],'paths')

@app.route('/cranepath/layerlist',methods=['GET'])
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
    

@app.route('/cranepath/tsp',methods=['POST'])
def tsp_sol():
    #Set Shapefile DIR
    #Create Layer Dictionary and identify turbines
    turbines = {}
    layerdict = request.json.copy()
    
    for layer in layerdict:
        if layerdict[layer]['interpretation'] == 'turbines':
            turbines['file'] =SHP_DIR+'/'+layer+'.shp'
            turbines['cost'] = float(layerdict[layer]['cost'])
            del layerdict[layer]
        elif layerdict[layer]['interpretation'] == 'boundary':
            layerdict[layer]['logic'] = 'boundary'
            layerdict[layer]['cd'] = float(layerdict[layer]['cost'])
            layerdict[layer]['cc'] = 0.0
        else:
            layerdict[layer]['cc'] = layerdict[layer]['cost']
            
    #Create Cost Ratser
    rasterfn = RASTER_DIR+'costraster.tif'
    geopy.create_cost_raster(rasterfn,layerdict,50.0)
    
    #Create Complete NetworkX graph
    complete = geopy.create_nx_graph(turbines['file'],rasterfn,PATHS_DIR+'/',layerdict)
    graph = complete[0]
    pos = complete[1]
    
    #Solve the graph
    solved = tsp.tsp_ca(graph)
    #Detailed Path Structure
    cost, solved = costing.get_total_cost(solved,pos, shpfiles,PATHS_DIR+'/',rasterfn)
    
    #Save to GeoJSON
    goodpos = {}
    with fiona.open(turbines['file']) as s:
        for d in s:
            goodpos[d['id']] = transform_to_wgs84(s.crs,d['geometry'])['coordinates']
    
    schedule = get_geojson(solved,turbines['cost'],goodpos)
    
    with open(os.path.join(app.config['STATIC'], 'schedule.json'),'w') as j:
        json.dump(schedule,j)
    
    #Save to CSV
    activities = []
    for part in schedule['features']: activities.append(part['properties'])
    
    pd.DataFrame(activities).to_csv(os.path.join(app.config['STATIC'], 'schedule.csv'))
    
    return jsonify({'result':'Success'})

@app.route('/solution',methods=['GET'])
def solved():
    return app.send_static_file('data.txt')