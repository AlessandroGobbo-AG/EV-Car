import streamlit as st
from login import authentication

def logout():
    if st.sidebar.button('Logout'):
        # Reset completo dello stato dell'utente
        st.session_state.user_state['logged_in'] = False
        st.session_state.user_state['mail'] = ''
        st.session_state.user_state['user_type'] = ''
        st.session_state.user_state['username'] = ''
        
        # Rimuovi anche altri stati se necessario
        if 'submitted' in st.session_state:
            del st.session_state.submitted
        
        st.rerun()

def page_list(permission):
    match permission:
        case 'admin':
            page_list = ['Personale', 'Dashboard', 'Vendita']
        case 'Venditore':
            page_list = ['Dashboard', 'Vendita']
        case 'Analista': 
            page_list = ['Dashboard']

    choose = st.sidebar.selectbox(
        'Pagina da visitare',
        (page_list)
    )
    return choose

def main():
    # Inizializza lo stato di autenticazione se non esiste
    if 'user_state' not in st.session_state:
        st.session_state.user_state = {
            'mail': '',
            'username': '',
            'user_type': '',
            'logged_in': False
        }

    # Controlla se l'utente è già autenticato
    if not st.session_state.user_state['logged_in']:
        # Chiama authentication e gestisce i valori di ritorno
        is_authenticated = authentication()
        
        if is_authenticated:
            # Aggiorna lo stato dell'utente
            st.session_state.user_state['logged_in'] = True
            st.rerun()  # Ricarica la pagina per mostrare il contenuto autenticato
    
    
    if st.session_state.user_state['logged_in']:

        st.sidebar.title(f"Benvenuto {st.session_state.user_state['username']}")
        page_to_see = page_list(st.session_state.user_state['user_type'])
        
        if page_to_see == 'Vendita':
            st.write('Aggiungerai una vendita in questa pagina')
        elif page_to_see == 'Dashboard':
            st.write('Qui vedrai la dashboard')
        else: 
            st.write('Qui vedi la pagina di admin in cui puoi fare tante cose')
            
        logout()


if __name__ == '__main__':
    main()