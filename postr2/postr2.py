from flask import Flask, request, redirect, url_for, render_template, session
#Note the new import of the flask session object
#The session object is just a box that you can use to store data that you 
#need everywhere in your program, like a global variable, but unique to
#each user
#You store data by saying session['someVariableYouMakeUp']= the data you want
#Note that using session requires a "SECRET_KEY" in your file (for some reason)
#The only changes you need to make to use the session object is add some 
#secret key and then after you create your app object, say 
#app.config.from_object(__name__)

SECRET_KEY='this_is_unnecessary'
app=Flask(__name__)
app.config.from_object(__name__)

class User:
    def __init__(self, username, password):
        self.name = username
        self.pw = password
        self.posts = []

    def add_post(self, post):
        self.posts.append()

users = {'james': User("james", "password"), "zeev": User("zeev","pass")}

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        name = request.form['user']
        pwd = request.form['password']
        if pwd == users[name].pw:
            session['user'] = name
            return redirect(url_for('make_post'))
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def make_post():
    user=users[session['user']]
    if request.method == "POST":
        user.add_post(request.form['my_post'])
    return render_template("user.html", my_posts=user.posts, my_user=user.name)

@app.route('/add', methods=['GET', 'POST'])
def adder():
    if request.method == 'POST':
        name = request.form['user']
        pwd = request.form['password']
        if name in users:
            return render_template('add_user.html')
        users[name] = User(name, pwd)
        session["user"] = name 
        return redirect('home')
    return render_template('add_user.html')

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')
