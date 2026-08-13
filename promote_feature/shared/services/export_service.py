import csv
import io
import mysql.connector as sql

from shared.config import Mysql_pass

def connect():
    cn= sql.connect(
        host="127.0.0.1",
        user="root",
        password=Mysql_pass,
        database="schooldb"
    )

    cur=cn.cursor()

    return cn,cur

def export_csv(class_value, sec):
    cn, cur = connect()

    try:
        cur.execute(
            "SELECT * FROM students WHERE class=%s AND section=%s",
            (class_value, sec)
        )

        output = io.StringIO()
        csv_writer = csv.writer(output)

        # Include column names
        csv_writer.writerow([column[0] for column in cur.description])

        # Write student data
        csv_writer.writerows(cur.fetchall())
    finally:
        cur.close()
        cn.close()

    return output.getvalue()

def import_csv(file, class_value, sec):
    cn,cur = connect()

    reader = csv.reader(io.TextIOWrapper(file, encoding="utf-8-sig"))

    added = 0
    updated = 0

    try:
        for row in reader:
            row = [c.strip() for c in row]
            if not row or not row[0]:
                continue
            if not row[0].isdigit():
                # skips a header row like "roll_no,student_name,..."
                continue

            roll_no = row[0]
            student_name = row[1] if len(row) > 1 else ""
            row_class = row[2] if len(row) > 2 and row[2] else class_value
            row_section = row[3] if len(row) > 3 and row[3] else sec
            student_gmail = row[4] if len(row) > 4 else None
            dob = row[5] if len(row) > 5 and row[5] else None
            mobile_no = row[6] if len(row) > 6 and row[6] else None

            cur.execute("SELECT 1 FROM students WHERE roll_no = %s", (roll_no,))
            exists = cur.fetchone() is not None

            cur.execute(
                """
                INSERT INTO students
                    (roll_no, student_name, class, section, student_gmail, DOB, mobile_no)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    student_name = VALUES(student_name),
                    class = VALUES(class),
                    section = VALUES(section),
                    student_gmail = VALUES(student_gmail),
                    DOB = VALUES(DOB),
                    mobile_no = VALUES(mobile_no)
                """,
                (roll_no, student_name, row_class, row_section, student_gmail, dob, mobile_no)
            )

            if exists:
                updated += 1
            else:
                added += 1

        cn.commit()
        return added, updated
    except Exception:
        cn.rollback()
        raise
    finally:
        cur.close()
        cn.close()

def promote():
    """
    Move every student up one class (roll_no encodes class*1000 + section*100 + no,
    so class+1 == roll_no+1000).

    Class 12 students graduate and are removed first - otherwise the class-11
    students being promoted into class 12 would collide with the roll numbers
    already used by the outgoing class-12 batch (roll_no is a primary key).
    Deleting a student cascades to their `marks` rows automatically (ON DELETE
    CASCADE); it does NOT touch `attendance`, since that table has no foreign
    key back to students and is meant to stay as a historical record.

    Classes are updated from 11 down to 1 (highest first) in separate
    statements so an already-promoted row is never picked up again by a
    later, lower-class UPDATE in the same run.
    """
    cn, cur = connect()

    try:
        cur.execute("SELECT COUNT(*) FROM students WHERE class = 12")
        graduated = cur.fetchone()[0]

        cur.execute("DELETE FROM students WHERE class = 12")

        promoted = 0
        for cls in range(11, 0, -1):
            cur.execute(
                """
                UPDATE students
                SET class = class + 1, roll_no = roll_no + 1000
                WHERE class = %s
                """,
                (cls,)
            )
            promoted += cur.rowcount

        cn.commit()
        return {"graduated": graduated, "promoted": promoted}
    except Exception:
        cn.rollback()
        raise
    finally:
        cur.close()
        cn.close()
