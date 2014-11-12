from flask import render_template, redirect, jsonify, send_file
from app import app
from io import BytesIO
from app.dbmodel import *

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
    
@app.route('/api/windday')
@auth.login_required
def get_project():
    try:
        project = Project.objects.get(name='default',user=g.user)
        if project.windTMatrix:
            return jsonify(result={"exists": True})
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})

@app.route('/api/windday/<project>/seasonality.png')
@auth.login_required
def get_seasonality(project):
    try:
        project = Project.objects.get(name=project,user=g.user)
        if project.windSeasonality:
            plot = BytesIO(project.windSeasonality.read())
            plot.seek(0)
            content_type = project.windSeasonality.content_type
            return send_file(plot,mimetype=content_type)
        else:
            return jsonify(result={"exists": False})
    except Project.DoesNotExist:
        return jsonify(result={"exists": False})
