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
    return cn

def export_csv(class_value,sec):
    cn=connect()

    cur = cn.cursor()

    cur.execute("select * from students where class=%s and section like %s",(class_value,sec))

    f = open(
    f"C:/Users/dell/Desktop/Student_Performance_Analysis/exports/students_{class_value}-{sec}.csv",
    "w",
    newline="")
    csv_writer=csv.writer(f)

    for data in cur:
        csv_writer.writerow(data)
    f.close()
    cn.close()

def import_csv(file, class_value, sec):
    """
    Reads a students CSV (columns: roll_no, student_name, class, section,
    student_gmail, DOB, mobile_no — no header row, same layout export_csv
    produces) and upserts it into the students table.

    `file` is a binary file-like object, e.g. request.files['csv_file'].stream.
    New roll numbers are inserted; roll numbers that already exist are updated.
    Rows missing class/section fall back to the class_value/sec the form was
    submitted with, so a plain "name, roll_no" style sheet still works for a
    single-class import.

    Returns (added, updated) counts.
    """
    cn = connect()
    cur = cn.cursor()

    reader = csv.reader(io.TextIOWrapper(file, encoding="utf-8-sig"))

    added = 0
    updated = 0

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
    cn.close()
    return added, updated
