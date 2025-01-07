import streamlit as st
import polars as pl
from pathlib import Path

'''
Funzione che crea Main del file
'''
def sale_main():

    #Titolo della pagina
    st.markdown(f'''
                <h1 style='text-align: center; color: orange'>
                    Sezione Vendita
                </h1'''
                , unsafe_allow_html=True)
    
    st.markdown(f'''
        <div style='border:2px solid orange; padding:20px; border-radius:8px; margin-bottom:30px; font-size:16px;'>
            <p>Sezione dedicata all'aggiunta di una nuova vendita di un auto BEV o PHEV nello stato di Washington.</p>   
            <p>L'inserimento avverrà un campo alla volta. Per gli inserimenti di campi di testi, l'ordine sarà ordine <b>alfabetico</b>.</p> 
            <p>Mentre per i campi numerici ci saranno dei <b>controlli</b>, ad esempio nell'autonomia e nella localizzazione della vendita.</p>
        </div>
        ''', unsafe_allow_html=True
    )

    st.markdown(f'''
                <h3 style='text-align: center;'>
                    Dati della vendita
                </h3'''
                , unsafe_allow_html=True)
    
    c1 = st.container(border=True)

    c1.write('Nuova vendita')

if __name__ == '__main__':
    print('Hello world')