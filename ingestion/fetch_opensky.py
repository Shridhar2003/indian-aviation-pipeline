import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("OPENSKY_CLIENT_ID")
CLIENT_SECRET = os.getenv("OPENSKY_CLIENT_SECRET")

INDIAN_AIRPORTS = {
    "VIDP": "Delhi IGI",
    "VABB": "Mumbai Chhatrapati Shivaji",
    "VOBL": "Bengaluru Kempegowda",
    "VOMM": "Chennai",
    "VECC": "Kolkata Netaji Subhas",
    "VOHB": "Hyderabad Rajiv Gandhi",
}

def get_access_token():
    response = requests.post(
        "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

def fetch_flights(airport_icao, begin_ts, end_ts, token, flight_type="arrival"):
    url = f"https://opensky-network.org/api/flights/{flight_type}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"airport": airport_icao, "begin": begin_ts, "end": end_ts}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 404:
        return []
    response.raise_for_status()
    return response.json()

def collect_flights(days_back=7):
    token = get_access_token()
    all_flights = []
    now = datetime.utcnow()

    for airport_icao, airport_name in INDIAN_AIRPORTS.items():
        print(f"\nFetching {airport_name} ({airport_icao})...")
        for day_offset in range(days_back):
            end_dt = now - timedelta(days=day_offset + 1)
            begin_dt = end_dt - timedelta(days=1)
            begin_ts = int(begin_dt.timestamp())
            end_ts = int(end_dt.timestamp())

            try:
                for flight_type in ["arrival", "departure"]:
                    flights = fetch_flights(airport_icao, begin_ts, end_ts, token, flight_type)
                    for f in flights:
                        f["airport_icao"] = airport_icao
                        f["airport_name"] = airport_name
                        f["flight_type"] = flight_type
                    all_flights.extend(flights)
                    print(f"  {begin_dt.date()} {flight_type}: {len(flights)} flights")
                time.sleep(1)
            except Exception as e:
                print(f"  Error: {e}")
                token = get_access_token()
                continue

    return all_flights

def process_and_save(flights):
    df = pd.DataFrame(flights)
    df["firstSeen_dt"] = pd.to_datetime(df["firstSeen"], unit="s", utc=True)
    df["lastSeen_dt"] = pd.to_datetime(df["lastSeen"], unit="s", utc=True)
    df["flight_duration_mins"] = ((df["lastSeen"] - df["firstSeen"]) / 60).round(1)
    df["callsign"] = df["callsign"].str.strip()
    df["flight_date"] = df["firstSeen_dt"].dt.date
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/indian_flights_raw.csv", index=False)
    print(f"\nSaved {len(df)} records to data/indian_flights_raw.csv")
    return df

if __name__ == "__main__":
    print("Starting OpenSky ingestion...")
    flights = collect_flights(days_back=7)
    if flights:
        df = process_and_save(flights)
        print(df.head())
    else:
        print("No flights fetched — check your credentials.")