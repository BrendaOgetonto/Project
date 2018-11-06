import pymysql

connection = pymysql.connect(host="localhost", user="root",passwd="",database="isproject")

cursor = connection.cursor()


connection.commit()
connection.close()