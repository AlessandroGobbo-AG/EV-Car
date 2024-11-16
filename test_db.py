import sqlite3

conn = sqlite3.connect('user.db')

dict_mail_pass = {}

# Crea un cursore
cursor = conn.cursor()
cursor.execute("SELECT Mail, Password FROM USER")
rows = cursor.fetchall()
for row in rows:
    dict_mail_pass[row[0]] = row[1]

print(dict_mail_pass)