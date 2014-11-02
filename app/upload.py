import os
import flask
from flask import Flask, request, redirect, url_for, render_template
from app import app
from app.auth import *
from werkzeug.utils import secure_filename
import zipfile


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

@app.route('/windyday/upload', methods=['POST'])
@auth.login_required
def upload_file():
    print "At upload"
    if request.method == 'POST':
        file = request.files['file']
        print "Got File"
        if file and allowed_file(file.filename,ALLOWED_EXTENSIONS):
            print "File is allowed"
            #filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'winddata.csv'))
            return flask.jsonify(result={"status": 200})
            
@app.route('/cranepath/zipupload',methods=['POST'])
@auth.login_required
def upload_ziplfile():
    clear_shpfiles()
    print "At upload"
    if request.method == 'POST':
        file = request.files['file']
        print "Got File"
        if file and allowed_file(file.filename,ZIP):
            print "File is allowed"
            #filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles.zip'))
            with zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], 'shapefiles.zip'), "r") as z:
                z.extractall(app.config['UPLOAD_FOLDER'])
            return flask.jsonify(result={"status": 200})