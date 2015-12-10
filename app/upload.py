import os
import flask
from flask import Flask, request, redirect, url_for, render_template, g
from app import app
from app.dbmodel import *
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import zipfile
from windscripts.wrangling import *
from windscripts.windday import *
from cStringIO import StringIO
from bson.binary import Binary
import cPickle
import time
import shutil
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
            #filename = secure_filename(file.filename)
            s = StringIO(fileobj.read())
            try:
                project = Project.objects.get(name = project_name)
            except Project.DoesNotExist:
                project = Project(name =  project_name)
            #if not project.windRaw: project.windRaw.put(file,content_type='text/csv')
            #else: project.windRaw.replace(file, content_type='text/csv')
            project.windHeight = int(request.values['height'])
            t0 = time.time()
            windseries, windcolumn = get_train_set(s)
            t1 = time.time()
            project.save_Seasonality(plot_seasonality(windseries))
            t2 = time.time()
            project.save_TMatrix(train_mcm_hm(windseries,windcolumn))
            project.save_Stationary(compute_stationary(project.get_TMatrix()))
            t3 = time.time()
            project.save()
            t4 = time.time()
            print 'train set = ' + str(t1-t0)
            print 'seasonality plot = ' + str(t2-t1)
            print 'tmatrix = ' +str(t3-t2)
            print 'save = ' + str(t4-t3)
            return flask.jsonify(result={"status": 200})