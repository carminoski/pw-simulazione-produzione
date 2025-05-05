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
    "simulation_days": 5,            # Numero di giorni da simulare (Impostato a 5 per test)
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
    L'output principale richiesto dalla traccia è il tempo di produzione complessivo,
    che corrisponde ai minuti usati totali nella giornata per setup e produzione.

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
            - total_time_spent_today (float): Il tempo totale (in minuti) speso oggi
                                               tra setup e produzione effettiva.
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
        requested_quantity = demand_of_the_day.get(product_to_produce, 0)

        # Se non c'è domanda per questo prodotto, passa al successivo
        if requested_quantity <= 0:
            # Aggiorna comunque l'ultimo item se questo era quello previsto
            # (utile se l'ultimo del giorno prima era A, e oggi A ha domanda 0,
            # il primo setup per B deve comunque considerare A come ultimo)
            # Ma solo se non abbiamo ancora iniziato a lavorare oggi (minutes_used == 0)
            # o se l'ultimo item lavorato era diverso. Questo evita di "saltare"
            # un prodotto senza aggiornare current_last_item se era già quello.
            # In realtà, la logica sotto gestisce già questo implicitamente,
            # quindi potremmo anche rimuovere questo 'if'. Per ora lo lascio per chiarezza.
            # if minutes_used == 0 or (current_last_item is not None and current_last_item != product_to_produce):
            #      pass # Non serve aggiornare qui, lo farà dopo il setup o la produzione
            continue # Passa al prossimo prodotto

        # --- Gestione del Tempo e Costo di Setup ---
        current_setup_time = 0.0
        current_setup_cost = 0.0
        needs_setup = False
        if current_last_item is not None and current_last_item != product_to_produce:
            needs_setup = True
            current_setup_time = float(setup_time)
            current_setup_cost = float(setup_cost)

        # Controlla se c'è abbastanza tempo rimasto nella giornata almeno per fare il setup
        if minutes_used + current_setup_time > total_available_minutes:
            break # Esce dal ciclo for dei prodotti

        # Se c'è tempo, scala i minuti usati per il setup
        minutes_used += current_setup_time
        total_cost_for_this_batch = current_setup_cost

        # --- Gestione della Produzione Effettiva ---
        minutes_available_for_production = total_available_minutes - minutes_used

        if minutes_available_for_production <= 0:
             current_last_item = product_to_produce # Aggiorna l'ultimo prodotto tentato
             # Aggiungiamo un report per il solo setup, se è stato fatto
             if needs_setup: # Solo se abbiamo effettivamente speso tempo/costo per il setup
                 daily_production_report.append({
                    "day": day_index, "product": product_to_produce,
                    "requested_qty": requested_quantity, "produced_qty": 0,
                    "scrap_qty": 0, "good_qty": 0,
                    "time_spent_producing_min": 0.0,
                    "setup_spent_min": round(current_setup_time, 2),
                    "total_cost_eur": round(total_cost_for_this_batch, 2)
                 })
             break # Esce dal ciclo perché non c'è tempo per produrre

        # Recupera i dettagli del prodotto
        product_details = products_config[product_to_produce]
        rate = product_details["rate_per_minute"]
        cost_piece = product_details["cost_per_piece"]
        scrap_percent = product_details["scrap_rate_percent"] / 100.0

        # Calcola quanti pezzi si possono produrre nel tempo rimanente
        max_producible_in_time = math.floor(minutes_available_for_production * rate)
        actual_produced_quantity = min(requested_quantity, max_producible_in_time)

        # Se si produce effettivamente qualcosa
        if actual_produced_quantity > 0:
            time_spent_producing = actual_produced_quantity / rate
            minutes_used += time_spent_producing

            cost_material = actual_produced_quantity * cost_piece
            cost_machine_running = time_spent_producing * cost_per_minute
            total_cost_for_this_batch += (cost_material + cost_machine_running)

            scrap_quantity = math.floor(actual_produced_quantity * scrap_percent)
            good_quantity = actual_produced_quantity - scrap_quantity

            batch_report = {
                "day": day_index, "product": product_to_produce,
                "requested_qty": requested_quantity,
                "produced_qty": actual_produced_quantity,
                "scrap_qty": scrap_quantity, "good_qty": good_quantity,
                "time_spent_producing_min": round(time_spent_producing, 2),
                "setup_spent_min": round(current_setup_time, 2),
                "total_cost_eur": round(total_cost_for_this_batch, 2)
            }
            daily_production_report.append(batch_report)
            current_last_item = product_to_produce # Aggiorna l'ultimo prodotto lavorato
        else:
             # Se non si è prodotto nulla (es. tempo finito dopo setup),
             # aggiorna comunque l'ultimo prodotto tentato
             current_last_item = product_to_produce
             # Aggiungiamo un report per il solo setup, se è stato fatto
             if needs_setup:
                 daily_production_report.append({
                    "day": day_index, "product": product_to_produce,
                    "requested_qty": requested_quantity, "produced_qty": 0,
                    "scrap_qty": 0, "good_qty": 0,
                    "time_spent_producing_min": 0.0,
                    "setup_spent_min": round(current_setup_time, 2),
                    "total_cost_eur": round(total_cost_for_this_batch, 2)
                 })

        # Se il tempo è esaurito, interrompi per oggi
        if minutes_used >= total_available_minutes - 0.01: # Tolleranza float
            break

    # Calcola il tempo totale speso oggi
    total_time_spent_today = minutes_used

    # Restituisce il report giornaliero, l'ultimo prodotto e il tempo totale
    return daily_production_report, current_last_item, total_time_spent_today

