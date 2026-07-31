from flask import Blueprint, render_template, redirect, request, session, current_app
from sqlalchemy import func
import re

from app.extensions import db
from app.models.student import Student
from app.models.teacher import Teacher
from app.decorators import login_required

home_bp = Blueprint("home", __name__)


@home_bp.route("/home", endpoint="home", strict_slashes=False)
@login_required
def home():
    class_value = int(session.get("class_value", 0)) or None
    sec = session.get("sec", "")


    if not class_value:
        return render_template("Home.html", class_value=None)

    students = Student.query.filter(
        Student.student_class == class_value,
        Student.section == sec
    ).all()
    return render_template(
            "Home.html",
            class_value=class_value,
            students=students
        )



@home_bp.route("/refresh", methods=["GET", "POST"], endpoint="refresh")
def refresh():
    if request.method == "POST":
        class_input = request.form.get("class", "").strip()
        if class_input:
            try:
                class_input = int(class_input)
            except ValueError:
                return render_template("Error.html",data="invalid class value", location="/home")
            students_exist = Student.query.filter(Student.student_class == class_input).first()
            if not students_exist:
                current_app.logger.error("No matching students found")
                return render_template("Error.html",data="No matching students found", location="/home")
            session["class_value"] = class_input

        class_value = session.get("class_value")
        if class_value is None:
                return render_template("Error.html",data="select a class first", location="/home")

        sec = request.form.get("section", "").strip() or session.get("sec", "")
        session["sec"] = sec

        return render_template(
            "Home.html",
            class_value=class_value,
            sec=sec
        )

    return redirect("/home")

@home_bp.route("/show_students", methods=["GET", "POST"], endpoint="show_students")
def show_students():
    if request.method == "POST":
        class_input = request.form.get("class", "").strip()
        sec = request.form.get("section", "").strip() or session.get("sec", "")
        session["sec"] = sec
        if class_input:
            try:
                class_input = int(class_input)
            except ValueError:
                return render_template("Error.html",data="invalid class value", location="/home")
            students_exist = Student.query.filter(Student.student_class == class_input,Student.section==session.get("sec","")).all()
            if not students_exist:
                current_app.logger.error("No matching students found")
                return render_template("Error.html",data="No matching students found", location="/home")
            session["class_value"] = class_input

        class_value = session.get("class_value")
        if class_value is None:
                return render_template("Error.html",data="select a class first", location="/home")
        log1=True
        return render_template(
                "Home.html",
                class_value=class_value,
                sec=sec,
                students=students_exist,
                log1=log1
            )
    return redirect("/home")

@home_bp.route("/teachers_data", methods=["GET", "POST"], endpoint="/teachers_data",)
def teachers_data():
    teachers=Teacher.query.all() 
    return render_template("teachers_data.html",teachers=teachers)

@home_bp.route("/edit/<int:roll_no>", methods=["GET", "POST"])
def edit(roll_no: int):
    student = Student.query.filter(
        Student.roll_no == roll_no
    ).first()
    if request.method == "POST" and student:
        DOB = request.form.get("content","")  # to get info from input box
        Mobile = request.form.get("Mobile","")
        if DOB:
           student.DOB = DOB
        if Mobile:
           student.mobile_no=Mobile 
        try:
                current_app.logger.info(f"{session.get('username', '')} has editted date of birth and phone number of student with roll no {roll_no}")
                db.session.commit()  # commiting it
                return redirect("/home")  # back to home
        except Exception as e:
            current_app.logger.error(e)
            return redirect("/")
        # create a new task
    else:
        return render_template("edit.html", student=student)

@home_bp.route("/edit_teacher/<Gmail>", methods=["GET", "POST"])
def edit_teacher(Gmail: str):
    pattern = r"^(?=.*[0-9])(?=.*[a-z]).+$"
    teacher = Teacher.query.filter(
        Teacher.Gmail == Gmail
    ).first()
    if request.method == "POST" and teacher:
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        if password==confirm_password and re.match(pattern,password):
            teacher.password=password
        try:
                current_app.logger.info(f"{session.get('username', '')} has changed password  of {Gmail}")
                db.session.commit()  # commiting it
                return redirect("/teachers_data")  # back to home
        except Exception as e:
            current_app.logger.error(e)
            return redirect("/")
        # create a new task
    else:
        return render_template("edit_teacher.html", teacher=teacher)