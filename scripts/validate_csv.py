#!/usr/bin/env python3
"""
CSV Validator for the Daily Air Quality Log dataset.

Checks the CSV at the given path (defaults to data/air_quality.csv) for:
  1.  File exists
  2.  Header is exactly date,pm25,pm10,us_aqi,location
  3.  Every data row has exactly 5 columns
  4.  Every date matches YYYY-MM-DD and is a valid calendar date
  5.  No duplicate dates
  6.  Dates are in ascending order (warning only, does not fail)
  7.  pm25, pm10, us_aqi are either empty or numeric
  8.  Numeric values are >= 0
  9.  us_aqi <= 1000 (sanity upper bound)
  10. location is non-empty for every row

Exits 0 on success, 1 on any failure.

Usage:
    python scripts/validate_csv.py [path]
    (defaults to data/air_quality.csv)
"""

import csv
import re
import sys
from datetime import datetime

EXPECTED_HEADER = ["date", "pm25", "pm10", "us_aqi", "location"]
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEFAULT_PATH = "data/air_quality.csv"
AQI_MAX = 1000  # sanity upper bound


def fail(message):
    """Print an error message to stderr and exit with code 1."""
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def is_numeric(value):
    """Return True if the string can be parsed as a float."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def validate(csv_path):
    # --- Check 1: file exists ---
    try:
        f = open(csv_path, "r", newline="")
    except FileNotFoundError:
        fail(f"File not found: {csv_path}")

    with f:
        reader = csv.reader(f)

        # --- Read header ---
        try:
            header = next(reader)
        except StopIteration:
            fail("File is empty — no header row found")

        # Skip blank lines before the header (defensive)
        while header == []:
            try:
                header = next(reader)
            except StopIteration:
                fail("File contains only blank lines — no header row found")

        # --- Check 2: header is correct ---
        if header != EXPECTED_HEADER:
            fail(
                f"Header mismatch.\n"
                f"  Expected: {','.join(EXPECTED_HEADER)}\n"
                f"  Got:      {','.join(header)}"
            )

        # --- Iterate data rows ---
        dates_seen = set()
        dates_list = []
        row_num = 0  # data row counter (1-indexed, excludes header)

        for row in reader:
            # Skip blank lines (e.g. trailing newline at end of file)
            if row == []:
                continue

            row_num += 1

            # --- Check 3: exactly 5 columns ---
            if len(row) != 5:
                fail(f"Row {row_num}: expected 5 columns, got {len(row)}: {row}")

            date_val, pm25, pm10, us_aqi, location = row

            # --- Check 4: date format and validity ---
            if not DATE_PATTERN.match(date_val):
                fail(f"Row {row_num}: date '{date_val}' is not in YYYY-MM-DD format")
            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                fail(f"Row {row_num}: '{date_val}' is not a valid calendar date")

            # --- Check 10: location is non-empty ---
            if location == "":
                fail(f"Row {row_num}: location is empty")

            # --- Check 5: no duplicate dates ---
            if date_val in dates_seen:
                fail(f"Row {row_num}: duplicate date '{date_val}'")
            dates_seen.add(date_val)
            dates_list.append(date_val)

            # --- Checks 7–9: numeric fields ---
            for col_name, col_val in [("pm25", pm25), ("pm10", pm10),
                                      ("us_aqi", us_aqi)]:
                # Empty string is the documented null representation — allowed
                if col_val == "":
                    continue

                # Check 7: must be numeric
                if not is_numeric(col_val):
                    fail(f"Row {row_num}: {col_name}='{col_val}' is not a number")

                num_val = float(col_val)

                # Check 8: must be non-negative
                if num_val < 0:
                    fail(f"Row {row_num}: {col_name}={col_val} is negative (must be >= 0)")

                # Check 9: us_aqi sanity bound
                if col_name == "us_aqi" and num_val > AQI_MAX:
                    fail(
                        f"Row {row_num}: us_aqi={col_val} exceeds "
                        f"sanity bound of {AQI_MAX}"
                    )

    # --- Check 6: dates in ascending order (warning only) ---
    for i in range(1, len(dates_list)):
        if dates_list[i] < dates_list[i - 1]:
            print(
                f"WARNING: dates are not in ascending order — "
                f"'{dates_list[i]}' comes after '{dates_list[i - 1]}'",
                file=sys.stderr,
            )
            break  # warn once

    # --- Success ---
    if row_num == 0:
        print("CSV valid: 0 data rows (header only)")
    else:
        print(f"CSV valid: {row_num} data rows")
    sys.exit(0)


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    validate(csv_path)
