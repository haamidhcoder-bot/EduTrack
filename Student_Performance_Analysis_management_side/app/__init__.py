import os

from flask import Flask
import mysql.connector as sql
from datetime import timedelta

from shared.config import Mysql_pass, session_key2
from shared import db
from utils.logger import setup_logger
from app.routes import register_blueprints

# Project root (one level above the app/ package), so templates/ and
# static/ are found in the same place they were relative to the original
# app.py.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app():
    # Same as the original module-level code: make sure the database exists
    # before SQLAlchemy tries to use it.
    cn = sql.connect(host="127.0.0.1", user="root", password=Mysql_pass)
    cr = cn.cursor()
    cr.execute("create database if not exists schooldb")

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static")
    )

    app.secret_key = session_key2  # required for sessions to work
    app.permanent_session_lifetime = timedelta(hours=1)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://root:{Mysql_pass}@localhost/schooldb"  # format for using mysql
    )

    db.init_app(app)

    setup_logger(app)

    register_blueprints(app)

    return app
