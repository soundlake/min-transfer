# all the imports
from flask import Flask, \
                  abort, \
                  flash, \
                  g, \
                  redirect, \
                  render_template, \
                  request, \
                  send_from_directory, \
                  session, \
                  url_for
from flask_assets import Environment, Bundle
import os
import sqlite3
import uuid
import urllib.parse



# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)



# Load default config and override config from an environment variable
with app.open_resource('secret.key', mode='r') as secret:
    app.config.update(dict(
        DATABASE            = os.path.join(app.root_path, 'var/flaskr.db'),
        SECRET_KEY          = secret.read().strip(),
        UPLOAD_FOLDER       = os.path.join(app.root_path, 'var', 'uploads'),
        ALLOWED_EXTENSIONS  = set(['txt', 'doc', 'docx', 'hwp', \
                                   'pdf', \
                                   'png', 'jpg', 'jpeg', 'gif', \
                                   'wav', 'wma', 'mp3', 'aiff', \
                                   'mov', 'avi', 'wmv', 'mp4', \
                                   'zip'])
    ))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)



# setup jinja2
app.jinja_env.globals.update(unquote=urllib.parse.unquote)



# setup assets
assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('style.scss', filters='pyscss', output='build/style.css')
assets.register('scss_all', scss)



# Function definitions for Database
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    """Connects to the specific database."""
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

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()



# Utilities
def allowed_file(the_file):
    filename = the_file.filename
    return '.' in filename and \
       filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def save_file(the_file):
    filename = urllib.parse.quote(the_file.filename)
    file_id = str(uuid.uuid4())
    db = get_db()
    db.execute('INSERT INTO upload (id, name) VALUES (?, ?)', (file_id, filename))
    db.commit()
    the_file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_id))
    return file_id



# Routing
@app.route('/', methods=['GET', 'POST'])
def index():
    error = []
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        if 'sender' not in request.form:
            flash('No sender', 'error')
            return redirect(request.url)
        if 'receiver' not in request.form:
            flash('No receiver', 'error')
            return redirect(request.url)
        uploaded_file = request.files['file']
        if not uploaded_file.filename:
            flash('No file selected', 'error')
            return redirect(request.url)
        if not error:
            if not uploaded_file:
                return redirect(url_for('show_file'))
            if not allowed_file(uploaded_file):
                return redirect(url_for('show_file'))
            file_id = save_file(uploaded_file)
            flash('File is uploaded.')
            return redirect(url_for('show_file', file_id = file_id))
    return render_template('index.html', error = error)



@app.route('/<uuid:file_id>', methods=['GET'])
def show_file(file_id):
    db = get_db()
    cur = db.execute('SELECT * FROM upload WHERE id = ?', (str(file_id), ))
    the_file = cur.fetchone()
    return render_template('show_file.html', the_file = the_file)



@app.route('/<uuid:file_id>/download', methods=['GET'])
def download_file(file_id):
    db = get_db()
    cur = db.execute('SELECT name, time FROM upload WHERE id = ?', (str(file_id), ))
    the_file = cur.fetchone()
    return send_from_directory(app.config['UPLOAD_FOLDER'], \
                               str(file_id), \
                               as_attachment = True, \
                               attachment_filename = the_file['name'])
