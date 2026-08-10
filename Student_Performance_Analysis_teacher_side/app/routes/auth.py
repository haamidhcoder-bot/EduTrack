from flask import Blueprint, render_template, redirect, request, session, url_for, current_app
import bcrypt as bp

from shared.models import Teacher

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["POST", "GET"], endpoint="login_page")
def login_page():
    if request.method == "POST":
        user_n = request.form.get("username", "").strip()
        pass_n = request.form.get("password", "")
        remember = request.form.get("remember", "")

        teacher = Teacher.query.filter(Teacher.Gmail == user_n).first()

        if not teacher or not bp.checkpw(pass_n.encode(), teacher.password.encode()):
            current_app.logger.error("incorrect username or password")
            return render_template(
                "Error.html",
                data="incorrect username or password",
                location="/"
            )

        # Start a clean teacher session after successful authentication.
        session.clear()
        session["username"] = user_n
        session["logged_in"] = True
        session["class_teacher"] = teacher.class_teacher
        session["class_teacher_sec"] = teacher.class_teacher_sec

        if remember:
            session.permanent = True

        current_app.logger.info(
            f"{user_n} logged in"
        )

        return redirect(url_for("home.home"))

    return render_template("login_page.html")


@auth_bp.route("/log-out", methods=["POST", "GET"])
def log_out():
    current_app.logger.info(
        f"{session.get('username', '')} has logged out"
    )
    session.clear()
    return redirect(url_for("auth.login_page"))
