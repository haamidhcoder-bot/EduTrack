from flask import Blueprint, render_template, request, session, url_for,redirect
from sqlalchemy import func

from shared.extensions import db
from shared.models import Student, Exam, Mark
from shared.decorators import login_required, class_teacher_required

home_bp = Blueprint("home", __name__)


def _teacher_class_context():
    class_value = session.get("class_teacher")
    sec = session.get("class_teacher_sec")

    if class_value is None or not sec:
        return None, None

    return int(class_value), sec


def _load_results(class_value, sec, subject, exam_name):
    students = Student.query.filter(
        Student.student_class == class_value,
        Student.section == sec
    ).all()

    exam = Exam.query.filter(Exam.exam_name == exam_name).first() if exam_name else None

    results = []
    if exam is not None and subject and subject != "All":
        results = Mark.query.join(
            Student, Student.roll_no == Mark.roll_no
        ).filter(
            Mark.student_class == class_value,
            Student.section == sec,
            Mark.exam_id == exam.exam_id,
            Mark.subject == subject
        ).all()

    return students, exam, results


@home_bp.route("/home", endpoint="home", strict_slashes=False)
@login_required
@class_teacher_required
def home():
    class_value, sec = _teacher_class_context()
    if class_value is None:
        return render_template(
            "Error.html",
            data="No class-teacher assignment found.",
            location="/"
        )

    sub = session.get("subject", "")
    exa = session.get("exam", "")

    students, exam, results = _load_results(
        class_value, sec, sub, exa
    )

    if sub == "All" and exam is not None:
        totals = db.session.query(
            Mark.roll_no,
            func.sum(Mark.marks).label("total")
        ).join(
            Student, Student.roll_no == Mark.roll_no
        ).filter(
            Mark.student_class == class_value,
            Student.section == sec,
            Mark.exam_id == exam.exam_id
        ).group_by(Mark.roll_no).all()

        total_marks = {row.roll_no: row.total for row in totals}

        return render_template(
            "Home.html",
            class_value=class_value,
            students=students,
            total_marks=total_marks,
            sub=sub,
            exam=exa,
            exam_id=exam.exam_id,
            sec=sec
        )

    return render_template(
        "Home.html",
        class_value=class_value,
        students=students,
        results=results,
        sub=sub,
        exam=exa,
        sec=sec
    )


@home_bp.route("/show_results", methods=["POST"], endpoint="show_results")
@login_required
@class_teacher_required
def show_results():
    class_value, sec = _teacher_class_context()

    if class_value is None:
        return render_template(
            "Error.html",
            data="No class-teacher assignment found.",
            location="/home"
        )

    sub = request.form.get("subject10", "") or request.form.get("subject12", "")
    exa = request.form.get("exam", "")

    if not sub or not exa:
        return render_template(
            "Error.html",
            data="Select the subject and exam.",
            location="/home"
        )

    # The class and section are deliberately NOT read from the form.
    # They always come from the logged-in teacher's assignment.
    session["class_value"] = class_value
    session["sec"] = sec
    session["subject"] = sub
    session["exam"] = exa

    return redirect(url_for("home.home"))
