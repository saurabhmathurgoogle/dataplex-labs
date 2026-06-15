import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import api_call_utils
import logging_utils

logger = logging_utils.get_logger()

project = "dc-cuj-staging-playground"
location = "us-central1"
entry_group_id = "dc_glossary_scale_test_eg"
num_glossaries = 300

def delete_dc_entry(i):
    entry_id = f"saurabh_auto_migration_test_glossary_{i}"
    url = f"https://datacatalog.googleapis.com/v2/projects/{project}/locations/{location}/entryGroups/{entry_group_id}/entries/{entry_id}"
    res = api_call_utils.fetch_api_response("DELETE", url, project)
    if res.get("error_msg") and "NOT_FOUND" not in res["error_msg"]:
        logger.error(f"Failed to delete DC entry {entry_id}: {res['error_msg']}")
        return False
    return True

def delete_dp_glossary(i):
    # dp_glossary_id normalization: replace "_" with "-"
    # saurabh_auto_migration_test_glossary_{i} -> saurabh-auto-migration-test-glossary-{i}
    glossary_id = f"saurabh-auto-migration-test-glossary-{i}"
    url = f"https://dataplex.googleapis.com/v1/projects/{project}/locations/{location}/glossaries/{glossary_id}"
    res = api_call_utils.fetch_api_response("DELETE", url, project)
    if res.get("error_msg") and "NOT_FOUND" not in res["error_msg"]:
        logger.error(f"Failed to delete DP glossary {glossary_id}: {res['error_msg']}")
        return False
    return True

def delete_dc_eg():
    url = f"https://datacatalog.googleapis.com/v2/projects/{project}/locations/{location}/entryGroups/{entry_group_id}"
    res = api_call_utils.fetch_api_response("DELETE", url, project)
    if res.get("error_msg") and "NOT_FOUND" not in res["error_msg"]:
        logger.error(f"Failed to delete DC Entry Group {entry_group_id}: {res['error_msg']}")
        return False
    logger.info(f"DC Entry Group {entry_group_id} deleted.")
    return True

def cleanup():
    logger.info("Starting cleanup of 300 test glossaries...")
    
    # 1. Delete Dataplex glossaries
    logger.info("Deleting Dataplex glossaries...")
    dp_success = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(delete_dp_glossary, i) for i in range(1, num_glossaries + 1)]
        for f in as_completed(futures):
            if f.result():
                dp_success += 1
    logger.info(f"Deleted {dp_success}/{num_glossaries} Dataplex glossaries.")

    # 2. Delete Data Catalog entries
    logger.info("Deleting Data Catalog entries...")
    dc_success = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(delete_dc_entry, i) for i in range(1, num_glossaries + 1)]
        for f in as_completed(futures):
            if f.result():
                dc_success += 1
    logger.info(f"Deleted {dc_success}/{num_glossaries} Data Catalog entries.")

    # 3. Delete Data Catalog Entry Group (only if all entries deleted)
    if dc_success == num_glossaries:
        delete_dc_eg()
    else:
        logger.warning("Not all DC entries were deleted, skipping entry group deletion.")

if __name__ == "__main__":
    cleanup()
