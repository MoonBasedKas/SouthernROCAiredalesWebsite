from flask import Flask
from flask import render_template
from flask import Flask, jsonify, request

app = Flask(__name__)


# @app.route('/home')
# def Welcome(name = None):
#     return render_template('index.html', person=name)

@app.route('/')
@app.route('/home')
@app.route('/index')
def Welcome():
    return render_template('home.html')

