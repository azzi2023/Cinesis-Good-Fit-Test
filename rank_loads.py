"""
Part B - Rank & Match

Filters the load board against the driver profile, then ranks the eligible
loads by effective rate per mile.

effective_rate_per_mile = price / (deadhead_to_origin + loaded_miles + deadhead_home)

Usage:
    python rank_loads.py loads.csv driver_profile.json
"""

import sys
import csv
import json
import math

EARTH_RADIUS_MI = 3958.8


def haversine(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(a))


def load_rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def is_complete(row):
    """A row is only usable if every field the formula needs is present."""
    required = ["origin_lat", "origin_lon", "dest_lat", "dest_lon", "price"]
    for field in required:
        val = row.get(field, "").strip()
        if val == "" or val.upper() == "MISSING":
            return False
    return True


def passes_filters(row, profile):
    if row["trailer"] not in profile["equipment_types"]:
        return False
    if float(row["weight"]) > profile["weight_capacity_lb"]:
        return False
    return True


def rank(loads_path, profile_path):
    profile = json.load(open(profile_path))
    rows = load_rows(loads_path)

    results = []
    skipped = []

    for row in rows:
        if not is_complete(row):
            skipped.append((row["load_id"], "missing price or destination, can't compute miles"))
            continue
        if not passes_filters(row, profile):
            continue

        dh_origin = haversine(
            profile["current_lat"], profile["current_lon"],
            float(row["origin_lat"]), float(row["origin_lon"]),
        )
        loaded = haversine(
            float(row["origin_lat"]), float(row["origin_lon"]),
            float(row["dest_lat"]), float(row["dest_lon"]),
        )
        dh_home = haversine(
            float(row["dest_lat"]), float(row["dest_lon"]),
            profile["home_lat"], profile["home_lon"],
        )
        total_miles = dh_origin + loaded + dh_home
        rate = float(row["price"]) / total_miles

        if rate < profile["min_rate_per_mile"]:
            continue

        results.append((row["load_id"], round(rate, 3)))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:3], skipped


if __name__ == "__main__":
    loads_path = sys.argv[1] if len(sys.argv) > 1 else "loads.csv"
    profile_path = sys.argv[2] if len(sys.argv) > 2 else "driver_profile.json"
    top3, skipped = rank(loads_path, profile_path)

    print("Top 3 eligible loads:")
    for rank_num, (load_id, rate) in enumerate(top3, 1):
        print(f"{rank_num}. {load_id}: {rate:.3f} $/mi")

    if skipped:
        print("\nSkipped (incomplete data):")
        for load_id, reason in skipped:
            print(f"- {load_id}: {reason}")
