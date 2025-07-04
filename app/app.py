from flask import Flask
from flask import render_template
from flask import Flask, jsonify, request

import pandas
import dbController

db = dbController.dbController()


try:
    dogs = pandas.read_csv("dogs.csv")
except:
    dogs = None
    
app = Flask(__name__)


# @app.route('/home')
# def Welcome(name = None):
#     return render_template('index.html', person=name)

@app.route('/')
@app.route('/home')
@app.route('/index')
def Welcome():
    return render_template('home.html')


"""
For viewing all the dogs
"""
@app.route('/dogs')
def dogs():
    return render_template('dogs.html')


"""
For viewing a singular dog
"""
@app.route('/dog')
def dog():
    photos = ["PlaceHolder.png"]
    name = "null"
    desc = "null description"
    dob = "1970/1/1"
    gender = False # False == Female because both start with f.

    # Parameter fetching
    id = request.args.get("id")
    # if id == None:
    if id == None:
        return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc)
    id = int(id)
    result = db.fetchDog(id)
    images = db.fetchImage(id)

    # If any images assign
    if images != []:
        photos = images
    
    # If dog doesn't exist write error page.
    if result.get("dogName", None) == None:
        return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc)

    name = result["dogName"]
    gender = result["gender"]
    # dob = result["dob"]
    desc = result["dogDesc"]

    if gender:
        gender = "Male"
    else:
        gender = "Female"
    return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc)

"""
I don't remember what this page was supposed to be./
"""
@app.route('/health_gaurantee')
def health():
    return render_template('health.html')


"""
For rendering the about us
"""
@app.route('/about')
def about():
    return render_template('about.html')


"""
For rendering the contact us
"""
@app.route('/contact')
def contact():
    return render_template('contact.html')