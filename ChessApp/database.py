# contains helper functions to connect to and query the database
import sys
import mysql.connector
from mysql.connector import errorcode

def dbConnect(username, passwd, database,host):
    try:
        db = mysql.connector.connect(user = username,
                                     password = passwd,
                                     database = database,
                                     host = host)
                                      
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("ERROR: Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("ERROR: Database does not exists")
        else:
            print("ERROR:", err)
        sys.exit()
    return db   