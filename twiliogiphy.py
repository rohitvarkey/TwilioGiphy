import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort,\
        render_template, flash
from twilio.rest import TwilioRestClient
from utils import sendTwilioGIF

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'twiliogiphy.db'),
    SECRET_KEY="",
    ACCOUNT_SID="",
    AUTH_TOKEN="",
    TWILIO_PHONE="",
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_client():
    if not hasattr(g, 'client'):
        g.client = TwilioRestClient(app.config["ACCOUNT_SID"], app.config["AUTH_TOKEN"])
    return g.client


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select term, url from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    client = get_client()
    body = "A GIF for the term :" + request.form['term']
    message, url = sendTwilioGIF(
        client, "+14045793137", body, request.form['term'], app.config["TWILIO_PHONE"]
    )
    db.execute('insert into entries (term, url) values (?, ?)',
                 [request.form['term'], url])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

if __name__ == "__main__":
    app.run(host='0.0.0.0')
