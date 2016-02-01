import flask
from flask import request, g, jsonify
from app import app, celery
from app.dbmodel import *
from windscripts.wrangling import *
from windscripts.windday import *
from cStringIO import StringIO
from errors import ProjectException
from windday import calculate_expected_winddays, calculate_windday_risks
import auth

ALLOWED_EXTENSIONS = set(['csv'])
ZIP = set(['zip'])

def allowed_file(filename,extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in extensions


@app.route('/api/windyday/<project_name>/upload', methods=['POST'])
@auth.login_required
def upload_file(project_name):
    print "At upload"
    if request.method == 'POST':
        fileobj = request.files['file']
        print "Got File"
        if fileobj and allowed_file(fileobj.filename,ALLOWED_EXTENSIONS):
            print "File is allowed"
            try:
                project = Project.objects.get(name = project_name)
            except Project.DoesNotExist:
                project = Project(name =  project_name)

            project.wind_status = "Storing raw data."
            project.save()
            try:
                if project.raw_wind_data:
                    project.raw_wind_data.delete()
                project.raw_wind_data.put(fileobj, content_type='text/csv')
                project.windHeight = int(request.values['height'])
                project.save()
            except Exception as e:
                project.wind_status = "There was an error storing wind data."
                project.save()
                raise ProjectException("There was an error storing wind data, " + str(e) )
            windday_conditions = {
            "height": 50,
            "maxws": 10.0,
            "maxhours": 4,
            "starthr": 7,
            "consecutive": True,
            "daylength": 10,
            "certainty": 0.9,
            }
            project.windday_conditions = windday_conditions
            training = train_wind_model.delay(g.username, project.name)
            project.wind_status = "Data stored, placed in queue for model training."
            project.save()
            return jsonify(result={"status": 200, "message": "Wind data stored successfully."})
        else:
            raise ProjectException("Wrong file type, please use a CSV file")



@celery.task(name = 'train_wind_model')
def train_wind_model(username, project_name):
    user, project = Project.get_user_and_project(username, project_name)
    try:
        windseries, windcolumn = get_train_set(StringIO(project.raw_wind_data.read()))
        project.save_Seasonality(plot_seasonality(windseries))
        project.save_TMatrix(train_mcm_hm(windseries,windcolumn))
        project.save_Stationary(compute_stationary(project.get_TMatrix()))
        project.wind_status = "Wind model trained."
        project.save()
        expected = calculate_expected_winddays.delay(*(username, project_name))
        risks = calculate_windday_risks.delay(*(username, project_name))
    except Exception as e:
        project.wind_status = "Wind model training failed."
        project.save()
        print str(e)
        return ("There was an error processing your wind file." + str(e))
    return project.windTMatrix
    