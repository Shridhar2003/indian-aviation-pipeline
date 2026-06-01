# Indian Aviation Analytics Pipeline

An end-to-end data engineering pipeline that ingests live ADS-B flight data for India's major airports, transforms and warehouses it across GCP and Snowflake, and surfaces insights through an interactive Looker Studio dashboard.

---

## Architecture

```
OpenSky Network API (ADS-B)
        │
        ▼
Python Ingestion Script
(OAuth2 auth, 6 airports, 7-day window)
        │
        ▼
GCP Cloud Storage (Data Lake)
gs://indian-flight-pipeline-raw/
├── raw/          ← raw CSV from API
└── exports/      ← processed tables exported from BigQuery
        │
        ▼
BigQuery (Transformation Layer)
├── raw_flights         ← base table (15,741 records)
├── route_summary       ← aggregated by origin/destination (378 routes)
├── airport_daily_traffic ← daily movements per airport
└── flight_features     ← feature-engineered table for ML readiness
        │
        ▼
Snowflake (Serving Layer)
INDIAN_FLIGHTS.ANALYTICS
├── ROUTE_SUMMARY
├── AIRPORT_DAILY_TRAFFIC
└── FLIGHT_FEATURES
        │
        ▼
Data Studio Dashboard (3 pages)
```

---

## Dashboard

**Page 1 — Airport Traffic**
- Daily flight movements over time by airport
- Total movements by airport (bar chart)

**Page 2 — Route Analysis**
- Top 378 routes ranked by flight frequency
- Origin airport traffic volume

**Page 3 — Flight Features**
- Domestic vs International split (donut chart)
- Flight count by duration category
- Flights by departure hour (line chart)

> Dashboard built on Snowflake data connected via Data Studio's partner connector.


<img width="1653" height="580" alt="image" src="https://github.com/user-attachments/assets/df006ccb-c3d9-4483-9840-b6d5d204792d" />


<img width="1650" height="541" alt="image" src="https://github.com/user-attachments/assets/6b1dcadb-f456-4f74-8ab8-9a5907a922f8" />


<img width="1655" height="658" alt="image" src="https://github.com/user-attachments/assets/4ca6d203-bf16-44ea-adfd-9e1c9a964b35" />


**[Live Dashboard](https://datastudio.google.com/reporting/ac64b087-7560-4a01-9d44-6869dd18539f)**

---

## Project Structure

```
indian-aviation-pipeline/
├── data/
│   └── indian_flights_raw.csv       # Raw ingested data (gitignored)
├── ingestion/
│   └── fetch_opensky.py             # OpenSky API ingestion script
├── upload/
│   └── upload_to_gcs.py             # GCS upload script
├── bigquery_transforms.sql          # BigQuery SQL transforms
├── .env.example                     # Environment variable template
├──snowflake_setup.sql               #Snowflake setup and loading
└── README.md
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data Source | OpenSky Network REST API (ADS-B) |
| Ingestion | Python, Requests, Pandas |
| Data Lake | GCP Cloud Storage |
| Transformation | BigQuery (SQL) |
| Serving Layer | Snowflake |
| Visualisation | Looker Studio |
| Auth | OAuth2 (OpenSky), Application Default Credentials (GCP), HMAC keys (Snowflake→GCS) |

---

## Setup & Usage

### Prerequisites
- Python 3.10+
- GCP account with BigQuery and Cloud Storage enabled
- OpenSky Network account with API client credentials
- Snowflake account (free trial works)

### 1. Clone the repo
```bash
git clone https://github.com/Shridhar2003/indian-aviation-pipeline.git
cd indian-aviation-pipeline
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
pip install requests pandas google-cloud-storage google-cloud-bigquery pyarrow python-dotenv
```

### 3. Configure environment variables
```bash
copy .env.example .env
```
Edit `.env` with your credentials:
```
OPENSKY_CLIENT_ID=your_client_id
OPENSKY_CLIENT_SECRET=your_client_secret
```

### 4. Authenticate with GCP
```bash
gcloud auth application-default login
gcloud config set project your-project-id
```

### 5. Run ingestion
```bash
python ingestion/fetch_opensky.py
```
Fetches 7 days of arrivals and departures across 6 Indian airports (~15,000+ records).

### 6. Upload to GCS
```bash
python upload/upload_to_gcs.py
```

### 7. Run BigQuery transforms
Run the SQL in `transforms/bigquery_transforms.sql` in the BigQuery console in order:
1. Load raw table from GCS
2. Create `route_summary`
3. Create `airport_daily_traffic`
4. Create `flight_features`

### 8. Load into Snowflake
- Export BigQuery tables to GCS using the EXPORT DATA statements in the transforms file
- Create a GCS external stage in Snowflake using HMAC keys
- Run COPY INTO statements to load all 3 tables

---

## Airports Covered

| ICAO | Airport |
|---|---|
| VIDP | Indira Gandhi International, Delhi |
| VABB | Chhatrapati Shivaji Maharaj International, Mumbai |
| VOBL | Kempegowda International, Bengaluru |
| VOMM | Chennai International |
| VECC | Netaji Subhas Chandra Bose International, Kolkata |
| VOHB | Rajiv Gandhi International, Hyderabad |

---

## Key Findings

- **Delhi IGI** handles ~1,400 flight movements per day — the busiest airport in the dataset by a significant margin
- **VIDP→VABB** (Delhi→Mumbai) is the busiest route with 867 flights over 7 days
- **56.6% of flights are international**, 43.4% domestic across these 6 hub airports
- **Medium haul (1–2.5 hrs)** is the most common flight duration category
- Peak departure activity occurs between **06:00–18:00 UTC**

---

## Data Limitations

- OpenSky Network provides ADS-B data, not commercial schedule data — **delay information is not available directly**
- Kolkata (VECC), Chennai (VOMM), and Hyderabad (VOHB) are underrepresented in visualisations due to sparse ADS-B receiver coverage in those regions, resulting in high null rates for departure/arrival airport fields after cleaning. Delhi, Mumbai, and Bengaluru have significantly better sensor density.
- Data reflects a 7-day snapshot; extend `days_back` in `fetch_opensky.py` for longer windows
- OpenSky coverage is denser over metro airports; smaller airports may be underrepresented

---

## Requirements

```
requests
pandas
google-cloud-storage
google-cloud-bigquery
pyarrow
python-dotenv
```

---

## Author

**Shridhar Shashank Joshi**  
B.Tech Biotechnology, NSUT Delhi  
[joshi.s.shridhar@gmail.com](mailto:joshi.s.shridhar@gmail.com)

---

## License

MIT License — free to use and adapt with attribution.

---
