
# -*- coding: utf-8 -*-
"""
Simulatore di processo produttivo per Sigma Manufacturing Srl
Project Work - Traccia 5
Autore: Carmine Russo
Matricola: 0312301777
"""

import random
# import math # Lo importeremo più avanti se servirà

# ---  Definizione Parametri di Simulazione ---
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
    }
    # Aggiungeremo altri parametri se necessario
}

# --- Struttura e Codice v1 ---

# Task 3.2: Implementazione generate_daily_demand
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
    # Inizializza un dizionario vuoto per la domanda del giorno
    daily_demand = {}
    # Estrae la lista dei nomi dei prodotti dal dizionario di configurazione
    # Usiamo .keys() per ottenere solo i nomi 'IS', 'IR', 'IAP'
    product_names = list(config_params["products"].keys())
    # Estrae la tupla (min, max) del range di domanda dalla configurazione
    min_demand, max_demand = config_params["demand_range"]

    # Itera su ciascun nome di prodotto
    for product_name in product_names:
        # Genera un numero intero casuale compreso tra min_demand e max_demand (inclusi)
        demand_qty = random.randint(min_demand, max_demand)
        # Aggiunge il prodotto e la sua domanda generata al dizionario daily_demand
        daily_demand[product_name] = demand_qty

    # Restituisce il dizionario contenente la domanda per tutti i prodotti
    return daily_demand

# --- Blocco di Esecuzione Principale (per test iniziale) ---
# Questo blocco viene eseguito solo se lo script è lanciato direttamente
# (es. `python simulatore_produzione.py`) e non quando viene importato.
if __name__ == "__main__":

    print("--- Inizio Test Script Simulatore ---")

    # Test della funzione generate_daily_demand
    print("\n--- Test Funzione: generate_daily_demand ---")
    # Chiamiamo la funzione passando il nostro dizionario 'config'
    domanda_generata = generate_daily_demand(config)
    # Stampiamo il risultato per verifica
    print(f"Domanda giornaliera generata casualmente: {domanda_generata}")

    # Stampiamo anche alcuni parametri di configurazione per assicurarci
    # che il dizionario 'config' sia stato definito correttamente
    print("\n--- Verifica Parametri di Configurazione ---")
    print(f"Numero giorni simulazione: {config.get('simulation_days', 'N/D')}")
    print(f"Minuti lavorativi giornalieri: {config.get('daily_minutes', 'N/D')}")
    print(f"Prodotti definiti: {list(config.get('products', {}).keys())}")
    # Esempio di accesso a un parametro specifico di un prodotto
    if 'IS' in config.get('products', {}):
         print(f"Tasso produzione IS (pezzi/min): {config['products']['IS'].get('rate_per_minute', 'N/D')}")

    print("\n--- Fine Test Script Simulatore ---")

