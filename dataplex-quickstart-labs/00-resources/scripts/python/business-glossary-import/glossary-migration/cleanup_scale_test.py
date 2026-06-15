import sys
import time
import api_call_utils
import logging_utils

logger = logging_utils.get_logger()

project = "dc-cuj-staging-playground"
location = "us-central1"
num_glossaries = 300

def delete_dp_glossary(i):
    glossary_id = f"saurabh-auto-migration-test-glossary-{i}"
    url = f"https://dataplex.googleapis.com/v1/projects/{project}/locations/{location}/glossaries/{glossary_id}"
    res = api_call_utils.fetch_api_response("DELETE", url, project)
    if res.get("error_msg") and "NOT_FOUND" not in res["error_msg"]:
        logger.error(f"Failed to delete DP glossary {glossary_id}: {res['error_msg']}")
        return False
    return True

def delete_dc_eg(i):
    group_id = f"dc_glossary_saurabh_auto_migration_test_glossary_{i}"
    url = f"https://datacatalog.googleapis.com/v2/projects/{project}/locations/{location}/entryGroups/{group_id}"
    res = api_call_utils.fetch_api_response("DELETE", url, project)
    if res.get("error_msg") and "NOT_FOUND" not in res["error_msg"]:
        logger.error(f"Failed to delete DC Entry Group {group_id}: {res['error_msg']}")
        return False
    return True

def cleanup():
    logger.info("Starting cleanup of 300 test glossaries (each in its own Entry Group)...")
    
    # 1. Delete Dataplex glossaries
    logger.info("Deleting Dataplex glossaries...")
    dp_success = 0
    for i in range(1, num_glossaries + 1):
        if delete_dp_glossary(i):
            dp_success += 1
        if i % 10 == 0:
            logger.info(f"Progress: Processed {i}/300 Dataplex glossaries.")
        time.sleep(1.2) # Stay well below 100 writes/min
    logger.info(f"Deleted {dp_success}/{num_glossaries} Dataplex glossaries.")

    # 2. Delete Data Catalog entry groups (this also deletes entries inside them)
    logger.info("Deleting Data Catalog entry groups...")
    dc_success = 0
    for i in range(1, num_glossaries + 1):
        if delete_dc_eg(i):
            dc_success += 1
        if i % 10 == 0:
            logger.info(f"Progress: Processed {i}/300 Data Catalog entry groups.")
        time.sleep(0.5) # Safe sleep for DC writes
    logger.info(f"Deleted {dc_success}/{num_glossaries} Data Catalog entry groups.")

if __name__ == "__main__":
    cleanup()
