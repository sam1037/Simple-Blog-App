"""The main Flask app"""

import json
import logging
import os
import sys
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from passlib.hash import bcrypt

import src.database.db_wrapper as db_wrapper

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY")
app.secret_key = SECRET_KEY

my_logger = logging.getLogger("my_flask_logger")
my_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(levelname)s] - %(filename)s:%(lineno)d - %(message)s")

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
if os.environ.get("FLASK_ENV") and os.environ.get("FLASK_ENV") == "dev":
    console_handler.setLevel(logging.DEBUG)
else:
    console_handler.setLevel(logging.INFO)
my_logger.addHandler(console_handler)


# Helper functions
def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)


def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def login_required(f):
    """
    decorator to ensure the user is login for UI endpoints, else redirect to the login page
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        # ensure login, else redirect to the login page
        if "username" not in session:
            flash("Login required!", "error")
            return redirect(url_for("login"))
        result = f(*args, **kwargs)
        return result

    return wrapper


def login_required_api(f):
    """
    decorator to ensure the user is login for API endpoints, else return json and 401
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        # ensure login, else redirect to the login page
        if "username" not in session:
            return jsonify({"message": "Login required"}), 401
        result = f(*args, **kwargs)
        return result

    return wrapper


# User login/logout
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get sent username and pw
        input_username = request.form["username"]
        input_pw = request.form["password"]
        # verify username and pw
        user_retrieved = db_wrapper.get_user_by_username(input_username)
        if user_retrieved and bcrypt.verify(input_pw, user_retrieved.get("hashed_pw")):
            session["username"] = input_username
            return redirect(url_for("index"))
        flash("Login Error!", "error")
        return render_template("login.html")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logout Successful!", "info")
    return redirect(url_for("login"))


# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # get sent username and pw, check unique username
        username = request.form["username"]
        pw = request.form["password"]
        # check if username valid, if valid add user else show error
        res = db_wrapper.get_user_by_username(username)
        my_logger.debug(f"res: {res}")
        if db_wrapper.get_user_by_username(username) is None:
            db_wrapper.add_user(username, pw)
            flash("Account Registration Successful!", "info")
            return render_template("register.html")
        flash("Username Already Taken!", "error")
        return render_template("register.html")

    return render_template("register.html")


# Blog index
# TODO rename this, future will serve as public blog section
@app.route("/index")
def index():
    # render differently depending on viewing as guest or login user
    if "username" not in session:
        return render_template("index.html", username="Guest")
    else:
        return render_template("index.html", username=session["username"])


# ??? this is actually an API route???
@app.route("/get_posts")
def get_posts():
    posts = db_wrapper.get_all_posts()
    return jsonify(posts)


# Create new post
@app.route("/write_post", methods=["GET", "POST"])
@login_required
def write_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = session["username"]
        # insert post to db
        db_wrapper.insert_new_post(author, title, content)
        return redirect(url_for("index"))
    return render_template("write_post.html")


# Edit an exisiting post
@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    # get the post by post id first and check if valid post id
    post = db_wrapper.get_post_by_id(post_id)
    my_logger.debug(f"editing this post: {post}")
    my_logger.debug(f"method: {request.method}")
    if not post:
        return jsonify(
            {"message": "Some error occured when trying to retrieve the post"}
        ), 403

    # check if user if authorized
    if session.get("username") != post["author"]:
        return jsonify({"message": "You are not authorized to edit this post"}), 403

    # GET route: verify, redirect to the write post page with some fields filled
    if request.method == "GET":
        # ??? should I use redirect or render template in this line???
        return render_template(
            "write_post.html", title=post["title"], text_content=post["content"]
        )

    # POST route: verify, save edit to the db
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        db_wrapper.edit_post_by_id(post_id, title=title, content=content)
        return redirect(url_for("index"))  # ??? redirect or render template here ???

    return render_template("index.html")  # ??? redirect or render template here ???


# Delete a post by post id
# ??? is this like an api route?
# TODO should i rename this to sth like 'api/posts, following REST?'
@app.route("/delete_post/<post_id>", methods=["DELETE"])
@login_required_api
def delete_post(post_id):
    # Verify if is author deleting his post
    username = session.get("username")
    if not username:
        return jsonify({"message": "Unauthorized"}), 401

    post = db_wrapper.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    if post["author"] != username:
        return jsonify({"message": "You are not authorized to delete this post"}), 403

    # Delete it
    if db_wrapper.delete_post_by_id(post_id):
        return jsonify({"message": "Post deleted successfully."})
    return jsonify({"message": "Error occured during post deletion"}), 404


if __name__ == "__main__":
    app.run(debug=True)
