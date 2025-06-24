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