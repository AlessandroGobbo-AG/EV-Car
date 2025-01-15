import streamlit as st
import polars as pl
from pathlib import Path
import sqlite3
import time

def database_data():
    '''
    Funzione che mi crea un dataframe con i dati degli utenti 
    presenti nei database

    RETURN
        dataframe: dataframe degli utenti presenti nel database
    '''
    db_dir = Path('DATABASE')
    db = sqlite3.connect(db_dir/'user.db')
    cursor = db.cursor()
    cursor.execute("SELECT Mail, User_Type, Name_Surname  FROM USER")
    rows = cursor.fetchall()
    
    df = pl.DataFrame(
        data = rows,
        schema=['Email', 'User Type', 'Username'],
        orient= 'row'
    )

    return df

def user_type_number(data):
    '''
    Funzione che mi ritorna un dataframe in cui vengono mostrati
    il numero di utenti per permessi (esempio sotto): 
        Venditore -> 2
        Analista -> 5
    
    PARAM
        dataframe: dataframe contenente i dati degli utenti

    RETURN
        dataframe: dataframe con numero di utenti per tipologia
    '''

    number_user = (
        data
        .filter(pl.col('User Type') != 'admin')
        .group_by(pl.col('User Type'))
        .agg(
            pl.col('User Type').count().alias('Total')
        )
        .sort(pl.col('User Type'))
    )

    return number_user

def change_user_type(User_Type, Mail):
    '''
    Funzione che va a cambiarere sul database i permessi dell'utente selezionato

    PARAM
        string: permesso che si vuole assegnare all'utente
        string: mail dell'utente che si vuole modificare

    RETURN
        boolean: True se avviene correttamente, 
                 False se viene sollevata eccezzione
    '''

    sql_update = '''UPDATE USER SET User_Type = ? WHERE Mail = ?'''
    db_dir = Path('DATABASE')
    db = sqlite3.connect(db_dir/'user.db')
    cursor = db.cursor()

    try: 
        cursor.execute(sql_update, (User_Type, Mail))
        db.commit()
    except sqlite3.Error as e:
        st.error(f"Errore nel database: {e}")
        return False
    finally:
        db.close()
    return True

def delete_user_by_email(email):
    '''
    Funziona che va ad eliminare dal database degli utenti, l'utente registrato con la mail
    passata come parametro

    PARAM
        string: mail dell'utente che si vuole modificare
    
    RETURN 
        boolean: True se viene eliminato con successo
                 False se viene sollevata eccezione
    '''

    sql_delete = '''DELETE FROM USER WHERE Mail = ?'''
    db_dir = Path('DATABASE')
    db = sqlite3.connect(db_dir/'user.db')
    cursor = db.cursor()

    try: 
        cursor.execute(sql_delete, (email,))
        db.commit()
    except sqlite3.Error as e:
        st.error(f"Errore nel database: {e}")
        return False
    finally:
        db.close()
    return True 

