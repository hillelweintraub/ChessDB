# contains helper functions to connect to and query the database
import sys
import mysql.connector
from mysql.connector import errorcode


##############################################################
# CONSTANTS
##############################################################
INFO = 0
DEBUG = 1 
WARNING = 2
ERROR = 3
FATAL = 4
DEBUG_LEVEL = DEBUG
##############################################################
# SQL STATEMENTS
##############################################################

#USERS TABLE
sqlSelectUser = (
  "SELECT u.uuid, u.username, u.password, u.email "
  "FROM Users u "
  "WHERE u.username = %(username)s AND u.password = %(password)s"
)

sqlInsertUser = (
  "INSERT INTO Users "
  "(username, password, email) "
  "VALUES (%(username)s, %(password)s, %(email)s)"
)   
                 
#GAMES TABLE
sqlInsertGame = (
  "INSERT INTO Games "
  "(Site, Event, Round, Date, White, Black, "
   "WhiteTitle, BlackTitle, WhiteElo, BlackElo, "
   "Result, ECO, Opening, Variation, "
   "number_of_moves, move_list, game_source) "
  "VALUES "
 "(%(Site)s, %(Event)s, %(Round)s, %(Date)s, %(White)s, %(Black)s, "
  "%(WhiteTitle)s, %(BlackTitle)s, %(WhiteElo)s, %(BlackElo)s, "
  "%(Result)s, %(ECO)s, %(Opening)s, %(Variation)s, "
  "%(number_of_moves)s, %(move_list)s, %(game_source)s) "   
)

sqlSelectGames = (
    "SELECT g.gid, g.Event "
    "FROM Games g "
    "WHERE g.gid<=10"
)

#PLAYED_MOVES TABLE
sqlInsertPlayedMove = (
  "INSERT INTO Played_Moves "
  "(prior_position, current_move) "
  "VALUES (%(prior_position)s, %(current_move)s)"  
)


##############################################################
# FUNCTIONS 
##############################################################

def dbConnect(username, passwd, database):
    try:
        db = mysql.connector.connect(user = username,
                                     password = passwd,
                                     database = database)
                                      
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("ERROR: Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("ERROR: Database does not exists")
        else:
            print("ERROR:", err)
        sys.exit()
    return db   


def execSql(cursor, sqlStmt):
    try:
        cursor.execute(sqlStmt)
        if DEBUG_LEVEL <= DEBUG: print("DEBUG: Executing ", cursor._executed,'\n')
        return 0
    except mysql.connector.Error as err:
        if DEBUG_LEVEL <= ERROR :
            print("ERROR: FAILED to execute: ", cursor._executed)
            print("ERROR: mysql.Error %s\n" % err)
        return -1

def execSqlWithParams(cursor, sqlStmt, params):
    try:
        cursor.execute(sqlStmt, params)
        if DEBUG_LEVEL <= DEBUG: print("DEBUG: Executing ", cursor._executed, "params:", params, '\n')
        return 0
    except mysql.connector.Error as err:
        if DEBUG_LEVEL <= ERROR:
            print("ERROR: FAILED to execute: ", cursor._executed, "params:", params)
            print("ERROR: mysql.Error: %s\n" % err)
        return -1
