# A script to parse collections of chess games in PGN format and insert them
# into the database

from __future__ import print_function
import sys
import mysql.connector
from mysql.connector import errorcode

DATABASE = "TestChessDB"
DEBUG = True 

def dbConnect(username, passwd, database):
	try:
		db = mysql.connector.connect(user = username,
									  password = passwd,
									  database = database)
									  
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exists")
		else:
			print(err)
		sys.exit()
	return db	

def execSql(cursor, sqlStmt):
    try:
        cursor.execute(sqlStmt)
    except mysql.connector.Error as err:
        print("mysql.Error: %s" % err)
    if DEBUG: print(cursor._executed, '\n')


def execSqlWithParams(cursor, sqlStmt, params):
    try:
        cursor.execute(sqlStmt, params)
    except mysql.connector.Error as err:
        print("mysql.Error: %s" % err)
    if DEBUG: print(cursor._executed, "params:", params, '\n')

def main():	
	# Validate input parameters
	if len(sys.argv) !=3:
		print("Usage: python fill_tables.py username password")
		sys.exit()

	# Connect to the database
	username = sys.argv[1]
	passwd   = sys.argv[2]
	database = DATABASE
	db = dbConnect(username, passwd, database)
	

	#Insert rows into the database
	addUserStmt = ("INSERT INTO Users "
				   "(username, password, email) "
				   "VALUES (%(username)s, %(password)s, %(email)s)" )
	data_user1 = {
		'username' : 'dummy_user1'
	   ,'password' : 'dummy_pass1'
	   ,'email'    :  'dummy_email1'
	};   

	data_user2 = {
		'username' : 'dummy_user2'
	   ,'password' : 'dummy_pass2'
	   ,'email'    : None
	};   
	
	data = [data_user1, data_user2]
	
	cursor = db.cursor()
	for d in data:
		execSqlWithParams(cursor, addUserStmt, d)
	db.commit()
	cursor.close()
	db.close()
	
if __name__ == '__main__':
	status = main()