from flask import Blueprint, render_template, redirect, request, session, url_for, current_app
import bcrypt as bp
import os

from shared.models import Teacher
from shared.services.email_service import email_file
from shared.config import administrator1,administrator2,dict_details

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["POST", "GET"], endpoint="login_page")
def login_page():
    if request.method == "POST":
        user_n = request.form.get("username", "").strip()
        pass_n = request.form.get("password", "")
        session["username"] = user_n
        remember = request.form.get("remember", "")

        teacher = Teacher.query.filter(Teacher.Gmail == user_n).first()

        if teacher and bp.checkpw(pass_n.encode(), teacher.password.encode()):
            session["logged_in"] = True
            if remember:
                session.permanent = True
            current_app.logger.info(f"{session.get('username', '')} logged in")
            return render_template(
                "Home.html",
                class_value=int(teacher.class_teacher),
                sec=teacher.class_teacher_sec
            )
        else:
            current_app.logger.error("incorrect username or password")
            return render_template("Error.html", data=" incorrect username or password", location="/")
    elif session.permanent:
        current_app.logger.info(f"{session.get('username', '')} logged in back")
        return render_template(
            "Home.html",
            class_value=int(session.get("class_value", 0)),
            sec=session.get("sec", ""),
            log=session.permanent,
            user=session.get("username", "")
        )
    return render_template("login_page.html")


@auth_bp.route("/log-out", methods=["POST", "GET"])
def log_out():
    current_app.logger.info(
        f"{session.get('username', '')} has logged out"
    )
    email_file(administrator2,administrator1,"log file",f"this is the log file of {session.get("username","")}","App.log",dict_details[administrator2])

    with open("App.log", "w"):pass
    
    session.clear()
    return redirect(url_for("auth.login_page"))
