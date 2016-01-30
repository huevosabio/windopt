from flask import render_template, redirect, jsonify, send_file, request, g
from app import app, celery
from io import BytesIO
from app.dbmodel import Project
from windscripts.windday import *
import auth
from auth import User
from errors import ProjectException
import json

@app.route('/api/windyday/<project_name>/status', methods=['GET'])
@auth.login_required
def check_wind_status(project_name):
    user, project = Project.get_user_and_project(g.username, project_name)
    expected_winddays_ready = bool(project.expected_winddays)
    expected_windday_risks_ready = bool(project.expected_winddays)
    if expected_winddays_ready and expected_windday_risks_ready:
        project.wind_status = "Wind Day calculations ready."
        project.save()
        return jsonify(
            result = {
                "status": project.wind_status,
                "byMonth": project.expected_winddays,
                "risks": project.risks,
                "conditions": project.windday_conditions
            })
    return jsonify({
        result = {"status": project.wind_status}
        })

@app.route('/api/windday/<project_name>/seasonality',methods=['POST','GET'])
@auth.login_required
def get_project_seasonality(project_name):
    user, project = Project.get_user_and_project(g.username, project_name)
    if project.windTMatrix:
        return jsonify(
            result={
            "exists": True,
            "seasonality":project.get_Seasonality()
            })
    else:
        return jsonify(result={"exists": False})

#Compute wind calcs
@app.route('/api/windday/<project_name>/calculate',methods=['POST'])
@auth.login_required
def calulate_wind(project_name):
    user, project = Project.get_user_and_project(g.username, project_name)
    if project.windTMatrix:
        try:
            conditions = request.json['conditions']
            project.windday_conditions = conditions
            project.wind_status = "Calculating Expected Risks of Wind Days"
            project.save()
            expected = calculate_expected.delay(*(g.username, project_name))
            risks = calculate_risks.delay(*(g.username, project_name))
        except Exception e:
            project.wind_status = "Error Calculating Wind Days"
            raise ProjectException("Error Calculating Wind Days: " + str(e))
        return jsonify(result={"message": project.wind_status})
    else:
        raise ProjectException("Please upload wind data.")

#Compute wind calcs task
@celery.task(name = 'calculate_expected_winddays')
def calculate_expected_winddays(username, project_name):
    user, project = Project.get_user_and_project(username, project_name)
    try:
        winddays = estimate_winddays(
                       project.windHeight,
                       project.windday_conditions.height,
                       project.conditions.maxws,
                       project.conditions.maxhours,
                       project.conditions.starthr,
                       project.conditions.daylength,
                       project.get_TMatrix(),
                       project.conditions.certainty,
                       consecutive = project.conditions.consecutive
                       )
        project.expected_winddays = winddays
        project.save()
        return winddays
    except Exception e:
        project.wind_status = "Error Calculating Wind Days"
        project.save()

#Compute risks task 
@celery.task(name = 'calculate_windday_risks')
def calculate_windday_risks(username, project_name):
    user, project = Project.get_user_and_project(username, project_name)
    try:
        risks = risk_by_hour_and_month(
            project.windHeight,
            project.windday_conditions.height,
            project.windday_conditions.maxws,
            project.windday_conditions.maxhours,
            project.windday_conditions.daylength,
            project.get_TMatrix(),
            consecutive=project.windday_conditions.consecutive
            )
        project.expected_windday_risks = risks
        project.save()
        return risks
    except Exception e:
        project.wind_status = "Error Calculating Wind Days"
        project.save()