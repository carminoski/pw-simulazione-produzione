# -*- coding: utf-8 -*-
"""
Simulatore di processo produttivo per Alfa Manufacturing Srl
Project Work - Traccia 5
Autore: Carmine Russo
Matricola: 0312301777

Versione 2: Implementazione logica di Rollover (con commenti migliorati)
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
    "simulation_days": 30,            # Numero di giorni da simulare (MODIFICARE PER TEST)
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
    # Definiamo l'ordine di produzione fisso (potrebbe diventare flessibile in futuro)
    "production_order": ["IS", "IR", "IAP"]
}

# --- FASE 3 & 4: Funzioni di Simulazione ---

# Funzione per generare la domanda giornaliera (invariata rispetto a v1)
def generate_daily_demand(config_params):
    """Genera domanda giornaliera casuale."""
    daily_demand = {}
    product_names = list(config_params["products"].keys())
    min_demand, max_demand = config_params["demand_range"]
    for product_name in product_names:
        demand_qty = random.randint(min_demand, max_demand)
        daily_demand[product_name] = demand_qty
    return daily_demand

# Funzione per simulare la giornata produttiva (MODIFICATA per Rollover)
def simulate_production_day(day_index, demand_of_the_day, last_produced_item,
                            remaining_from_yesterday, config_params):
    """
    Simula le operazioni di produzione per una singola giornata (day_index).
    Gestisce il rollover: le quantità non prodotte il giorno precedente
    (remaining_from_yesterday) vengono sommate alla nuova domanda del giorno
    (demand_of_the_day) per determinare il carico di lavoro totale.

    Args:
        day_index (int): Numero del giorno.
        demand_of_the_day (dict): Nuova domanda per oggi {'IS': qty, ...}.
        last_produced_item (str | None): Ultimo prodotto lavorato ieri.
        remaining_from_yesterday (dict): Quantità residue da ieri {'IS': qty, ...}.
        config_params (dict): Configurazione globale.

    Returns:
        tuple: (daily_production_report, final_last_produced_item,
                total_time_spent_today, new_remaining_production)
               - daily_production_report (list): Log dettagliato dei lotti prodotti oggi.
               - final_last_produced_item (str | None): Ultimo prodotto lavorato/tentato.
               - total_time_spent_today (float): Tempo totale speso oggi (setup + prod.).
               - new_remaining_production (dict): Quantità residue per domani.
    """
    # Estrazione parametri dalla configurazione per leggibilità
    total_available_minutes = config_params["daily_minutes"]
    setup_time = config_params["setup_time"]
    setup_cost = config_params["setup_cost"]
    cost_per_minute = config_params["cost_per_minute_running"]
    products_config = config_params["products"]
    production_order = config_params["production_order"]

    # Inizializzazione variabili giornaliere
    minutes_used = 0.0
    current_last_item = last_produced_item # Mantiene traccia dell'ultimo prodotto per i setup
    daily_production_report = [] # Log delle produzioni odierne
    # new_remaining_production conterrà le quantità non prodotte oggi,
    # che diventeranno il rollover per domani. Inizia come COPIA del residuo di ieri.
    new_remaining_production = remaining_from_yesterday.copy()

    # Ciclo sui prodotti secondo l'ordine definito
    for product_to_produce in production_order:

        # Calcola il carico totale per questo prodotto oggi:
        # quantità residua da ieri + nuova domanda di oggi
        rollover_quantity = new_remaining_production.get(product_to_produce, 0)
        new_demand_quantity = demand_of_the_day.get(product_to_produce, 0)
        total_quantity_to_produce = rollover_quantity + new_demand_quantity

        # Se non c'è nulla da produrre (né residuo né nuova domanda), salta al prossimo
        if total_quantity_to_produce <= 0:
            # Rimuove la chiave dal dizionario dei residui se presente (per pulizia)
            if product_to_produce in new_remaining_production:
                 del new_remaining_production[product_to_produce]
            continue # Vai al prossimo prodotto nel ciclo for

        # Verifica se è necessario un setup
        current_setup_time = 0.0
        current_setup_cost = 0.0
        needs_setup = False
        if current_last_item is not None and current_last_item != product_to_produce:
            needs_setup = True
            current_setup_time = float(setup_time)
            current_setup_cost = float(setup_cost)

        # Controlla se c'è tempo sufficiente anche solo per il setup
        if minutes_used + current_setup_time > total_available_minutes:
            # Se non c'è tempo, il carico totale (rollover + new demand)
            # diventa interamente residuo per domani.
            new_remaining_production[product_to_produce] = total_quantity_to_produce
            # Interrompe la produzione per oggi
            break

        # Esegue il setup (se necessario)
        minutes_used += current_setup_time
        total_cost_for_this_batch = current_setup_cost # Costo iniziale del lotto = costo setup

        # Calcola tempo rimanente per la produzione effettiva
        minutes_available_for_production = total_available_minutes - minutes_used

        # Quantità effettivamente prodotta oggi per questo prodotto
        actual_produced_quantity = 0
        time_spent_producing = 0.0

        # Procede solo se c'è tempo disponibile dopo il setup
        if minutes_available_for_production > 0:
            product_details = products_config[product_to_produce]
            rate = product_details["rate_per_minute"]

            # Calcola quanti pezzi può fare al massimo nel tempo rimasto
            max_producible_in_time = math.floor(minutes_available_for_production * rate)
            # Produce il minimo tra il carico totale e quanto fattibile nel tempo
            actual_produced_quantity = min(total_quantity_to_produce, max_producible_in_time)

            if actual_produced_quantity > 0:
                # Calcola tempo e costi della produzione
                time_spent_producing = actual_produced_quantity / rate
                minutes_used += time_spent_producing

                cost_piece = product_details["cost_per_piece"]
                cost_material = actual_produced_quantity * cost_piece
                cost_machine_running = time_spent_producing * cost_per_minute
                total_cost_for_this_batch += (cost_material + cost_machine_running)

                # Calcola scarti
                scrap_percent = product_details["scrap_rate_percent"] / 100.0
                scrap_quantity = math.floor(actual_produced_quantity * scrap_percent)
                good_quantity = actual_produced_quantity - scrap_quantity

                # Registra i dettagli della produzione di questo lotto
                batch_report = {
                    "day": day_index,
                    "product": product_to_produce,
                    "requested_qty_today": total_quantity_to_produce, # Totale da fare oggi
                    "produced_qty": actual_produced_quantity,       # Quanto fatto oggi
                    "scrap_qty": scrap_quantity,
                    "good_qty": good_quantity,
                    "time_spent_producing_min": round(time_spent_producing, 2),
                    "setup_spent_min": round(current_setup_time, 2),
                    "total_cost_eur": round(total_cost_for_this_batch, 2)
                }
                daily_production_report.append(batch_report)

        # Calcola la quantità residua per questo prodotto da passare a domani
        remaining_for_this_product = total_quantity_to_produce - actual_produced_quantity
        if remaining_for_this_product > 0:
            # Aggiorna/inserisce il residuo nel dizionario per domani
            new_remaining_production[product_to_produce] = remaining_for_this_product
        elif product_to_produce in new_remaining_production:
            # Se il residuo è 0 o negativo e la chiave esisteva, la rimuove
            del new_remaining_production[product_to_produce]

        # Aggiorna l'ultimo prodotto (anche se si è fatto solo setup o prodotto 0)
        current_last_item = product_to_produce

        # Se il tempo giornaliero è terminato, esce dal ciclo dei prodotti
        if minutes_used >= total_available_minutes - 0.01: # Tolleranza float
            break

    # Tempo totale effettivamente speso nella giornata
    total_time_spent_today = minutes_used

    # Restituisce i risultati della giornata
    return daily_production_report, current_last_item, total_time_spent_today, new_remaining_production

# Funzione per eseguire l'intera simulazione (gestisce lo stato tra i giorni)
def run_simulation(config_params):
    """Esegue la simulazione per n giorni, gestendo il rollover."""
    num_days = config_params["simulation_days"]
    simulation_log = [] # Log completo di tutti i lotti di tutti i giorni
    last_produced = None # Stato iniziale: nessun prodotto lavorato prima del giorno 1
    remaining_production = {} # Stato iniziale: nessun residuo prima del giorno 1

    print(f"\n--- Avvio Simulazione con Rollover per {num_days} giorni ---")

    # Ciclo su ogni giorno della simulazione
    for day in range(1, num_days + 1):
        # Genera la nuova domanda specifica per questo giorno
        current_demand = generate_daily_demand(config_params)

        # Salva il residuo attuale (da ieri) per la stampa di log
        residuo_iniziale_giorno_corrente = remaining_production.copy()

        # Esegue la simulazione della giornata
        daily_report, new_last_produced, time_today, new_remaining = simulate_production_day(
            day_index=day,
            demand_of_the_day=current_demand,
            last_produced_item=last_produced,
            remaining_from_yesterday=remaining_production, # Passa il residuo di ieri
            config_params=config_params
        )

        # Aggiunge i risultati di oggi al log generale
        simulation_log.extend(daily_report)

        # Aggiorna lo stato per il giorno successivo
        last_produced = new_last_produced # Aggiorna l'ultimo prodotto
        remaining_production = new_remaining # Aggiorna il residuo per domani

        # Stampa un riepilogo della giornata (utile per debug e comprensione)
        print(f"Giorno {day}: Nuova Domanda={current_demand}, "
              f"Residuo Iniziale={residuo_iniziale_giorno_corrente}, "
              f"Tempo Speso={round(time_today, 1)} min, "
              f"Ultimo Prod={last_produced}, "
              f"Residuo Finale={remaining_production}")

    print(f"--- Simulazione Completata ---")
    # Restituisce il log completo
    return simulation_log

# --- Blocco di Esecuzione Principale ---
if __name__ == "__main__":
    print("--- Inizio Esecuzione Script Simulatore (Fase 4) ---")

    # Imposta il numero di giorni per il test finale della FASE 4
    # Potresti voler aumentare questo valore per i test più lunghi
    config["simulation_days"] = 30 # Esempio: test su 10 giorni
    print(f"\nEsecuzione simulazione per {config['simulation_days']} giorni con rollover...")

    # Esegui la simulazione completa
    final_results = run_simulation(config)

    # Stampa l'output completo per verifica finale
    print(f"\n--- Report Completo Simulazione con Rollover ({config['simulation_days']} giorni) ---")
    if not final_results:
        print("Nessun risultato prodotto dalla simulazione.")
    else:
        # Stampa intestazioni in modo robusto
        if final_results:
            headers = final_results[0].keys()
            headers_display = [h.replace('requested_qty_today', 'req_tot_day') for h in headers]
            print(" | ".join(f"{h:<12}" for h in headers_display))
            print("-" * (len(headers_display) * 15))
            # Stampa tutti i record
            for record in final_results:
                print(" | ".join(f"{str(record.get(h, '')):<12}" for h in headers)) # Usato get per sicurezza
        else:
             print("La simulazione non ha prodotto report dettagliati.")

    print(f"\n--- Fine Esecuzione Script Simulatore (Fase 4) ---")

