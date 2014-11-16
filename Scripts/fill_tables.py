# A script to parse collections of chess games in PGN format and insert them
# into the database

from __future__ import print_function
import sys
import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime
from math import ceil

##############################################################
# CONSTANTS
##############################################################
DATABASE = "TestChessDB"
PGN_FILE  = "../data/out2.pgn"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
START_FEN_PROCESSED = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
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
		return 0
    except mysql.connector.Error as err:
        print("mysql.Error: %s" % err)
		return -1
    if DEBUG: print(cursor._executed, '\n')


def execSqlWithParams(cursor, sqlStmt, params):
    try:
        cursor.execute(sqlStmt, params)
		return 0
    except mysql.connector.Error as err:
        print("mysql.Error: %s" % err)
		return -1
    if DEBUG: print(cursor._executed, "params:", params, '\n')
    
def getGame(pgn):
    data_game = {
      'Site':None, 'Event':None, 'Round':None, 'White':None, 'Black':None, 
      'WhiteTitle':None, 'BlackTitle':None, 'Date':None,  
      'WhiteElo':None, 'BlackElo':None, 'Result':None, 'ECO':None, 'Opening':None,
      'Variation':None, 'number_of_moves':None, 'move_list':None, 'game_source':None
    }
    
     moves = []
     
    #parse the metadata
    util_parseMetadata(pgn)
    for line in pgn:
        if not line or line == '\n': break
        line = line.strip().replace('[','').replace(']','').replace('"','').split()
        field_name = line[0]
        field_value = ' '.join(line[1:])
        if field_name in data_game:
            if field_name == 'Date':
                field_value = util_convert2SqlDate(field_value)
            data_game[field_name] = field_value
    #parse the move list
    # util_parseMovetext
    for line in pgn:
        if not line or line == '\n': break
        moves.append(line.strip())
    moves = ' '.join(moves)
    data_game['move_list'] = moves     
    moves = moves.split().pop() #split into tokens and get rid of result token 
    for token in moves[:]:
        if token[-1] == '.': moves.remove(token)  #remove move number tokens
    data_game['number_of_moves'] =  int(ceil(len(moves)/2.0)))    
    data_game['game_source'] = 'TWIC'
    return data_game, moves

def getPriorPositions(fen):
    prior_position_list = [START_FEN_PROCESSED] #include start position
    for line in fen:
        if line.strip() == START_FEN:
            if len(prior_position_list) > 1: break  #reached beginning of next game         
            else: continue                          #first game in file
        else:
            line = ' '.join(line.split()[:-2])
            prior_position_list.append(line)
    return prior_position_list        

def util_convert2SqlDate(field_value):
    field_value.replace(".","-")
    field_value.replace("??","01")
    return field_value
##############################################################
# SQL STATEMENTS
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

#CONTAINED_MOVEs TABLE
sqlInsertContained_Moves = (
  "INSERT INTO Contained_Moves "
  "(gid, mid)" 
  "VALUES (%(gid)s, %(mid)s)"
)

###############################################################
# MAIN
##############################################################
def main():	
    # Validate number of input parameters
    if len(sys.argv) !=3:
        print("Usage: python fill_tables.py <username> <password>")
        sys.exit()

    # Connect to the database and open files
    db = dbConnect(sys.argv[1], sys.argv[2], DATABASE)
    cursor = db.cursor()
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
            execSqlWithParams(cursor, sqlInsertPlayedMove, data_played_move)
            mid = cursor.lastrowid
            data_contained_move = {'gid' : gid,'mid' : mid}  
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