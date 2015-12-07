from flask import render_template, redirect, jsonify, send_file, request, g
from app import app
from io import BytesIO
from app.dbmodel import Project
from windscripts.windday import *
import auth
from auth import User

@app.route('/api/windday/<project_name>',methods=['POST','GET'])
@auth.login_required
def get_project(project_name):
    try:
        user = User.objects.get(username = g.username)
        project = Project.objects.get(name = project_name, user = user)
        if project.windTMatrix:
            return jsonify(result={"exists": True,"seasonality":project.get_Seasonality()})
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})


@app.route('/api/windday/<project_name>/expected',methods=['POST'])
@auth.login_required
def get_winddays(project_name):
    try:
        user = User.objects.get(username = g.username)
        project = Project.objects.get(name = project_name, user = user)
        if project.windTMatrix:
            winddays = estimate_winddays(
                project.windHeight,
                request.json['height'],
                request.json['maxws'],
                request.json['maxhours'],
                request.json['starthr'],
                request.json['daylength'],
                project.get_TMatrix(),
                request.json['certainty'],
                consecutive = request.json['consecutive']
                )
            return jsonify(result={"exists": True,"byMonth":winddays[0],"cumulative":winddays[1]})
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})
        
@app.route('/api/windday/<project_name>/risks',methods=['POST'])
@auth.login_required
def get_risks(project_name):
    try:
        user = User.objects.get(username = g.username)
        project = Project.objects.get(name = project_name, user = user)
        if project.windTMatrix:
            risks = risk_by_hour_and_month(project.windHeight,request.json['height'],request.json['maxws'],request.json['maxhours'],request.json['daylength'],project.get_TMatrix(),consecutive=request.json['consecutive'])
            return jsonify(result={"exists": True,"risks":risks})
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})