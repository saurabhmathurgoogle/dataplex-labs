import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging_utils
import api_layer
import migration_utils
from models import Context

logger = logging_utils.get_logger()

def build_context(url_parts: dict, user_project: str, project_number: str, is_staging: bool) -> Context:
    ctx = Context(
        user_project=user_project, project=url_parts["project"],
        location_id=url_parts["location_id"], entry_group_id=url_parts["entry_group_id"],
        dc_glossary_id=url_parts["glossary_id"], dp_glossary_id=migration_utils.normalize_id(url_parts["glossary_id"]),
        is_staging=is_staging
    )
    ctx.display_name = api_layer.fetch_glossary_display_name(ctx)
    return ctx

def process_glossary(url: str, user_project: str, project_number: str, is_staging: bool) -> bool:
    try:
        url_parts = migration_utils.parse_glossary_url(url)
        ctx = build_context(url_parts, user_project, project_number, is_staging)
        api_layer.create_dataplex_glossary(ctx)
        return True
    except Exception as e:
        logger.error(f"Failed for {url}: {e}")
        return False

def scope_urls(urls: list, project_id: str, project_number: str) -> list:
    scoped = []
    for u in urls:
        parts = migration_utils.parse_glossary_url(u)
        if parts.get("project") in (project_id, project_number):
            scoped.append(u)
    return scoped

def process_glossaries_concurrently(urls: list, user_project: str, proj_num: str, is_staging: bool) -> tuple:
    successes = 0
    failures = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_glossary, u, user_project, proj_num, is_staging) for u in urls]
        for f in as_completed(futures):
            if f.result():
                successes += 1
            else:
                failures += 1
    return successes, failures

def get_target_urls(args, proj_num: str) -> list:
    urls = args.glossaries
    if not urls:
        raw_urls = api_layer.discover_glossaries(args.project, args.user_project, args.staging)
        urls = [u.replace("/entries/", "/glossaries/") for u in raw_urls]
    else:
        urls = scope_urls(urls, args.project, proj_num)
    return urls

def main(args: argparse.Namespace):
    logger.info(f"Starting glossary migration for project {args.project}")
    proj_num = api_layer.get_project_number(args.project, args.user_project)
    urls = get_target_urls(args, proj_num)
    if not urls:
        logger.warning("No glossaries found.")
        sys.exit(0)
    successes, failures = process_glossaries_concurrently(urls, args.user_project, proj_num, args.staging)
    logger.info(f"Migration complete: {successes} succeeded, {failures} failed.")

if __name__ == "__main__":
    main(migration_utils.get_args())
