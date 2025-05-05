# -*- coding: utf-8 -*-
"""
Simulatore di processo produttivo per Alfa Manufacturing Srl
Project Work - Traccia 5
Autore: Carmine Russo
Matricola: 0312301777
"""

import random
import math # Importato per usare math.floor per arrotondare per difetto

# --- FASE 2: Definizione Parametri di Simulazione ---
# Dizionario contenente tutti i parametri configurabili della simulazione
config = {
    "daily_minutes": 480,            # Minuti lavorativi in una giornata (8 ore)
    "setup_time": 30,                # Minuti necessari per il setup cambio prodotto
    "setup_cost": 15.0,              # Costo fisso per ogni setup (€)
    "cost_per_minute_running": 0.10, # Costo operativo macchina (€/minuto)
    "demand_range": (50, 150),       # Range (min, max) per la domanda giornaliera casuale
    "simulation_days": 30,           # Numero di giorni da simulare
    "products": {
        # Caratteristiche specifiche per ciascun prodotto
        "IS": { # Ingranaggio Standard
            "rate_per_minute": 0.5,  # Pezzi prodotti al minuto (1 pezzo / 2 min)
            "cost_per_piece": 1.20,  # Costo materia prima / base (€)
            "scrap_rate_percent": 3.0 # Percentuale media scarti (%)
        },
        "IR": { # Ingranaggio Rinforzato
            "rate_per_minute": 0.4,  # Pezzi prodotti al minuto (1 pezzo / 2.5 min)
            "cost_per_piece": 1.50,
            "scrap_rate_percent": 4.0
        },
        "IAP": { # Ingranaggio Alta Precisione
            "rate_per_minute": 0.3,  # Pezzi prodotti al minuto (1 pezzo / ~3.3 min)
            "cost_per_piece": 1.80,
            "scrap_rate_percent": 5.0
        }
    },
    # Definiamo l'ordine di produzione fisso per la v1
    "production_order": ["IS", "IR", "IAP"]
}

# --- FASE 3: Struttura e Codice v1 ---

# Task 3.2: Implementazione generate_daily_demand (Già fatta)
def generate_daily_demand(config_params):
    """
    Genera una domanda giornaliera casuale per ciascun prodotto definito
    nella configurazione.

    Utilizza il range di domanda specificato in config_params["demand_range"].

    Args:
        config_params (dict): Il dizionario di configurazione globale.

    Returns:
        dict: Un dizionario dove le chiavi sono i nomi dei prodotti (es. 'IS')
              e i valori sono le quantità richieste generate casualmente.
              Esempio: {'IS': 120, 'IR': 85, 'IAP': 95}
    """
    daily_demand = {}
    product_names = list(config_params["products"].keys())
    min_demand, max_demand = config_params["demand_range"]
    for product_name in product_names:
        demand_qty = random.randint(min_demand, max_demand)
        daily_demand[product_name] = demand_qty
    return daily_demand

