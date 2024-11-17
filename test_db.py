import sqlite3

def user_list():

    #dictionary with user's mail and password
    dict_mail_pass = {}

    #database connection
    db = sqlite3.connect('user.db')
    cursor = db.cursor()
    cursor.execute("SELECT Mail, Password FROM USER")
    rows = cursor.fetchall()

    for row in rows:
        dict_mail_pass[row[0]] = row[1]
    
    return dict_mail_pass

def insert_user():
    sql_insert = '''INSERT into USER(Mail, Name_Surname, User_Type, Password) values ('mail_prova','prova','viewer', 'password')'''
    db = sqlite3.connect('user.db')
    cursor = db.cursor()
    cursor.execute(sql_insert)
    db.commit()
    db.close()

if __name__ == '__main__':
    insert_user()
    print(user_list())
