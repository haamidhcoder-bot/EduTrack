from flask import Blueprint, render_template, session, request, redirect, url_for, current_app, jsonify
import random
import bcrypt as bp
import os

from shared.extensions import db
from shared import login_required
from shared.models import Teacher
from shared.config import dict_details,administrator1
from shared.services.email_service import email
from shared.services.face_id_service import save_face, FACE_ID_DIR
from shared.services.profile_service import initials_for_name, password_bytes

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
            if request.is_json:
                data = request.get_json(silent=True) or {}
                otp = data.get("onepass", "")
            else:
                otp = request.form.get("onepass", "")

            if otp==session.get("OTP"):
                teacher.password = bp.hashpw(password.encode(),bp.gensalt()).decode("utf-8") 
                db.session.commit()
                session.pop("OTP", None)
                current_app.logger.info(f"Password reset requested for {username}")
                if request.is_json:
                    return jsonify({"success": True, "message": "Code verified.", "redirect": url_for("auth.login_page")})
            else:
                if request.is_json:
                    return jsonify({"success": False, "message": "Incorrect OTP."}), 400
                return render_template("Error.html", data="incorrect OTP.",location="/")
        return redirect(url_for("auth.login_page"))

@pages_bp.route("/profile", endpoint="profile")
@login_required
def profile():
    username = session.get("username", "")
    teacher = Teacher.query.filter_by(Gmail=username).first()
    if not teacher:
        session.clear()
        return redirect(url_for("auth.login_page"))

    display_name = teacher.name.strip() if teacher.name and teacher.name.strip() else "Set your name"
    return render_template(
        "profile.html",
        account=teacher,
        display_name=display_name,
        initials=initials_for_name(teacher.name),
        role="Teacher",
    )


@pages_bp.route("/profile-details", methods=["GET", "POST"], endpoint="profile_details")
@login_required
def profile_details():
    username = session.get("username", "")
    teacher = Teacher.query.filter_by(Gmail=username).first()
    if not teacher:
        session.clear()
        return redirect(url_for("auth.login_page"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("profile_details.html", account=teacher, role="Teacher", error="Please enter your name.")
        if len(name) > 100:
            return render_template("profile_details.html", account=teacher, role="Teacher", error="Name must be 100 characters or fewer.")

        teacher.name = name
        db.session.commit()
        current_app.logger.info(f"{username} updated profile name")
        return redirect(url_for("pages.profile"))

    return render_template("profile_details.html", account=teacher, role="Teacher")


@pages_bp.route("/settings", endpoint="settings")
@login_required
def settings():
    teacher = Teacher.query.filter_by(Gmail=session.get("username", "")).first()
    if not teacher:
        session.clear()
        return redirect(url_for("auth.login_page"))
    return render_template("settings.html", role="Teacher", face_enabled=bool(teacher.face_id))


@pages_bp.route("/change-password", methods=["GET", "POST"], endpoint="change_password")
@login_required
def change_password():
    username = session.get("username", "")
    teacher = Teacher.query.filter_by(Gmail=username).first()
    if not teacher:
        session.clear()
        return redirect(url_for("auth.login_page"))

    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not current_password or not new_password or not confirm_password:
            return render_template("change_password.html", error="Please fill in all fields.", role="Teacher")

        if not bp.checkpw(current_password.encode(), password_bytes(teacher.password)):
            return render_template("change_password.html", error="Current password is incorrect.", role="Teacher")

        if new_password != confirm_password:
            return render_template("change_password.html", error="New passwords do not match.", role="Teacher")

        if len(new_password) < 8:
            return render_template("change_password.html", error="New password must contain at least 8 characters.", role="Teacher")

        teacher.password = bp.hashpw(new_password.encode(), bp.gensalt()).decode("utf-8")
        db.session.commit()
        current_app.logger.info(f"{username} changed the password")
        return redirect(url_for("pages.settings", password_changed=1))

    return render_template("change_password.html", role="Teacher")


@pages_bp.route("/face-id", methods=["GET", "POST"], endpoint="face_id")
@login_required
def face_id():
    username = session.get("username", "")
    teacher = Teacher.query.filter_by(Gmail=username).first()
    if not teacher:
        session.clear()
        return redirect(url_for("auth.login_page"))

    if request.method == "POST":
        image = request.files.get("face")
        if not image:
            return render_template("face_id.html", error="Please capture your face before saving.", enabled=bool(teacher.face_id))

        old_face = teacher.face_id
        new_face = save_face(image)
        teacher.face_id = new_face
        db.session.commit()

        if old_face:
            old_path = os.path.join(FACE_ID_DIR, old_face)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    current_app.logger.warning(f"Could not remove old Face ID file for {username}")

        current_app.logger.info(f"{username} updated Face ID")
        return redirect(url_for("pages.settings", face_updated=1))

    return render_template("face_id.html", enabled=bool(teacher.face_id))
