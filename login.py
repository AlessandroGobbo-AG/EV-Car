import streamlit as st
import sqlite3
import time
import smtplib 
from email.mime.text import MIMEText
from random import randrange
import hashlib
from pathlib import Path

'''
Gestisce il processo di estrazione degli utenti presenti nel database:
- Viene creato un dizionario che conterrà la mail e le rispettive 
  password e permessi
- Avviene il colegamento al database
- Viene creata la select
- Viene riempito il dizionario

Returns:
    dict_mail_pass: dict, contiente come chiavi le e-mail degli utenti, con 
                    con le rispettive password e permessi dell'utente.
'''
def user_list():
    dict_mail_pass = {}
    db_dir = Path('DATABASE')
    db = sqlite3.connect(db_dir/'user.db')
    cursor = db.cursor()
    cursor.execute("SELECT Mail, Password, User_Type, Name_Surname  FROM USER")
    rows = cursor.fetchall()
    
    for row in rows:
        dict_mail_pass[row[0]] = {'password': row[1], 'user_type': row[2], 'username': row[3]}
    
    return dict_mail_pass

'''
Gestisce il processo di aggiunta di un nuovo utente sul database:
- Viene creato l'insert
- Si collega al database
- La password viene Hashata con sha256
Param: 
    Mail: e-mail del nuovo utente
    Username: nome e cognome del nuovo utente
    User_type: tipologia del utente (Viewer, Sales)
    Password: passaword del nuovo utente
Return: 
    boolean: True se non ci sono errori nell'aggiunta sul database, 
             False altrimenti
'''
def add_user(Mail, Username, User_type, Password):
    sql_insert = '''INSERT INTO USER(Mail, Name_Surname, User_Type, Password) 
                    VALUES (?, ?, ?, ?)'''
    db_dir = Path('DATABASE')
    db = sqlite3.connect(db_dir/'user.db')
    cursor = db.cursor()
    
    try:
        cursor.execute(sql_insert, (Mail, Username, User_type, hashlib.sha256(Password.encode('utf-8')).hexdigest()))
        db.commit()
    except sqlite3.Error as e:
        st.error(f"Errore nel database: {e}")
        return False
    finally:
        db.close()
    return True

'''
Gesisce il cambio di password di un utente del database:
- Viene creata la funzione di update
- Avviene il collegamento al database
- La password viene hashata con sha256
Param: 
    Mail: mail dell'utente
    Passoword: password dell'utente
Returns: 
    boolean: True se avviene correttamente la modifica sul database, 
             False altrimenti.
'''
def change_password(Mail, Password):

    sql_update = '''UPDATE USER SET Password = ? WHERE Mail = ?'''
    db_dir = Path('DATABASE')
    db = sqlite3.connect(db_dir/'user.db')
    cursor = db.cursor()

    try: 
        cursor.execute(sql_update, (hashlib.sha256(Password.encode('utf-8')).hexdigest(), Mail))
        db.commit()
    except sqlite3.Error as e:
        st.error(f"Errore nel database: {e}")
        return False
    finally:
        db.close()
    return True

