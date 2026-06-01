from google.cloud import storage
import os

BUCKET_NAME = "indian-flight-pipeline-raw"
LOCAL_FILE = "data/indian_flights_raw.csv"

def upload():
    client = storage.Client(project="flight-pipeline-498106")

    # Create bucket
    try:
        bucket = client.create_bucket(BUCKET_NAME, location="asia-south1")
        print(f"Created bucket: {BUCKET_NAME}")
    except Exception:
        bucket = client.bucket(BUCKET_NAME)
        print(f"Using existing bucket: {BUCKET_NAME}")

    blob = bucket.blob("raw/indian_flights_raw.csv")
    blob.upload_from_filename(LOCAL_FILE)
    print(f"Uploaded to gs://{BUCKET_NAME}/raw/indian_flights_raw.csv")

if __name__ == "__main__":
    upload()