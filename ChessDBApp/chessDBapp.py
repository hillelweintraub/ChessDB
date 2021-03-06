from __future__ import print_function
import database
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, make_response
from flask.ext.login import LoginManager, current_user, login_user, \
     logout_user, login_required, UserMixin as User
from pagination import Pagination
from functools import wraps, update_wrapper
from datetime import datetime
import random     


# configuration
USERNAME = 'root'
PASSWORD = '1234'
DATABASE = 'TestChessDB'
DEBUG = True
SECRET_KEY = 'development key'


#create the application
app = Flask(__name__)
app.config.from_object(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


def pop_game_explorer_query():
    session.pop('game_explorer_query',None)
    session.pop('game_explorer_form',None)
    session.pop('number_of_matches',None)


@app.before_request
def before_request():
    g.db = database.dbConnect(app.config['USERNAME'],
                              app.config['PASSWORD'],
                              app.config['DATABASE'])
        
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.commit()
        db.close()

@login_manager.user_loader
def load_user(uuid):
    cursor = g.db.cursor()
    user_query = (
        "SELECT u.uuid, u.username, u.password, u.email "
        "FROM Users u "
        "WHERE u.uuid = %(uuid)s"
        )
    params = dict(uuid=uuid)
    database.execSqlWithParams(cursor,user_query,params)
    row = cursor.fetchone()
    cursor.close()
    if not row: return None
    user = User()
    user.id = row[0]
    user.username = row[1]
    user.password = row[2]
    user.email = row[3]
    return user 

################################################################################
#
#   REGISTRATION/ LOGIN/ LOGOFF (all non-login/registration pages)
#
################################################################################

@app.route('/register', methods=['GET', 'POST'])
def register():
    pop_game_explorer_query()
    error = None
    if request.method == 'POST':
        form  = {k:v for k,v in request.form.iteritems()}
        if not form['email']: form['email'] = None 
        if  DEBUG:
            print("REGISTERING with username=%(username)s, "
                                   "password=%(password)s, "
                                   "cpassword=%(cpassword)s "
                                   "email=%(email)s" % form)
        #Check that  password == cpassword
        if request.form.get('password') != request.form.get('cpassword'):
            error = "Your entered passwords don't match. Please try again."
        else:
            cursor = g.db.cursor()
            rc = database.execSqlWithParams(cursor,database.sqlInsertUser,form)
            cursor.close()
            if rc == 0:
                flash('Congratulations! You were successfully registered.'
                      ' You can now log in.')
                return redirect(url_for('login'))
            else:
                error = ('Somebody is already registered with this username.'
                         'Please choose something different.')
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    pop_game_explorer_query()
    error = None
    if request.method == 'POST':
        if DEBUG:
            print("LOGGING IN with username=%(username)s, "
                                  "password=%(password)s" % request.form)  
        cursor = g.db.cursor()
        database.execSqlWithParams(cursor, database.sqlSelectUser, request.form)
        userInfo = cursor.fetchone()
        cursor.close()
        if  userInfo == None:
            error = 'Invalid username or password'
        else:
            uuid, username, password, email = userInfo
            user = User()
            user.id = uuid
            user.username = username
            user.password = password
            user.email = email
            login_user(user)
            flash('Congratulations! You have successfully logged in.')
            if 'redirectToCollectionExplorer' in session:
                session.pop('redirectToCollectionExplorer')
                return redirect(url_for('collection_explorer'))
            else: 
                return redirect(url_for('game_explorer'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    pop_game_explorer_query()
    logout_user()
    flash('Congratulations! You have seccuessfully logged out')
    return redirect(url_for('game_explorer'))

################################################################################
#
#  GAME EXPLORER (game_explorer.html)
#
################################################################################
def get_players():
    db=database.dbConnect(app.config['USERNAME'],
                              app.config['PASSWORD'],
                              app.config['DATABASE'])
    cursor = db.cursor()
    white_player_query = ("SELECT Distinct g.White "
                          "From Games g ORDER BY g.White "
                         )
    black_player_query = ("SELECT Distinct g.Black "
                          "From Games g ORDER BY g.Black"
                         )
    database.execSql(cursor,white_player_query)
    white_players = [dict(name=row[0]) for row in cursor.fetchall()]
    database.execSql(cursor,black_player_query)
    black_players = [dict(name=row[0]) for row in cursor.fetchall()]
    db.commit()
    db.close()
    white_players.insert(0,dict(name=''))
    black_players.insert(0,dict(name=''))
    return white_players, black_players

global_white_players,global_black_players = get_players()

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page  

@app.route('/', defaults={'page': 1},methods=['GET', 'POST'])
@app.route('/<int:page>')
def game_explorer(page):
    games = None
    pagination = None
    number_of_matches = None
    records_per_page = 30
    record_offset = records_per_page*(page-1)
    cursor = g.db.cursor()
    if request.method == 'POST':
        game_explorer_query,count_query=build_game_explorer_query(request.form)
        if not game_explorer_query:
            flash('Search was not specific enough')
            return redirect(url_for('game_explorer'))
        database.execSqlWithParams(cursor, count_query,request.form)
        number_of_matches = cursor.fetchone()[0]
        game_explorer_form = {k:v for k,v in request.form.iteritems()}
        #store form params and query for use in entering page 
        #through pagination link
        session['game_explorer_form'] = game_explorer_form
        session['game_explorer_query'] = game_explorer_query
        session['number_of_matches'] = number_of_matches
        
        game_explorer_query+="Limit %d,%d"%(record_offset,records_per_page)
        database.execSqlWithParams(cursor, game_explorer_query, request.form)
        games = \
        [dict(Date=row[0],White=row[1],Black=row[2],WhiteElo=row[3],
              BlackElo=row[4], Event=row[5],Site=row[6],ECO=row[7],
              Opening=row[8],Variation=row[9],Round=row[10],Result=row[11],
              number_of_moves=row[12],gid=row[13]
              ) for row in cursor.fetchall()]
        if not games:
            flash("Search didn't match any games.") 
            session.pop('game_explorer_query',None)
            session.pop('game_explorer_form',None)
            session.pop('number_of_matches',None)
        cursor.close() 
        pagination = Pagination(page,records_per_page,number_of_matches)
        session['keep_game_explorer_query'] = True
        return render_template('game_explorer.html', entries=games,
            white_players=global_white_players,
            black_players=global_black_players,pagination=pagination,
            number_of_matches=number_of_matches) 
    
    if 'game_explorer_query' in session:
        game_explorer_query=session['game_explorer_query']+\
            "Limit %d,%d"%(record_offset,records_per_page)
        database.execSqlWithParams(cursor, game_explorer_query,
            session['game_explorer_form'])
        games = \
        [dict(Date=row[0],White=row[1],Black=row[2],WhiteElo=row[3],
              BlackElo=row[4], Event=row[5],Site=row[6],ECO=row[7],
              Opening=row[8],Variation=row[9],Round=row[10],Result=row[11],
              number_of_moves=row[12],gid=row[13]
              ) for row in cursor.fetchall()]
        number_of_matches = session['number_of_matches']
        pagination = Pagination(page,records_per_page,number_of_matches)

    cursor.close() 
    session['keep_game_explorer_query'] = True
    return render_template('game_explorer.html', 
                            entries=games,
                            white_players=global_white_players,
                            black_players=global_black_players,
                            pagination=pagination,
                            number_of_matches=number_of_matches)


def build_game_explorer_query(form):
    game_explorer_query = ("SELECT g.Date, g.White, g.Black, g.WhiteElo, "
                        "g.BlackElo, g.Event, g.Site, g.ECO, g.Opening, "
                        "g.Variation, g.Round, g.Result, "
                        "g.number_of_moves, g.gid "
                        "From Games g ")
    count_query = "SELECT count(*) from Games g "
    where_clause_list = []
    if form['elo_min']:
        where_clause_list.append("g.WhiteElo >= %(elo_min)s AND "
                                 "g.BlackElo >= %(elo_min)s ")
    if form['elo_max']:
        where_clause_list.append("g.WhiteElo <= %(elo_max)s AND "
                                 " g.BlackElo <= %(elo_max)s ")
    if form['date_min']:
        where_clause_list.append("g.Date >= %(date_min)s ")
    if form['date_max']:
        where_clause_list.append("g.Date <= %(date_max)s ")
    if form['num_moves_min']:
        where_clause_list.append("g.number_of_moves >= %(num_moves_min)s ")
    if form['num_moves_max']:
        where_clause_list.append("g.number_of_moves <= %(num_moves_max)s ")
    if form['white_player']:
        where_clause_list.append("g.White = %(white_player)s ")
    if form['black_player']:
        where_clause_list.append("g.Black = %(black_player)s ")
    if form['eco']:
        where_clause_list.append("g.ECO = %(eco)s ")

    if not where_clause_list: return ('','') # no fields in form were filled in 
    where_clause = "WHERE " + 'AND '.join(where_clause_list)
    game_explorer_query+= where_clause
    count_query+=where_clause
    return game_explorer_query,count_query


################################################################################
#  PGN VIEWER (pgn_viewer.html)
#  (Invoked from  game explorer.html page, upon hitting view
#   and from pgn_viewer.html page upon unsuccessful add_game_to_collection) 
#
################################################################################

@app.route('/pgn_viewer',methods=['GET','POST'])
def pgn_viewer():
    pop_game_explorer_query()
    collections = None
    cursor = g.db.cursor()
    game_query = ("SELECT g.White, g.Black, g.Event, g.move_list, g.gid "
                  "From Games g "
                  "WHERE g.gid = %(gid)s"
                 )
    form  = {k:v for k,v in request.form.iteritems()}
    if 'gid' not in form: #re-entry from failed add to collection
        form['gid'] = session.get('gid')
        session.pop('gid', None)  
    database.execSqlWithParams(cursor, game_query, form)
    row = cursor.fetchone()
    game = dict(White=row[0],Black=row[1],Event=row[2],
                move_list=row[3], gid=row[4])
 
    if current_user.is_authenticated():
        uuid ={'uuid': current_user.get_id()}
        collection_query = ("SELECT c.cid, c.cname  "
                            "From Owned_Collections c "
                            "WHERE c.uuid = %(uuid)s "
                            "ORDER BY c.cname"
                           )
        database.execSqlWithParams(cursor, collection_query, uuid)
        collections=[dict(cid=row[0],cname=row[1]) for row in cursor.fetchall()]  
    cursor.close()
    return render_template('pgn_viewer.html',game=game, collections=collections)

@app.route('/add_to_collection',methods=['POST'])
@login_required
def add_to_collection():
    pop_game_explorer_query()
    cursor = g.db.cursor()
    form  = {k:v for k,v in request.form.iteritems()}
    if not form['label']: form['label'] = None 
    insert_contained_game_statement = ("INSERT INTO Contained_Games "
                                       "(cid, gid, label) "
                                       "VALUES "
                                       "(%(cid)s, %(gid)s, %(label)s)"
                                      ) 
    status = database.execSqlWithParams(cursor,
                                        insert_contained_game_statement,
                                        form)
    cursor.close()
    if status == 0:
        flash("You have successfully added a game to a collection!")
        return redirect(url_for('collection_explorer'))
    else:
        flash("A problem occurred! "
              "Unable to add game to collection. (game already there)")
        session['gid'] = request.form['gid']
        return redirect(url_for('pgn_viewer'))
    

################################################################################
#
#  COLLECTION EXPLORER  (collection_explorer.html)
#
################################################################################
@app.route('/collection_explorer',methods=['GET', 'POST'])
def collection_explorer():
    pop_game_explorer_query()
    if not current_user.is_authenticated():
        session['redirectToCollectionExplorer'] = True
        flash("Please log in to access this page.")
        return redirect(url_for('login'))
    else:      
        cursor = g.db.cursor()
        if request.method == 'POST':
            insert_collection_statement = \
                ("INSERT INTO Owned_Collections "
                 "(cname, uuid, description, tag) "
                 "VALUES "
                 "(%(cname)s, %(uuid)s, %(description)s, %(tag)s)"
                ) 
            collection  = {k:v for k,v in request.form.iteritems()}
            collection['uuid'] = current_user.get_id()
            status = database.execSqlWithParams(cursor, 
                                                insert_collection_statement,
                                                collection)
            cursor.close()
            if status == 0:
                flash("You have successfully created a collection!")
                return redirect(url_for('collection_explorer'))
            else:
                flash("A problem occurred! Unable to create collection.")
                return redirect(url_for('collection_explorer'))
        collections = get_collections(cursor)
        cursor.close()
        return render_template('collection_explorer.html',
                               collections = collections)
 

@app.route('/delete_collection/<cid>')
def delete_collection(cid):
    pop_game_explorer_query()
    cursor = g.db.cursor()
    delete_collection_query = ("DELETE FROM Owned_Collections "
                               "WHERE cid = %s"%cid)
    database.execSql(cursor,delete_collection_query)
    cursor.close()
    flash("Successfully deleted collection!")
    return redirect(url_for('collection_explorer'))

@app.route('/show_collection_games/<cid>')
@login_required
def show_collection_games(cid):
    pop_game_explorer_query()
    cursor = g.db.cursor()
    game_query = ("SELECT cg.gid, cg.label, g.White, g.Black, g.Event, g.Date "
                  "FROM Contained_Games cg, Games g "
                  "WHERE cg.cid = %s AND cg.gid = g.gid"%cid)
    database.execSql(cursor,game_query)
    games = [dict(gid=row[0],label=row[1],White=row[2],Black=row[3],
                  Event=row[4],Date=row[5]) for row in cursor.fetchall()]
    if not games:
        cursor.close()
        flash("No games in this collection to view")
        return redirect(url_for('collection_explorer'))
    collections = get_collections(cursor)
    cursor.close()
    return render_template('collection_explorer.html',
                           collections = collections,
                           games = games,
                           cid = int(cid))

@app.route('/delete_contained_game/<cid>/<gid>')
def delete_contained_game(cid,gid):
    pop_game_explorer_query()
    cursor = g.db.cursor()
    delete_game_query = ("DELETE FROM Contained_Games "
                         "WHERE cid = %s AND gid = %s"%(cid,gid)
                        )
    database.execSql(cursor,delete_game_query)
    cursor.close()
    flash("Successfully deleted game from collection!")
    return redirect(url_for('collection_explorer'))    

def get_collections(cursor):
   collection_query = ("SELECT c.cname, c.description, c.tag, "
                       "c.date_last_modified, c.cid "
                       "From Owned_Collections c "
                       "WHERE c.uuid = %(uuid)s "
                       "ORDER BY date_last_modified DESC"
                      )
   params = dict(uuid=current_user.get_id())
   database.execSqlWithParams(cursor, collection_query, params)
   collections = [dict(cname=row[0],description=row[1],
                       tag=row[2],cid=row[4]) for row in cursor.fetchall()]
   return collections    

################################################################################
#
#  OPENING EXPLORER  (collection_explorer.html)
#
################################################################################

@app.route('/opening_explorer',methods=['GET', 'POST'])
def opening_explorer():
    pop_game_explorer_query()
    START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    START_FEN_PROCESSED = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq" 
    MAX_GAMES = 20        # maximum number of games displayed
    move_text = '1.' 
    ply = 0
    mid = 0
    stats = None
    games = None
    position =  START_FEN
    processed_position = START_FEN_PROCESSED
    
    cursor = g.db.cursor()
    
    if request.method == 'POST':
        position = request.form['position']
        processed_position = util_processFEN(position);
        move_text = request.form['move_text']
        ply = request.form['ply']
        mid = request.form['mid']

    opening_query = ("SELECT PM.current_move, "
                            "count(*) AS NUM, "
                            "SUM(G.Result = '1-0'), "
                            "SUM(G.Result ='1/2-1/2'), "
                            "SUM(G.Result = '0-1'), "
                            "PM.mid "
                     "FROM  Played_Moves PM NATURAL JOIN "
                           "Contained_Moves CM  NATURAL JOIN "
                           "Games G "
                     "WHERE PM.prior_position = %(position)s "
                     "GROUP BY PM.mid "
                     "ORDER BY NUM DESC"
                    )

    params = {'position' : processed_position}

    database.execSqlWithParams(cursor, opening_query, params)

    stats = [dict(move=row[0],
                  num_games=row[1], 
                  white_win="%.2f" % (float(row[2])*100/float(row[1])),
                  draw="%.2f" % (float(row[3])*100/float(row[1])),
                  black_win="%.2f" % (float(row[4])*100/float(row[1])),
                  mid=row[5]) for row in cursor.fetchall()]
   
    if mid:
        view_games_query = ("SELECT g.Date, g.White, g.Black, g.WhiteElo, "
                            "g.BlackElo, g.Event, g.Site, g.ECO, g.Opening, "
                            "g.Variation, g.Round, g.Result, "
                            "g.number_of_moves, g.gid "
                            "From Games g  NATURAL JOIN Contained_Moves CM "
                            "WHERE CM.mid = %(mid)s" 
                           )
        params = {'mid' : int(mid)}

        database.execSqlWithParams(cursor, view_games_query, params)

        games = \
            [dict(Date=row[0],White=row[1],Black=row[2],WhiteElo=row[3],
                  BlackElo=row[4], Event=row[5],Site=row[6],ECO=row[7],
                  Opening=row[8],Variation=row[9],Round=row[10],Result=row[11],
                  number_of_moves=row[12],gid=row[13]
                  ) for row in cursor.fetchall()]
        
        #Limit output to a random selection of MAX_GAMES games   
        if len(games) > MAX_GAMES:   
            random.shuffle(games)
            games = games[0:MAX_GAMES]    

    cursor.close()

    return render_template('opening_explorer.html', move_text = move_text,
                                                    ply = ply,
                                                    stats = stats,
                                                    games = games,
                                                    position = position,
                                                    MAX_GAMES=MAX_GAMES)

def util_processFEN(line):
    return ' '.join(line.split()[:-3])     


################################################################################
#
# MAIN
#
################################################################################
if __name__ == '__main__':

    app.run(host='0.0.0.0')