# Task 3.3: Implementazione simulate_production_day (v1 - senza rollover)
def simulate_production_day(day_index, demand_of_the_day, last_produced_item, config_params):
    """
    Simula le operazioni di produzione per una singola giornata.
    Versione 1: senza gestione del rollover della produzione non completata.

    Args:
        day_index (int): Il numero progressivo del giorno simulato (es. 1, 2, ...).
        demand_of_the_day (dict): La domanda giornaliera per ciascun prodotto.
                                     Esempio: {'IS': 100, 'IR': 50, 'IAP': 70}
        last_produced_item (str | None): Il nome dell'ultimo prodotto lavorato
                                          il giorno precedente (None se è il primo giorno).
        config_params (dict): Il dizionario di configurazione globale.

    Returns:
        tuple: Una tupla contenente:
            - daily_production_report (list): Una lista di dizionari, uno per ogni
                                              lotto di prodotto lavorato nel giorno.
                                              Ogni dizionario contiene le metriche di produzione.
            - final_last_produced_item (str | None): L'ultimo prodotto effettivamente
                                                     lavorato o tentato in questo giorno.
    """
    # Estrae i parametri generali necessari dalla configurazione
    total_available_minutes = config_params["daily_minutes"]
    setup_time = config_params["setup_time"]
    setup_cost = config_params["setup_cost"]
    cost_per_minute = config_params["cost_per_minute_running"]
    products_config = config_params["products"]
    # Recupera l'ordine di produzione fisso dalla configurazione
    production_order = config_params["production_order"]

    # Inizializza le variabili per tracciare lo stato della giornata
    minutes_used = 0.0 # Usiamo float per precisione nei calcoli dei tempi
    current_last_item = last_produced_item # L'ultimo item prodotto all'inizio del giorno
    daily_production_report = [] # Lista per raccogliere i dati dei lotti prodotti oggi

    # Itera sui prodotti secondo l'ordine definito in config["production_order"]
    for product_to_produce in production_order:
        # Ottiene la quantità richiesta per questo prodotto dalla domanda giornaliera
        # .get() è usato per sicurezza: se il prodotto non fosse nella domanda, ritorna 0
        requested_quantity = demand_of_the_day.get(product_to_produce, 0)

        # Se non c'è domanda per questo prodotto, passa al successivo
        if requested_quantity <= 0:
            continue

        # --- Gestione del Tempo e Costo di Setup ---
        current_setup_time = 0.0
        current_setup_cost = 0.0
        # Il setup è necessario SOLO se:
        # 1. Non è il primo prodotto lavorato in assoluto (current_last_item non è None)
        # 2. Il prodotto da lavorare ora è DIVERSO dall'ultimo lavorato
        if current_last_item is not None and current_last_item != product_to_produce:
            current_setup_time = float(setup_time) # Convertiamo in float
            current_setup_cost = float(setup_cost)   # Convertiamo in float

        # Controlla se c'è abbastanza tempo rimasto nella giornata almeno per fare il setup
        if minutes_used + current_setup_time > total_available_minutes:
            # Se non c'è tempo neanche per il setup, la produzione per oggi termina qui.
            # Non si processeranno altri prodotti.
            break # Esce dal ciclo 'for product_to_produce...'

        # Se c'è tempo, scala i minuti usati per il setup
        minutes_used += current_setup_time
        # Inizia ad accumulare il costo per questo lotto (partendo dal costo di setup)
        total_cost_for_this_batch = current_setup_cost

        # --- Gestione della Produzione Effettiva ---
        # Calcola quanti minuti rimangono per produrre pezzi
        minutes_available_for_production = total_available_minutes - minutes_used

        # Se non sono rimasti minuti dopo il setup, non si può produrre.
        # Aggiorna l'ultimo prodotto (quello per cui si è fatto setup) e passa al prossimo
        # (anche se nel break uscirà subito dal ciclo).
        if minutes_available_for_production <= 0:
             # Aggiorniamo l'ultimo prodotto tentato anche se non si produce nulla
             current_last_item = product_to_produce
             break # Esce dal ciclo perché non c'è tempo per produrre

        # Recupera i dettagli (rate, costo, scarto) del prodotto specifico dalla config
        product_details = products_config[product_to_produce]
        rate = product_details["rate_per_minute"] # Pezzi/minuto
        cost_piece = product_details["cost_per_piece"] # €/pezzo
        scrap_percent = product_details["scrap_rate_percent"] / 100.0 # Es: 3.0 -> 0.03

        # Calcola quanti pezzi si potrebbero teoricamente produrre nel tempo rimasto
        # Arrotondiamo per difetto perché non si possono fare pezzi incompleti
        max_producible_in_time = math.floor(minutes_available_for_production * rate)

        # La quantità effettivamente prodotta è il minimo tra quella richiesta
        # e quella massima producibile nel tempo rimasto
        actual_produced_quantity = min(requested_quantity, max_producible_in_time)

        # Se si produce effettivamente qualcosa (quantità > 0)
        if actual_produced_quantity > 0:
            # Calcola il tempo esatto impiegato per produrre questa quantità
            # Tempo = Quantità / Tasso (es. 10 pezzi / 0.5 pezzi/min = 20 min)
            time_spent_producing = actual_produced_quantity / rate

            # Aggiorna i minuti totali usati nella giornata
            minutes_used += time_spent_producing

            # Calcola i costi di produzione aggiuntivi
            cost_material = actual_produced_quantity * cost_piece
            cost_machine_running = time_spent_producing * cost_per_minute
            # Aggiunge questi costi al costo totale del lotto (che già includeva il setup)
            total_cost_for_this_batch += (cost_material + cost_machine_running)

            # Calcola la quantità di scarti (arrotondando per difetto)
            scrap_quantity = math.floor(actual_produced_quantity * scrap_percent)
            # Calcola la quantità di pezzi buoni
            good_quantity = actual_produced_quantity - scrap_quantity

            # Crea un dizionario con i risultati per questo lotto specifico
            batch_report = {
                "day": day_index,
                "product": product_to_produce,
                "requested_qty": requested_quantity,
                "produced_qty": actual_produced_quantity,
                "scrap_qty": scrap_quantity,
                "good_qty": good_quantity,
                "time_spent_producing_min": round(time_spent_producing, 2),
                "setup_spent_min": round(current_setup_time, 2), # Arrotonda anche il setup time
                "total_cost_eur": round(total_cost_for_this_batch, 2) # Arrotonda il costo finale
            }
            # Aggiunge il report del lotto alla lista dei report giornalieri
            daily_production_report.append(batch_report)

            # Aggiorna l'ultimo prodotto effettivamente lavorato
            current_last_item = product_to_produce
        else:
            # Se actual_produced_quantity è 0 (non c'era tempo dopo il setup),
            # Aggiorna comunque l'ultimo prodotto tentato
             current_last_item = product_to_produce


        # Se abbiamo usato tutto il tempo disponibile (o più, per via degli arrotondamenti),
        # interrompiamo la produzione per oggi.
        if minutes_used >= total_available_minutes:
            break # Esce dal ciclo 'for product_to_produce...'

    # Alla fine del ciclo (o se interrotto da un break),
    # restituisce la lista dei report dei lotti prodotti e l'ultimo prodotto toccato.
    return daily_production_report, current_last_item


