from flask import render_template, redirect
from app import app

@app.route('/')
def home():
    return redirect('/windyday')
    
@app.route('/windyday')
def windyday():
    #return app.render_template('windday.html')
    return app.send_static_file('index.html')
    
@app.route('/cranepath')
def cranepath():
    return app.send_static_file('zipupload.html')