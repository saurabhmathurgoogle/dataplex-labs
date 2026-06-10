import google.auth
from google.auth.transport.requests import Request
import requests
import sys

project = "dc-cuj-staging-playground"
location = "us-central1"

def get_token():
    creds, _ = google.auth.default()
    creds.refresh(Request())
    return creds.token

def create_entry_group(base_url, name):
    url = f"{base_url}/projects/{project}/locations/{location}/entryGroups?entryGroupId={name}"
    headers = {"Authorization": f"Bearer {get_token()}", "x-goog-user-project": project}
    res = requests.post(url, headers=headers, json={"displayName": f"{name} Display", "description": "Test entry group"})
    print(f"EntryGroup {name}: {res.status_code} {res.text}")

def create_glossary(base_url, group_name, entry_name, display_name, description):
    url = f"{base_url}/projects/{project}/locations/{location}/entryGroups/{group_name}/entries?entryId={entry_name}"
    headers = {"Authorization": f"Bearer {get_token()}", "x-goog-user-project": project}
    payload = {
        "displayName": display_name,
        "userSpecifiedType": "glossary",
        "userSpecifiedSystem": "glossary",
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"Glossary {entry_name}: {res.status_code} {res.text}")
    
    if res.status_code < 300 or res.status_code == 409:
        # Patch business context
        aspect_url = f"{base_url}/projects/{project}/locations/{location}/entryGroups/{group_name}/entries/{entry_name}"
        # wait, datacatalog doesn't use 'aspects' in V1, it uses tags or core aspects?
        # Let's just create it. The migration script expects business_context inside coreAspects.
        pass

create_entry_group("https://datacatalog.googleapis.com/v1", "test_prod_eg")
create_glossary("https://datacatalog.googleapis.com/v1", "test_prod_eg", "test_prod_glos", "Prod Glossary", "Prod Desc")

create_entry_group("https://staging-datacatalog.sandbox.googleapis.com/v1", "test_staging_eg")
create_glossary("https://staging-datacatalog.sandbox.googleapis.com/v1", "test_staging_eg", "test_staging_glos", "Staging Glossary", "Staging Desc")

