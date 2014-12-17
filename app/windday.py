from flask import render_template, redirect, jsonify, send_file, request
from app import app
from io import BytesIO
from app.dbmodel import *
from windscripts.windday import *

@app.route('/')
@auth.login_required
def home():
    return app.send_static_file('index.html')
    
@app.route('/windyday')
@auth.login_required
def windyday():
    return home()
    
@app.route('/cranepath')
@auth.login_required
def cranepath():
    return app.send_static_file('zipupload.html')
    
@app.route('/api/windday',methods=['POST','GET'])
@auth.login_required
def get_project():
    try:
        project = Project.objects.get(name='default')
        if project.windTMatrix:
            return jsonify(result={"exists": True,"seasonality":project.get_Seasonality()})
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})

@app.route('/api/windday/seasonality/<project>')
@auth.login_required
def get_seasonality(project):
    try:
        project = Project.objects.get(name=project)
        if project.windSeasonality:
            seasonality = project.get_seasonality()
            data = {"seasonality":seasonality}
            return jsonify(result={"exists": False})
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})
        

@app.route('/api/windday/expected',methods=['POST'])
@auth.login_required
def get_winddays():
    try:
        project = Project.objects.get(name='default')
        if project.windTMatrix:
            winddays = estimate_winddays(project.windHeight,request.json['height'],request.json['maxws'],request.json['maxhours'],request.json['starthr'],request.json['daylength'],project.get_TMatrix(),request.json['certainty'],consecutive=request.json['consecutive'])
            print winddays
            return jsonify(result={"exists": True,"byMonth":winddays[0],"cumulative":winddays[1]})
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})
        
@app.route('/api/windday/risks',methods=['POST'])
@auth.login_required
def get_risks():
    try:
        project = Project.objects.get(name='default')
        if project.windTMatrix:
            risks = risk_by_hour_and_month(project.windHeight,request.json['height'],request.json['maxws'],request.json['maxhours'],request.json['daylength'],project.get_TMatrix(),consecutive=request.json['consecutive'])
            return jsonify(result={"exists": True,"risks":risks})
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})