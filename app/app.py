from flask import Flask, render_template, jsonify, request, redirect, session, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

import pandas
import numpy as np
# import dbController

restrictedPages = {}

# db = dbController.dbController()

#Create the pandas database. Slower than sql but I don't think this database will ever get so large it won't matter.
dogDB = None
photos = None
counter = 0
try:
    dogDB = pandas.read_csv("dogs.csv")
except:
    dogDB=pandas.DataFrame(columns=["id", "name", "gender", "available", "registration", "dob", "desc"])

try:
    photos = pandas.read_csv("photos.csv")
except:
    photos=pandas.DataFrame(columns=["id", "dogID", "photoName"])
    
# App Config    
app = Flask(__name__)
app.secret_key = "A Super Secret Key"




# Config of SQL alchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# @app.route('/home')
# def Welcome(name = None):
#     return render_template('index.html', person=name)

@app.route('/')
@app.route('/home')
@app.route('/index')
def Welcome():
    global counter

        
    available = dogDB[dogDB["available"] == True]
    
    males = available[available["gender"] ==  True]
    females = available[available["gender"] ==  False]

    # Set Cookies
    visit = request.cookies.get("visited")
    if visit != "true":
        counter += 1
    else:
        resp = make_response(render_template('home.html', males=males.values.tolist(), females=females.values.tolist(), count=counter))
        resp.set_cookie(key="visited", value="true", max_age=90*60*60*24)
        return resp

    return render_template('home.html', males=males.values.tolist(), females=females.values.tolist(), count=counter)


"""
For viewing all the dogs
"""
@app.route('/dogs/<string:gender>')
def dogs(gender):
    
    # Female is only false because they both start with f.
    if gender.lower() == "female":
        dog = dogDB[dogDB["gender"] == False]
    else:
        dog = dogDB[dogDB["gender"] == True]

    return render_template('dogs.html', dogInfo=dogs.values.tolist())


"""
For viewing a singular dog
"""
@app.route('/dogs/dog/<int:id>')
def dog(id):
    dog = dogDB[dogDB["id"] == id]
    photos = ["PlaceHolder.png"]
    name = "null"
    desc = "null"
    dob = "1970/01/01"
    gender = "Female"
    mainPhoto=""
    org=""
    photos=[]
    query = dog.values.tolist()
    if query == []:
        return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc, mainPhoto=mainPhoto, org=org)
    print(query)
    query = query[0]
    name = query[1]
    gender = query[2]
    org = query[4]
    dob = query[5]
    mainPhoto= query[6]
    desc = query[7]
    if type(desc) == float:
        desc = ""

    if gender:
        gender = "Male"
    else:
        gender = "Female"

    return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc, mainPhoto=mainPhoto, org=org)

# def dog():
#     photos = ["PlaceHolder.png"]
#     name = "null"
#     desc = "null description"
#     dob = "1970/1/1"
#     gender = False # False == Female because both start with f.

#     # Parameter fetching
#     id = request.args.get("id")
#     # if id == None:
#     if id == None:
#         return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc)
#     id = int(id)
#     result = db.fetchDog(id)
#     images = db.fetchImage(id)

#     # If any images assign
#     if images != []:
#         photos = images
    
#     # If dog doesn't exist write error page.
#     if result.get("dogName", None) == None:
#         return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc)

#     name = result["dogName"]
#     gender = result["gender"]
#     # dob = result["dob"]
#     desc = result["dogDesc"]

#     if gender:
#         gender = "Male"
#     else:
#         gender = "Female"
#     return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc)

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
    if "username" in session:
        return "yes"
    return render_template('contact.html')




# Login Magic
# Remember to use do @login_required
# def login_required(secrets, funcName):
#     if "username" not in session:
#         return redirect(url_for("home"))
#     return secrets[funcName]

# Protected pages
@app.route("/secret")
def secret():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    return "Secret Key"





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)