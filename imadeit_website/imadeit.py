'''import statements
Imports are used to source code from other libraries and files
so that we can use their methods without explicitly including all 
of their code
'''
import sqlite3, re, hashlib
import user
from random import random
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

#This portion of the program tells flask what to do if it receives requests
#at various 'routes'. If anyone visits <this IP address>/<one of these routes>
#the code below will be run

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
    	pw = request.form['login_pw']

        #From the database, select the fields relevant for verifying a 
        #students ID from the database records that match the given username
        query = "SELECT PORT, PASSWORD, SALT FROM USERS WHERE USERNAME=?"
        result = db.execute(query, [name]).fetchone()
        
        #If the user record exists in the database, let's check their password
        if result is not None:
            port, password, salt = result
            if encrypt_password(pw, salt) == password:
                set_session_vars(name, port)
                flash("You were logged in!")
                return redirect(url_for('home'))

            else:
                error = 'Invalid Password'
        else:
            error = 'Invalid Username'
    
    #If the request was just a GET, or something went wrong in the login, 
    #show the login page
    return render_template('login.html', error=error)


############################## USER CREATION ##################################
#This is actually the same HTML page as the login page, but I put two seperate
#forms on the page, which each cause their own action, one for login, and one
#for creating new accounts
#This is because I am a lazy developer. It could all be done at one route
@app.route('/create', methods=['GET', 'POST'])
def create_account():
    error = None
    print 'in create'

    #Like in login, if the page request was POST, it probably means the user
    #clicked the create account button. So let's make them an account!
    if request.method == 'POST':

        #First we collect all jount they typed in
        db = get_db() 
	name = request.form['create_username']
        pw = request.form['create_pw']
        email = request.form['email']
	college = request.form['college']
        marketing = request.form['marketing']
        prog = request.form['prog_expr']

        #Let's make sure they didn't select someone else's user name
        result = db.execute("SELECT USER_ID FROM STUDENTS WHERE " \
        "USERNAME=?", [name]).fetchone()
        if result is None and valid_email(email):

            #Encrypt the password so I'm not tempted to hax ur facebookzzz
            salt = hex(int(random() * 1000000))
            enc_pw = encrypt_password(pw, salt)

            #Stick all the collected info into the DB so I can stalk y'all forever
	    query = "INSERT INTO USERS (USERNAME, PASSWORD, SALT, EMAIL," \
            + " COLLEGE, MARKETING, PROG_EXPR, PORT, PARTNER_PORT) " \
            + "VALUES(?, ?, ?, ?, ?, ?, ?, 0, 0)"
            db.execute(query, [name, enc_pw, salt, email, college, marketing, prog])
            db.commit()
            
            #Create an account on the server so that you guys can log in
            try:
                user.create(name, pw)
            except:
                print "FAILED during user creation"

            set_session_vars(name, 0)
            flash('Your account was created successfully!')
            return redirect(url_for('home'))
        else:
            if not valid_email(email):
                error = 'Invalid email format'
            else: 
                error = 'That user name already exists :('
    
    #If the request was just a GET, or something went wrong in the login, 
    #show the login page
    return render_template('login.html', error=error)
    

################################# PORT AUTHORITY ##############################
#This handles assigning ports so that everyone's got their own phone number
#and it's not like growing up with my sister who was always on the phone and 

#all I wanted to do was go on the Harry Potter website but noooooooo she HAD
#talk to her friends about chia pets or whatever the hell teenage girls talked
#about in the 90's
@app.route('/port_authority', methods=['GET', 'POST'])
def port_authority():
    error = None
    
    #if the user isn't logged in, redirect them to the home page
    if not session.get('logged_in'):
        flash('You need to login to access that!')
        return redirect(url_for('login'))

    #If the request for was a POST type, try to register the port
    if request.method == 'POST':
        error = register_port(request.form['port'])
    
    return render_template('port_authority.html', error=error)

#Attempts to register the given port for the current user
def register_port(port):
    try:
        port = int(port)
    except:
        return "You forgot to type a port"

    if port > 5000 and port < 10000:
        db = get_db()
        query = 'SELECT PORT FROM STUDENTS WHERE PORT = ?'
        port_in_db = db.execute(query, [port]).fetchone()
        
        #If their is no user with the given port, let's register!
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

################################# SOURCE ######################################
@app.route('/source')
def source():
    return login_check('source.html')

################################# BLOG ########################################
@app.route('/blog')
def blog():
    return render_template('blog.html')

################################# LOGOUT ######################################
#Log me out, Scotty!
@app.route('/logout')
def logout():
    session.pop('logged_in')
    return redirect(url_for('home'))

###############################################################################
############################# HELPER FUNCTIONS ################################
###############################################################################

#If the user is not logged in, redirects to the login page, else renders the url
def login_check(url):
    if not session.get('logged_in'):
        flash('You need to login to access that!')
        return redirect(url_for('login'))
    else:
        return render_template(url)

#Updates the users session variables to the given arguments
def set_session_vars(name, port):
    session['logged_in'] = True
    session['name'] = name
    session['port'] = port

#Regex that checks that the given string is a valid email
#We won't get into regular expressions in this course, but if you have any 
#interest, just talk to James
#Regex are user for determing if a string matches a specific pattern
#They're stupid efficient
def valid_email(email): 
    one_char = '[a-zA-Z0-9_]'
    chars = '{}+'.format(one_char)
    charsdotchars = '({}+)(\.{}+)*'.format(one_char, one_char)
    email_re ='^' + charsdotchars + '@' + chars + '\.'+ charsdotchars + '$'
    return re.match(email_re, email) is not None

#Encrypts the password
def encrypt_password(password, salt):
    round_one = hashlib.sha224(password)
    round_two = hashlib.sha224(round_one.hexdigest() + salt)
    return round_two.hexdigest()

#This line is not strictly needed, but it is convention
#__name__ is a special variable in a python program that reflects whether the
#script is being run as the main thread of execution('__main__'), or if it is
#being invoked by another program, in which case, we don't want it to start
#the app
if __name__ == '__main__':
    
    #Initalizes any changes that have been made to the database structure
    #Usually nothing, but it makes it easy to make changes to the database
    init_db()
    
    #Port 80 is the default port for HTTP requests. When you visit 
    #imadeit.nu, your browser automatically appends ":80", but for 
    #other ports, you have to explicitly say it
    app.run(host='0.0.0.0', port=80)
