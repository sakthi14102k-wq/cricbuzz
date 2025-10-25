import mysql.connector as my

def get_connection():
    return my.connect(
        host="localhost",
        user="root",
        password="sakthi@2000",
        database="crudtrail"
    )

