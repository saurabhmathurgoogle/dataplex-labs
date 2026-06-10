import google.auth
from google.auth.transport.requests import Request
import requests

def get_token():
    creds, _ = google.auth.default()
    creds.refresh(Request())
    return creds.token

url = "https://datacatalog.googleapis.com/v1/projects/dc-cuj-staging-playground/locations/us-central1/entryGroups/test_prod_eg_v6/entries/test_prod_glos_v6"
headers = {"Authorization": f"Bearer {get_token()}", "x-goog-user-project": "dc-cuj-staging-playground"}
payload = {"description": "A test description"}
res_patch = requests.patch(f"{url}?updateMask=description", headers=headers, json=payload)
print("Patch:", res_patch.status_code, res_patch.json())

res_get = requests.get(url, headers=headers)
print("Get:", res_get.json())
