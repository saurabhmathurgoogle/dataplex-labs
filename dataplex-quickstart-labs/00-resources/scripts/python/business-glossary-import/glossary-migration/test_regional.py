import requests
import google.auth
from google.auth.transport.requests import Request

creds, _ = google.auth.default()
creds.refresh(Request())
token = creds.token

url = "https://regional-staging-datacatalog.sandbox.googleapis.com/v2/projects/migration-test-458209/locations/us-central1/entryGroups/dc_glossary_saurabh_auto_migration_test_glossary5s5ke34w/entries/saurabh_auto_migration_test_glossary5ygxqen5"
headers = {"Authorization": f"Bearer {token}", "x-goog-user-project": "migration-test-458209"}

res = requests.get(url, headers=headers)
print("regional-staging:", res.status_code, res.text[:200])

url2 = "https://staging-datacatalog.sandbox.googleapis.com/v1/projects/migration-test-458209/locations/us-central1/entryGroups/dc_glossary_saurabh_auto_migration_test_glossary5s5ke34w/entries/saurabh_auto_migration_test_glossary5ygxqen5"
res2 = requests.get(url2, headers=headers)
print("staging:", res2.status_code, res2.text[:200])
