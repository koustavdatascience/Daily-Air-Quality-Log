# Daily Air Quality Log

![Daily Collection](https://github.com/koustavdatascience/Daily-Air-Quality-Log/actions/workflows/collect.yml/badge.svg)

An auto-updating dataset of daily air quality measurements for Chittaranjan, West Bengal, India. A GitHub Actions workflow collects one row of real data every day and commits it automatically — no manual effort, no empty commits. After enough data accumulates, a Jupyter notebook turns it into charts and written insights.

## Why this exists

I'm a student on the Data Analytics with AI & GenAI course, building a public portfolio on GitHub. I want my contribution graph to show consistent activity, but I don't want to fake it with empty commits or meaningless "checked in" lines — anyone who opens the repo can see that.

So I built a project where the daily commits are real. A scheduled job collects a small piece of real-world air quality data every day and commits it. The dataset grows on its own, and after a few weeks I can run an actual time-series analysis on it. The commit graph stays green because the repo is genuinely alive, and the repo ends up with something worth showing a recruiter.

## How it works

Every day at 12:00 noon IST (06:30 UTC), a GitHub Actions workflow runs automatically:

1. **Collect** — Calls the free Open-Meteo Air Quality API for Chittaranjan's coordinates (23.87° N, 86.87° E) and gets PM2.5, PM10, and US AQI values.
2. **Validate** — Checks the full CSV for correct columns, duplicate dates, and sane value ranges. If anything is wrong, the job fails and no bad data is committed.
3. **Commit** — Appends one row to `data/air_quality.csv` and pushes with message `data: YYYY-MM-DD`.

If the API is down or returns no data, the job fails loudly (GitHub sends an email notification). If today's date is already in the CSV, it skips — no duplicate rows.

The workflow can also be triggered manually from the Actions tab for testing.

### Key files

| File | What it does |
|------|-------------|
| `.github/workflows/collect.yml` | The GitHub Actions workflow (schedule, steps, permissions) |
| `scripts/collect.py` | Calls the API, appends one row to the CSV |
| `scripts/validate_csv.py` | Checks the CSV before the commit lands |
| `data/air_quality.csv` | The growing dataset (one row per day) |
| `notebooks/` | Will hold the analysis notebook (added after ~30 days of data) |

## Data dictionary

**File:** `data/air_quality.csv`  
**Timezone:** All dates are in UTC.  
**Cadence:** One row per day, collected at approximately 12:00 noon IST.

| Column | Type | Unit | Description | Null handling |
|--------|------|------|-------------|--------------|
| `date` | string | — | UTC date of collection (`YYYY-MM-DD`) | Never null |
| `pm25` | float | µg/m³ | Instantaneous modelled PM2.5 concentration at collection time | Empty string if null |
| `pm10` | float | µg/m³ | Instantaneous modelled PM10 concentration at collection time | Empty string if null |
| `us_aqi` | int | index | US Air Quality Index (0–500+) | Empty string if null |
| `location` | string | — | City name as configured in `scripts/collect.py` | Never null |

### US AQI categories

| Range | Category |
|-------|----------|
| 0–50 | Good |
| 51–100 | Moderate |
| 101–150 | Unhealthy for Sensitive Groups |
| 151–200 | Unhealthy |
| 201–300 | Very Unhealthy |
| 301–500+ | Hazardous |

## Data limitations

The values are **model-derived**, not from ground-level monitoring sensors. Open-Meteo serves air quality data from the Copernicus Atmosphere Monitoring Service (CAMS). For locations outside Europe (including India), the data comes from the CAMS global atmospheric composition forecast at approximately **45 km spatial resolution**.

This means:

- A single reading represents a large grid cell (~45 km), not a specific street or neighbourhood.
- Modelled concentrations may differ from local ground sensor readings.
- The values are useful for tracking broad trends over time, but should not be treated as precise point measurements.

## Setup (forking and adapting)

To run this for your own location:

1. **Fork or clone** this repository.
2. **Change the coordinates** at the top of `scripts/collect.py`:
   ```python
   LATITUDE = 23.87          # your latitude
   LONGITUDE = 86.87         # your longitude
   LOCATION_NAME = "Chittaranjan"  # your city name
   ```
3. **Enable GitHub Actions** on your fork (see the checklist below).
4. **Trigger the first run** manually from the Actions tab to verify it works.

## GitHub setup checklist

These are the steps to get the workflow running on a new repository:

1. **Enable Actions** — Go to the repo → **Actions** tab → click "I understand my workflows, go ahead and enable them."
2. **Set workflow permissions** — **Settings** → **Actions** → **General** → scroll to "Workflow permissions" → select "Read and write permissions" → **Save**. (This is in addition to the `permissions:` key in the workflow file — GitHub has a repo-level default that can override it.)
3. **Verify your commit email** — Go to **Settings** → **Emails**. Look for a noreply email in the format `{id}+{username}@users.noreply.github.com`. If it's not listed, enable **"Keep my email addresses private"** — this generates and connects your noreply email so commits count toward your contribution graph.
4. **Enable failure notifications** — Go to **Settings** → **Notifications** → **Email** → check "Actions." This ensures GitHub emails you if the daily workflow fails.
5. **First manual test** — **Actions** tab → select "Daily Air Quality Collection" → **Run workflow** → select the `main` branch → click the green **Run workflow** button. Watch the run complete (usually 30–60 seconds).
6. **Check the contribution graph** — After the first commit, wait a few minutes and check your profile. If it doesn't appear, verify the commit author email matches your noreply email in Settings → Emails.

## Latest results

_This section will be updated after 30 days of data collection with charts and written insights from the analysis notebook._

## Honesty statement

**Data collection is automated by GitHub Actions.** The analysis, charts, and written insights are by koustavdatascience. The dataset is real — each row contains actual air quality measurements from the Open-Meteo API for the given date and location.

## Data sources and attribution

- **API:** [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) — free, no API key required for non-commercial use.
- **Data provider:** Copernicus Atmosphere Monitoring Service (CAMS) — air quality forecasts based on the CAMS European and global atmospheric composition models.

## License

MIT — see [LICENSE](LICENSE).
