from flask import Flask, render_template

app = Flask(__name__)

@app.route('/<user>')
def hello(user):
	return render_template('hello.html', name=user)

app.run()