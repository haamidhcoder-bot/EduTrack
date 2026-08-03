from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
import random
import bcrypt as bp

from app.extensions import db
from app.models.teacher import Teacher
from app.models.Administration import Admin
from app.services.create_account_service import create_account
from app.decorators import login_required
from config import dict_details,administrator1
from app.services.email_service import email

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/about", endpoint="about")
def about():
    return render_template("about_us.html")


@pages_bp.route("/support", endpoint="support")
def support():
    return render_template("support.html")


@pages_bp.route("/forget_pass", methods=["GET", "POST"], endpoint="forgot_password")
def forgot_password():
    if request.method == "POST":
        gmail = request.form.get("email", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        admin = Admin.query.filter(Admin.Gmail == gmail).first()
        
        if not gmail or not new_password or not confirm_password:
            return render_template("forgot_password.html", error="Please fill in all fields.")

        if new_password != confirm_password:
            return render_template("forgot_password.html", error="Passwords do not match.")

        if not admin:
            return render_template("forgot_password.html", error="No Admin account found for that email.")

        OTP=str(random.randint(1000,9999))
        session["OTP"]=OTP
        email(administrator1,gmail,"OTP verification",f"The OTP for {gmail} is  --{OTP}-- for changing password",dict_details[administrator1])
        
        return render_template("forgot_password_verification.html",username=gmail,password=new_password)


    return render_template("forgot_password.html")

@pages_bp.route("/forgot_password_verification/<username>/<password>", methods=["POST", "GET"])
def forgot_password_verification(username: str,password:str):
        admin = Admin.query.filter(Admin.Gmail == username).first()
        if request.method=="POST":
            otp=request.form.get("onepass","")
            if otp==session.get("OTP"):
                admin.password = bp.hashpw(password.encode(),bp.gensalt()) 
                db.session.commit()
                current_app.logger.info(f"Password reset requested for {username}")
            else:
                return render_template("Error.html", data="incorrect OTP.",location="/")
        return redirect(url_for("auth.login_page"))

@pages_bp.route("/profile", endpoint="profile")
def profile():
    return render_template("profile.html", username=session.get("username", "").removesuffix("@gmail.com"))

@pages_bp.route("/register",endpoint="register")
def register():
    return render_template("register.html")

@pages_bp.route("/add_teacher", methods=["GET", "POST"],endpoint="add_teacher")
@login_required
def add_teacher():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            class_teacher=request.form.get("class_teacher","").strip()
            class_teacher_sec=request.form.get("class_teacher_sec","").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            if not username or not password or not confirm_password:
                return render_template("Error.html", data="Please fill in all fields.",location="/")

            if class_teacher and class_teacher_sec:
                verification=create_account(user=username,password=password,confirm_password=confirm_password,Table=Teacher,class_teacher=class_teacher,class_teacher_sec=class_teacher_sec)
            else:
                verification=create_account(user=username,password=password,confirm_password=confirm_password,Table=Teacher)

            if not verification:
                return render_template("Error.html", data="duplicate entry.",location="/")

            if  verification=="pass":
                return render_template("Error.html", data="passwords are not same.",location="/")

            if verification:
                return redirect("/teachers_data")
        return render_template("add_teacher.html")