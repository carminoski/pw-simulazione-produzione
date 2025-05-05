# -*- coding: utf-8 -*-
"""
Simulatore di processo produttivo per Alfa Manufacturing Srl
Project Work - Traccia 5
Autore: Carmine Russo
Matricola: 0312301777

Versione 2: Implementazione logica di Rollover (con correzione NameError)
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
    # Definiamo l'ordine di produzione fisso (potrebbe diventare flessibile in futuro)
    "production_order": ["IS", "IR", "IAP"]
}

# --- FASE 3 & 4: Funzioni di Simulazione ---

# Funzione per generare la domanda giornaliera (invariata rispetto a v1)
def generate_daily_demand(config_params):
    """Genera domanda giornaliera casuale."""
    # Dizionario per contenere la domanda del giorno
    daily_demand = {}
    # Estrae la lista dei nomi dei prodotti (es. ['IS', 'IR', 'IAP'])
    # dal dizionario di configurazione
    product_names = list(config_params["products"].keys())
    # Estrae la tupla (min, max) del range di domanda dalla configurazione
    min_demand, max_demand = config_params["demand_range"]

    # Itera (scorre) su ciascun nome di prodotto nella lista
    for product_name in product_names:
        # Per ogni prodotto, genera un numero intero casuale
        # compreso tra min_demand e max_demand (estremi inclusi)
        demand_qty = random.randint(min_demand, max_demand)
        # Aggiunge il prodotto e la sua domanda generata al dizionario daily_demand
        # Esempio: daily_demand['IS'] = 135
        daily_demand[product_name] = demand_qty

    # Restituisce il dizionario completo contenente la domanda per tutti i prodotti
    return daily_demand

# Funzione per simulare la giornata produttiva (MODIFICATA per Rollover)
def simulate_production_day(day_index, demand_of_the_day, last_produced_item,
                            remaining_from_yesterday, config_params):
    """
    Simula le operazioni di produzione per una singola giornata.
    Versione 2: Gestisce il rollover della produzione non completata.

    Args:
        day_index (int): Numero del giorno.
        demand_of_the_day (dict): Nuova domanda per oggi.
        last_produced_item (str | None): Ultimo prodotto lavorato ieri.
        remaining_from_yesterday (dict): Dizionario con quantità residue da ieri
                                         {'IS': 10, 'IAP': 5}.
        config_params (dict): Configurazione globale.

    Returns:
        tuple: Una tupla contenente:
            - daily_production_report (list): Log dettagliato dei lotti prodotti oggi.
            - final_last_produced_item (str | None): Ultimo prodotto lavorato/tentato oggi.
            - total_time_spent_today (float): Tempo totale speso oggi (setup + prod.).
            - new_remaining_production (dict): Dizionario con le quantità residue
                                                da produrre domani.
    """
    # Estrae parametri
    total_available_minutes = config_params["daily_minutes"]
    setup_time = config_params["setup_time"]
    setup_cost = config_params["setup_cost"]
    cost_per_minute = config_params["cost_per_minute_running"]
    products_config = config_params["products"]
    production_order = config_params["production_order"]

    # Inizializza stato giornaliero
    minutes_used = 0.0
    current_last_item = last_produced_item
    daily_production_report = []
    # Dizionario per le quantità che rimarranno non prodotte OGGI
    # Inizia con una COPIA del residuo di ieri. È importante usare .copy()
    # per non modificare l'originale passato da run_simulation
    new_remaining_production = remaining_from_yesterday.copy()

    # Itera sui prodotti nell'ordine stabilito
    for product_to_produce in production_order:

        # --- Calcola la quantità totale da produrre OGGI per questo prodotto ---
        # Quantità residua da ieri (presa dalla copia che modificheremo)
        rollover_quantity = new_remaining_production.get(product_to_produce, 0)
        # Nuova domanda di oggi
        new_demand_quantity = demand_of_the_day.get(product_to_produce, 0)
        # Totale da tentare di produrre oggi
        total_quantity_to_produce = rollover_quantity + new_demand_quantity

        # Se non c'è nulla da produrre per questo prodotto, passa al successivo
        if total_quantity_to_produce <= 0:
            # Assicurati che non rimanga una chiave con 0 nel residuo
            if product_to_produce in new_remaining_production:
                 del new_remaining_production[product_to_produce]
            continue

        # --- Gestione Setup ---
        current_setup_time = 0.0
        current_setup_cost = 0.0
        needs_setup = False
        if current_last_item is not None and current_last_item != product_to_produce:
            needs_setup = True
            current_setup_time = float(setup_time)
            current_setup_cost = float(setup_cost)

        # Controlla tempo per setup
        if minutes_used + current_setup_time > total_available_minutes:
            # Non c'è tempo neanche per il setup, la produzione di oggi termina.
            # Le quantità richieste (rollover + new demand) rimangono nel residuo.
            # Aggiorna il dizionario new_remaining_production con il totale da fare
            new_remaining_production[product_to_produce] = total_quantity_to_produce
            break # Esce dal ciclo prodotti

        minutes_used += current_setup_time
        total_cost_for_this_batch = current_setup_cost

        # --- Gestione Produzione ---
        minutes_available_for_production = total_available_minutes - minutes_used

        actual_produced_quantity = 0 # Inizializza a 0
        time_spent_producing = 0.0

        if minutes_available_for_production > 0:
            # Recupera dettagli prodotto
            product_details = products_config[product_to_produce]
            rate = product_details["rate_per_minute"]
            cost_piece = product_details["cost_per_piece"]
            scrap_percent = product_details["scrap_rate_percent"] / 100.0

            # Calcola quanti pezzi si possono fare nel tempo rimasto
            max_producible_in_time = math.floor(minutes_available_for_production * rate)

            # Quantità effettiva prodotta oggi per questo prodotto
            actual_produced_quantity = min(total_quantity_to_produce, max_producible_in_time)

            if actual_produced_quantity > 0:
                # Calcola tempo e costi produzione
                time_spent_producing = actual_produced_quantity / rate
                minutes_used += time_spent_producing

                cost_material = actual_produced_quantity * cost_piece
                cost_machine_running = time_spent_producing * cost_per_minute
                total_cost_for_this_batch += (cost_material + cost_machine_running)

                # Calcola scarti
                scrap_quantity = math.floor(actual_produced_quantity * scrap_percent)
                good_quantity = actual_produced_quantity - scrap_quantity

                # Crea report per questo lotto
                batch_report = {
                    "day": day_index,
                    "product": product_to_produce,
                    # Nota: 'requested_qty_today' ora rappresenta il totale da fare oggi (rollover + new)
                    "requested_qty_today": total_quantity_to_produce,
                    "produced_qty": actual_produced_quantity,
                    "scrap_qty": scrap_quantity, "good_qty": good_quantity,
                    "time_spent_producing_min": round(time_spent_producing, 2),
                    "setup_spent_min": round(current_setup_time, 2),
                    "total_cost_eur": round(total_cost_for_this_batch, 2)
                }
                daily_production_report.append(batch_report)

        # --- Calcola il nuovo residuo per domani ---
        # Sottrae quanto prodotto oggi dal totale che doveva essere prodotto
        remaining_for_this_product = total_quantity_to_produce - actual_produced_quantity
        if remaining_for_this_product > 0:
            # Se c'è un residuo, lo salva/aggiorna nel dizionario per domani
            new_remaining_production[product_to_produce] = remaining_for_this_product
        elif product_to_produce in new_remaining_production:
            # Se abbiamo completato la produzione (residuo <= 0)
            # e il prodotto era presente nel residuo iniziale, lo rimuoviamo.
            del new_remaining_production[product_to_produce]

        # Aggiorna l'ultimo prodotto lavorato/tentato
        # Va fatto anche se abbiamo prodotto 0, per gestire correttamente il setup successivo
        current_last_item = product_to_produce

        # Se il tempo è esaurito, interrompi
        if minutes_used >= total_available_minutes - 0.01: # Tolleranza float
            break

    # Calcola tempo totale speso
    total_time_spent_today = minutes_used

    # Restituisce report, ultimo prodotto, tempo speso, e il NUOVO residuo
    return daily_production_report, current_last_item, total_time_spent_today, new_remaining_production

# Funzione per eseguire l'intera simulazione (MODIFICATA per Rollover)
def run_simulation(config_params):
    """
    Esegue la simulazione per il numero di giorni specificato, gestendo il rollover.

    Args:
        config_params (dict): Il dizionario di configurazione globale.

    Returns:
        list: Una lista contenente tutti i dizionari di report dei lotti
              prodotti durante l'intera simulazione.
    """
    num_days = config_params["simulation_days"]
    simulation_log = []
    last_produced = None
    # Stato iniziale: nessun residuo dal giorno 0
    remaining_production = {}

    print(f"\n--- Avvio Simulazione con Rollover per {num_days} giorni ---")

    for day in range(1, num_days + 1):
        # 1. Genera la NUOVA domanda per oggi
        current_demand = generate_daily_demand(config_params)

        # Salva lo stato del residuo *prima* della simulazione del giorno per la stampa
        residuo_iniziale_giorno_corrente = remaining_production.copy()

        # 2. Simula la giornata, passando il RESIDUO di ieri
        # La variabile 'remaining_production' qui contiene il residuo ALLA FINE del giorno precedente
        daily_report, new_last_produced, time_today, new_remaining = simulate_production_day(
            day_index=day,
            demand_of_the_day=current_demand,
            last_produced_item=last_produced,
            remaining_from_yesterday=remaining_production, # Passa il residuo corretto
            config_params=config_params
        )

        # 3. Accumula i risultati di oggi
        simulation_log.extend(daily_report)

        # 4. Aggiorna lo stato per il GIORNO SUCCESSIVO
        last_produced = new_last_produced
        remaining_production = new_remaining # Salva il nuovo residuo per domani

        # Stampa riepilogo giornaliero (mostra anche il residuo per domani)
        print(f"Giorno {day}: Nuova Domanda={current_demand}, "
              f"Residuo Iniziale={residuo_iniziale_giorno_corrente}, " # Usa la variabile salvata
              f"Tempo Speso={round(time_today, 1)} min, "
              f"Ultimo Prod={last_produced}, "
              f"Residuo Finale={remaining_production}") # Stampa il residuo calcolato per domani

    print(f"--- Simulazione Completata ---")
    return simulation_log

# --- Blocco di Esecuzione Principale (Aggiornato per testare v2 con Rollover) ---
if __name__ == "__main__":
    print("--- Inizio Esecuzione Script Simulatore (Fase 4.1 - Rollover) ---")

    # Task 4.3: Test con run_simulation per 5 giorni
    config["simulation_days"] = 5 # Manteniamo 5 giorni per test
    print(f"\nEsecuzione simulazione per {config['simulation_days']} giorni con rollover...")

    final_results_v2 = run_simulation(config)

    # Stampa l'output completo per verifica
    print(f"\n--- Report Completo Simulazione con Rollover ({config['simulation_days']} giorni) ---")
    if not final_results_v2:
        print("Nessun risultato prodotto dalla simulazione.")
    else:
        # Stampa intestazioni (assumendo che il primo record esista e abbia le chiavi)
        # Gestisce il caso in cui il primo report sia vuoto (improbabile ma possibile)
        if final_results_v2:
            # Trova tutte le possibili chiavi da tutti i record (più robusto)
            # headers = set().union(*(d.keys() for d in final_results_v2))
            # Oppure assume che il primo record le abbia tutte:
            headers = final_results_v2[0].keys()
            # Modificato nome colonna per chiarezza
            headers_display = [h.replace('requested_qty_today', 'req_tot_day') for h in headers]
            print(" | ".join(f"{h:<12}" for h in headers_display))
            print("-" * (len(headers_display) * 15)) # Usa headers_display per la lunghezza
            # Stampa tutti i record accumulati
            for record in final_results_v2:
                # Assicura che tutti i valori siano stringhe e allineati
                # Usiamo .get(h, 'N/A') per gestire casi in cui una chiave potrebbe mancare
                # (anche se non dovrebbe succedere con la logica attuale)
                print(" | ".join(f"{str(record.get(h, 'N/A')):<12}" for h in headers))
        else:
             print("La simulazione non ha prodotto report dettagliati.")


    print(f"\n--- Fine Esecuzione Script Simulatore (Fase 4.1) ---")

