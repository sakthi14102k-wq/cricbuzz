import mysql.connector as my

def get_connection():
    """
    Create and return a MySQL database connection
    
    Returns:
        mysql.connector.connection: MySQL connection object
    """
    return my.connect(
        host="localhost",
        user="root",
        password="sakthi@2000",
        database="crudtrail"
    )
