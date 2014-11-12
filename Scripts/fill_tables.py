# A script to parse collections of chess games in PGN format and insert them
# into the database

import sys
import mysql.connector
from mysql.connector import errorcode

if len(sys.argv) !=3:
	print "Usage: python fill_tables.py username password"
	sys.exit()
#connect to the database
username = sys.argv[1]
passwd   = sys.argv[2]
database = 'ChessDB'
try:
  cnx = mysql.connector.connect(user = username,
  	                            password = passwd,
                                database = database)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exists")
  else:
    print(err)



 cnx.close()