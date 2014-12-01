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
    g.db = database.dbConnect(app.config['USERNAME'],app.config['PASSWORD'],
                              app.config['DATABASE'])

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.commit()
        db.close()

# @app.route('/')
# def hello_world():
#     flash('Time to login doofus!')
#     return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/')
def show_game_explorer_page():
    return render_template('game_explorer.html')


def build_find_games_query(form):
    find_games_query = ("SELECT g.Date, g.White, g.Black, g.WhiteElo, "
                        "g.BlackElo, g.Event, g.Site, g.ECO, g.Opening, "
                        "g.Variation, g.Round, g.Result, g.number_of_moves "
                        " From Games g ")
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
    find_games_query+= where_clause
    return find_games_query


  #   "(%(Site)s, %(Event)s, %(Round)s, %(Date)s, %(White)s, %(Black)s, "
  # "%(WhiteTitle)s, %(BlackTitle)s, %(WhiteElo)s, %(BlackElo)s, "
  # "%(Result)s, %(ECO)s, %(Opening)s, %(Variation)s, "
  # "%(number_of_moves)s, %(move_list)s, %(game_source)s) "


@app.route('/find_games',methods=['POST'])
def find_games():
    cursor = g.db.cursor()
    find_games_query = build_find_games_query(request.form)
    if not find_games_query:
        flash('Search was not specific enough')
        return redirect(url_for('show_game_explorer_page'))
    database.execSqlWithParams(cursor,find_games_query,request.form)

    games = \
        [dict(Date=row[0],White=row[1],Black=row[2],WhiteElo=row[3],
              BlackElo=row[4], Event=row[5],Site=row[6],ECO=row[7],
              Opening=row[8],Variation=row[9],Round=row[10],Result=row[11],
              number_of_moves=row[12]
              ) for row in cursor.fetchall()]
    cursor.close()
    return render_template('show_entries.html', entries=games)

#@app.route('/')
def show_entries():
    #cur = g.db.execute('select title, text from entries order by id desc')
    #entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    cursor = g.db.cursor()
    database.execSql(cursor,database.sqlSelectGames)
    entries = [dict(gid=row[0], Event=row[1]) for row in cursor.fetchall()]
    cursor.close()
    return render_template('show_entries.html', entries=entries)

@app.route('/game_explorer',methods=['GET', 'POST'])
def game_explorer():
    #sql
    if request.method == 'POST':
        pass


        # ( cid                 INTEGER AUTO_INCREMENT,
        #                             cname               VARCHAR(50) NOT NULL,
        #                             uuid                INTEGER NOT NULL,
        #                             description         VARCHAR(150),
        #                             tag                 VARCHAR(20),
        #                             date_last_modified  TIMESTAMP NOT NULL,
        #                                        PRIMARY KEY (cid),
        #                                        UNIQUE (cname, uuid),
        #                                        FOREIGN KEY (uuid) REFERENCES Users(uuid)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    


if __name__ == '__main__':
    app.run(host='0.0.0.0')
