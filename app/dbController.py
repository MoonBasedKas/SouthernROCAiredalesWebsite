import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

class dbController:
    def __init__(self):
        env = open(".env", "r")
        lines = env.readlines()
        user = lines[0].split("=")[1].strip()
        password = lines[1].split("=")[1].strip()
        host = lines[2].split("=")[1].strip()
        port = lines[3].split("=")[1].strip()
        database = lines[4].split("=")[1].strip()
        self.cnx = mysql.connector.connect(user=user, password=password,
                                host=host,
                                port=port, # Change this as need be
                                database=database)
        self.cursor = self.cnx.cursor()

    """
    Returns dictionary of the query result.
    """
    def fetchDog(self, id):
        query = 'select id, dogName, gender, available, registration, dob, mainPhoto, dogDesc, purchase from dogs where id = %s'
        params = (id,)
        self.cursor.execute(query, params)
        
        # Fetch the data found.
        fetchedData = self.cursor.fetchall()
        return fetchedData
    



    """
    Fetches all available dogs
    """
    def getAvail(self):
        query = 'select id, dogName, gender, available, registration, dob, mainPhoto, dogDesc, purchase from dogs where available = %s'
        params = (True,)
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchall()
        return fetchedData
    

    """
    Fetches all available dogs
    """
    def getAvailFemales(self):
        query = 'select id, dogName, gender, available, registration, dob, mainPhoto, dogDesc, purchase from dogs where available = %s and gender = %s'
        params = (True, False, )
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchall()
        return fetchedData
    

    """
    Fetches all available dogs
    """
    def getAvailMales(self):
        query = 'select id, dogName, gender, available, registration, dob, mainPhoto, dogDesc, purchase from dogs where available = %s and gender = %s'
        params = (True, True, )
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchall()
        return fetchedData
    

    def getVisiblePuppies(self):
        query = 'select id, photoName, dateTaken, visible, photo from Puppies where visible = %s'
        params = (True, )
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchall()
        return fetchedData
    
    def getVisiblePuppiesIdRange(self, low, max):
        query = 'select id, photoName, dateTaken, visible, photo from Puppies where visible = %s and id > %s and id < %s'
        params = (True, low, max, )
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchall()
        return fetchedData
    
    def getPuppiesIdRange(self, low, max):
        query = 'select id, photoName, dateTaken, visible, photo from Puppies where id > %s and id < %s'
        params = (low, max, )
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchall()
        return fetchedData

    def getTotalPuppies(self):
        query = 'select count(id) from Puppies where visible = %s'
        params = (True,)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def getTotalPhotos(self):
        query = 'select count(id) from photos'
        params = ()
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    
    def getTotalDogs(self):
        query = 'select count(id) from dogs'
        params = ()
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def getMaxID(self):
        query = 'select max(id) from dogs'
        params = ()
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    """
    Fetches the images for a given dog.
    """
    def fetchImage(self, id):
        query = 'select photoName from photos where dogId = %s'
        params = (id,)
        self.cursor.execute(query, params)
        
        # Fetch the data found.
        fetchedData = self.cursor.fetchall()
        data = fetchedData
        return data
    
    
    """
    Fetches the images for a given dog.
    """
    def fetchImageID(self, id):
        query = 'select id, photoName from photos where dogId = %s'
        params = (id,)
        self.cursor.execute(query, params)
        
        # Fetch the data found.
        fetchedData = self.cursor.fetchall()
        data = fetchedData
        return data
    

    """
    Inserts a dog into the database.
    """
    def insertDog(self, name, gender, available, registration, dob, mainPhoto, dogDesc, purchase):
        query = "INSERT INTO dogs (dogName, gender, available, registration, dob, mainPhoto, dogDesc, purchase) Values (%s, %s, %s, %s, %s, %s, %s, %s)"
        params = (name, gender, available, registration, dob, mainPhoto, dogDesc, purchase, )
        
        self.cursor.execute(query, params)
        self.cnx.commit()

    def getDogID(self, name, gender, available, registration, dob, mainPhoto, dogDesc, purchase):
        query = "select id from dogs where dogName = %s and gender = %s and available = %s and registration = %s and dob = %s and mainPhoto = %s and dogDesc = %s and purchase = %s"
        params = (name, gender, available, registration, dob, mainPhoto, dogDesc, purchase, )
        
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchone()
        return fetchedData[0]

    """
    Inserts a photo
    """
    def insertPhoto(self, dogID, photoName):
        query = "INSERT INTO photos (dogId, photoName) Values (%s, %s)"
        params = (dogID, photoName, )
        self.cursor.execute(query, params)
        self.cnx.commit()

    """
    Gets the Available dogs.
    """
    def insertPuppy(self, photoName, dateTaken, visible, photo):
        query = "Insert into Puppies (photoName, dateTaken, visible, photo) values (%s, %s, %s, %s)"
        params = (photoName, dateTaken, visible, photo)
        self.cursor.execute(query, params)
        self.cnx.commit()

    """
    Inserts a new user, returns false if user already exists.
    """
    def insertUser(self, username, password):
        query = "select * from Users where username = %s"
        params = (username, )
        self.cursor.execute(query, params)
        res = self.cursor.fetchone()
        if res != None:
            return False
        
        query = "insert into users (username, password) values (%s, %s)"
        params = (username, generate_password_hash(password),)
        self.cursor.execute(query, params)
        self.cnx.commit()

        return True
    

    """
    Checks if the correct crediental were put in for the user
    """
    def validateSignin(self, username, password):
        query = "select username, password from Users where username = %s"
        params = (username, )
        self.cursor.execute(query, params)

        data = self.cursor.fetchall()
        if data == []:
            return False
        return check_password_hash(data[0][1], password)
    

    """
    Sets a new account password.
    """
    def newPassword(self, username, password):
        query = "select username, password from Users where username = %s"
        params = (username, )
        self.cursor.execute(query, params)

        data = self.cursor.fetchone()
        if data == None:
            return False
        
        query = "update Users set password = %s where username = %s"
        params = (generate_password_hash(password), username, )
        self.cursor.execute(query, params)
        self.cnx.commit()


        return check_password_hash(data[0][1], password)
    
    """
    Updates all values of the dog except for its main photo.
    """
    def updateDog(self, id, name, gender, available, registration, dob, dogDesc, purchase):
        query = "update dogs set dogName=%s, gender=%s, available=%s, registration=%s, dob=%s, dogDesc=%s, purchase=%s where id = %s"
        params = (name, gender, available, registration, dob, dogDesc, purchase, id, )
        
        self.cursor.execute(query, params)
        self.cnx.commit()

    """
    Updates a main photo for a given dog.
    """
    def updateMainPhoto(self, dogID, mainphoto):
        query = "update dogs set mainPhoto = %s where id = %s"
        params = (mainphoto, dogID, )
        print(params)
        self.cursor.execute(query, params)
        self.cnx.commit()

    """
    Deletes a given photo from the database.
    """
    def deletePhoto(self, id):
        query = "DELETE from photos where id = %s"
        params = (id,)
        self.cursor.execute(query, params)
        self.cnx.commit()

    """
    Gets all dogs stored in the database.
    """
    def getDogs(self):
        query = 'select id, dogName, gender, available, registration, dob, mainPhoto, dogDesc, purchase from dogs'
        params = ()
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchall()
        return fetchedData
    
    """
    Gets a range of dog ids.
    """
    def getDogsIdRange(self, low, max):
        query = 'select id, dogName, gender, available, registration, dob, mainPhoto, dogDesc, purchase from dogs where id > %s and id < %s'
        params = (low, max, )
        self.cursor.execute(query, params)
        fetchedData = self.cursor.fetchall()
        return fetchedData
    
    """
    Updates the visibility of a puppy's photo.
    """
    def puppiesUpdateVisisible(self, id, vis):
        query = 'update Puppies set visible = %s where id = %s'
        params = (vis, id, )
        self.cursor.execute(query, params)
        self.cnx.commit()