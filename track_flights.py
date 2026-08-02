#!/usr/bin/env python3
"""
Flight Price Tracker – Wien → Rio de Janeiro
Komplexe Kombinationen für 3 Personen
"""

from datetime import datetime
import csv
from pathlib import Path

from fast_flights import FlightQuery, Passengers, create_query, get_flights

# === Einstellungen ===
ORIGIN = "VIE"
DESTINATION = "GIG"
OUTBOUND = "2026-10-23"          # Freitag
CSV_FILE = "prices.csv"

# Rückflug-Optionen
RETURN_1P = ["2026-10-31", "2026-11-01"]   # 1 Person: Sa oder So
RETURN_2P = ["2026-11-02", "2026-11-03"]   # 2 Personen: Mo oder Di

CABINS = ["economy", "premium-economy", "business"]

def search_price(adults: int, return_date: str, cabin: str, label: str):
    """Eine einzelne Suche durchführen"""
    try:
        query = create_query(
            flights=[
                FlightQuery(
                    date=OUTBOUND,
                    from_airport=ORIGIN,
                    to_airport=DESTINATION,
                    max_stops=1,
                    earliest_departure_hour=19,   # ab 19:00 Uhr
                ),
                FlightQuery(
                    date=return_date,
                    from_airport=DESTINATION,
                    to_airport=ORIGIN,
                    max_stops=1,
                ),
            ],
            trip="round-trip",
            seat=cabin,
            passengers=Passengers(adults=adults),
            currency="EUR",
            language="de",
        )

        result = get_flights(query)

        if not result:
            print(f"  Keine Flüge: {label}")
            return None

        cheapest = min(result, key=lambda f: f.price if getattr(f, "price", None) else 99999)

        return {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "label": label,
            "adults": adults,
            "return_date": return_date,
            "cabin": cabin,
            "price": getattr(cheapest, "price", ""),
            "airline": str(getattr(cheapest, "airlines", "")),
            "details": str(cheapest)[:180],
        }
    except Exception as e:
        print(f"  Fehler bei {label}: {e}")
        return None

def save_price(data: dict):
    file = Path(CSV_FILE)
    write_header = not file.exists()

    fieldnames = ["timestamp", "label", "adults", "return_date", "cabin", "price", "airline", "details"]

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(data)

    print(f"Gespeichert: {data['label']} → {data['price']} € ({data['cabin']})")

if __name__ == "__main__":
    print("=== Starte erweiterte Preissuche ===")

    # 1. Person (Rückflug Sa/So)
    for ret in RETURN_1P:
        for cabin in CABINS:
            label = f"1P | Rück {ret} | {cabin}"
            print(f"Suche: {label}")
            data = search_price(adults=1, return_date=ret, cabin=cabin, label=label)
            if data:
                save_price(data)

    # 2 Personen (Rückflug Mo/Di)
    for ret in RETURN_2P:
        for cabin in CABINS:
            label = f"2P | Rück {ret} | {cabin}"
            print(f"Suche: {label}")
            data = search_price(adults=2, return_date=ret, cabin=cabin, label=label)
            if data:
                save_price(data)

    print("=== Fertig ===")
    
