from flask import Flask, render_template, jsonify, request, redirect, session, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import numpy as np
import math as mt
import secrets
from datetime import date # I'm not sure why this says its not used.
import dbController 

counter = 0
UPLOAD_FOLDER="static/dogPhotos/"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PUPPY_FOLDER="static/puppies/"




db = dbController.dbController()
print(db.fetchDog(1))



# App Config
app = Flask(__name__)

app.secret_key = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




@app.route('/')
def Welcome():
    global counter
    
    males = db.getAvailMales()
    females = db.getAvailFemales()
    puppies = db.getVisiblePuppies()

    
    puppies = puppies

    print(puppies.reverse())
    shown = []
    hits = 0
    for i in puppies:
        shown.append(i)
        if hits == 12:
            break
        hits += 1
    
    # Set Cookies
    visit = request.cookies.get("visited")
    if visit != "true":
        counter += 1
    else:
        resp = make_response(render_template('home.html', males=males, females=females.values, count=counter))
        resp.set_cookie(key="visited", value="true", max_age=90*60*60*24)
        return resp
    
    return render_template('home.html', males=males, females=females, puppies=shown, count=counter)

@app.route("/blackAiredale")
def blacks():
    return render_template('blackAiredale.html')

@app.route("/myPartner")
def myPartner():
    return render_template('jaunCarlos.html')


"""
Shows all of the dogs for what to modify
"""
@app.route("/puppies", methods=["GET"])
def puppies():
    querySize = 30

    
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

    
    pageMax = db.getTotalPuppies()[0]
    pageMax = pageMax[0]
    print(pageMax)
    pageMax = pageMax / querySize
    pageMax = mt.ceil(pageMax)

    if pageMax == pageNo:
        pageNo = pageMax - 1
    page = pageNo * querySize
    # Adjusts indeces
    result = db.getVisiblePuppiesIdRange(page, page + querySize)
    print(result)
    
    return render_template('puppies.html', results=result, query=query, pageNo=pageNo, pageMax=pageMax)


"""
For viewing a singular dog
"""
@app.route('/dogs/dog/<int:id>')
def dog(id):
    photos = ["PlaceHolder.png"]
    name = "null"
    desc = "null"
    dob = "1970/01/01"
    gender = "Female"
    mainPhoto=""
    org=""
    query = db.fetchDog(id)
    if query == []:
        return render_template('noDog.html')
    photos = db.fetchImage(id)
    query = query[0]
    print(photos)
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
    if reg == "True":
        reg = True
    else:
        reg = False
    dob = request.form['dob']
    desc = request.form['desc']
    desc = desc.replace("\t", "&emsp;")


    if 'files[]' not in request.files:
        print("no photo sent")
    else:
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






    return redirect(url_for('admin'))

"""
Admin page for hiding videos.
"""
@app.route("/admin/puppyPhotos")
def viewPuppies():
    if "username" not in session:
        return redirect(url_for('Welcome'))
    querySize = 30

    
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

    
    pageMax = db.getTotalPuppies()[0]
    pageMax = pageMax[0]
    print(pageMax)
    pageMax = pageMax / querySize
    pageMax = mt.ceil(pageMax)

    if pageMax == pageNo:
        pageNo = pageMax - 1
    page = pageNo * querySize
    # Adjusts indeces
    result = db.getVisiblePuppiesIdRange(page, page + querySize)
    print(result)

    return render_template('adminPuppies.html', results=result, query=query, pageNo=pageNo, pageMax=pageMax)


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
    
    db.puppiesUpdateVisisible(id, newValue)
    
    return redirect(url_for('viewPuppies'))

"""
Shows all of the dogs for what to modify
"""
@app.route("/admin/dogs", methods=["GET"])
def dogQuery():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    querySize = 18


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

    pageMax = db.getTotalDogs()[0]
    pageMax = pageMax[0]
    print(pageMax)
    pageMax = pageMax / querySize
    pageMax = mt.ceil(pageMax)

    if pageMax == pageNo:
        pageNo = pageMax - 1
    page = pageNo * querySize
    # Adjusts indeces
    result = db.getDogsIdRange(page, page + querySize)
    return render_template('adminDogs.html', results=result, query=query, pageNo=pageNo, pageMax=pageMax)


