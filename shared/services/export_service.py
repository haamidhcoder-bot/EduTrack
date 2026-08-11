import csv
import mysql.connector as sql

from shared.config import Mysql_pass

def export_csv(class_value,sec):
    conn = sql.connect(
        host="127.0.0.1",
        user="root",
        password=Mysql_pass,
        database="schooldb"
    )

    cur = conn.cursor()

    cur.execute("select * from students where class=%s and section like %s",(class_value,sec))

    f = open(
    f"C:/Users/dell/Desktop/Student_Performance_Analysis/exports/students_{class_value}-{sec}.csv",
    "w",
    newline="")
    csv_writer=csv.writer(f)

    for data in cur:
        csv_writer.writerow(data)
