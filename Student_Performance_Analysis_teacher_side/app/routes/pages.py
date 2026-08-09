from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
import random
import bcrypt as bp

from shared.extensions import db
from shared.models import Teacher
from shared.config import dict_details,administrator1
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

        teacher = Teacher.query.filter(Teacher.Gmail == gmail).first()
        
        if not gmail or not new_password or not confirm_password:
            return render_template("forgot_password.html", error="Please fill in all fields.")

        if new_password != confirm_password:
            return render_template("forgot_password.html", error="Passwords do not match.")

        if not teacher:
            return render_template("forgot_password.html", error="No Teacher account found for that email.")

        OTP=str(random.randint(1000,9999))
        session["OTP"]=OTP
        email(administrator1,gmail,"OTP verification",f"The OTP for {gmail} is  --{OTP}-- for changing password",dict_details[administrator1])
        
        return render_template("forgot_password_verification.html",username=gmail,password=new_password)
        

    return render_template("forgot_password.html")

@pages_bp.route("/forgot_password_verification/<username>/<password>", methods=["POST", "GET"])
def forgot_password_verification(username: str,password:str):
        teacher = Teacher.query.filter(Teacher.Gmail == username).first()
        if request.method=="POST":
            otp=request.form.get("onepass","")
            if otp==session.get("OTP"):
                teacher.password = bp.hashpw(password.encode(),bp.gensalt()) 
                db.session.commit()
                current_app.logger.info(f"Password reset requested for {username}")
            else:
                return render_template("Error.html", data="incorrect OTP.",location="/")
        return redirect(url_for("auth.login_page"))

@pages_bp.route("/profile", endpoint="profile")
def profile():
    return render_template("profile.html", username=session.get("username", "").removesuffix("@gmail.com"))
