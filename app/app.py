from flask import Flask, render_template, jsonify, request, redirect, session, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import threading
import pandas
import numpy as np
import math as mt
import secrets
from datetime import date # I'm not sure why this says its not used.


#Create the pandas database. Slower than sql but I don't think this database will ever get so large it won't matter.
dogDB = None
photoDB = None
counter = 0
UPLOAD_FOLDER="static/dogPhotos/"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PUPPY_FOLDER="static/puppies/"
try:
    dogDB = pandas.read_csv("Dogs.tsv",  sep='\t')

except:
    print("failed read")
    dogDB=pandas.DataFrame(columns=["id", "name", "gender", "available", "registration", "dob", "mainPhoto", "desc", "purchase"])

try:
    puppiesDB = pandas.read_csv("Puppies.tsv", sep='\t')
except:
    puppiesDB = pandas.DataFrame(columns=["id", "photoName", "photo", "date", "visible", "photo"])


try:
    photoDB = pandas.read_csv("Photos.tsv", sep="\t")

except:
    photoDB=pandas.DataFrame(columns=["id", "dogID", "photoName"])

try:
    airedaleDB = pandas.read_csv("Blacks.tsv", sep="\t")
except:
    airedaleDB = pandas.DataFrame(columns=["id", "photoName"])


# App Config
app = Flask(__name__)

app.secret_key = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

autoKeyReset = False
lastReset = date.today()



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



@app.route('/')
def Welcome():
    global counter
    
    available = dogDB[dogDB["available"] == True]
    males = available[available["gender"] ==  True]
    females = available[available["gender"] ==  False]
    # print(puppiesDB)
    puppies = puppiesDB[puppiesDB["visible"] == True]
    # puppies = puppiesDB[puppiesDB["photo"] == True]
    
    puppies = puppies.sort_values(by='id', ascending=False)

    

    puppies = puppies[:12]
    
    # Set Cookies
    visit = request.cookies.get("visited")
    if visit != "true":
        counter += 1
    else:
        resp = make_response(render_template('home.html', males=males.values.tolist(), females=females.values.tolist(), count=counter))
        resp.set_cookie(key="visited", value="true", max_age=90*60*60*24)
        return resp
    return render_template('home.html', airedales=airedaleDB.values.tolist(), males=males.values.tolist(), females=females.values.tolist(), puppies=puppies.values.tolist(), count=counter)

@app.route("/blackAiredale")
def blacks():
    return render_template('blackAiredale.html', airedales=airedaleDB.values.tolist())

@app.route("/myPartner")
def myPartner():
    return render_template('jaunCarlos.html')


"""
Shows all of the dogs for what to modify
"""
@app.route("/puppies", methods=["GET"])
def puppies():
    querySize = 30

    result = puppiesDB[puppiesDB["visible"] == True]
    result = result.sort_values(by='id', ascending=False)
    
    pageNo = request.args.get('page', default=0, type=int)
    query = request.args.get('search', default="", type=str)
    window = request.args.get('window', default="none", type=str)

    if window == 'inc':
        pageNo += 1
    elif window == 'dec':
        pageNo -= 1
        if pageNo < 0:
            pageNo = 0

    # if query != "":
    #     result = result[result["name"].str.contains(query, case=False)]

    
    pageMax = result.shape[0]
    pageMax = pageMax / querySize
    pageMax = mt.ceil(pageMax)

    if pageMax == pageNo:
        pageNo = pageMax - 1
    page = pageNo * querySize
    # Adjusts indeces
    result = result[page:page + querySize - 1]
    return render_template('puppies.html', results=result.values.tolist(), query=query, pageNo=pageNo, pageMax=pageMax)


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
    query = dog.values.tolist()
    if query == []:
        return render_template('noDog.html')
    photos = photoDB[photoDB["dogID"] == id]
    photos = photos[["photoName"]].values.tolist()

    query = query[0]
    name = query[1]
    gender = query[2]
    org = query[4]
    try:
        org = bool(org)
    except:
        org = True

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
    dogID = 1
    photoID = 0
    purchase = False
    if "username" not in session:
        return redirect(url_for("Welcome"))

    fname = ""

    if dogDB.size != 0:
        dogID = dogDB["id"].max() + 1

    if dogID == np.nan:
        dogID = 1
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
    desc = desc.replace("\t", "&emsp;")


    if 'files[]' not in request.files:
        print("no photo sent")
    else:
        if 0 != photoDB.size:
            photoID = photoDB['id'].max()

        sent = request.files.getlist('files[]')
        for file in sent:
            # try:
                fname = secure_filename(str(photoID) + file.filename)
                # TODO: Check file types
                file.save(UPLOAD_FOLDER + fname)
                photoID += 1
                # This could honestly slow everything down a lot.
                addPhoto(photoID, dogID, fname)
            # except:
            #     print
            #     pass


    if fname == "":
        fname = "placeholder.jpg"

    addDog(dogID, name, gender, avail, reg, dob, fname, desc, purchase)


    threading.Thread(target=saveUpdates, args=([])).start()


    return redirect(url_for('admin'))


