import time
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import api_call_utils
import logging_utils

logger = logging_utils.get_logger()

project = "dc-cuj-staging-playground"
location = "us-central1"
num_glossaries = 300

def create_one_glossary_v2_style(i):
    group_id = f"dc_glossary_saurabh_auto_migration_test_glossary_{i}"
    entry_id = f"saurabh_auto_migration_test_glossary_{i}"
    display_name = f"saurabh-auto-migration-test-glossary{i}"
    
    # 1. Create Entry Group
    eg_url = f"https://datacatalog.googleapis.com/v2/projects/{project}/locations/{location}/entryGroups?entryGroupId={group_id}"
    res = api_call_utils.fetch_api_response("POST", eg_url, project, {})
    if res.get("error_msg") and "ALREADY_EXISTS" not in res["error_msg"]:
        logger.error(f"Failed to create Entry Group {group_id}: {res['error_msg']}")
        return False, None
        
    # 2. Create Entry
    entry_url = f"https://datacatalog.googleapis.com/v2/projects/{project}/locations/{location}/entryGroups/{group_id}/entries?entryId={entry_id}"
    payload = {
        "displayName": display_name,
        "entryType": "glossary",
        "coreAspects": {
            "business_context": {
                "aspectType": "business_context",
                "jsonContent": {
                    "description": f"Description for glossary {i} to test scale migration overview update."
                }
            }
        }
    }
    res = api_call_utils.fetch_api_response("POST", entry_url, project, payload)
    if res.get("error_msg"):
        if "ALREADY_EXISTS" in res["error_msg"]:
            return True, f"projects/{project}/locations/{location}/entryGroups/{group_id}/glossaries/{entry_id}"
        logger.error(f"Failed to create glossary {entry_id} in group {group_id}: {res['error_msg']}")
        return False, None
        
    return True, f"projects/{project}/locations/{location}/entryGroups/{group_id}/glossaries/{entry_id}"

def create_all_glossaries():
    logger.info(f"Creating {num_glossaries} glossaries (each in its own Entry Group) in Data Catalog...")
    urls = []
    success_count = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_one_glossary_v2_style, i) for i in range(1, num_glossaries + 1)]
        for f in as_completed(futures):
            success, url = f.result()
            if success:
                success_count += 1
                urls.append(url)
    logger.info(f"Successfully created {success_count}/{num_glossaries} glossaries.")
    return urls

def run_migration(urls):
    logger.info("Starting migration...")
    glossaries_arg = ",".join(urls)
    cmd = [
        sys.executable, "run.py",
        "--project", project,
        "--user-project", project,
        "--glossaries", glossaries_arg
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    logger.info("Migration Output:")
    logger.info(result.stdout)
    if result.stderr:
        logger.error("Migration Errors/Logs:")
        logger.error(result.stderr)
        
    duration = end_time - start_time
    logger.info(f"Migration finished in {duration:.2f} seconds.")
    return duration

if __name__ == "__main__":
    urls = create_all_glossaries()
    if len(urls) < num_glossaries:
        logger.warning(f"Only {len(urls)}/ {num_glossaries} were created. Proceeding with migration for created ones.")
    if urls:
        run_migration(urls)
    else:
        logger.error("No glossaries created. Aborting migration.")
