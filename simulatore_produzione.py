# -*- coding: utf-8 -*-
"""
Simulatore di processo produttivo per Alfa Manufacturing Srl
Project Work - Traccia 5
Autore: Carmine Russo
Matricola: 0312301777

Versione 3: Aggiunta output CSV e finalizzazione codice simulazione.
"""

import random
import math
import csv  # Importa la libreria per gestire i file CSV
import os   # Importa la libreria per interagire col sistema operativo (per il percorso file)

# --- FASE 2: Definizione Parametri di Simulazione ---
# Dizionario contenente tutti i parametri configurabili della simulazione
config = {
    "daily_minutes": 480,            # Minuti lavorativi in una giornata (8 ore)
    "setup_time": 30,                # Minuti necessari per il setup cambio prodotto
    "setup_cost": 15.0,              # Costo fisso per ogni setup (€)
    "cost_per_minute_running": 0.10, # Costo operativo macchina (€/minuto)
    "demand_range": (50, 150),       # Range (min, max) per la domanda giornaliera casuale
    "simulation_days": 30,           # Numero di giorni da simulare (ORA IMPOSTATO AL VALORE FINALE)
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
    # Definiamo l'ordine di produzione fisso
    "production_order": ["IS", "IR", "IAP"]
}

# --- FASE 3 & 4: Funzioni di Simulazione ---

# Funzione per generare la domanda giornaliera (invariata)
def generate_daily_demand(config_params):
    """Genera domanda giornaliera casuale."""
    daily_demand = {}
    product_names = list(config_params["products"].keys())
    min_demand, max_demand = config_params["demand_range"]
    for product_name in product_names:
        demand_qty = random.randint(min_demand, max_demand)
        daily_demand[product_name] = demand_qty
    return daily_demand

# Funzione per simulare la giornata produttiva con rollover (invariata)
def simulate_production_day(day_index, demand_of_the_day, last_produced_item,
                            remaining_from_yesterday, config_params):
    """
    Simula le operazioni di produzione per una singola giornata (day_index),
    gestendo il rollover. (Logica invariata rispetto alla v2)
    """
    total_available_minutes = config_params["daily_minutes"]
    setup_time = config_params["setup_time"]
    setup_cost = config_params["setup_cost"]
    cost_per_minute = config_params["cost_per_minute_running"]
    products_config = config_params["products"]
    production_order = config_params["production_order"]

    minutes_used = 0.0
    current_last_item = last_produced_item
    daily_production_report = []
    new_remaining_production = remaining_from_yesterday.copy()

    for product_to_produce in production_order:
        rollover_quantity = new_remaining_production.get(product_to_produce, 0)
        new_demand_quantity = demand_of_the_day.get(product_to_produce, 0)
        total_quantity_to_produce = rollover_quantity + new_demand_quantity

        if total_quantity_to_produce <= 0:
            if product_to_produce in new_remaining_production:
                 del new_remaining_production[product_to_produce]
            continue

        current_setup_time = 0.0
        current_setup_cost = 0.0
        needs_setup = False
        if current_last_item is not None and current_last_item != product_to_produce:
            needs_setup = True
            current_setup_time = float(setup_time)
            current_setup_cost = float(setup_cost)

        if minutes_used + current_setup_time > total_available_minutes:
            new_remaining_production[product_to_produce] = total_quantity_to_produce
            break

        minutes_used += current_setup_time
        total_cost_for_this_batch = current_setup_cost

        minutes_available_for_production = total_available_minutes - minutes_used
        actual_produced_quantity = 0
        time_spent_producing = 0.0

        if minutes_available_for_production > 0:
            product_details = products_config[product_to_produce]
            rate = product_details["rate_per_minute"]
            max_producible_in_time = math.floor(minutes_available_for_production * rate)
            actual_produced_quantity = min(total_quantity_to_produce, max_producible_in_time)

            if actual_produced_quantity > 0:
                time_spent_producing = actual_produced_quantity / rate
                minutes_used += time_spent_producing

                cost_piece = product_details["cost_per_piece"]
                cost_material = actual_produced_quantity * cost_piece
                cost_machine_running = time_spent_producing * cost_per_minute
                total_cost_for_this_batch += (cost_material + cost_machine_running)

                scrap_percent = product_details["scrap_rate_percent"] / 100.0
                scrap_quantity = math.floor(actual_produced_quantity * scrap_percent)
                good_quantity = actual_produced_quantity - scrap_quantity

                batch_report = {
                    "day": day_index,
                    "product": product_to_produce,
                    "requested_qty_today": total_quantity_to_produce,
                    "produced_qty": actual_produced_quantity,
                    "scrap_qty": scrap_quantity, "good_qty": good_quantity,
                    "time_spent_producing_min": round(time_spent_producing, 2),
                    "setup_spent_min": round(current_setup_time, 2),
                    "total_cost_eur": round(total_cost_for_this_batch, 2)
                }
                daily_production_report.append(batch_report)

        remaining_for_this_product = total_quantity_to_produce - actual_produced_quantity
        if remaining_for_this_product > 0:
            new_remaining_production[product_to_produce] = remaining_for_this_product
        elif product_to_produce in new_remaining_production:
            del new_remaining_production[product_to_produce]

        current_last_item = product_to_produce

        if minutes_used >= total_available_minutes - 0.01:
            break

    total_time_spent_today = minutes_used
    return daily_production_report, current_last_item, total_time_spent_today, new_remaining_production

