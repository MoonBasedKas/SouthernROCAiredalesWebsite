import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

class dbController:
    def __init__(self):
        env = open("DB_CONFIG", "r")
        lines = env.readlines()
        user = lines[0].split("=")[1].strip()
        password = lines[1].split("=")[1].strip()
        self.cnx = mysql.connector.connect(user=user, password=password,
                                host='127.0.0.1',
                                port=3307, # Change this as need be
                                database='SouthernROC')
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
    
    def getTotalPuppies(self):
        query = 'select count(id) from puppies where visible = %s'
        params = (True,)
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
    Inserts a dog into the database.
    """
    def insertDog(self, name, gender, available, registration, dob, mainPhoto, dogDesc, purchase):
        query = "INSERT INTO dogs (dogName, gender, available, registration, dob, mainPhoto, dogDesc, purchase) Values (%s, %s, %s, %s, %s, %s, %s, %s)"
        params = (name, gender, available, registration, dob, mainPhoto, dogDesc, purchase, )
        
        self.cursor.execute(query, params)
        self.cnx.commit()

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
        if self.cursor.fetchall() != []:
            return False
        
        query = "insert into users (username, password) values (%s, %s)"
        params = (username, generate_password_hash(password),)
        self.cursor.execute(query, params)
        self.cnx.commit()

        return True
    