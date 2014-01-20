from flask import Flask, request, url_for, render_template

app=Flask(__name__)

posts = ["Hello, world!"]

@app.route('/home', methods=['GET', 'POST'])
def addPost():
    if request.method == "POST":
        posts.append(request.form['myPost'])
    return render_template("postr.html", myPosts=posts)

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')
