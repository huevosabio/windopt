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

def clear_shpfiles():
    shpdir = os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles')
    if os.path.exists(shpdir):
        for the_file in os.listdir(shpdir):
            file_path = os.path.join(shpdir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e

@app.route('/api/windyday/upload', methods=['POST'])
@auth.login_required
def upload_file():
    print "At upload"
    if request.method == 'POST':
        fileobj = request.files['file']
        print "Got File"
        if fileobj and allowed_file(fileobj.filename,ALLOWED_EXTENSIONS):
            print "File is allowed"
            #filename = secure_filename(file.filename)
            s = StringIO(fileobj.read())
            try:
                project = Project.objects.get(name='default')
            except Project.DoesNotExist:
                project = Project(name = 'default')
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
            
@app.route('/api/cranepath/zipupload',methods=['POST'])
@auth.login_required
def upload_ziplfile():
    clear_shpfiles()
    print "At upload"
    if request.method == 'POST':
        fileobj = request.files['file']
        print "Got File"
        if fileobj and allowed_file(fileobj.filename,ZIP):
            print "File is allowed"
            #filename = secure_filename(file.filename)
            fileobj.save(os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles.zip'))
            path = os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles')
            with zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles.zip'), "r") as z:
                for member in z.namelist():
                    filename = os.path.basename(member)
                    if not filename: continue
                    # copy file (taken from zipfile's extract)
                    source = z.open(member)
                    target = file(os.path.join(path, filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
                    
            return flask.jsonify(result={"status": 200})