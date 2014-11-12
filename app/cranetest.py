from flask import Flask, request, redirect, url_for, jsonify
import os
from app import app
from app.dbmodel import *

@app.route('/cranetest')
@auth.login_required
def cranetest():
    """This is a predefined test to be able to test the output of our
    crane optimization software."""
    
    #--- SET SHAPEFILES ---
    layers = []
    for file in os.listdir("home/ubuntu/macksburg/shapefiles"):
        if file.endswith(".shp"):
            layers.append(file)
        shpfiles = {}
    for layer in layers:
        if layer not in ('Wetlands_trans.shp','Wetlands.shp','ProposedTurbineCoord.shp','ProposedTurbineCoord_trans.shp'):
            shpfiles[layer[:layer.index('.')]] = {}
            shpfiles[layer[:layer.index('.')]]['file'] = 'home/ubuntu/macksburg/shapefiles/'+layer
        
    for layername in shpfiles:
        shpfiles[layername]['cd'] = 1.20
    
    shpfiles['DitchLine']['cc'] = 1250.0
    shpfiles['Fence']['cc'] = 300.0
    shpfiles['NaturalGas']['cc'] = 0.0
    shpfiles['PowerLine']['cc'] = 10000. #Assuming they are all drop and bury
    shpfiles['ProposedAccessRoads']['cc'] = 0.0
    shpfiles['RoadAsphalt']['cc'] = 5600.0
    shpfiles['RoadConcrete']['cc'] = 5600.0
    shpfiles['RoadDriveway']['cc'] = 5600.0
    shpfiles['RoadGravel']['cc'] = 5600.0
    shpfiles['TreeLine']['cc'] = 0.0
    shpfiles['WaterPipe']['cc'] = 0.0
    