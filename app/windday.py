from flask import render_template
from app import app

@app.route('/')
def home():
    #return app.render_template('windday.html')
    return app.send_static_file('cranepath.html')
    
@app.route('/cranepath')
def cranepath():
    return app.send_static_file('cranepath.html')