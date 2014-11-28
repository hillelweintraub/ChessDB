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
def show_entries():
    #cur = g.db.execute('select title, text from entries order by id desc')
    #entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    cursor = g.db.cursor()
    database.execSql(cursor,database.sqlSelectGames)
    entries = [dict(gid=row[0], Event=row[1]) for row in cursor.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
