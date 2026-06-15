import google.auth
from google.auth.transport.requests import Request
import requests

creds, _ = google.auth.default()
creds.refresh(Request())
token = creds.token

project = "migration-test-458209"
entry_group = "dc_glossary_saurabh_auto_migration_test_glossary5s5ke34w"
entry = "saurabh_auto_migration_test_glossary5ygxqen5"
location = "us-central1"

print("Checking PROD...")
prod_url = f"https://datacatalog.googleapis.com/v1/projects/{project}/locations/{location}/entryGroups/{entry_group}/entries/{entry}"
res = requests.get(prod_url, headers={"Authorization": f"Bearer {token}", "x-goog-user-project": project})
print("PROD:", res.status_code, res.text[:200])

print("\nChecking STAGING...")
staging_url = f"https://regional-staging-datacatalog.sandbox.googleapis.com/v2/projects/{project}/locations/{location}/entryGroups/{entry_group}/entries/{entry}"
res2 = requests.get(staging_url, headers={"Authorization": f"Bearer {token}", "x-goog-user-project": project})
print("STAGING:", res2.status_code, res2.text[:200])
