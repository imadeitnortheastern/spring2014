from flask import Flask, request, url_for, render_template, session

class Person:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.pw = password
        self.friends = []
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)

james = Person('James', 'james@mac.com', 'jamesrules')

james.add_post('iMadeIT also rules!')
users = [james]

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = str(request.form['email'])
        pw = str(request.form['password'])
        for user in users:
            if user.email == email and user.pw == pw:
                session['name'] = user.name
                session['user'] = user
                return render_template('hello.html', name=user.name, tweets = user.posts)
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def post():
    user = session['user']
    if request.method == 'POST':
        user.add_post(request.form['tweet'])
    return render_template('hello.html', name=user.name, tweets=user.posts)

app.debug = True
app.run(host='0.0.0.0', port = 6478)



