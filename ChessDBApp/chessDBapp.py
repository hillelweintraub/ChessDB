from __future__ import print_function
import database
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# configuration
USERNAME = 'root'
PASSWORD = '1234'
DATABASE = 'ChessDB'
DEBUG = True
SECRET_KEY = 'development key'


#create the application
app = Flask(__name__)
app.config.from_object(__name__)


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

@app.route('/', methods=['GET', 'POST'])
def game_explorer():
    games = None
    if request.method == 'POST':
        cursor = g.db.cursor()
        game_explorer_query = build_game_explorer_query(request.form)
        if not game_explorer_query:
            flash('Search was not specific enough')
            return redirect(url_for('game_explorer'))
        database.execSqlWithParams(cursor, game_explorer_query, request.form)

        games = \
            [dict(Date=row[0],White=row[1],Black=row[2],WhiteElo=row[3],
                  BlackElo=row[4], Event=row[5],Site=row[6],ECO=row[7],
                  Opening=row[8],Variation=row[9],Round=row[10],Result=row[11],
                  number_of_moves=row[12],gid=row[13]
                  ) for row in cursor.fetchall()]
        cursor.close()
        if not games: flash("Search didn't match any games.")   
    return render_template('game_explorer.html', entries=games)
   # return render_template('show_entries.html')

@app.route('/pgn_viewer',methods=['GET','POST'])
def pgn_viewer():
    collections = None
    cursor = g.db.cursor()
    game_query = ("SELECT g.White, g.Black, g.Event, g.move_list, g.gid "
                  "From Games g "
                  "WHERE g.gid = %(gid)s"
                 )

    form  = {k:v for k,v in request.form.iteritems()}
    if 'gid' not in form: #re-entry from failed add to collection
        print("RE-ENTRY")
        form['gid'] = session.get('gid')
        session.pop('gid', None)
    print(form)    
    database.execSqlWithParams(cursor, game_query, form)
    row = cursor.fetchone()
    game = dict(White=row[0],Black=row[1],Event=row[2],move_list=row[3], gid=[4])
 
    if 'logged_in' in session:
        uuid ={'uuid': session['uuid']}
        collection_query = ("SELECT c.cid, c.cname  "
                            "From Owned_Collections c "
                            "WHERE c.uuid = %(uuid)s "
                            "ORDER BY c.cname"
                           )
        database.execSqlWithParams(cursor, collection_query, uuid)
        collections = [dict(cid=row[0],cname=row[1]) for row in cursor.fetchall()]  
    cursor.close()
    return render_template('pgn_viewer.html',game=game, collections=collections)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        form  = {k:v for k,v in request.form.iteritems()}
        if not form['email']: form['email'] = None 
        if  DEBUG:
            print("REGISTERING with username=%(username)s, password=%(password)s, "
                     "cpassword=%(cpassword)s email=%(email)s" % form)
         #Check that  password == cpassword
        if request.form.get('password') != request.form.get('cpassword'):
            error = "Your entered passwords don't match. Please try again."
        else:
            cursor = g.db.cursor()
            rc = database.execSqlWithParams(cursor, database.sqlInsertUser, form)
            cursor.close()
            if rc == 0:
                flash('Congratulations! You were successfully registered. You can now log in.')
                return redirect(url_for('game_explorer'))
            else:
                error = 'Somebody is already registered with this username and password. Please choose something different.'
    return render_template('register.html', error=error)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if DEBUG:
            print("LOGGING IN with username=%(username)s, password=%(password)s" % request.form)  
        cursor = g.db.cursor()
        database.execSqlWithParams(cursor, database.sqlSelectUser, request.form)
        userInfo = cursor.fetchone()
        cursor.close()
        if  userInfo == None:
            error = 'Invalid username or password'
        else:
            uuid, username, password, email = userInfo
            session['logged_in'] = True
            session['uuid'] = uuid
            session['username']  = username
            flash('Congratulations! You have successfully logged in.')
            return redirect(url_for('game_explorer'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('uuid',None)
    session.pop('username',None)
    flash('Congratulations! You have seccuessfully logged out')
    return redirect(url_for('game_explorer'))

@app.route('/collection_explorer',methods=['GET', 'POST'])
def collection_explorer():
    if not session['logged_in']:
        flash("You must log in to view your collections.")
        return redirect(url_for('login'))
    cursor = g.db.cursor()
    if request.method == 'POST':
        insert_collection_statement = \
            ("INSERT INTO Owned_Collections "
             "(cname, uuid, description, tag) "
             "VALUES "
             "(%(cname)s, %(uuid)s, %(description)s, %(tag)s)"
            ) 
        collection  = {k:v for k,v in request.form.iteritems()}
        collection[uuid] = session['uuid']
        status = database.execSqlWithParams(cursor, insert_collection_statement,
                                            collection)
        cursor.close()
        if status == 0:
            flash("You have successfully created a collection!")
            return redirect(url_for('collection_explorer'))
        else:
            flash("A problem occurred! Unable to create collection.")
            return redirect(url_for('collection_explorer'))
    uuid ={'uuid': session['uuid']}
    collection_query = ("SELECT c.cname, c.description, c.tag, c.date_last_modified "
                        "From Owned_Collections c "
                        "WHERE c.uuid = %(uuid)s "
                        "ORDER BY date_last_modified DESC "
                       )
    database.execSqlWithParams(cursor, collection_query, uuid)
    collections = [dict(cname=row[0],description=row[1],
                        tag=row[2]) for row in cursor.fetchall()]
    cursor.close()
    return render_template('collection_explorer.html', collections = collections)

@app.route('/add_to_collection',methods=['POST'])
def add_to_collection():
    print('ADD TO COLLECTION FORM:', request.form)
    cursor = g.db.cursor()
    insert_contained_game_statement = ("INSERT INTO Contained_Games "
                                       "(cid, gid) "
                                       "VALUES "
                                       "(%(cid)s, %(gid)s)"
                                      ) 
    status = database.execSqlWithParams(cursor,
                                        insert_contained_game_statement,
                                        request.form)
    cursor.close()
    if status == 0:
        flash("You have successfully added a game to a collection!")
        return redirect(url_for('collection_explorer'))
    else:
        flash("A problem occurred! Unable to add game to collection.")
        session['gid'] = request.form['gid']
        return redirect(url_for('pgn_viewer'))


@app.route('/opening_explorer',methods=['GET', 'POST'])
def opening_explorer():
    return render_template('opening_explorer.html')
    #todo: fill in

def build_game_explorer_query(form):
    game_explorer_query = ("SELECT g.Date, g.White, g.Black, g.WhiteElo, "
                        "g.BlackElo, g.Event, g.Site, g.ECO, g.Opening, "
                        "g.Variation, g.Round, g.Result, g.number_of_moves, g.gid "
                        "From Games g ")
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

    if not where_clause_list: return '' # no fields in form were filled in 
    where_clause = "WHERE " + 'AND '.join(where_clause_list)
    game_explorer_query+= where_clause
    return game_explorer_query


def show_entries():
    #cur = g.db.execute('select title, text from entries order by id desc')
    #entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    cursor = g.db.cursor()
    database.execSql(cursor,database.sqlSelectGames)
    entries = [dict(gid=row[0], Event=row[1]) for row in cursor.fetchall()]
    cursor.close()
    return render_template('show_entries.html', entries=entries)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
