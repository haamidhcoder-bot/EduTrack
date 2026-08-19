from flask import Blueprint, render_template, session, request, redirect, url_for, current_app, jsonify
import random
import bcrypt as bp
from datetime import datetime

from shared import db,login_required
from shared.models import Teacher,Admin,Student
from shared.services.create_account_service import create_account
from shared.services.face_id_service import save_face
from shared.config import dict_details,administrator1
from shared.services.email_service import email

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

        current_app.logger.info(f"{gmail} has changed the password")
        return render_template("forgot_password_verification.html",username=gmail,password=new_password)


    return render_template("forgot_password.html")

@pages_bp.route("/forgot_password_verification/<username>/<password>", methods=["POST", "GET"])
def forgot_password_verification(username: str,password:str):
        admin = Admin.query.filter(Admin.Gmail == username).first()
        if request.method=="POST":
            if request.is_json:
                data = request.get_json(silent=True) or {}
                otp = data.get("onepass", "")
            else:
                otp = request.form.get("onepass", "")

            if otp==session.get("OTP"):
                admin.password = bp.hashpw(password.encode(),bp.gensalt()) 
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
            image = request.files.get("face")

            if not image:
                return "No image received", 400

            face_filename = save_face(image)

            teacher=Teacher.query.filter(Teacher.class_teacher==class_teacher,
                                  Teacher.class_teacher_sec==class_teacher_sec
                                  ).first()
            
            if not username or not password or not confirm_password:
                return render_template("Error.html", data="Please fill in all fields.",location="/")

            print(teacher)

            if not teacher:
                verification=create_account(user=username,password=password,confirm_password=confirm_password,Table=Teacher,class_teacher=class_teacher,class_teacher_sec=class_teacher_sec,face_id=face_filename)

                if not verification:
                    return render_template("Error.html", data="duplicate entry.",location="/add_teacher")

                if  verification=="pass":
                    return render_template("Error.html", data="passwords are not same.",location="/home")

                if verification:
                    return redirect("/teachers_data")
                current_app.logger.info(f"{session.get("username","")} has added {username} as a teacher")
            else:
                return render_template("Error.html", data="duplicate entry.",location="/add_teacher")
        return render_template("add_teacher.html")

@pages_bp.route("/add_student", methods=["GET", "POST"], endpoint="add_student")
@login_required
def add_student():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        class_input = request.form.get("class", "").strip()
        sec = request.form.get("section", "").strip()
        student_gmail = request.form.get("student_gmail", "").strip()
        dob = request.form.get("DOB", "").strip()
        mobile_no = request.form.get("mobile_no", "").strip()

        if not student_name or not class_input or not sec:
            return render_template("Error.html", data="Please fill in all required fields.", location="/add_student")

        try:
            class_value = int(class_input)
        except ValueError:
            return render_template("Error.html", data="invalid class value", location="/add_student")

        if class_value < 1 or class_value > 12:
            return render_template("Error.html", data="Class must be between 1 and 12.", location="/add_student")

        if sec not in ("A", "B", "C"):
            return render_template("Error.html", data="invalid section", location="/add_student")

        dob_value = None
        if dob:
            try:
                dob_value = datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                return render_template("Error.html", data="invalid date of birth", location="/add_student")

        mobile_value = None
        if mobile_no:
            if not mobile_no.isdigit():
                return render_template("Error.html", data="invalid mobile number", location="/add_student")
            mobile_value = int(mobile_no)

        # Automatically generate the next roll number for this class and section.
        # A=1, B=2, C=3:
        # Class 5-A -> 50101, 50102, ...
        # Class 5-B -> 50201, 50202, ...
        # Class 5-C -> 50301, 50302, ...
        section_code = {"A": 1, "B": 2, "C": 3}[sec]
        roll_prefix = class_value * 1000 + section_code * 100

        last_student = (
            Student.query
            .filter(
                Student.student_class == class_value,
                Student.section == sec
            )
            .order_by(Student.roll_no.desc())
            .first()
        )

        if last_student:
            next_roll_no = last_student.roll_no + 1
        else:
            next_roll_no = roll_prefix + 1

        # Allow roll numbers 01 through 99 within each class/section.
        if next_roll_no > roll_prefix + 99:
            return render_template(
                "Error.html",
                data=f"No more roll numbers available for Class {class_value}-{sec}.",
                location="/add_student"
            )

        # Protect against an already-used generated roll number.
        while Student.query.filter_by(roll_no=next_roll_no).first():
            next_roll_no += 1
            if next_roll_no > roll_prefix + 99:
                return render_template(
                    "Error.html",
                    data=f"No more roll numbers available for Class {class_value}-{sec}.",
                    location="/add_student"
                )

        student = Student(
            roll_no=next_roll_no,
            student_name=student_name,
            student_class=class_value,
            section=sec,
            student_gmail=student_gmail or None,
            DOB=dob_value,
            mobile_no=mobile_value
        )

        try:
            db.session.add(student)
            current_app.logger.info(f"{session.get("username","")} has added {student_name} as a student")
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Could not add student: {e}")
            return render_template("Error.html", data="Could not add the student.", location="/add_student")

        current_app.logger.info(f"{session.get('username', '')} added student {student_name} (roll no {student.roll_no})")

        session["class_value"] = class_value
        session["sec"] = sec

        return redirect("/home")

    return render_template("add_student.html")