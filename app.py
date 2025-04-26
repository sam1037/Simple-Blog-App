from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import json, os, datetime

app = Flask(__name__)
app.secret_key = 'secret'

# Helper functions
def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# User login/logout
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # get sent username and pw, verify
        username = request.form['username']
        pw = request.form["password"]
        users_json = load_json("users.json")
        for user in users_json:
            if user['username'] == username and user['password'] == pw:
                session['username'] = username
                return redirect(url_for('index'))
        return render_template("login.html", error="Login Error!")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# User registration
@app.route('/register', methods=['GET', "POST"])
def register():
    if request.method == "POST":
        # get sent username and pw, check unique username
        username = request.form['username']
        pw = request.form["password"]
        users_json = load_json("users.json")
        # if duplicate
        for user in users_json:
            if user["username"] == username:
                return render_template("register.html", error = "Username has already been used!")
        # if unique username
        users_json.append({"username": username, "password": pw})
        save_json("users.json", users_json)
        return redirect(url_for("login"))

    return render_template("register.html")

# Blog index
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/get_posts')
def get_posts():
    posts = load_json('posts.json')
    return jsonify(posts)

# Create new post
@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        posts = load_json('posts.json')
        posts.insert(0, {
            'author': session['username'],
            'title': title,
            'content': content,
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_json('posts.json', posts)
        return redirect(url_for('index'))
    return render_template('new_post.html')

if __name__ == '__main__':
    app.run(debug=True)