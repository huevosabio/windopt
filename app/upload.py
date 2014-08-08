import os
import flask
from flask import Flask, request, redirect, url_for, render_template
from app import app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    print "At upload"
    if request.method == 'POST':
        file = request.files['file']
        print "Got File"
        if file and allowed_file(file.filename):
            print "File is allowed"
            #filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'winddata.csv'))
            return flask.jsonify({'status':'success'})