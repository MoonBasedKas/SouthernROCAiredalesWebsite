import mysql.connector


class dbController:
    def __init__(self):
        env = open("DB_CONFIG", "r")
        lines = env.readlines()
        user = lines[0].split("=")[1].strip()
        password = lines[1].split("=")[1].strip()
        self.cnx = mysql.connector.connect(user=user, password=password,
                                host='127.0.0.1',
                                database='dogs')
        self.cursor = self.cnx.cursor()

    """
    Returns dictionary of the query result.
    """
    def fetchDog(self, id):
        query = 'select dogName, gender, available, dogDesc from dogs where id = %s'
        # query = 'select * from dogs'
        params = (id,)
        self.cursor.execute(query, params)
        
        # Fetch the data found.
        fetchedData = self.cursor.fetchall()
        data = {"dogName":fetchedData[0], "gender":fetchedData[1], "available":fetchedData[2], "dogDesc":fetchedData[3]}
        return data
    