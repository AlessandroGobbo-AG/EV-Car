# PROGETTO SISTEME DI ELABORAZIONE 2

Progetto Alessandro Gobbo di Sistemi di Elaborazione 2.

## ARGOMENTO DEL PROGETTO

L'argomento principale del progetto è l'analisi delle auto elettriche (BEV) e ibride plug-in (PHEV) che sono
possedute da cittadini dello stato di **WASHINGTON**.  
Questa analisi verrà accompagnati da elementi interattivi e grafici accompagnati da legende e/o spiegazioni.

*Origine dei dati*: [Electric Vehicle Population Data](https://catalog.data.gov/dataset/electric-vehicle-population-data)  
*Data download dati*: 10-12-2024  
*Data ultimo aggiornamento dei dati*: 22-11-2024

## LINGUAGGI DI PROGRAMMAZIONE USATI

Il linguaggio di programamzione usato è PYTHON, principalmente sono state usate le seguenti librerie:

- *Streamlit*: per la parte front-end
- *Polars*: manipolazione dei dati e analisi
- *Altair*: creazione di grafici

## REQUISITI DI SISTEMA E DIPENDENZE

Il progetto è stato realizzato in [Python 3.12.7](https://www.python.org/downloads/release/python-3127/) e le dipendenze sono state gestite con [uv](https://docs.astral.sh/uv/).

All'avvio dell'applicazione viene creato un ambiente virtuale in cui saranno presenti tutte le librerie usate.

## OBIETTIVO DEL PROGETTO

L'obiettivo del progetto è quello di simulare semplice gestionale in cui gli utenti, in base al loro
permesso, possono visualizzare le seguenti pagine:

- Pagina di Admin
- Pagina di Vendita
- Pagina Dashboard

Successivamente verrà spiegato come avviene l'accesso alle pagine, e quali pagine sono visualizzabili in
base al permesso.

## FASE DI ANALSI

La fase di analisi del dataset viene eseguita nel file EDA/eda_proj.ipynb ed è possibile
vedere il risultato nel file EDA/eda_proj.html.

I risultati sono stati utilizzati successivamente per la creazione delle pagine dell'applicazione.

## PAGINE DEL PROGRAMMA

In seguito verranno spiegate le funzionalità delle varie pagine, i punti deboli e i possibili miglioramenti.

### PAGINA DI LOGIN

La pagina **login.py** permette di eseguire tre operazioni principali:

- Login alle pagine personali
- Registrazione nuovo utente
- Recupero della password

#### Recupero password utente

Il recupero della password avviene tramite una verifica via mail,
un volta inserito il codice a 6 cifre è possibile procedere al cambiamento
della password.

## PAGINA DASHBOARD

La pagina **dashboard.py** contiene tutta la parte di analisi
grafica del dataset scelto, tramite elementi interattivi.  
I grafici sono tutti accompagnati da legende, spiegazioni o label che
vanno ad incrementare le informazioni che si vogliono comunicare.  

### Sezioni della Dashboard

- Sezione di analisi delle delle immatricolazioni delle auto possedute
dagli abitanti dello stato di Washington.  
In questa sezione vengono analizzati i dati dei vari produttori e modelli presenti
nel dataset.
- Sezione di analisi sull'autonomia delle auto presenti nel dataset, approffondendo
le differenze delle auto BEV da quelle PHEV.
- Sezione di analisi sui prezzi delle auto presenti nel dataset.

> **CHI PUO' VEDERE QUESTA PAGINA**  
> Questa pagina è visibile da tutti gli utenti registrati all'applicazione

## PAGINA DI VENDITA

Nella pagina **sale.py** avviene la fase di inserimento di una nuova immatricolazione
nello stato di Washington.  
Questo avviene tramite la compilazione dei vari campi.

> **CHI PUO' VEDERE QUESTA PAGINA**  
> Questa pagina è visibile dagli utenti registrati all'applicazione che hanno i permessi:  
> -*ADMIN*  
> -*VENDITORE*

## PAGINA DI ADMIN

Nella pagina **admin.py** contiene la parte di analisi degli utenti iscritti
all'applicazione, inoltre è possibile modificare i permessi ed eliminare
utenti dal database.

> **CHI PUO' VEDERE QUESTA PAGINA**  
> Questa pagina è visibile dagli utenti che hanno il permesso di *ADMIN*, solitamente è solo 1.

## AVVIO DELL'APPLICAZIONE

Passaggi necessari per l'avvio del progetto.

### 1. Clona repository

```bash
git clone https://github.com/AlessandroGobbo13/PROJECT_SE2.git
```