# Funzione per eseguire l'intera simulazione (invariata)
def run_simulation(config_params):
    """Esegue la simulazione per n giorni, gestendo il rollover."""
    num_days = config_params["simulation_days"]
    simulation_log = []
    last_produced = None
    remaining_production = {}

    print(f"\n--- Avvio Simulazione con Rollover per {num_days} giorni ---")

    for day in range(1, num_days + 1):
        current_demand = generate_daily_demand(config_params)
        residuo_iniziale_giorno_corrente = remaining_production.copy()

        daily_report, new_last_produced, time_today, new_remaining = simulate_production_day(
            day_index=day,
            demand_of_the_day=current_demand,
            last_produced_item=last_produced,
            remaining_from_yesterday=remaining_production,
            config_params=config_params
        )

        simulation_log.extend(daily_report)
        last_produced = new_last_produced
        remaining_production = new_remaining

        # Riduciamo la verbosità della stampa giornaliera per simulazioni lunghe
        if day <= 5 or day % 10 == 0 or day == num_days : # Stampa i primi 5, poi ogni 10 e l'ultimo
             print(f"Giorno {day:>{len(str(num_days))}}: "
                   # f"Nuova Domanda={current_demand}, " # Commentato per brevità
                   f"Residuo Iniziale={residuo_iniziale_giorno_corrente if residuo_iniziale_giorno_corrente else '{}'}, "
                   f"Tempo Speso={round(time_today, 1):<5} min, "
                   f"Ultimo Prod={last_produced if last_produced else 'None':<3}, "
                   f"Residuo Finale={remaining_production if remaining_production else '{}'}")

    print(f"--- Simulazione Completata ({num_days} giorni) ---")
    return simulation_log

# --- FASE 5: Output Finale ---
# Task 5.2: Implementazione Output CSV
def save_results_to_csv(results, filename="simulazione_output.csv"):
    """
    Salva i risultati della simulazione (una lista di dizionari) in un file CSV.

    Args:
        results (list): La lista di dizionari contenente i report dei lotti.
        filename (str): Il nome del file CSV da creare.
    """
    if not results:
        print("Attenzione: Nessun risultato da salvare nel file CSV.")
        return

    # Determina il percorso completo del file nella stessa cartella dello script
    script_dir = os.path.dirname(__file__) # Directory dello script corrente
    filepath = os.path.join(script_dir, filename)

    try:
        # Estrae gli header (nomi delle colonne) dal primo dizionario nella lista
        headers = results[0].keys()

        # Apre il file CSV in modalità scrittura ('w')
        # newline='' evita righe vuote extra in Windows
        # encoding='utf-8' per supportare caratteri speciali
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Crea un oggetto DictWriter, che scrive dizionari in righe CSV
            # fieldnames=headers specifica l'ordine delle colonne
            # delimiter=';' usa il punto e virgola come separatore (comune in Italia/Excel IT)
            writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=';')

            # Scrive la riga di intestazione nel file CSV
            writer.writeheader()
            # Scrive tutte le righe di dati (i dizionari nella lista results)
            writer.writerows(results)

        print(f"\nRisultati della simulazione salvati con successo nel file: {filepath}")

    except IOError as e:
        print(f"Errore durante il salvataggio del file CSV: {e}")
    except Exception as e:
        print(f"Errore imprevisto durante il salvataggio CSV: {e}")


# --- Blocco di Esecuzione Principale ---
if __name__ == "__main__":
    print("--- Inizio Esecuzione Script Simulatore (Fase 5) ---")

    # Task 5.1: Eseguire la simulazione completa (es. 30 giorni)
    # Assicurati che config["simulation_days"] sia impostato al valore desiderato
    config["simulation_days"] = 30 # O 60, o il valore scelto
    print(f"\nEsecuzione simulazione per {config['simulation_days']} giorni...")

    # Esegui l'intera simulazione
    final_results = run_simulation(config)

    # Task 5.2: Salvare i risultati in CSV
    if final_results: # Salva solo se ci sono risultati
        save_results_to_csv(final_results, filename="report_simulazione_produzione.csv")
    else:
        print("\nNessun risultato prodotto dalla simulazione, file CSV non creato.")

    # Task 5.3 (Manuale): Analizzare l'output CSV e la console per validare
    print("\n--- Analisi Output (Manuale) ---")
    print("Verificare il file 'report_simulazione_produzione.csv' generato.")
    print("Controllare la coerenza dei dati, l'accumulo/smaltimento dei residui,")
    print("e il rispetto dei limiti di tempo giornalieri.")

    print(f"\n--- Fine Esecuzione Script Simulatore (Fase 5) ---")

