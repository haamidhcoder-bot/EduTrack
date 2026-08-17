import mysql.connector
import chromadb
from shared.config import Mysql_pass

cn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=Mysql_pass,
    database="schooldb"
)

cursor = cn.cursor()

cursor.execute("""
SELECT
    roll_no,
    student_name,
    class,
    section,
    student_gmail,
    mobile_no
FROM students
""")

students = cursor.fetchall()

print("Rows returned from MySQL:", len(students))

client = chromadb.PersistentClient(path="./data_db")

try:
    client.delete_collection(
        "student_data"
    )
except:
    pass

collection = client.create_collection(
    "student_data"
)

documents = []
ids = []

for index, student in enumerate(students):

    text = f"""
    Roll number: {student[0]}
    Student name: {student[1]}
    Class: {student[2]}
    Section: {student[3]}
    Email: {student[4]}
    Mobile number: {student[5]}
    """

    documents.append(text)

    ids.append(str(index))

collection.add(
    documents=documents,
    ids=ids
)

print("Documents added:", len(documents))

print("Documents in ChromaDB:",
      collection.count())

print("Vector database created.")

cn.close()