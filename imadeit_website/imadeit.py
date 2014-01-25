'''import statements
Imports are used to source code from other libraries and files
so that we can use their methods without explicitly including all 
of their code
'''
import sqlite3, re, hashlib
import user
from flask import Flask, session, request, redirect, \
render_template, url_for, g, flash

#First things first, I'm creating a new Flask object and calling it app
#It will do all the routing for the requests that come in to our IP address
app = Flask(__name__)

#Here I am updating the configuration of my Flask object
#This won't be necessary unless you are working with a database or sessions
app.config.update(dict(
    SECRET_KEY = 'nicodemus',
    DATABASE = 'imadeit.db',
))

############################### DATABASE SHTUFF ###############################
#This method will create and return a connection to the database
def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

#The last method created a new connection to the database, but we may already
#have one open
#this method checks if the 'g' object has a live database connection stored
#and then either uses that or creates one
#A NOTE ON G: g is one of the imports up at the top. g is like a global 
#purse than you can use to store arbitrary objects, and they are accessible
#globally in your app 
def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

#This initializes the database from a schema file. A schema file is like
#the blueprints for a database; it describes what tables should be created
#what rows they have, and what types of data (like strings or numbers)
#will go into that column
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', 'r') as f:
            db.executescript(f.read())
            db.commit()

#This will close the database connection everytime the app context is 
#popped
#To be perfectly blunt, I don't actually know when that ever happens,
#so I wouldn't worry about understanding it either
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

###############################################################################
############################ WEB PAGE ROUTING #################################
###############################################################################



################################## HOME ####################################
@app.route('/')
def redirect_to_home():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

################################# LOGIN #####################################

#Either displays the login page or redirects to the home page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    #If HTTP request that came to this webpage was a 'post' request then it 
    #should have come from the user clicking the login button, so lets check
    if request.method == 'POST':
        db = get_db() 
	name = request.form['login_username']
    	pw = encrypt_password(request.form['login_pw'])
        query = "SELECT PORT FROM STUDENTS WHERE USERNAME=? AND PASSWORD=?"
        result = db.execute(query, [name, pw]).fetchone()
        if result is not None:
            port = result[0]
            set_session_vars(name, port)
            flash("You were logged in!")
            return redirect(url_for('home'))
        else:
            error = 'Invalid Username or Password'
    return render_template('login.html', error=error)

@app.route('/create', methods=['GET', 'POST'])
def create_account():
    error = None
    if request.method == 'POST':
        db = get_db() 
	name = request.form['create_username']
        password = request.form['create_pw']
    	pw = encrypt_password(password)
        email = request.form['email']
	college = request.form['college']
        marketing = request.form['marketing']
        prog = request.form['prog_expr']
        result = db.execute("SELECT USER_ID FROM STUDENTS WHERE " \
        "USERNAME=?", [name]).fetchone()
        if result is None and valid_email(email):
	    query = "INSERT INTO STUDENTS (USERNAME, PASSWORD, EMAIL," \
            + " COLLEGE, MARKETING, PORT, PROG_EXPR, PARTNER_PORT, YEAR) " \
            + "VALUES(?, ?, ?, ?, ?, ?, 0, 0, 0)"
            db.execute(query, [name, pw, email, college, marketing, prog])
            db.commit()
            user.create(name, password)
            set_session_vars(name, 0)
            flash('Your account was created successfully!')
            return redirect(url_for('home'))
        else:
            if not valid_email(email):
                error = 'Invalid email format'
            else: 
                error = 'That user name already exists :('
    return render_template('login.html', error=error)
    
@app.route('/port_authority', methods=['GET', 'POST'])
def port_authority():
    error = None
    if not session.get('logged_in'):
        flash('You need to login to access that!')
        return redirect(url_for('login'))
    if request.method == 'POST':
        error = register_port(request.form['port'])
    return render_template('port_authority.html', error=error)

def register_port(port):
    try:
        port = int(port)
    except:
        return "You forgot to type a port"
    if port > 5000 and port < 10000:
        db = get_db()
        query = 'SELECT PORT FROM STUDENTS WHERE PORT = ?'
        port_in_db = db.execute(query, [port]).fetchone()
        if port_in_db is None:
            set_port = 'UPDATE STUDENTS SET PORT=? WHERE USERNAME=?' 
            db.execute(set_port, [port, session.get('name')])
            db.commit() 
            session['port'] = port
            flash('You have registered port {}'.format(port))
        else:
            return'Some varmit took your port number already!'
    else:
        return 'Invalid port number, dude'

@app.route('/source')
def source():
    return login_check('source.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/logout')
def logout():
    session.pop('logged_in')
    return redirect(url_for('home'))

def login_check(url):
    if not session.get('logged_in'):
        flash('You need to login to access that!')
        return redirect(url_for('login'))
    else:
        return render_template(url)

def set_session_vars(name, port):
    session['logged_in'] = True
    session['name'] = name
    session['port'] = port

def valid_email(email): 
    one_char = '[a-zA-Z0-9_]'
    chars = '{}+'.format(one_char)
    charsdotchars = '({}+)(\.{}+)*'.format(one_char, one_char)
    email_re ='^' + charsdotchars + '@' + chars + '\.'+ charsdotchars + '$'
    return re.match(email_re, email) is not None

def encrypt_password(password):
    sha = hashlib.sha224(password)
    return sha.hexdigest()


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80)
