from flask import Blueprint, render_template, redirect, request, session, url_for, current_app, jsonify
import hashlib
import hmac
import re
import secrets
import time
import bcrypt as bp

from shared import db
from shared.models import Admin
from shared.services.create_account_service import create_account
from shared.services.face_id_service import match_face
from shared.services.email_service import email, email_file
from shared.config import dict_details, administrator1, administrator2
from shared.services.profile_service import password_bytes


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["POST", "GET"], endpoint="login_page")
def login_page():
    if request.method == "POST" and not session.permanent:
        user_n = request.form.get("username", "")
        pass_n = request.form.get("password", "")
        session["username"] = user_n
        remember = request.form.get("remember", "")

        Admins = Admin.query.filter(
            Admin.Gmail == user_n
        ).first()

        if Admins and bp.checkpw(pass_n.encode(), password_bytes(Admins.password)):
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


@auth_bp.route("/login-face", methods=["POST"], endpoint="login_face")
def login_face():
    image = request.files.get("face")

    if not image:
        return render_template("Error.html", data="No image received", location="/")

    captured_bytes = image.read()

    matched_admin = None
    for admin in Admin.query.filter(Admin.face_id.isnot(None)).all():
        if match_face(admin.face_id, captured_bytes):
            matched_admin = admin
            break

    if matched_admin:
        session["username"] = matched_admin.Gmail
        session["logged_in"] = True
        current_app.logger.info(f"{session.get('username', '')} logged in with Face ID")
        return render_template(
            "Home.html",
            class_value=int(session.get("class_value", 0)),
            sec=session.get("sec", "")
        )

    current_app.logger.error("face id login failed: no matching face")
    return render_template("Error.html", data="Face not recognized", location="/")


@auth_bp.route("/log-out", methods=["POST", "GET"])
def log_out():
    current_app.logger.info(f"{session.get('username', '')} has logged out")
    email_file(
        administrator2,
        administrator1,
        "log file",
        f"this is the log file of {session.get('username', '')}",
        "App.log",
        dict_details[administrator2],
    )

    with open("App.log", "w"):
        pass

    session.clear()
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/register", methods=["POST", "GET"])
def register():
    """Start administrator registration without putting credentials in the URL."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            return render_template("Error.html", data="Please fill in all fields.", location="/")

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        if not re.match(r"^(?=.*[0-9])(?=.*[a-z]).+$", password):
            return render_template(
                "register.html",
                error="Password must contain at least one lowercase letter and one number.",
            )

        # Do not put username/password in the verification URL.
        # The password is hashed before being placed in Flask's signed session.
        password_hash = bp.hashpw(password.encode(), bp.gensalt()).decode("utf-8")

        otp = str(secrets.randbelow(9000) + 1000)
        otp_hash = hmac.new(
            current_app.secret_key.encode("utf-8"),
            otp.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        session["registration_email"] = username
        session["registration_password_hash"] = password_hash
        session["registration_otp_hash"] = otp_hash
        session["registration_otp_expires"] = time.time() + 300
        session["registration_otp_attempts"] = 0

        email(
            administrator1,
            administrator2,
            "OTP verification",
            f"The OTP for {username} is --{otp}-- for registering an account. It expires in 5 minutes.",
            dict_details[administrator1],
        )

        current_app.logger.info(f"Registration OTP sent for {username}")
        return render_template("register_verification.html")

    return render_template("register.html")


@auth_bp.route("/register_verification", methods=["POST", "GET"])
def register_verification():
    """Verify registration OTP and create the account without exposing credentials in the URL."""
    if not session.get("registration_email") or not session.get("registration_password_hash"):
        return redirect(url_for("auth.register"))

    if request.method == "GET":
        return render_template("register_verification.html")

    if request.is_json:
        data = request.get_json(silent=True) or {}
        otp = str(data.get("onepass", "")).strip()
    else:
        otp = request.form.get("onepass", "").strip()

    stored_otp_hash = session.get("registration_otp_hash")
    expires_at = session.get("registration_otp_expires", 0)
    attempts = session.get("registration_otp_attempts", 0)

    def clear_registration_state():
        for key in (
            "registration_email",
            "registration_password_hash",
            "registration_otp_hash",
            "registration_otp_expires",
            "registration_otp_attempts",
        ):
            session.pop(key, None)

    if not stored_otp_hash or time.time() > expires_at:
        clear_registration_state()
        message = "The OTP has expired. Please start registration again."
        if request.is_json:
            return jsonify({"success": False, "message": message}), 400
        return render_template("Error.html", data=message, location=url_for("auth.register"))

    if attempts >= 5:
        clear_registration_state()
        message = "Too many incorrect attempts. Please start registration again."
        if request.is_json:
            return jsonify({"success": False, "message": message}), 400
        return render_template("Error.html", data=message, location=url_for("auth.register"))

    submitted_otp_hash = hmac.new(
        current_app.secret_key.encode("utf-8"),
        otp.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not secrets.compare_digest(submitted_otp_hash, str(stored_otp_hash)):
        session["registration_otp_attempts"] = attempts + 1
        message = "Incorrect OTP."
        if request.is_json:
            return jsonify({"success": False, "message": message}), 400
        return render_template("Error.html", data=message, location=url_for("auth.register"))

    username = session["registration_email"]
    password_hash = session["registration_password_hash"]

    # The password was already validated and hashed before OTP verification.
    if Admin.query.filter_by(Gmail=username).first():
        clear_registration_state()
        message = "An account with this email already exists."
        if request.is_json:
            return jsonify({"success": False, "message": message}), 400
        return render_template("Error.html", data=message, location=url_for("auth.register"))

    verified = create_account(
        user=username,
        password_hash=password_hash,
        Table=Admin,
    )

    if verified is True:
        clear_registration_state()
        current_app.logger.info(f"{username} completed account registration")
        if request.is_json:
            return jsonify({"success": True, "message": "Code verified.", "redirect": url_for("auth.login_page")})
        return redirect(url_for("auth.login_page"))

    clear_registration_state()
    message = "Unable to create the account. Please try again."

    if request.is_json:
        return jsonify({"success": False, "message": message}), 400
    return render_template("Error.html", data=message, location=url_for("auth.register"))