"""
Shows all of the dogs for what to modify
"""
@app.route("/admin/update/<int:id>", methods=["POST"])
def updateDog(id):
    purchase = False
    if "username" not in session:
        return redirect(url_for("Welcome"))


    fname = ""
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
    if reg == "True":
        reg = True
    else:
        reg = False
    dob = request.form['dob']
    desc = request.form['desc']
    desc = desc.replace("\t", "&emsp;")



    if 'files[]' not in request.files:
        print("Warning | No photo sent.")
    else:
        sent = request.files.getlist('files[]')
        check = True
        for file in sent:
            if file.filename != "":
                try:
                    fname = secure_filename(str(photoID) + file.filename)

                    print(sent)
                    # TODO: Check file types
                    file.save(UPLOAD_FOLDER + fname)
                    photoID += 1
                    # Avoid checking the count each time after its been set

                    addPhoto(photoID, dogID, fname)
                except:
                    pass





    if fname == "":
        fname = "placeholder.jpg"

    updateDog(dogID, name, desc, dob, gender, avail, reg, purchase)
    return redirect(f"/admin/details/{dogID}")


"""
Shows us the details of the dogs, let's us see each dog so we can modify it.
"""
@app.route("/admin/details/<int:id>")
def dogDetails(id):
    if "username" not in session:
        return redirect(url_for("Welcome"))
    dog = db.fetchDog(id)
    pics = ["PlaceHolder.png"]
    name = "null"
    desc = "null"
    dob = "1970/01/01"
    gender = "Female"
    mainPhoto=""
    org=""
    pics=[]

    if dog == []:
        # TODO upodate to no dog found.
        return render_template('noDog.html')
    query = dog[0]
    name = query[1]
    gender = query[2]
    avail = query[3]
    org = query[4]
    dob = query[5]
    mainPhoto= query[6]
    desc = query[7]
    if type(desc) == float:
        desc = ""

    pics = db.fetchImageID(id)
    print(pics)

    return render_template('details.html', id=id, pics=pics, name=name, gender=gender, dob=dob, desc=desc, mainPhoto=mainPhoto, org=org, avail=avail)

@app.route("/admin/deletePhoto", methods=["POST"])
def deletePhoto():
    if "username" not in session:
        return redirect(url_for("Welcome"))

    photoID = request.form["photoID"]
    photoID = int(photoID)
    dogID = int(request.form["dogID"])
    db.deletePhoto(photoID)

    return redirect(f"/admin/details/{dogID}")

@app.route("/admin/setMainPhoto", methods=["POST"])
def setMainPhoto():
    if "username" not in session:
        return redirect(url_for("Welcome"))
    photoName = request.form["photoName"]
    dogID = request.form["dogID"]
    dogID = int(dogID)
    # Query to update the dogs primary photo
    db.updateMainPhoto(id, photoName)
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

    db.newPassword(session["username"], password)

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

    if db.validateSignin(username, password):
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
    
    db.insertUser(username, password)

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
    db.insertPhoto(dogID, photo)
    return

"""
Adds a new dog to the database
"""
def addDog(id, name, gender, available, registration, dob, mainPhoto, desc, purchase):
    db.insertDog(name, gender, available, registration, dob, mainPhoto, desc, purchase)
    return




def addPuppy(id, photoName, date, visible, photo):
    db.insertPuppy(photoName, date, visible, photo)
    return

"""
Updates every parameter of a dog except for the mainPhoto
"""
def updateDog(id, name, desc, dob, gender, avail, reg, purchase):
    db.updateDog(id, name, gender, avail, reg, dob, desc, purchase)


with app.app_context():
        db.insertUser("ROCAdmin", "test1234")


if __name__ == '__main__':


    app.run(debug=True)