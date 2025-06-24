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
def dog(id=0):
    photos = ["PlaceHolder.png"]
    name = "null"
    desc = "null description"
    dob = "1970/1/1"
    gender = False # False == Female because both start with f.

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