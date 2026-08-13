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

def remove(roll_no=0,name=""):
    cn,cur=connect()
    try:
        if roll_no:
            cur.execute("delete from students where roll_no=%s",(roll_no,))
        elif name:
            cur.execute("delete from teachers where Gmail=%s",(name,))

        cn.commit()
    except Exception:
        cn.rollback()
        raise
    finally:
        cur.close()
        cn.close()