"""
Gestisce il processo di autenticazione (login, registrazione, recupero password)
- Se un utente si registra o cambia la password, verrà indirizzato nuovamente al login
- In fase di registrazione, l'utente sceglierà il suo permesso
- Per il cambiamento della password, l'utente prima dovrà eseguire una verifica a due fattori
Returns:
    tuple: (bool) - (autenticato)
"""
def authentication():
    
    '''
    Inizializzazione degli session_state:
    -user_state: inizializza gli stati dell'utente
    -user_list: inizializza un dizionario che ha come chiave 'mail' dell'utente
    -widget_key: sessione che mi permette di resettare per tornare alla pagina di login
    '''
    if 'user_state' not in st.session_state:
        st.session_state.user_state = {
            'mail': '',
            'username': '',
            'user_type': '',
            'logged_in': False
        }
    
    if 'users_list' not in st.session_state:
        st.session_state.users_list = user_list()

    if 'widget_key' not in st.session_state:
        st.session_state.widget_key = 0

    st.title('User Login Page')

    # Selectbox per scegliere l'azione 
    option = st.selectbox(
        'Choose the action',
        ("Login", "Sign Up", "Forgot Password"),
        key=f"select_{st.session_state.widget_key}"
    )

    '''
    Condizioni che servono per eseguire l'azione scelta dall'utente
    '''
    if option == 'Login':
        #st.write(st.session_state.users_list)
        container = st.container(border=True)
        st.session_state.user_state['mail'] = container.text_input('E-Mail')
        password = container.text_input('Password', type='password')
        #container.write(st.session_state.user_state['mail'].lower())
        #st.write(st.session_state.users_list)
        submit = st.button('Login')

        if 'submitted' not in st.session_state:
            st.session_state.submitted = None

        if submit:
            st.session_state.submitted = True

        # Verifica che la mail sia presente del DB e che la password hashata coincida con password DB
        if st.session_state.submitted:
            if st.session_state.user_state['mail'].lower() in st.session_state.users_list and \
            hashlib.sha256(password.encode('utf-8')).hexdigest() == st.session_state.users_list[st.session_state.user_state['mail'].lower()]['password']:
                #st.session_state.authenticated = True
                st.session_state.user_state['user_type'] = st.session_state.users_list[st.session_state.user_state['mail'].lower()]['user_type']
                st.session_state.user_state['username'] = st.session_state.users_list[st.session_state.user_state['mail'].lower()]['username']
                st.session_state.user_state['logged_in'] = True
                st.success('Login successful!')
                return st.session_state.user_state['logged_in']
                        
            else:
                st.error('Invalid email or password')

    elif option == 'Sign Up':
        container = st.container(border=True)
        col1, col2 = container.columns(2)
        
        # Compilazione dei campi dell'utente
        with container:
            mail = col1.text_input('Inserisci e-mail')
            username = col1.text_input('Inserisci nome e cognome')
            password = col2.text_input('Inserisci password', type='password')
            user_type = col2.selectbox('User Type',('Analista', 'Venditore'))
            submit = st.button('Sign Up')

        # Verifica della non presenza dell'utente sul DB 
        if submit:
            if mail and username and password:
                if mail not in st.session_state.users_list:
                    if add_user(mail.lower(), username.lower(), user_type, password):
                        st.success("Registrazione completata! Verrai indirizzato al login.")

                        # Aggiorno il dizionario degli utenti una volta inserito il nuovo utente
                        st.session_state.users_list = user_list()
                        time.sleep(4)
                        st.session_state.widget_key += 1  # Incrementa la key

                        st.rerun()
                else:
                    st.error("Email già registrata")
            else:
                st.warning("Compila tutti i campi")

    # Forgot Passowrd
    else:  
        container = st.container(border=True)
        email_recovery = container.text_input('Inserisci la tua email')
        submit = st.button('Recupera Password')
        
        # Inizializzazione delle variabili di sessione
        if 'verify_number' not in st.session_state:
            st.session_state.verify_number = 0
        if 'check_user' not in st.session_state:
            st.session_state.check_user = False
        if 'code_recovery' not in st.session_state:
            st.session_state.code_recovery = None
        if 'code_verified' not in st.session_state:
            st.session_state.code_verified = False

        # Gestione dell'invio email
        if submit:
            if email_recovery in st.session_state.users_list:
                st.session_state.check_user = True
                
                #campi della mail e invio messaggio
                email_send = 'gobbo.progetto.sistemi@gmail.com'
                subject = 'Codice di verifica ALESSANDRO GOBBO'
                password_app = 'rrin kfau fdai tqyh'
                verify_number = randrange(100000, 999999)  # Codice a 6 cifre
                
                st.session_state.verify_number = verify_number
                message = f"""
                Il tuo codice di verifica è: {verify_number}
                Inserisci questo codice per completare il processo di recupero password.
                """
                
                try:
                    msg = MIMEText(message)
                    msg['From'] = email_send
                    msg['To'] = email_recovery
                    msg['Subject'] = subject

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email_send, password_app)
                    server.sendmail(email_send, email_recovery, msg.as_string())
                    server.quit()
                    st.success("Email inviata con successo!")
                except Exception as e:
                    st.error(f"Errore invio della mail : {e}")
            else:
                st.error("Email non trovata")
            
        # Verifica del codice e reset password
        if st.session_state.check_user:
            st.title('Prosegui con verifica dell\'utente')
            code_recovery = st.number_input('Inserisci il numero', min_value=0)
            st.session_state.code_recovery = code_recovery
            

            # Verifica del codice
            verify_code = st.button('Verifica Codice')
            if verify_code and st.session_state.code_recovery == st.session_state.verify_number:
                st.session_state.code_verified = True
                st.success('Codice verificato con successo!')
            elif verify_code:
                st.error('Codice non valido')

            # Cambio della password
            if st.session_state.code_verified:
                new_password = st.text_input('Inserisci la nuova password', type='password')
                ver_password = st.text_input('Inserisci nuovamente la password', type='password')
                
                submit_password = st.button('Cambia Password')
                if submit_password:
                    if new_password == ver_password:
                        if change_password(email_recovery, new_password):
                            st.success('Cambiamento eseguito con successo, verrai indirizzato al login')
                            # Reset degli stati dopo il cambio password
                            st.session_state.check_user = False
                            st.session_state.code_verified = False
                            del st.session_state.submitted
                            st.session_state.users_list = user_list()
                            time.sleep(2)
                            st.session_state.widget_key += 1
                            st.rerun()
                    else:
                        st.error('Le password non coincidono')
        

    return False

# Esempio di utilizzo in main.py
if __name__ == "__main__":
    is_authenticated, user_email, user_type, username = authentication()
    
    if is_authenticated:
        st.write(f"Benvenuto {user_email}")
        st.write(f"Il tuo username è: {username}")
        st.write(f"Il tuo tipo utente è: {user_type}")
    
