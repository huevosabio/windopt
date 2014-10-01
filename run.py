#!venv/bin/python
from app import app

app.host = '0.0.0.0'
app.debug = True

#app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')