# A script to parse collections of chess games in PGN format and insert them
# into the database

from __future__ import print_function
import sys
import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime,

##############################################################
# CONSTANTS
##############################################################
DATABASE = "TestChessDB"
PGN_FILE  = "../data/out2.pgn"
DEBUG = True 

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
    
def getGame(pgn):
    data_game = 
    current_move_list = []
    "(event_site, event_name, event_round, date, "
    "white_player_name, black_player_name, "
    "white_title, black_title, "
    "white_player_rating, black_player_rating, "
    "result, ECO_code, opening, variation, "
    "number_of_moves, move_list, game_source) "
    #parse the metadata
    for line in pgn:
        if not line or line = '\n': break
        line = line.replace('[','').replace(']','').replace('"','').split()
        field_name = line[0]
        field_value = ' '.join(line[1:])
        if field_name in data_game:
            if field_name == 'Date':
                #convert date format
            data_game[field_name] = field_value
    #parse the move list
    for line in pgn:
        if not line or line = '\n': break

def getPlayedMoves(prior_position_list,current_move_list):
    data_played_moves_list = []
    for prior_pos,curr_move in zip(prior_position_list,current_move_list):
        data_played_move = {'prior_position':prior_pos
                           ,'current_move':curr_move}
        data_played_moves_list.append(data_played_move)
    return data_played_moves_list
      

    

	
##############################################################
# SQL INSERT STATEMENTS
##############################################################

#USERS TABLE
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

#PLAYED_MOVES TABLE
sqlInsertPlayedMove = (
  "INSERT INTO Played_Moves "
  "(prior_position, current_move) "
  "VALUES (%(prior_position)s, %(current_move)s)"  
)

#CONTAINED_MOVES TABLE
sqlInsertContained_Moves = (
  "INSERT INTO Contained_Moves "
  "(gid, mid)" 
  "VALUES (%(gid)s, %(mid)s)"
)

#SELECT PLAYED_MOVE
sqlSelectPlayedMove = (
  "SELECT P.mid"
  "FROM Played_Moves P"
  "WHERE p.prior_position = %(prior_position)s AND"
        "p.current_move = %(current_move)s"
)

###############################################################
# MAIN
##############################################################
def main():	
    # Validate number of input parameters
    if len(sys.argv) !=3:
        print("Usage: python fill_tables.py <username> <password>")
        sys.exit()

    # Connect to the database
    db = dbConnect(sys.argv[1], sys.argv[2], DATABASE)
    cursor = db.cursor()
    
    # Parse file, execute SQL statements, and commit transaction
    with open(PGN_FILE,'r') as pgn:
        game = getGame(pgn):
        while game:
            execSqlWithParams(cursor, sqlInsertGame, game)
            game = get_game(pgn)
    #TODO: 
    #insert into Games table
    #insert into Played_Moves table
    #insert into Contained_Moves table

    pgn = open(pgn_file,'r')
    fen = open(fen_file,'r')

    while true:
        data_game, current_move_list,  = getGame(pgn)
        if not current_move_list break
        #insert game into the database
        execSqlWithParams(cursor, sqlInsertGame, data_game)
        gid = cursor.lastrowid
        prior_position_list = getPriorPositions(fen)
        assert( len(prior_position_list) == len(current_move_list) )
        data_played_moves_list = getPlayedMoves(prior_position_list,
                                                current_move_list)
        for data_played_move in data_played_moves_list:
            #insert played_move into the DB
            execSqlWithParams(cursor, sqlInsertPlayedMove, data_played_move)
            #get the mid of the played_move
            mid = execSqlWithParams(cursor,sqlSelectPlayedMove,
                                    data_played_move)
            data_contained_move = {'gid' : gid,'mid' : mid}  
            #insert contained_move into the DB
            execSqlWithParams(cursor, sqlInsertContained_Moves,
                              data_contained_move)

    #close files and commit the transaction
    pgn.close()
    fen.close()
    db.commit()
    
   # Close connection to database 
    cursor.close()
    db.close()
    
if __name__ == '__main__':
    status = main()