import streamlit as st
import sqlite3



# Crea un cursore
#cursor = conn.cursor()
#cursor.execute("SELECT * FROM USER")
#rows = cursor.fetchall()

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

st.session_state.users_list = user_list()

st.title('Amazing User Login App')

# Create user_state
if 'user_state' not in st.session_state:
    st.session_state.user_state = {
        'username': '',
        'password': '',
        'logged_in': False
    }

if not st.session_state.user_state['logged_in']:
    # Create login form
    st.write('Please login')
    username = st.text_input('E-Mail')
    password = st.text_input('Password', type='password')
    submit = st.button('Login')

    # Check if user is logged in
    if submit and st.session_state.user_state['logged_in'] == False:
        if username in st.session_state.users_list and password == st.session_state.users_list[username]:
            st.session_state.user_state['username'] = username
            st.session_state.user_state['password'] = password
            st.session_state.user_state['logged_in'] = True
            st.write('You are logged in')
            st.rerun()
        else:
            st.write('Invalid username or password')

elif st.session_state.user_state['logged_in']:
    st.write('Welcome to the app')
    st.write('You are logged in as:', st.session_state.user_state['username'])