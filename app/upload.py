import os
from flask import Flask, request, redirect, url_for, render_template
from app import app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'winddata.csv'))
            return redirect(url_for('visualization',
                                    filename='winddata.csv'))
    return render_template("upload.html")