"""This file is the blueprint for blog related stuff, e.g. write post, edit post, read post"""

import logging

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from src.auth import login_required, login_required_api
from src.database import db_wrapper

# ??? prefix url ??? do what, should i use
bp = Blueprint("blog", __name__)
my_logger = logging.getLogger("my_flask_logger")


# Blog index
# TODO rename this, future will serve as public blog section
@bp.route("/index")
def index():
    # render differently depending on viewing as guest or login user
    if "username" not in session:
        return render_template("index.html", username="Guest")
    else:
        return render_template("index.html", username=session["username"])


# TODO: rename this, modify the get_posts api endpoint s.t. it returns a json containing a list of all the post and a list of post_id liked by current user
@bp.route("/get_posts")
def get_posts():
    """
    API endpoint to return a json containing a list of all the post and a list of posts liked by current user
    """
    user_id = session.get("user_id")
    current_user_liked_post_ids: list[int] = []
    if user_id:
        current_user_liked_post_ids = db_wrapper.get_current_user_liked_post_ids(
            user_id
        )
        my_logger.debug(f"current_user_liked_post_ids: {current_user_liked_post_ids}")
    posts = db_wrapper.get_all_posts()
    my_logger.debug(f"post count: {len(posts)}")

    res = jsonify(
        {"posts": posts, "current_user_liked_post_ids": current_user_liked_post_ids}
    )

    return res


@bp.route("/test", methods=["GET"])
def test():
    """
    API endpoint to return a json containing a list of all the post and a list of posts liked by current user
    """
    return get_posts()


# Create new post
@bp.route("/write_post", methods=["GET", "POST"])
@login_required
def write_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = session["username"]
        # insert post to db
        db_wrapper.insert_new_post(author, title, content)
        return redirect(url_for("blog.index"))
    return render_template("write_post.html")


# Edit an exisiting post
@bp.route("/edit_post/<post_id>", methods=["GET", "POST"])
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
        return redirect(
            url_for("blog.index")
        )  # ??? redirect or render template here ???

    return render_template("index.html")  # ??? redirect or render template here ???


# Delete a post by post id
# ??? is this like an api route?
# TODO should i rename this to sth like 'api/posts, following REST?'
@bp.route("/delete_post/<post_id>", methods=["DELETE"])
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


@bp.route("/like_post/<post_id>", methods=["POST"])
# @profile_this_endpoint
@login_required_api
# TODO add type hint for the api endpoints
def toggle_like_post(post_id):
    """
    API endpoint to like/ unlike a post (toggle), return json (message, new like count, liked by user) and HTTP status code
    """

    # validify post id and user id
    user_id = session.get("user_id")
    if user_id is None:
        my_logger.error("Invalid user id")
        return jsonify({"message": "Invalid user id"}), 400

    post_with_like_status = db_wrapper.get_post_and_if_user_liked_it(user_id, post_id)
    if post_with_like_status is None:
        my_logger.error("Invalid post id")
        return jsonify({"message": "Invalid post id"}), 400

    # check if user liked the post already, modify db accordingly
    prev_liked_by_current_user = post_with_like_status.get("user_liked")
    new_like_count: int = post_with_like_status.get("like_count")
    message: str

    if prev_liked_by_current_user:  # if liked by current user, should unlike it
        db_wrapper.undo_like_post(user_id, post_id)  # 0.129
        message = "Unliked a post, should modify db successfully"
        new_like_count -= 1
    else:
        db_wrapper.like_post(user_id, post_id)  # 0.129
        message = "Liked a post, should modify db successfully"
        new_like_count += 1

    new_like_count = max(new_like_count, 0)

    # return
    res = (
        jsonify(
            {
                "message": message,
                "new_like_count": new_like_count,
                "liked_by_user": not prev_liked_by_current_user,
            }
        ),
        200,
    )
    my_logger.debug(
        f"the 3 data returned by toggle_like_post: {message, new_like_count, not prev_liked_by_current_user}"
    )
    return res
    # TODO test this