"""
Does the request for when an admin sends a new dog to add.
"""
@app.route("/admin/newPuppy", methods=["POST"])
def newPuppy():
    if "username" not in session:
        return redirect(url_for('Welcome'))

    photoID = 0
    photo = True



    if puppiesDB.size != 0:
        photoID = puppiesDB["id"].max() + 1


    if 'files[]' not in request.files:
        print("no photo sent")
    else:
        day = date.today()
        sent = request.files.getlist('files[]')
        for file in sent:
                fname = secure_filename(str(photoID) + file.filename)
                if ".mp4" in fname.lower():
                    photo = False
                else:
                    photo = True



                file.save(PUPPY_FOLDER + fname)
                
                addPuppy(photoID, fname, day, True, photo)
                photoID += 1




    threading.Thread(target=savePuppies, args=([])).start()


    return redirect(url_for('admin'))

"""
Admin page for hiding videos.
"""
@app.route("/admin/puppyPhotos")
def viewPuppies():
    if "username" not in session:
        return redirect(url_for('Welcome'))
    querySize = 30

    result = puppiesDB
    result = result.sort_values(by='id', ascending=False)
    
    pageNo = request.args.get('page', default=0, type=int)
    query = request.args.get('search', default="", type=str)
    window = request.args.get('window', default="none", type=str)

    if window == 'inc':
        pageNo += 1
    elif window == 'dec':
        pageNo -= 1
        if pageNo < 0:
            pageNo = 0

    
    pageMax = result.shape[0]
    pageMax = pageMax / querySize
    pageMax = mt.ceil(pageMax)

    if pageMax == pageNo:
        pageNo = pageMax - 1
    page = pageNo * querySize
    # Adjusts indeces
    result = result[page:page + querySize - 1]
    return render_template('adminPuppies.html', results=result.values.tolist(), query=query, pageNo=pageNo, pageMax=pageMax)


"""
Updates if a photo should be visible to users or not.
"""
@app.route("/admin/updateVisible/<int:id>", methods=["POST"])
def updateVisible(id):
    if "username" not in session:
        return redirect(url_for('Welcome'))
    
    newValue = request.form["visible"]

    if newValue == "True":
        newValue = True
    else:
        newValue = False
    
    puppiesDB.loc[puppiesDB["id"] == id, "visible"] = newValue
    threading.Thread(target=savePuppies, args=[]).start()
    
    return redirect(url_for('viewPuppies'))

"""
Shows all of the dogs for what to modify
"""
@app.route("/admin/dogs", methods=["GET"])
def dogQuery():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    querySize = 18

    result = dogDB
    pageNo = request.args.get('page', default=0, type=int)
    query = request.args.get('search', default="", type=str)
    window = request.args.get('window', default="none", type=str)

    if window == 'inc':
        pageNo += 1
    elif window == 'dec':
        pageNo -= 1
        if pageNo < 0:
            pageNo = 0

    if query != "":
        result = result[result["name"].str.contains(query, case=False)]


    pageMax = result.shape[0]
    pageMax = pageMax / querySize
    pageMax = mt.ceil(pageMax)

    if pageMax == pageNo:
        pageNo = pageMax - 1
    page = pageNo * querySize
    # Adjusts indeces
    result = result.loc[page:page + querySize - 1]
    return render_template('adminDogs.html', results=result.values.tolist(), query=query, pageNo=pageNo, pageMax=pageMax)


"""
Shows all of the dogs for what to modify
"""
@app.route("/admin/update/<int:id>", methods=["POST"])
def updateDog(id):
    purchase = False
    if "username" not in session:
        return redirect(url_for("Welcome"))


    fname = ""
    if "username" not in session:
        return redirect(url_for("Welcome"))

    dogID = int(request.form['dogID'])

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
    desc = desc.replace("\t", "&emsp;")



    if 'files[]' not in request.files:
        print("Warning | No photo sent.")
    else:
        photoID = photoDB['id'].max()
        sent = request.files.getlist('files[]')
        check = True
        size = photoDB[photoDB["dogID"] == dogID].size
        for file in sent:
            if file.filename != "":
                try:
                    fname = secure_filename(str(photoID) + file.filename)

                    print(sent)
                    # TODO: Check file types
                    file.save(UPLOAD_FOLDER + fname)
                    photoID += 1
                    # Avoid checking the count each time after its been set
                    print(photoDB[photoDB["dogID"] == dogID].size)
                    if size == 0:
                        dogDB.loc[dogDB["id"] == dogID, "mainPhoto"] = fname
                        size += 1

                    addPhoto(photoID, dogID, fname)
                except:
                    pass





    if fname == "":
        fname = "placeholder.jpg"

    updateDog(dogID, name, desc, dob, gender, avail, reg, purchase)
    # saveUpdates()
    threading.Thread(target=saveUpdates, args=()).start()
    return redirect(f"/admin/details/{dogID}")


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
        return render_template('noDog.html')
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

    pics = photoDB[photoDB["dogID"] == id]
    pics = pics.values.tolist()

    return render_template('details.html', id=id, pics=pics, name=name, gender=gender, dob=dob, desc=desc, mainPhoto=mainPhoto, org=org, avail=avail)

