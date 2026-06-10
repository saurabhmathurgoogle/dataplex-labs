import argparse
import re
import logging_utils

logger = logging_utils.get_logger()

def normalize_id(name: str) -> str:
    if not name: return ""
    norm = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not norm or not norm[0].isalpha(): norm = "g" + norm
    return norm[:63]

def parse_glossary_url(url: str) -> dict:
    pattern = r"projects/(?P<project>[^/]+)/locations/(?P<location_id>[^/]+)/entryGroups/(?P<entry_group_id>[^/]+)/glossaries/(?P<glossary_id>[^/?#]+)"
    match = re.search(pattern, url)
    if not match:
        raise Exception(f"Invalid glossary URL: {url}")
    return match.groupdict()

def parse_glossary_ids_list(value: str) -> list:
    if not isinstance(value, str): return []
    items = []
    for raw in value.split(","):
        base = raw.strip().split("?", 1)[0]
        if "/glossaries/" in base:
            items.append(base)
    return items

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--user-project", required=True)
    parser.add_argument("--glossaries", type=parse_glossary_ids_list, default=[])
    parser.add_argument("--staging", action="store_true", help="Use Dataplex staging environment")
    return parser.parse_args()
