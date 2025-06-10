"""This file is the blueprint for auth related stuff, e.g. login, logout, registration"""

import logging
from functools import wraps

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from passlib.hash import bcrypt

from src.database import db_wrapper

bp = Blueprint("auth", __name__)
my_logger = logging.getLogger("my_flask_logger")


def login_required(f):
    """
    decorator to ensure the user is login for UI endpoints, else redirect to the login page
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        # ensure login, else redirect to the login page
        if "username" not in session:
            flash("Login required!", "error")
            return redirect(url_for("auth.login"))
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
# TODO change this to /login
@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get sent username and pw
        input_username = request.form["username"]
        input_pw = request.form["password"]
        # verify username and pw
        user_retrieved = db_wrapper.get_user_by_username(input_username)
        if user_retrieved and bcrypt.verify(input_pw, user_retrieved.get("hashed_pw")):
            session["username"] = input_username
            return redirect(url_for("blog.index"))
        flash("Login Error!", "error")
        return render_template("login.html")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logout Successful!", "info")
    return redirect(url_for("auth.login"))


# User registration
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # get sent username and pw, check unique username
        username = request.form["username"]
        pw = request.form["password"]
        # check if username valid, if valid add user else show error
        res = db_wrapper.get_user_by_username(username)
        my_logger.debug(f"res: {res}")
        if res is None:
            db_wrapper.add_user(username, pw)
            flash("Account Registration Successful!", "info")
            return render_template("register.html")
        flash("Username Already Taken!", "error")
        return render_template("register.html")

    return render_template("register.html")