@app.route("/admin/deletePhoto", methods=["POST"])
def deletePhoto():
    if "username" not in session:
        return redirect(url_for("Welcome"))

    photoID = request.form["photoID"]
    photoID = int(photoID)
    dogID = int(request.form["dogID"])
    photoName = photoDB.loc[photoDB["id"] == photoID, "photoName"].item()

    photoDB.loc[photoDB["id"] == photoID, "dogID"] = -1 # invalidate photo
    value = dogDB.loc[dogDB["id"] == dogID, "mainPhoto"].item()

    # Attempt to find a replacement
    if photoName == value:
        try:
            canidates = photoDB[photoDB["dogID"] == dogID][["photoName"]]
            if canidates == []:
                raise ValueError

            dogDB.loc[dogDB["id"] == dogID, "mainPhoto"] =  canidates[0][0]
        except:
            dogDB.loc[dogDB["id"] == dogID, "mainPhoto"] = "placeholder.jpg"

    threading.Thread(target=saveUpdates).start()
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
    threading.Thread(target=saveUpdates).start()
    return redirect(f"/admin/details/{dogID}")


@app.route("/admin/settings", methods=["GET"])
def settings():
    if "username" not in session:
        return redirect(url_for("Welcome"))

    return render_template('settings.html')


"""
Generates a new Secret Key
"""
@app.route("/admin/keyReset", methods=["POST"])
def keyReset():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    app.secret_key = secrets.token_hex(32)
    return render_template('settings.html')

"""
Resets the logged in users password.
"""
@app.route("/admin/passwordReset", methods=["POST"])
def passwordReset():
    if "username" not in session:
        return redirect(url_for("Welcome"))

    password = request.form['password']
    second = request.form['second']

    if second != password:
        return redirect(url_for('settings'))

    user = User.query.filter_by(username=session["username"]).first()

    user.set_password(password)
    db.session.commit()

    return redirect(url_for('settings'))



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
    if "username" not in session:
        return redirect(url_for('Welcome'))

    username = request.form['username']
    password = request.form['password']
    second = request.form['second']

    if second != password:
        return redirect(url_for('settings'))

    user = User.query.filter_by(username=username).first()
    if user:
        print("ERROR")
        return render_template("index.html", error="Username already exists")

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('admin'))

# Log out the user
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
    photoDB.loc[len(photoDB)] = new
    return

"""
Adds a new dog to the database
"""
def addDog(id, name, gender, available, registration, dob, mainPhoto, desc, purchase):
    new = {"id":id, "name":name, "gender":gender, "available":available, "registration":registration, "dob":dob, "mainPhoto":mainPhoto, "desc":desc, "purchase": purchase}
    dogDB.loc[len(dogDB)] = new
    return

"""
Saves updates to a database
"""
def saveUpdates():
    dogDB.to_csv("Dogs.tsv", sep="\t", index=False)
    photoDB.to_csv("Photos.tsv", sep="\t", index=False)
    return



def addPuppy(id, photoName, date, visible, photo):
    new = {"id":id,"photoName":photoName,"date":date, "visible":visible, "photo":photo}
    puppiesDB.loc[len(puppiesDB)] = new
    return

def savePuppies():
    puppiesDB.to_csv("Puppies.tsv", sep="\t", index=False)
    return

"""
Updates every parameter of a dog except for the mainPhoto
"""
def updateDog(id, name, desc, dob, gender, avail, reg, purchase):
    dogDB.loc[dogDB["id"] == id, "name"] = name
    dogDB.loc[dogDB["id"] == id, "desc"] = desc
    dogDB.loc[dogDB["id"] == id, "dob"] = dob
    dogDB.loc[dogDB["id"] == id, "gender"] = gender
    dogDB.loc[dogDB["id"] == id, "available"] = avail
    dogDB.loc[dogDB["id"] == id, "registration"] = reg
    dogDB.loc[dogDB["id"] == id, "purchase"] = purchase


with app.app_context():
    try:
        file = open(".env", "r")
        fp = file.readlines()
        db.create_all()
        username = fp[0].split("=")[1].strip()
        fresh = fp[2].split("=")[1].strip()
        # For some reason bool converts "False" -> True
        if fresh.lower() == "True":
            user = User.query.filter_by(username=username).first()
            if not user:
                new_user = User(username=username)
                new_user.set_password(fp[1].split("=")[1].strip())
                db.session.add(new_user)
                db.session.commit()
            # Write that this instance has been written to.
            file.close()
            file = open(".env", "w")
            file.write(f"username={username}\npassword={fp[1].split('=')[1].strip()}\nread=False")
    except FileNotFoundError:
        print("Warning | Login may not be possible.")

if __name__ == '__main__':


    app.run(debug=True)