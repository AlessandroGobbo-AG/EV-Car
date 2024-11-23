import streamlit as st
from login import authentication

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
        is_authenticated, email, user_type, username = authentication()
        
        if is_authenticated:
            # Aggiorna lo stato dell'utente
            st.session_state.user_state['logged_in'] = True
            st.session_state.user_state['mail'] = email
            st.session_state.user_state['user_type'] = user_type
            st.session_state.user_state['username'] = username
            st.rerun()  # Ricarica la pagina per mostrare il contenuto autenticato
    else:
        # Mostra la pagina dopo il login
        st.sidebar.title(f"Benvenuto {st.session_state.user_state['username']}")
        st.write(f"Email: {st.session_state.user_state['mail']}")
        st.write(f"Tipo utente: {st.session_state.user_state['user_type']}")

        # Pulsante logout
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

if __name__ == '__main__':
    main()