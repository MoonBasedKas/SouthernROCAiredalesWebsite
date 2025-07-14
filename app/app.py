from flask import Flask, render_template, jsonify, request, redirect, session, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import threading
import pandas
import numpy as np
# import dbController

# Disable this
logins = True
# db = dbController.dbController()

#Create the pandas database. Slower than sql but I don't think this database will ever get so large it won't matter.
dogDB = None
photos = None
counter = 0
UPLOAD_FOLDER="./static/dogPhotos/"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
try:
    dogDB = pandas.read_csv("dogs.csv",  sep=',')
    # dogDB.set_index("id")
except:
    print("failed read")
    dogDB=pandas.DataFrame(columns=["id", "name", "gender", "available", "registration", "dob", "desc"])
    # dogDB.set_index("id")

try:
    photos = pandas.read_csv("photos.csv")
    # photos.set_index("id")
except:
    photos=pandas.DataFrame(columns=["id", "dogID", "photoName"])
    # photos.set_index("id")
    
# App Config    
app = Flask(__name__)
app.secret_key = "A Super Secret Key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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




# Protected pages
@app.route("/admin")
def admin():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    return render_template("admin.html")

"""
Does the request for when an admin sends a new dog to add.
"""
@app.route("/admin/newDog", methods=["POST"])
def newDog():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    
    fname = ""
    if "username" not in session:
        return redirect(url_for("Welcome"))
    
    dogID = dogDB["id"].max() + 1
    name = request.form['Name']

    gender = request.form['gender']
    if gender == "Female":
        gender = False
    else:
        gender = True

    avail = request.form['avail']
    if avail == "true":
        avail = True
    else:
        avail = False

    reg = request.form['reg']
    dob = request.form['dob']
    desc = request.form['desc']
    

    if 'files[]' not in request.files:
        print("no photo sent")
    else:
        photoID = photos['id'].max()
        sent = request.files.getlist('files[]')
        for file in sent:
            fname = secure_filename(file.filename)
            # TODO: Check file types
            file.save(UPLOAD_FOLDER + fname)
            photoID += 1
            # This could honestly slow everything down a lot.
            addPhoto(photoID, dogID, fname)


    if fname == "":
        fname = "placeholder.jpg"

    addDog(dogID, name, gender, avail, reg, dob, fname, desc)
    
    
    threading.Thread(target=saveUpdates, args=([]))    


    return redirect(url_for('admin'))

"""
Shows all of the dogs for what to modify
"""
@app.route("/admin/modify")
def modify():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    
    result = dogDB
    
    page = request.args.get('page', default=0, type=int) * 20
    query = request.args.get('search', default="", type=str)
    
    if query != "":
        result = result["name"].str.contains(query)

    result = result.loc[page:page + 20]


    return render_template('modify.html', results=result.values.tolist())


"""
Shows all of the dogs for what to modify
"""
@app.route("/admin/update/<int:id>", methods=["POST"])
def updateDog(id):
    if "username" not in session:
        return redirect(url_for("Welcome"))
    

    return redirect(url_for("modify"))


"""
Shows us the details of the dogs, let's us see each dog so we can modify it.
"""
@app.route("/admin/details/<int:id>")
def dogDetails(id):
    if "username" not in session:
        return redirect(url_for("Welcome"))
    dog = dogDB[dogDB["id"] == id]
    pics = ["PlaceHolder.png"]
    name = "null"
    desc = "null"
    dob = "1970/01/01"
    gender = "Female"
    mainPhoto=""
    org=""
    pics=[]
    query = dog.values.tolist()
    if query == []:
        # TODO upodate to no dog found.
        return render_template('dog.html', photos=photos, name=name, gender=gender, dob=dob, desc=desc, mainPhoto=mainPhoto, org=org)
    query = query[0] # Set to first value because it'll return [[]] if it exists.
    name = query[1]
    gender = query[2]
    avail = query[3]
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

    print(photos)
    pics = photos[photos["dogID"] == id]
    pics = pics.values.tolist()

    return render_template('details.html', id=id, pics=pics, name=name, gender=gender, dob=dob, desc=desc, mainPhoto=mainPhoto, org=org, avail=avail)
    
@app.route("/admin/deletePhoto", methods=["POST"])
def deletePhoto():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    photoID = request.form["photoID"]
    photoID = int(photoID)
    dogID = request.form["dogID"]
    
    photos.loc[photos["id"] == photoID, "dogID"] = -1
    print(photos)
    return redirect(f"/admin/details/{dogID}")

@app.route("/admin/setMainPhoto", methods=["POST"])
def setMainPhoto():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    photoName = request.form["photoName"]
    dogID = request.form["dogID"]
    dogID = int(dogID)
    # Query to update the dogs primary photo
    dogDB.loc[dogDB["id"] == dogID, "mainPhoto"] = photoName
    return redirect(f"/admin/details/{dogID}")


# Login Route
@app.route("/login", methods=["POST", "GET"])
def login():
    if "username" in session:
        return redirect(url_for("admin"))
    if request.method == "GET":
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('login'))


# Register Route
@app.route("/register", methods=["POST"])
def register():
    if not logins:
        return redirect(url_for('Welcome'))

    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="Username already exists")
    
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    session['username'] = username
    return redirect(url_for('admin'))


@app.route('/logout')
def logout():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    session.pop('username', None)

    return redirect(url_for('Welcome'))


# Util functions
"""
Adds a photo to the database
"""
def addPhoto(id, dogID, photo):
    new = {"id":id,"dogID":dogID,"photoName":photo}
    photos.loc[len(photos)] = new
    return

"""
Adds a new dog to the database
"""
def addDog(id, name, gender, available, registration, dob, mainPhoto, desc):
    new = {"id":id, "name":name, "gender":gender, "available":available, "registration":registration, "dob":dob, "mainPhoto":mainPhoto, "desc":desc}
    dogDB.loc[len(dogDB)] = new
    return

"""
Saves updates to a database

threads - the current disbatched threads. Waits until all threads are done before writing.
"""
def saveUpdates(threads):
    while threads != []:
        if not threads[0].is_alive():
            threads.pop(0)

    dogDB.to_csv("newDogs.csv")
    photos.to_csv("newPhotos.csv")
    return



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        try:
            fp = open(".env")
            fp = fp.readlines()
            username = fp[0].split("=")[1].strip()
            user = User.query.filter_by(username=username).first()
            if not user:
                new_user = User(username=username)
                new_user.set_password(fp[1].split("=")[1].strip())
                db.session.add(new_user)
                db.session.commit()
                
        except FileNotFoundError:
            print("Warning | Login may not be possible.")
    app.run(debug=True)