def admin_main():

    '''
    Funzione che crea la pagina main dell'admin
    '''

    if 'admin_key' not in st.session_state:
        st.session_state.admin_key = 0

    #creaiamo un dataframe degli utenti presenti nel database
    user = database_data()

    '''
    Parte della pagina admin in cui si vedono le informazioni degli utenti presenti nel sistema.
    '''

    st.markdown(f'''<h1 style='color: orange; text-align: center;'>
                        Informazioni sugli utenti registrati
                        </h1>  
                        ''', unsafe_allow_html=True)

    st.write('')
    #Creazione del container in cui saranno presenti le informazioni generali sugli utenti del database
    c1 = st.container()

    col1c1, col2c1 = c1.columns(2)

    #colonna 1 DX
    col1c1.markdown(f'''<h3 style='color: white'>
                        Numero Utenti Registrati
                        </h3>  
                        ''', unsafe_allow_html=True)
    col1c1.metric(label='utenti registrati', value=user.height-1)
    col1c1.divider()
    col1c1.markdown(f'''<h3 style='color: white'>
                        Tabella Permessi-Numero Utenti
                        </h3>  
                        ''', unsafe_allow_html=True)
    col1c1.markdown('''Tabella che indica quanti utenti sono registrati con i relativi permessi''')
    col1c1.write(user_type_number(user))

    #colonna 2 SX
    col2c1.markdown(f'''<h3 style='color: white'>
                        Lista degli Utenti
                        </h3>  
                        ''', unsafe_allow_html=True)
    col2c1.write(user.filter(pl.col('User Type') != 'admin'))
    

    #-----------------------------------------------------------------------------------------------
    st.divider()

    '''
    Parte della pagina admin in cui si può cambiare il permesso di un utente del sistema.
    '''

    st.markdown(f'''<h1 style='color: orange; text-align: center;'>
                        Modifica Permessi Utente
                        </h1>  
                        ''', unsafe_allow_html=True)
    st.write('')
    #Settaggio delle sessioni di stato

    #sessione stato: mail a cui cambiare permesso
    if 'user_change_permission' not in st.session_state:
        st.session_state.user_change_permission = ''

    #sessione stato: permesso scelto
    if 'permission_choice' not in st.session_state:
        st.session_state.permission_choice = ''

    
    #Creazione del container in cui sarà contenuto la parte di modifica dei permessi dell'utente
    c2 = st.container(border=True)

    col1c2 , col2c2 = c2.columns(2)

    #colonna 1 DX

    col1c2.markdown(f'''<h3 style='color: white'>
                        Seleziona utente da modificare
                        </h3>  
                        ''', unsafe_allow_html=True)

    st.session_state.user_change_permission = col1c2.selectbox('Selezione E-mail utente', 
                   options=user.filter(pl.col('User Type') != 'admin')['Email'].to_list())
    
    col1c2.markdown(f'''<h3 style='color: white'>
                        Verifica  Username 
                        </h3>  
                        ''', unsafe_allow_html=True)
    col1c2.write(f'''Email: {user.filter(pl.col('Email') == st.session_state.user_change_permission)['Username'].item()}''')

    #colonna 2 SX 
    col2c2.markdown(f'''<h3 style='color: white'>
                        Nuovo permesso da assegnare
                        </h3>  
                        ''', unsafe_allow_html=True)
    st.session_state.permission_choice = col2c2.selectbox(f'''Seleziona nuovo permesso per {st.session_state.user_change_permission}''', 
                                                      options=['Analista', 'Venditore'])

    col2c2.write('')
    col2c2.write('')
    col2c2.write('')
    col2c2.write('')

    submit_change = col2c2.button('Cambia Tipo Utente', type="primary")
    if submit_change:
        if change_user_type(st.session_state.permission_choice,st.session_state.user_change_permission):
            st.success('Cambiato il permesso')
            user = database_data()
            st.session_state.user_change_permission = ''
            st.session_state.admin_key += 1
            time.sleep(2)
            st.rerun()

    #-------------------------------------------------------------
    # Sezione cancellazione utente

    st.divider()
    st.markdown(f'''<h1 style='color: orange; text-align: center;'>
                        Elimina utente da sistema
                        </h1>  
                        ''', unsafe_allow_html=True)
    
    st.write('')

    c3 = st.container(border= True)

    c3.subheader("Seleziona Email dell'utente da eliminare dal sistema")

    if 'user_to_delete' not in st.session_state:
        st.session_state.user_to_delete = ''

    st.session_state.user_to_delete = c3.selectbox("E-mail dell'utente",
                                                   options=user.filter(pl.col('User Type') != 'admin')['Email'].to_list())
    

    col1c3, col2c3 = c3.columns([.84,.16])
    submit_delete = col2c3.button('Elimina utente', type='primary')

    if submit_delete:
        if delete_user_by_email(st.session_state.user_to_delete):
            c3.success('utente eliminato con successo')
            user = database_data()
            st.session_state.user_to_delete = ''
            st.session_state.admin_key += 1
            time.sleep(2)
            st.rerun()

if __name__ == '__main__':
    admin_main()
    
    
    