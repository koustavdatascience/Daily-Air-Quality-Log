#!/usr/bin/env python3
"""
Daily Air Quality Data Collector

Calls the free Open-Meteo Air Quality API and appends one row to
data/air_quality.csv. Designed to run once per day via GitHub Actions
or manually from the repo root.

- If today's date is already in the CSV, the script exits without changes.
- If the API fails or returns no data, the script exits with a non-zero
  code so the GitHub Actions job fails loudly (and GitHub emails the owner).
- Null/missing fields are stored as empty strings in the CSV.

Usage:
    python scripts/collect.py
(Run from the repository root directory.)
"""

import csv
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration — change these values to collect for a different location
# ---------------------------------------------------------------------------

LATITUDE = 23.87        # Chittaranjan, West Bengal
LONGITUDE = 86.87
LOCATION_NAME = "Chittaranjan"

# ---------------------------------------------------------------------------
# Internal settings (usually no need to change these)
# ---------------------------------------------------------------------------

CSV_PATH = "data/air_quality.csv"
HEADER = ["date", "pm25", "pm10", "us_aqi", "location"]
API_URL = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
    f"?latitude={LATITUDE}"
    f"&longitude={LONGITUDE}"
    "&current=pm2_5,pm10,us_aqi"
    "&timezone=UTC"
)
API_TIMEOUT = 30  # seconds before giving up on the API call


def get_today_utc():
    """Return today's date as a YYYY-MM-DD string in UTC."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def already_collected(csv_path, today):
    """Check if a row for 'today' already exists in the CSV."""
    if not os.path.exists(csv_path):
        return False
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("date") == today:
                return True
    return False


def fetch_air_quality():
    """Call the Open-Meteo API and return the parsed JSON.

    Exits with a non-zero code on any error so the job fails loudly.
    """
    try:
        with urllib.request.urlopen(API_URL, timeout=API_TIMEOUT) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
    except urllib.error.URLError as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse API response as JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # The API returns {"error": true, "reason": "..."} on bad requests
    if "error" in data:
        reason = data.get("reason", "unknown error")
        print(f"ERROR: API returned an error: {reason}", file=sys.stderr)
        sys.exit(1)

    return data


def extract_values(data):
    """Extract pm25, pm10, us_aqi from the API response.

    Returns empty string for null/missing values. Uses an explicit None
    check (not `or ""`) so that a real zero reading is preserved correctly.
    """
    current = data.get("current")
    if not current:
        print("ERROR: API response has no 'current' object", file=sys.stderr)
        sys.exit(1)

    pm25 = current.get("pm2_5")
    pm25 = "" if pm25 is None else round(pm25, 2)

    pm10 = current.get("pm10")
    pm10 = "" if pm10 is None else round(pm10, 2)

    us_aqi = current.get("us_aqi")
    us_aqi = "" if us_aqi is None else round(us_aqi)

    return pm25, pm10, us_aqi


def append_row(today, pm25, pm10, us_aqi):
    """Append one row to the CSV, creating the file with a header if needed."""
    # Make sure the data/ directory exists
    directory = os.path.dirname(CSV_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Write the header if the file is new or empty
    file_has_content = os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0

    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        if not file_has_content:
            writer.writerow(HEADER)
        writer.writerow([today, pm25, pm10, us_aqi, LOCATION_NAME])


def main():
    today = get_today_utc()

    # Step 1: skip if already collected today
    if already_collected(CSV_PATH, today):
        print(f"Already collected for {today} — skipping.")
        return

    # Step 2: fetch data from the API (exits on error)
    data = fetch_air_quality()

    # Step 3: extract values (empty string for nulls)
    pm25, pm10, us_aqi = extract_values(data)

    # Step 4: fail if all three values are null — no data to record
    if pm25 == "" and pm10 == "" and us_aqi == "":
        print("ERROR: All air quality values are null — no data to record.",
              file=sys.stderr)
        sys.exit(1)

    # Step 5: append the row to the CSV
    append_row(today, pm25, pm10, us_aqi)

    print(f"Collected: {today} pm25={pm25} pm10={pm10} us_aqi={us_aqi}")


if __name__ == "__main__":
    main()