# Task 3.4: Implementazione run_simulation
def run_simulation(config_params):
    """
    Esegue la simulazione per il numero di giorni specificato nella configurazione.

    Args:
        config_params (dict): Il dizionario di configurazione globale.

    Returns:
        list: Una lista contenente tutti i dizionari di report dei lotti
              prodotti durante l'intera simulazione.
    """
    # Estrae il numero di giorni da simulare dalla configurazione
    num_days = config_params["simulation_days"]
    # Lista per accumulare tutti i report di tutti i giorni
    simulation_log = []
    # Stato iniziale: nessun prodotto lavorato il giorno prima
    last_produced = None

    print(f"\n--- Avvio Simulazione per {num_days} giorni ---")

    # Ciclo principale della simulazione per ogni giorno
    for day in range(1, num_days + 1):
        # 1. Genera la domanda per il giorno corrente
        current_demand = generate_daily_demand(config_params)

        # 2. Simula la giornata produttiva
        daily_report, last_produced, time_today = simulate_production_day(
            day_index=day,
            demand_of_the_day=current_demand,
            last_produced_item=last_produced, # Passa l'ultimo prodotto del giorno precedente
            config_params=config_params
        )

        # 3. Aggiunge i risultati della giornata al log complessivo
        # Usiamo extend per aggiungere tutti gli elementi della lista daily_report
        # alla lista simulation_log
        simulation_log.extend(daily_report)

        # Stampa un riepilogo giornaliero (opzionale, per debug)
        print(f"Giorno {day}: Domanda={current_demand}, Tempo Speso={round(time_today, 1)} min, Ultimo Prod={last_produced}")
        # Se vuoi vedere i dettagli di ogni giorno durante la simulazione, decommenta le righe sotto
        # print(f"  Report Giorno {day}:")
        # if daily_report:
        #     headers = daily_report[0].keys()
        #     print("  " + " | ".join(f"{h:<12}" for h in headers))
        #     print("  " + "-" * (len(headers) * 15))
        #     for item in daily_report:
        #         print("  " + " | ".join(f"{str(v):<12}" for v in item.values()))
        # else:
        #     print("  Nessuna produzione.")


    print(f"--- Simulazione Completata ---")
    # Restituisce il log completo della simulazione
    return simulation_log


# --- Blocco di Esecuzione Principale (Aggiornato per testare run_simulation) ---
if __name__ == "__main__":
    print("--- Inizio Esecuzione Script Simulatore (Fase 3.4) ---")

    # Task 3.5: Test con run_simulation per 5 giorni
    # Modifica temporaneamente simulation_days nella config per il test
    config["simulation_days"] = 5
    print(f"\nEsecuzione simulazione per {config['simulation_days']} giorni...")

    # Esegui l'intera simulazione
    final_results = run_simulation(config)

    # Task 3.6: Stampa l'output completo per verifica
    print(f"\n--- Report Completo Simulazione ({config['simulation_days']} giorni) ---")
    if not final_results:
        print("Nessun risultato prodotto dalla simulazione.")
    else:
        # Stampa intestazioni basate sul primo record
        headers = final_results[0].keys()
        print(" | ".join(f"{h:<12}" for h in headers))
        print("-" * (len(headers) * 15))
        # Stampa tutti i record accumulati
        for record in final_results:
            print(" | ".join(f"{str(v):<12}" for v in record.values()))

    print(f"\n--- Fine Esecuzione Script Simulatore (Fase 3.4) ---")

