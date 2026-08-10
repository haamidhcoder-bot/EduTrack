from functools import wraps

from flask import abort, redirect, url_for, session

from shared.models import Teacher


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("logged_in"):
            return func(*args, **kwargs)

        return redirect(url_for("auth.login_page"))

    return wrapper


def class_teacher_required(func):
    """Allow access only to a logged-in teacher with an assigned class/section.

    The assignment is read from the Teacher record on every protected request,
    so class/section access is never taken from a user-selected form value.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login_page"))

        username = session.get("username", "")
        teacher = Teacher.query.filter_by(Gmail=username).first()

        if (
            teacher is None
            or teacher.class_teacher is None
            or not teacher.class_teacher_sec
        ):
            abort(403)

        # Keep the session synchronized with the authoritative Teacher record.
        session["class_teacher"] = teacher.class_teacher
        session["class_teacher_sec"] = teacher.class_teacher_sec

        return func(*args, **kwargs)

    return wrapper
