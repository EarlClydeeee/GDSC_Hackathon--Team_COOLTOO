import mysql.connector


def connect_to_db():
    db = mysql.connector.connect(
        host="gdghackathon.c76i04gyid3y.ap-southeast-1.rds.amazonaws.com",
        user="admin",
        passwd="gdghackathonpw",
        database="gdghackathon"
    )
    cursor = db.cursor()
    return db, cursor
