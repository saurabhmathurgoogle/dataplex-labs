import google.auth
from google.auth.transport.requests import Request
import requests
import subprocess
import time
import sys

project = "dc-cuj-staging-playground"
location = "us-central1"

def get_token():
    creds, _ = google.auth.default()
    creds.refresh(Request())
    return creds.token

def create_entry_group(base_url, eg_id, dp_name):
    url = f"{base_url}/projects/{project}/locations/{location}/entryGroups?entryGroupId={eg_id}"
    headers = {"Authorization": f"Bearer {get_token()}", "x-goog-user-project": project, "Content-Type": "application/json"}
    payload = {"displayName": dp_name, "description": "Test EG"}
    res = requests.post(url, headers=headers, json=payload)
    print(f"EntryGroup {eg_id}: {res.status_code}")

def create_glossary(base_url, eg_id, entry_id, display_name):
    url = f"{base_url}/projects/{project}/locations/{location}/entryGroups/{eg_id}/entries?entryId={entry_id}"
    headers = {"Authorization": f"Bearer {get_token()}", "x-goog-user-project": project, "Content-Type": "application/json"}
    payload = {
        "displayName": display_name,
        "userSpecifiedType": "glossary",
        "userSpecifiedSystem": "glossary",
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"Glossary {entry_id}: {res.status_code}")

def verify_dataplex(base_url, expected_display_name):
    url = f"{base_url}/projects/{project}/locations/global/glossaries"
    headers = {"Authorization": f"Bearer {get_token()}", "x-goog-user-project": project}
    res = requests.get(url, headers=headers)
    if res.status_code >= 400:
        print(f"Dataplex verification failed: {res.status_code} {res.text}")
        return
    glossaries = res.json().get("glossaries", [])
    found = any(g.get("displayName") == expected_display_name for g in glossaries)
    print(f"Verification against {base_url} for '{expected_display_name}': {'SUCCESS' if found else 'FAILED'}")

if __name__ == "__main__":
    print("=== 1. Creating Source Data in Data Catalog ===")
    create_entry_group("https://datacatalog.googleapis.com/v1", "test_prod_eg_v6", "Test Prod EG")
    create_glossary("https://datacatalog.googleapis.com/v1", "test_prod_eg_v6", "test_prod_glos_v6", "Prod Glossary V6")

    create_entry_group("https://regional-staging-datacatalog.sandbox.googleapis.com/v2", "dc_glossary_test_staging_eg_v6", "Test Staging EG")
    create_glossary("https://regional-staging-datacatalog.sandbox.googleapis.com/v2", "dc_glossary_test_staging_eg_v6", "test_staging_glos_v6", "Staging Glossary V6")

    print("\n=== 2. Running Migration Scripts ===")
    subprocess.run([sys.executable, "run.py", "--project", project, "--user-project", project, "--glossaries", f"projects/{project}/locations/{location}/entryGroups/test_prod_eg_v6/glossaries/test_prod_glos_v6"])
    subprocess.run([sys.executable, "run.py", "--project", project, "--user-project", project, "--staging", "--glossaries", f"projects/{project}/locations/{location}/entryGroups/dc_glossary_test_staging_eg_v6/glossaries/test_staging_glos_v6"])

    print("\n=== 3. Verifying in Dataplex ===")
    verify_dataplex("https://dataplex.googleapis.com/v1", "Prod Glossary V6")
    verify_dataplex("https://staging-dataplex.sandbox.googleapis.com/v1", "Staging Glossary V6")
