import json
from datetime import date

from flask import Blueprint, render_template, request, session,current_app,redirect
from sqlalchemy import func

from shared.models import Attendance,Student,teacher
from app.services.graph_service import generate_graph, generate_pie_graph
from app.services.leaderboard_service import compute_leaderboard
from shared import db,login_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/graph/<int:roll_no>/<string:subject>/<int:exam_id>", methods=["POST", "GET"], endpoint="graph")
def graph(roll_no: int, subject: str, exam_id: int):
    if subject:
        graph_image, _exam1 = generate_graph(
            roll_no=roll_no,
            subject=subject,
            exam_id=exam_id,
            class_value=session.get("class_value"),
            sec=session.get("sec")
        )
        return render_template("graph.html", graph=graph_image)


@reports_bp.route("/piegraph/<int:roll_no>/<int:exam_id>", methods=["POST", "GET"], endpoint="piegraph")
def piegraph(roll_no: int, exam_id: int):
    graph_image, _exam1 = generate_pie_graph(
        roll_no=roll_no,
        exam_id=exam_id,
        class_value=session.get("class_value"),
        sec=session.get("sec")
    )
    return render_template("graph.html", graph=graph_image)


@reports_bp.route("/leaderboard", methods=["GET", "POST"], endpoint="leaderboard")
@login_required
def leaderboard():
    exa = request.form.get("exam", "")
    class_input = request.form.get("class", "").strip()
    if request.method=="POST":
            if class_input:
                try:
                    class_input = int(class_input)
                except ValueError:
                        return render_template("Error.html",data="invalid class value", location="/leaderboard")
                students_exist = Student.query.filter(Student.student_class == class_input).first()
                if not students_exist:
                        return render_template("Error.html",data="No matching students found", location="/leaderboard")
                session["class_value"] = class_input

            class_value = session.get("class_value")

            if exa and class_value is not None:
                result = compute_leaderboard(class_value, exa)
                if result is None:
                        return render_template("Error.html",data="No matching students found", location="/leaderboard")

                students, podium, total_marks = result

                return render_template(
                    "leaderboard.html",
                    class_value=class_value,
                    students=students,
                    total_marks=total_marks,
                    podium=podium,
                    sub="All",
                    exam=exa
                )
            else:
                return render_template("Error.html",data="select the exam and class",location="/leaderboard")
    return render_template("leaderboard.html", class_value=class_input if class_input is not None else "")

@reports_bp.route("/attendence", methods=["GET", "POST"], endpoint="attendence")
@login_required
def attendence():
    teachers = teacher.Teacher.query.filter(teacher.Teacher.Gmail == session.get("username", "")).first()
    class_input = teachers.class_teacher
    sec_input = teachers.class_teacher_sec

    if request.method == "POST":
        payload = request.form.get("attendance_data", "")
        if not payload:
            return render_template("Error.html", data="No attendance data received", location="/attendence")

        try:
            data = json.loads(payload)
        except (TypeError, ValueError):
            return render_template("Error.html", data="Invalid attendance data", location="/attendence")

        month_str = data.get("month", "")
        records = data.get("records", {})

        try:
            year, month = [int(part) for part in month_str.split("-")]
        except (ValueError, AttributeError):
            return render_template("Error.html", data="Invalid month", location="/attendence")

        for roll_no_str, days in records.items():
            try:
                roll_no = int(roll_no_str)
            except ValueError:
                continue

            for day_str, status in days.items():
                if status not in ("present", "absent", "leave"):
                    continue
                try:
                    day = int(day_str)
                    entry_date = date(year, month, day)
                except (ValueError, TypeError):
                    continue

                existing = Attendance.query.filter_by(
                    roll_no=roll_no,
                    class_value=class_input,
                    section=sec_input,
                    date=entry_date
                ).first()

                if existing:
                    existing.status = status
                    existing.marked_by = session.get("username", "")
                else:
                    db.session.add(Attendance(
                        roll_no=roll_no,
                        class_value=class_input,
                        section=sec_input,
                        date=entry_date,
                        status=status,
                        marked_by=session.get("username", "")
                    ))

        db.session.commit()

    students_exist = Student.query.filter(Student.student_class == class_input, Student.section == sec_input).all()
    students = [{"roll_no": i.roll_no, "name": i.student_name} for i in students_exist]

    month_param = request.values.get("month", "")
    try:
        view_year, view_month = [int(part) for part in month_param.split("-")]
    except (ValueError, AttributeError):
        today = date.today()
        view_year, view_month = today.year, today.month
    selected_month = f"{view_year:04d}-{view_month:02d}"

    existing = Attendance.query.filter(
        Attendance.class_value == class_input,
        Attendance.section == sec_input,
        Attendance.date >= date(view_year, view_month, 1),
        Attendance.date < date(view_year + (1 if view_month == 12 else 0), 1 if view_month == 12 else view_month + 1, 1)
    ).all()
    existing_records = {}
    for row in existing:
        existing_records.setdefault(str(row.roll_no), {})[str(row.date.day)] = row.status

    return render_template(
        "attendence.html",
        students=students,
        class_value=class_input,
        sec=sec_input,
        selected_month=selected_month,
        existing_records=existing_records
    )