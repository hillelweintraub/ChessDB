# A script to parse collections of chess games in PGN format and insert them
# into the database

from __future__ import print_function
import os
import sys
from glob import glob
import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime
from math import ceil

##############################################################
# CONSTANTS
##############################################################
DATABASE = "TestChessDB"

PGN_DIR  = "../data/NewTWIC/PGN/"
FEN_DIR = "../data/NewTWIC/FEN/"

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
START_FEN_PROCESSED = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq" 

GAME_SRC = "TWIC"

INFO = 0
DEBUG = 1 
WARNING = 2
ERROR = 3
FATAL = 4
DEBUG_LEVEL = DEBUG

STATUS_EOF = 0
STATUS_SHORT_GAME = 1
STATUS_WELL_FORMED = 2

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

#CONTAINED_MOVES TABLE
sqlInsertContained_Moves = (
  "INSERT INTO Contained_Moves "
  "(gid, mid) " 
  "VALUES (%(gid)s, %(mid)s)"
)

#SELECT PLAYED_MOVE
sqlSelectPlayedMove = (
  "SELECT P.mid "
  "FROM Played_Moves P "
  "WHERE P.prior_position = %(prior_position)s AND "
        "P.current_move = %(current_move)s"
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
        if DEBUG_LEVEL <= DEBUG: print("DEBUG: Executing ", cursor._executed, "params:", params, '\n')
        return 0
    except mysql.connector.Error as err:
        if DEBUG_LEVEL <= ERROR :
            print("ERROR: FAILED to execute: ", cursor._executed, "params:", params)
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
        
def getGame(pgn):
    data_game = util_parseMetadata(pgn)            #parse the metadata
    moves, move_list = util_parseMoveText(pgn)     #parse the move list
    data_game['move_list'] = move_list 
    data_game['number_of_moves'] =  int(ceil(len(moves)/2.0))    
    data_game['game_source'] = GAME_SRC
    if not moves and move_list == '':
        status = STATUS_EOF
    elif len(moves)<=1: #In this case there is no corresponding fen
        status = STATUS_SHORT_GAME
    else:
        status = STATUS_WELL_FORMED
    return data_game, moves, status 
    
def getPriorPositions(fen):
    prior_position_list = [START_FEN_PROCESSED] #include start position
    for line in fen:
        if line.strip() == START_FEN:
            if len(prior_position_list) > 1: break  #reached beginning of next game         
            else: continue                          #first game in file
        else:
            line = util_processFENLine(line)     
            prior_position_list.append(line)
    return prior_position_list        

def getPlayedMoves(prior_position_list,current_move_list):
    data_played_moves_list = []
    for prior_pos,curr_move in zip(prior_position_list,current_move_list):
        data_played_move = {'prior_position':prior_pos
                           ,'current_move':curr_move}
        data_played_moves_list.append(data_played_move)
    return data_played_moves_list
      
def util_parseMetadata(pgn):
    data_game = {
      'Site':None, 'Event':None, 'Round':None, 'White':None, 'Black':None, 
      'WhiteTitle':None, 'BlackTitle':None, 'Date':None,  
      'WhiteElo':None, 'BlackElo':None, 'Result':None, 'ECO':None, 'Opening':None,
      'Variation':None, 'number_of_moves':None, 'move_list':None, 'game_source':None
    }       
    for line in pgn:
        if not line or line.strip() == '': break
        line = line.strip().replace('[','').replace(']','').replace('"','').split()
        field_name = line[0]
        field_value = ' '.join(line[1:])
        if field_name in data_game:
            if field_name == 'Date':
                field_value = util_convert2SqlDate(field_value)
            data_game[field_name] = field_value
    return data_game        

def util_parseMoveText(pgn):
    moves = []
    for line in pgn:
        if not line or line.strip() == '': break
        moves.append(line.strip())
    move_list = ' '.join(moves)    
    moves = move_list.split()  #split into tokens 
    if len(moves) >= 1: moves.pop()               #get rid of result token 
    for token in moves[:]:
        if token[-1] == '.': moves.remove(token)  #remove move number tokens
    return moves, move_list

def util_convert2SqlDate(field_value):
    field_value.replace(".","-").replace("??","01")
    return field_value  

def util_processFENLine(line):
    return ' '.join(line.split()[:-3])     
    

###############################################################
# MAIN
##############################################################
def processFile(pgn_file, fen_file, cursor): 
    # Open pgn and fen files
    pgn = open(pgn_file,'r')
    fen = open(fen_file,'r')

    while True:
        # Get data from pgn and fen files
        data_game, current_move_list, status = getGame(pgn)
        if status == STATUS_EOF: 
            print("DEBUG: EOF reached\n")
            break
        elif status == STATUS_SHORT_GAME :
            print("ERROR: STATUS_SHORT_GAME \n")
            continue
        prior_position_list = getPriorPositions(fen)
        # Insert game into the database
        if execSqlWithParams(cursor, sqlInsertGame, data_game) != 0: continue
        gid = cursor.lastrowid
        assert( len(prior_position_list) == len(current_move_list) )
        data_played_moves_list = getPlayedMoves(prior_position_list,
                                                current_move_list)
        for data_played_move in data_played_moves_list:
            # Insert played_move into the DB
            execSqlWithParams(cursor, sqlInsertPlayedMove, data_played_move)
            # Get the mid of the played_move
            execSqlWithParams(cursor,sqlSelectPlayedMove,
                                    data_played_move)
            row = cursor.fetchone()
            assert(row != None and len(row) == 1)
            mid = row[0]
            data_contained_move = {'gid' : gid,'mid' : mid}  
            # Insert contained_move into the DB
            execSqlWithParams(cursor, sqlInsertContained_Moves,
                              data_contained_move)

    # Close files
    pgn.close()
    fen.close()
    
def main():
    # Validate number of input parameters
    start_file = 0; end_file = 99999
    if len(sys.argv) == 4: start_file = int(sys.argv[3])
    elif len(sys.argv) == 5: 
        start_file = int(sys.argv[3]);
        end_file = int(sys.argv[4])
    elif len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python fill_tables.py <username> <password> [start_#] [end_#]")
        sys.exit()
    
    # Connect to database
    db = dbConnect(sys.argv[1], sys.argv[2], DATABASE)
    cursor = db.cursor()
    
    for pgn_file in glob(os.path.join(PGN_DIR,'*.pgn')):
        # Skip if before start_file
        file_num = int(pgn_file[-9:-4])
        if file_num < start_file or file_num > end_file: continue
        #Get FEN file
        fen_file = 'twic%05d'%file_num + '.fen'
        fen_file = os.path.join(FEN_DIR,fen_file)
        # Process file and commit the transaction
        print("PROCESSING FILE: %s" % pgn_file)
        print("============================================\n")
        processFile(pgn_file, fen_file, cursor)
        db.commit()
        print( "PROCESSING COMPLETE: %s" %pgn_file)
        print("============================================\n")
    # Close connection to database 
    cursor.close()
    db.close()
    if DEBUG_LEVEL <= DEBUG: print("DEBUG: DB CLOSED!!!!")
    
 
if __name__ == '__main__':
    status = main()