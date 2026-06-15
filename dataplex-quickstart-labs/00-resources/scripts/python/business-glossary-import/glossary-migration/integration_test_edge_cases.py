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
    payload = {"displayName": dp_name, "description": "Test EG Edge"}
    res = requests.post(url, headers=headers, json=payload)
    print(f"EntryGroup {eg_id}: {res.status_code}")

def create_glossary(base_url, eg_id, entry_id, display_name=None, description=None):
    url = f"{base_url}/projects/{project}/locations/{location}/entryGroups/{eg_id}/entries?entryId={entry_id}"
    headers = {"Authorization": f"Bearer {get_token()}", "x-goog-user-project": project, "Content-Type": "application/json"}
    payload = {
        "userSpecifiedType": "glossary",
        "userSpecifiedSystem": "glossary",
    }
    if display_name is not None:
        payload["displayName"] = display_name
    if description is not None:
        payload["description"] = description
        
    res = requests.post(url, headers=headers, json=payload)
    print(f"Glossary {entry_id}: {res.status_code}")

if __name__ == "__main__":
    print("=== 1. Creating Edge Case Source Data ===")
    create_entry_group("https://regional-staging-datacatalog.sandbox.googleapis.com/v2", "dc_glossary_edge_eg_v1", "Edge EG")
    
    # Normal case: Display name and standard description
    normal_desc = "This is a normal business glossary description for testing aspects."
    create_glossary("https://regional-staging-datacatalog.sandbox.googleapis.com/v2", "dc_glossary_edge_eg_v1", "normal_glossary_v1", display_name="Normal Glossary", description=normal_desc)
    
    # Edge case 1: No display name, no description
    create_glossary("https://regional-staging-datacatalog.sandbox.googleapis.com/v2", "dc_glossary_edge_eg_v1", "no_display_no_desc_v1", display_name=None)
    
    # Edge case 2: Emojis and very long description
    long_desc = "Long description 🚀\n" * 50
    create_glossary("https://regional-staging-datacatalog.sandbox.googleapis.com/v2", "dc_glossary_edge_eg_v1", "long_desc_emojis_v1", display_name="Edge 🚀 漢字", description=long_desc)
    
    print("\n=== 2. Running Targeted Migration Scripts on Edge Cases ===")
    subprocess.run([sys.executable, "run.py", "--project", project, "--user-project", project, "--glossaries", f"projects/{project}/locations/{location}/entryGroups/dc_glossary_edge_eg_v1/glossaries/normal_glossary_v1", "--staging"])
    subprocess.run([sys.executable, "run.py", "--project", project, "--user-project", project, "--glossaries", f"projects/{project}/locations/{location}/entryGroups/dc_glossary_edge_eg_v1/glossaries/no_display_no_desc_v1", "--staging"])
    subprocess.run([sys.executable, "run.py", "--project", project, "--user-project", project, "--glossaries", f"projects/{project}/locations/{location}/entryGroups/dc_glossary_edge_eg_v1/glossaries/long_desc_emojis_v1", "--staging"])

    print("\n=== 3. Verifying Dataplex Entry Overview (Description) ===")
    # Let's verify the NORMAL description was successfully patched into Dataplex
    aspect_type_full = "projects/418487367933/locations/global/aspectTypes/overview"
    dp_url = f"https://staging-dataplex.sandbox.googleapis.com/v1/projects/{project}/locations/global/entryGroups/@dataplex/entries/projects/313634309590/locations/global/glossaries/normal-glossary-v1?view=CUSTOM&aspectTypes={aspect_type_full}"
    headers = {"Authorization": f"Bearer {get_token()}", "x-goog-user-project": project}
    dp_res = requests.get(dp_url, headers=headers)
    
    if dp_res.status_code == 200:
        aspects = dp_res.json().get("aspects", {})
        overview_key = next((k for k in aspects.keys() if "overview" in k), None)
        if overview_key:
            content = aspects[overview_key].get("data", {}).get("content", "")
            print(f"Verified Dataplex Description Length: {len(content)}")
            if content == normal_desc:
                print("SUCCESS: Normal description exactly matches!")
            else:
                print(f"FAILED: Description doesn't match. Got: {content}")
        else:
            print("FAILED: No overview aspect found. The API call silently dropped the aspect payload!")
    else:
        print(f"FAILED to fetch Dataplex Entry: {dp_res.status_code} {dp_res.text}")
