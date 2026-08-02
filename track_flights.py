#!/usr/bin/env python3
"""
Flight Price Tracker – Wien → Rio de Janeiro
23.10.2026 – 01.11.2026
"""

from datetime import datetime
import csv
from pathlib import Path

from fast_flights import FlightQuery, Passengers, create_query, get_flights

# === Deine Suche ===
ORIGIN = "VIE"
DESTINATION = "GIG"
DEPARTURE = "2026-10-23"
RETURN = "2026-11-01"
CSV_FILE = "prices.csv"

def get_cheapest():
    query = create_query(
        flights=[
            FlightQuery(date=DEPARTURE, from_airport=ORIGIN, to_airport=DESTINATION, max_stops=1),
            FlightQuery(date=RETURN, from_airport=DESTINATION, to_airport=ORIGIN, max_stops=1),
        ],
        trip="round-trip",
        seat="economy",
        passengers=Passengers(adults=1),
        currency="EUR",
        language="de",
    )

    result = get_flights(query)

    if not result or not result.flights:
        print("Keine Flüge gefunden")
        return None

    cheapest = min(result.flights, key=lambda f: f.price if f.price else 99999)

    return {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "price": cheapest.price,
        "airline": getattr(cheapest, "name", "") or getattr(cheapest, "airlines", ""),
        "stops": getattr(cheapest, "stops", ""),
        "duration": getattr(cheapest, "duration", ""),
        "details": str(cheapest)[:200],
    }

def save_price(data: dict):
    file = Path(CSV_FILE)
    write_header = not file.exists()

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "price", "airline", "stops", "duration", "details"])
        if write_header:
            writer.writeheader()
        writer.writerow(data)

    print(f"Gespeichert: {data['price']} € – {data['airline']}")

if __name__ == "__main__":
    print(f"Suche Flüge {ORIGIN} → {DESTINATION} ({DEPARTURE} – {RETURN}) ...")
    data = get_cheapest()
    if data:
        save_price(data)
    else:
        print("Kein Preis gespeichert")
