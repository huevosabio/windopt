from flask import render_template, redirect
from app import app
from app.auth import *

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