# maybe i should move things from src.app to here, and rename src to simple-blog-app
"""The main Flask app"""

import logging
import os
import sys

import click  # noqa: F401
from flask import Flask, redirect, url_for


def create_app():
    # app create and config
    app = Flask(__name__)
    SECRET_KEY = os.environ.get("SECRET_KEY")
    app.secret_key = SECRET_KEY

    # logger
    my_logger = logging.getLogger("my_flask_logger")
    my_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(levelname)s] - %(filename)s:%(lineno)d - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    if os.environ.get("FLASK_ENV") and os.environ.get("FLASK_ENV") == "dev":
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    my_logger.addHandler(console_handler)

    # redirect to login
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # add cmds to app.cli with click
    # test cli
    @click.command("hello")
    def hello_cmd():
        """A testing cmd that will echo 'hello'"""
        click.echo("hello")

    # init db cmd
    from src.database.db import init_db_cmd

    app.cli.add_command(init_db_cmd)
    app.cli.add_command(hello_cmd)

    # blueprint
    from src import auth, blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    return app
