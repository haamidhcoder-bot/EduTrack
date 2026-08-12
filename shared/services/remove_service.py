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

def remove_student(roll_no:int):
    cn,cur=connect()

    cur.execute("delete from students where roll_no=%s",(roll_no,))

    cn.commit()
    cn.close()
