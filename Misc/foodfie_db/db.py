import pymysql
import config


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


def getData(sql):
    conn, cursor = connectDB()
    cursor.execute(sql)
    data = cursor.fetchall()
    return data
