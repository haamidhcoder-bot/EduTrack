import re
import bcrypt as bp

from app.extensions import db

PASSWORD_PATTERN = r"^(?=.*[0-9])(?=.*[a-z]).+$"


def create_account(
    user,
    password,
    confirm_password,
    Table,
    class_teacher=None,
    class_teacher_sec=None,
):
    """
    Creates an account for any model.

    Returns:
        True   -> Account created successfully.
        "pass" -> Password validation failed.
        ""     -> Database error.
    """

    # Validate password
    if password != confirm_password or not re.match(PASSWORD_PATTERN, password):
        return "pass"

    # Common fields
    data = {
        "Gmail": user,
        "password": bp.hashpw(password.encode(), bp.gensalt()),
    }

    # Add teacher-specific fields
    if Table.__name__ == "Teacher":
        data["class_teacher"] = class_teacher
        data["class_teacher_sec"] = class_teacher_sec

    try:
        new_user = Table(**data)
        db.session.add(new_user)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {e}")
        return ""