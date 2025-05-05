# -*- coding: utf-8 -*-
"""
Simulatore di processo produttivo per Alfa Manufacturing Srl
Project Work - Traccia 5
Autore: Carmine Russo
Matricola: 0312301777
"""

import random
import math # Potrebbe servire per arrotondamenti

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
    # Definiamo l'ordine di produzione per la v1
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
            - final_last_produced_item (str | None): L'ultimo prodotto effettivamente
                                                     lavorato in questo giorno.
    """
    # Estrae i parametri necessari dalla configurazione
    total_available_minutes = config_params["daily_minutes"]
    setup_time = config_params["setup_time"]
    setup_cost = config_params["setup_cost"]
    cost_per_minute = config_params["cost_per_minute_running"]
    products_config = config_params["products"]
    production_order = config_params["production_order"] # Ordine fisso per v1

    # Inizializza le variabili per la giornata
    minutes_used = 0
    current_last_item = last_produced_item # L'ultimo item prodotto all'inizio del giorno
    daily_production_report = [] # Lista per raccogliere i dati dei lotti prodotti

    # Itera sui prodotti secondo l'ordine definito
    for product_to_produce in production_order:
        # Controlla se c'è domanda per questo prodotto
        requested_quantity = demand_of_the_day.get(product_to_produce, 0)
        if requested_quantity <= 0:
            continue # Passa al prossimo prodotto se non c'è domanda

        # --- Gestione Setup ---
        current_setup_time = 0
        current_setup_cost = 0
        # Applica setup solo se è necessario cambiare prodotto rispetto all'ultimo lavorato
        # e se non è il primissimo prodotto lavorato in assoluto (current_last_item != None)
        if current_last_item is not None and current_last_item != product_to_produce:
            current_setup_time = setup_time
            current_setup_cost = setup_cost

        # Verifica se c'è abbastanza tempo anche solo per il setup
        if minutes_used + current_setup_time > total_available_minutes:
            # Non c'è tempo neanche per il setup, interrompi la produzione per oggi
            break # Esce dal ciclo for dei prodotti

        # Se c'è tempo per il setup, lo esegue
        minutes_used += current_setup_time
        total_day_cost_for_product = current_setup_cost # Inizia a calcolare il costo per questo lotto

        # --- Gestione Produzione ---
        # Calcola i minuti rimanenti per la produzione effettiva
        minutes_available_for_production = total_available_minutes - minutes_used
        if minutes_available_for_production <= 0:
             # Non c'è più tempo dopo il setup, interrompi
             current_last_item = product_to_produce # Aggiorna l'ultimo prodotto (anche se non ha prodotto pezzi)
             break

        # Recupera i parametri specifici del prodotto
        product_details = products_config[product_to_produce]
        rate = product_details["rate_per_minute"]
        cost_piece = product_details["cost_per_piece"]
        scrap_percent = product_details["scrap_rate_percent"] / 100.0

        # Calcola quanti pezzi si potrebbero produrre nel tempo rimanente
        max_producible_in_time = math.floor(minutes_available_for_production * rate)

        # Determina quanti pezzi produrre effettivamente: il minimo tra richiesti e producibili
        actual_produced_quantity = min(requested_quantity, max_producible_in_time)

        if actual_produced_quantity > 0:
            # Calcola il tempo effettivamente impiegato per produrre questa quantità
            time_spent_producing = actual_produced_quantity / rate

            # Aggiorna i minuti totali usati nella giornata
            minutes_used += time_spent_producing

            # Calcola i costi di produzione (materia prima + costo macchina)
            cost_material = actual_produced_quantity * cost_piece
            cost_machine_running = time_spent_producing * cost_per_minute
            total_day_cost_for_product += (cost_material + cost_machine_running)

            # Calcola gli scarti
            scrap_quantity = math.floor(actual_produced_quantity * scrap_percent)
            good_quantity = actual_produced_quantity - scrap_quantity

            # Aggiungi i dati di questo lotto al report giornaliero
            daily_production_report.append({
                "day": day_index,
                "product": product_to_produce,
                "requested_qty": requested_quantity,
                "produced_qty": actual_produced_quantity,
                "scrap_qty": scrap_quantity,
                "good_qty": good_quantity,
                "time_spent_producing_min": round(time_spent_producing, 2),
                "setup_spent_min": current_setup_time,
                "total_cost_eur": round(total_day_cost_for_product, 2)
            })

            # Aggiorna l'ultimo prodotto lavorato
            current_last_item = product_to_produce
        else:
             # Se non si produce nulla (es. tempo finito dopo setup),
             # aggiorna comunque l'ultimo prodotto tentato
             current_last_item = product_to_produce


        # Se il tempo è esaurito, esci dal ciclo dei prodotti
        if minutes_used >= total_available_minutes:
            break

    # Restituisce il report della giornata e l'ultimo prodotto lavorato
    return daily_production_report, current_last_item


# --- Blocco di Esecuzione Principale (per test iniziale) ---
if __name__ == "__main__":
    print("--- Inizio Test Script Simulatore ---")

    # Test della funzione generate_daily_demand
    print("\n--- Test Funzione: generate_daily_demand ---")
    domanda_giorno_1 = generate_daily_demand(config)
    print(f"Domanda Giorno 1: {domanda_giorno_1}")

    # Test della funzione simulate_production_day (v1)
    print("\n--- Test Funzione: simulate_production_day (v1) ---")
    # Simuliamo il giorno 1, partendo da None come ultimo prodotto
    report_giorno_1, ultimo_prodotto_giorno_1 = simulate_production_day(
        day_index=1,
        demand_of_the_day=domanda_giorno_1,
        last_produced_item=None,
        config_params=config
    )

    print(f"\n--- Report Produzione Giorno 1 ---")
    if not report_giorno_1:
        print("Nessuna produzione completata.")
    else:
        # Stampa intestazioni
        headers = report_giorno_1[0].keys()
        print(" | ".join(f"{h:<12}" for h in headers))
        print("-" * (len(headers) * 15))
        # Stampa i dati di ogni lotto prodotto
        for report_item in report_giorno_1:
            print(" | ".join(f"{str(v):<12}" for v in report_item.values()))

    print(f"\nUltimo prodotto lavorato Giorno 1: {ultimo_prodotto_giorno_1}")

    # Simuliamo il giorno 2, usando l'ultimo prodotto del giorno 1
    print("\n--- Test Funzione: simulate_production_day (v1) - Giorno 2 ---")
    domanda_giorno_2 = generate_daily_demand(config)
    print(f"Domanda Giorno 2: {domanda_giorno_2}")

    report_giorno_2, ultimo_prodotto_giorno_2 = simulate_production_day(
        day_index=2,
        demand_of_the_day=domanda_giorno_2,
        last_produced_item=ultimo_prodotto_giorno_1, # Usa l'ultimo del giorno prima
        config_params=config
    )

    print(f"\n--- Report Produzione Giorno 2 ---")
    if not report_giorno_2:
        print("Nessuna produzione completata.")
    else:
        headers = report_giorno_2[0].keys()
        print(" | ".join(f"{h:<12}" for h in headers))
        print("-" * (len(headers) * 15))
        for report_item in report_giorno_2:
            print(" | ".join(f"{str(v):<12}" for v in report_item.values()))

    print(f"\nUltimo prodotto lavorato Giorno 2: {ultimo_prodotto_giorno_2}")


    print("\n--- Fine Test Script Simulatore ---")
