# Simulatore Processo Produttivo - Project Work (Traccia 5)

Ciao! Questo è il repository per il mio Project Work del corso L-31 Informatica per le Aziende Digitali (Unipegaso).

**Autore:** Carmine Russo
**Matricola:** 0312301777
**Traccia Scelta:** Tema 1, Traccia 5 (Simulazione Python nel Settore Secondario)
**Titolo del Mio Elaborato:** Simulazione Python del Processo Produttivo di Ingranaggi per Sigma Manufacturing Srl

## Cosa Fa Questo Progetto?

In pratica, ho scritto uno script Python (`simulatore_produzione.py`) che cerca di imitare come funziona (in modo semplificato!) la produzione giornaliera in un'azienda metalmeccanica fittizia che ho chiamato Sigma Manufacturing Srl.

L'azienda produce tre tipi di ingranaggi (Standard, Rinforzato, Alta Precisione). Il simulatore prova a capire cosa succederebbe giorno per giorno considerando un po' di cose:

*   **Ordini Casuali:** Ogni giorno arriva una richiesta di pezzi (generata a caso entro un certo range).
*   **Tempo Limitato:** Si lavora per un tot di minuti al giorno (tipo 8 ore).
*   **Prodotti Diversi:** Ogni ingranaggio ha i suoi tempi per essere fatto.
*   **Cambio Prodotto (Setup):** Per passare da un tipo di ingranaggio all'altro ci vuole tempo (e costa).
*   **Scarti:** Non tutti i pezzi escono perfetti.
*   **Costi:** Ho provato a stimare i costi (materiali, macchina, setup).
*   **Lavoro Arretrato (Rollover):** Se non si finisce un ordine oggi, quello che manca passa al giorno dopo.

L'idea è usare questo simulatore per vedere dove potrebbero esserci problemi (colli di bottiglia), quanto costa produrre e magari testare cosa succede se si cambiano alcuni parametri (tipo ridurre il tempo di setup).

## Com'è Fatto il Codice

Tutto sta nel file `simulatore_produzione.py`. Ho cercato di organizzarlo in funzioni per non fare troppo caos:

*   `config`: Un dizionario all'inizio dove ho messo tutti i numeri e i parametri che si possono cambiare per fare le prove.
*   `generate_daily_demand()`: Crea la richiesta casuale di pezzi per la giornata.
*   `simulate_production_day()`: È il "motore" che simula cosa succede nelle 8 ore, tenendo conto di tutto (setup, produzione, tempo, costi, scarti, rollover).
*   `run_simulation()`: Fa partire la simulazione per tutti i giorni che decidi e mette insieme i risultati.
*   `save_results_to_csv()`: Salva tutti i dettagli in un file CSV alla fine.
*   Il blocco `if __name__ == "__main__":` è quello che fa partire tutto quando esegui lo script.

## Come Usarlo

Niente di complicato:

1.  **Python:** Devi avere Python installato (versione 3.8 o più recente). Non servono librerie particolari, vengono usate solo quelle standard.
2.  **Scarica il Codice:** Puoi clonare questo repository o scaricare direttamente il file `simulatore_produzione.py`.
    ```bash
    # Esempio clonazione
    git clone https://github.com/carminoski/pw-simulazione-produzione.git
    cd pw-simulazione-produzione
    ```
3.  **(Opzionale) Cambia i Parametri:** Se vuoi provare scenari diversi, apri `simulatore_produzione.py` e modifica i valori nel dizionario `config` (es. `simulation_days`, `demand_range`, `setup_time`...).
4.  **Esegui:** Apri il terminale nella cartella dove hai il file e lancia:
    ```bash
    python simulatore_produzione.py
    ```
5.  **Guarda i Risultati:**
    *   Il terminale ti mostrerà un riassunto veloce giorno per giorno.
    *   Alla fine, troverai un file `report_simulazione_produzione.csv` nella stessa cartella. Aprilo con Excel, Google Sheets o simili (ricorda che usa il punto e virgola ';' come separatore) per vedere tutti i dettagli.

## Cosa C'è nei CSV

Il file `report_simulazione_produzione.csv` ha una riga per ogni "lotto" lavorato (anche se parziale) in ogni giorno. Le colonne sono:

*   `day`: Il giorno della simulazione.
*   `product`: IS, IR, o IAP.
*   `requested_qty_today`: Quanti pezzi si dovevano fare (inclusi quelli rimasti da ieri).
*   `produced_qty`: Quanti pezzi sono stati fatti effettivamente.
*   `scrap_qty`: Quanti di quelli prodotti sono scarti.
*   `good_qty`: Quanti pezzi buoni (`produced_qty` - `scrap_qty`).
*   `time_spent_producing_min`: Minuti usati solo per produrre.
*   `setup_spent_min`: Minuti usati per il setup (se c'è stato).
*   `total_cost_eur`: Costo totale stimato del lotto.

---
*(Questo README fa parte della documentazione del Project Work)*
