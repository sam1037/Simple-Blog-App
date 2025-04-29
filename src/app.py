from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import json, os, datetime
from database.db_wrapper import add_user, get_user_by_username, get_all_posts, insert_new_post, delete_post_by_id, get_post_by_id

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
        # get sent username and pw
        username = request.form['username']
        pw = request.form["password"]
        # verify username and pw
        user_retrieved = get_user_by_username(username)
        print(user_retrieved)
        if user_retrieved and user_retrieved[2] == pw: #how to make this not hardcode
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
        # check if username valid, if valid add user else show error
        res = get_user_by_username(username)
        print(f"res: {res}")
        if get_user_by_username(username) is None:
            add_user(username, pw)
            return render_template("register.html", success=True)
        return render_template("register.html", error="Username already taken!")        

    return render_template("register.html")

# Blog index
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/get_posts')
def get_posts():
    posts = get_all_posts()
    #print(posts)
    return jsonify(posts)

# Create new post
@app.route('/write_post', methods=['GET', 'POST'])
def write_post():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = session['username']
        # insert post to db
        insert_new_post(author, title, content)
        return redirect(url_for('index'))
    return render_template('write_post.html')

# Delete a post by post id
@app.route('/delete_post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Verify if is author deleting his post
    username = session.get('username')
    if not username:
        return jsonify({'message': 'Unauthorized'}), 401

    post = get_post_by_id(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404

    if post['author'] != username:
        return jsonify({'message': 'You are not authorized to delete this post'}), 403

    # Delete it
    if delete_post_by_id(post_id):
        return jsonify({'message': 'Post deleted successfully.'})
    return jsonify({'message': 'Error occured during post deletion'}), 404
    


if __name__ == '__main__':
    app.run(debug=True)