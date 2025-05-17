"""The main Flask app"""

from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import json, os
from passlib.hash import bcrypt
import src.database.db_wrapper as db_wrapper

app = Flask(__name__) 
SECRET_KEY = os.environ.get("SECRET_KEY")
app.secret_key = SECRET_KEY 

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
        input_username = request.form['username']
        input_pw = request.form["password"]
        # verify username and pw
        user_retrieved = db_wrapper.get_user_by_username(input_username)
        if user_retrieved and bcrypt.verify(input_pw, user_retrieved.get('hashed_pw')):
            session['username'] = input_username
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
        res = db_wrapper.get_user_by_username(username)
        print(f"res: {res}")
        if db_wrapper.get_user_by_username(username) is None:
            db_wrapper.add_user(username, pw)
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
    posts = db_wrapper.get_all_posts()
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
        db_wrapper.insert_new_post(author, title, content)
        return redirect(url_for('index'))
    return render_template('write_post.html')

# Edit an exisiting post
@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    # check username login (authentication)
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # get the post by post id first and check if valid post id
    post = db_wrapper.get_post_by_id(post_id)
    print(f"editing this post: {post}")
    print(f"method: {request.method}")
    if not post:
        return jsonify({'message': 'Some error occured when trying to retrieve the post'}), 403
    
    # check if user if authorized
    if session.get('username') != post['author']: 
        return jsonify({'message': 'You are not authorized to edit this post'}), 403

    # GET route: verify, redirect to the write post page with some fields filled
    if request.method == 'GET':
        # ??? should I use redirect or render template in this line???
        return render_template('write_post.html', title=post['title'], text_content=post['content'])

    # POST route: verify, save edit to the db
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db_wrapper.edit_post_by_id(post_id, title=title, content=content)
        return redirect(url_for('index')) #??? redirect or render template here ???

    return render_template('index.html') #??? redirect or render template here ???

# Delete a post by post id
@app.route('/delete_post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Verify if is author deleting his post
    username = session.get('username')
    if not username:
        return jsonify({'message': 'Unauthorized'}), 401

    post = db_wrapper.get_post_by_id(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404

    if post['author'] != username:
        return jsonify({'message': 'You are not authorized to delete this post'}), 403

    # Delete it
    if db_wrapper.delete_post_by_id(post_id):
        return jsonify({'message': 'Post deleted successfully.'})
    return jsonify({'message': 'Error occured during post deletion'}), 404

if __name__ == '__main__':
    app.run(debug=True) 