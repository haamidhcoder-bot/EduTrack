from flask import Blueprint, render_template, redirect, request, session, url_for, current_app
import random
import bcrypt as bp

from shared.models import Admin
from app.services.create_account_service import create_account
from app.services.email_service import email
from shared.config import dict_details,administrator1,administrator2

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["POST", "GET"], endpoint="login_page")
def login_page():
    if request.method == "POST" and not session.permanent:
        user_n = request.form.get("username", "")
        pass_n =request.form.get("password", "")
        session["username"] = user_n
        remember = request.form.get("remember", "")
        Admins = Admin.query.filter(
            Admin.Gmail == user_n
        ).first()

        if Admins and bp.checkpw(pass_n.encode(),Admins.password.encode()):
            session["logged_in"] = True
            if remember:
                session.permanent = True
            current_app.logger.info(f"{session.get('username', '')} logged in")
            return render_template(
                "Home.html",
                class_value=int(session.get("class_value", 0)),
                sec=session.get("sec", "")
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
    current_app.logger.info(f"{session.get('username', '')} has logged out")
    session.clear()
    return redirect(url_for("auth.login_page"))

@auth_bp.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not password or not confirm_password:
            return render_template("Error.html", data="Please fill in all fields.",location="/")

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")
        
        OTP=str(random.randint(1000,9999))
        session["OTP"]=OTP
        email(administrator1,administrator2,"OTP verification",f"The OTP for {username} is --{OTP}-- for registering an account",dict_details[administrator1])

        return render_template("register_verification.html",username=username,password=password,confirm_password=confirm_password)
    return render_template("register.html")
        

@auth_bp.route("/register_verification/<username>/<password>/<confirm_password>", methods=["POST", "GET"])
def register_verification(username: str,password:str,confirm_password:str):
        if request.method=="POST":
            otp=request.form.get("onepass","")
            if otp==session.get("OTP"):
                verified=create_account(user=username,password=password,confirm_password=confirm_password,Table=Admin)

                if not verified:
                    return render_template("Error.html", data="Passwords do not match.",location="/")
            else:
                return render_template("Error.html", data="incorrect OTP.",location="/")
        return redirect(url_for("auth.login_page"))