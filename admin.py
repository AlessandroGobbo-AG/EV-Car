import streamlit as st
import polars as pl
from pathlib import Path
import sqlite3


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
    )

    return number_user

def change_user_type(User_Type, Mail):
    '''
    Funzione che va a cambiarere sul database i permessi dell'utente selezionato
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
    

def admin_main():

    '''
    Funzione che crea la pagina main dell'admin
    '''

    #creaiamo un dataframe degli utenti presenti nel database
    user = database_data()

    '''
    Parte della pagina admin in cui si vedono le informazioni degli utenti presenti nel sistema.
    '''

    st.title('Informazioni sugli utenti presenti nel sistema')

    #Creazione del container in cui saranno presenti le informazioni generali sugli utenti del database
    c1 = st.container()

    col1c1, col2c1 = c1.columns(2)

    #colonna 1 DX
    col1c1.metric(label='Numero di utenti registrati', value=user.height)
    col1c1.write(user_type_number(user))

    #colonna 2 SX
    col2c1.write(user.filter(pl.col('User Type') != 'admin'))

    #-----------------------------------------------------------------------------------------------
    st.divider()

    '''
    Parte della pagina admin in cui si può cambiare il permesso di un utente del sistema.
    '''

    st.title('Modifica permessi utente')

    #Settaggio delle sessioni di stato

    #sessione stato: mail a cui cambiare permesso
    if 'user_change_permission' not in st.session_state:
        st.session_state.user_change_permission = ''

    #sessione stato: permesso scelto
    if 'permission_choice' not in st.session_state:
        st.session_state.permission_choice = ''

    
    #Creazione del container in cui sarà contenuto la parte di modifica dei permessi dell'utente
    c2 = st.container()

    col1c2 , col2c2 = c2.columns(2)

    #colonna 1 DX

    st.session_state.user_change_permission = col1c2.selectbox('Selezione username utente', 
                   options=user.filter(pl.col('User Type') != 'admin')['Email'].to_list())
    
    col1c2.write(user.filter(pl.col('Email') == st.session_state.user_change_permission)['Username'].item())

    #colonna 2 SX 
    st.session_state.permission_choice = col2c2.selectbox(f'''Seleziona nuovo permesso per {st.session_state.user_change_permission}''', 
                                                      options=user.filter(pl.col('User Type') != 'admin')['User Type'].unique().to_list())

    submit_change = c2.button('Cambia Tipo Utente')
    if submit_change:
        if change_user_type(st.session_state.permission_choice,st.session_state.user_change_permission):
            st.success('Cambiato il permesso')
            #user = database_data()
            st.rerun()

    
if __name__ == '__main__':
    admin_main()
    
