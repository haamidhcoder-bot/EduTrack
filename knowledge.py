import chromadb
import mysql.connector as sql

from shared.config import Mysql_pass


def connect():
    cn = sql.connect(
        host="127.0.0.1",
        user="root",
        password=Mysql_pass,
        database="schooldb"
    )

    cur = cn.cursor()

    return cn, cur


client = chromadb.PersistentClient(
    path="./data_db"
)


cn, cur = connect()

try:

    collection = client.get_or_create_collection(
        name="school_notes"
    )

    cur.execute("""
        SELECT
            roll_no,
            student_name,
            class,
            section,
            student_gmail,
            DOB,
            mobile_no
        FROM students
    """)

    rows = cur.fetchall()

    documents = []

    for row in rows:

        document = f"""
        Student roll number: {row[0]}
        Student name: {row[1]}
        Class: {row[2]}
        Section: {row[3]}
        Email: {row[4]}
        Date of birth: {row[5]}
        Mobile number: {row[6]}
        """

        documents.append(document.strip())

    if not documents:
        print("No student data found.")
    else:

        collection.add(
            ids=[
                str(i)
                for i in range(len(documents))
            ],
            documents=documents
        )

        print(
            f"Knowledge base created with "
            f"{len(documents)} documents."
        )

finally:

    cur.close()
    cn.close()