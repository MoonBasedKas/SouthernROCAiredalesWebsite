from flask import Flask
from flask import render_template
from models import dbCon, main, paillierObj, paillerKeys





from flask import Flask, jsonify, request
keys = paillerKeys.paillerKeys() # Update this
db = dbCon.DBCon() # Connect to the database
app = Flask(__name__)


# @app.route('/home')
# def Welcome(name = None):
#     return render_template('index.html', person=name)

@app.route('/')
@app.route('/home')
def Welcome():
    return render_template('home.html')