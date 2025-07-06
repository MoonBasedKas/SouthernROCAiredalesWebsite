from flask import Flask
from flask import render_template
from flask import Flask, jsonify, request

import pandas
import dbController

# db = dbController.dbController()

dogDB=None
photos=None
try:
    dogDB = pandas.read_csv("dogs.csv")
except:
    pass

try:
    photos = pandas.read_csv("photos.csv")
except:
    pass
    
app = Flask(__name__)


# @app.route('/home')
# def Welcome(name = None):
#     return render_template('index.html', person=name)

@app.route('/')
@app.route('/home')
@app.route('/index')
def Welcome():
    available = dogDB[dogDB["available"] == True]
    
    males = available[available["gender"] ==  True]
    females = available[available["gender"] ==  False]
    return render_template('home.html', males=males.values.tolist(), females=females.values.tolist())


"""
For viewing all the dogs
"""
@app.route('/dogs/<gender>')
def dogs():
    return render_template('dogs.html')


"""
For viewing a singular dog
"""
@app.route('/dogs/dog/<int:id>')
def dog(id):
    dog = dogDB[dogDB["id"] == id]

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
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, Threading=True)