# --- Blocco di Esecuzione Principale (Aggiornato per testare entrambe le funzioni) ---
if __name__ == "__main__":
    print("--- Inizio Test Script Simulatore (Fase 3.3) ---")

    # 1. Genera la domanda per il Giorno 1
    print("\n--- Generazione Domanda Giorno 1 ---")
    domanda_giorno_1 = generate_daily_demand(config)
    print(f"Domanda Giorno 1: {domanda_giorno_1}")

    # 2. Simula la produzione del Giorno 1
    print("\n--- Simulazione Produzione Giorno 1 ---")
    # Il primo giorno, non c'è un "ultimo prodotto" dal giorno precedente (None)
    report_giorno_1, ultimo_prodotto_g1 = simulate_production_day(
        day_index=1,
        demand_of_the_day=domanda_giorno_1,
        last_produced_item=None, # Nessun prodotto precedente il primo giorno
        config_params=config
    )

    # 3. Stampa il report del Giorno 1
    print(f"\n--- Report Dettagliato Giorno 1 ---")
    if not report_giorno_1:
        print("Nessuna produzione registrata per il Giorno 1.")
    else:
        # Stampa intestazioni dinamiche basate sulle chiavi del primo dizionario
        headers = report_giorno_1[0].keys()
        print(" | ".join(f"{h:<12}" for h in headers)) # Allinea le intestazioni
        print("-" * (len(headers) * 15)) # Linea separatrice
        # Stampa i dati per ogni lotto prodotto nel giorno
        for report_item in report_giorno_1:
             # Allinea i valori sotto le rispettive intestazioni
            print(" | ".join(f"{str(v):<12}" for v in report_item.values()))

    print(f"\nUltimo prodotto lavorato/tentato nel Giorno 1: {ultimo_prodotto_g1}")

    # 4. Genera la domanda per il Giorno 2
    print("\n--- Generazione Domanda Giorno 2 ---")
    domanda_giorno_2 = generate_daily_demand(config)
    print(f"Domanda Giorno 2: {domanda_giorno_2}")

    # 5. Simula la produzione del Giorno 2, passando l'ultimo prodotto del Giorno 1
    print("\n--- Simulazione Produzione Giorno 2 ---")
    report_giorno_2, ultimo_prodotto_g2 = simulate_production_day(
        day_index=2,
        demand_of_the_day=domanda_giorno_2,
        last_produced_item=ultimo_prodotto_g1, # Passa l'ultimo prodotto del giorno prima!
        config_params=config
    )

    # 6. Stampa il report del Giorno 2
    print(f"\n--- Report Dettagliato Giorno 2 ---")
    if not report_giorno_2:
        print("Nessuna produzione registrata per il Giorno 2.")
    else:
        # Controlla se la lista non è vuota prima di accedere al primo elemento per le chiavi
        if report_giorno_2:
            headers = report_giorno_2[0].keys()
            print(" | ".join(f"{h:<12}" for h in headers))
            print("-" * (len(headers) * 15))
            for report_item in report_giorno_2:
                print(" | ".join(f"{str(v):<12}" for v in report_item.values()))
        else:
             # Questo caso non dovrebbe verificarsi se sopra abbiamo già controllato
             # ma lo teniamo per robustezza
             pass # Già gestito dal controllo 'if not report_giorno_2'


    print(f"\nUltimo prodotto lavorato/tentato nel Giorno 2: {ultimo_prodotto_g2}")

    print("\n--- Fine Test Script Simulatore (Fase 3.3) ---")

