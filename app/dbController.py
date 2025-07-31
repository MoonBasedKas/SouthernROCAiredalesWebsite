# print(__version__)

import mysql.connector
# import mariadb

class dbController:
    def __init__(self):
        env = open("DB_CONFIG", "r")
        lines = env.readlines()
        user = lines[0].split("=")[1].strip()
        password = lines[1].split("=")[1].strip()
        self.cnx = mysql.connector.connect(user=user, password=password,
                                host='127.0.0.1',
                                port=3307,
                                database='dogs')
        self.cursor = self.cnx.cursor()

    """
    Returns dictionary of the query result.
    """
    def fetchDog(self, id):
        query = 'select dogName, gender, available, dogDesc from dogs where id = %s'
        params = (id,)
        self.cursor.execute(query, params)
        
        # Fetch the data found.
        fetchedData = self.cursor.fetchall()
        if fetchedData == []:
            return {}
        
        print(fetchedData)
        # data = {"dogName":fetchedData[0][0], "gender":fetchedData[0][1], "available":fetchedData[0][2], "dogDesc":fetchedData[0][3]}
        # return data
    
    """
    Fetches the images for a given dog.
    """
    def fetchImage(self, id):
        query = 'select photoName from images where id = %s'
        params = (id,)
        self.cursor.execute(query, params)
        
        # Fetch the data found.
        fetchedData = self.cursor.fetchall()
        data = fetchedData
        return data