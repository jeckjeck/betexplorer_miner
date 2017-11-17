import pymysql

con = pymysql.connect(host="",  # your host, usually localhost
                       user="",  # your username
                       passwd="",  # your password
                       db="",  # name of the database
                       autocommit=True)
with con:
    cur = con.cursor()
