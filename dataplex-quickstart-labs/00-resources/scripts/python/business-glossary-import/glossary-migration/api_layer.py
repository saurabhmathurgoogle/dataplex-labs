import time
import api_call_utils
import logging_utils
from models import Context
from constants import *

logger = logging_utils.get_logger()

def _build_glossary_search_request(project_id: str) -> dict:
    return {"query": "type=glossary", "scope": {"includeProjectIds": [project_id]}, "pageSize": 1000}

def get_search_base_url(is_staging: bool) -> str:
    return SEARCH_STAGING_BASE_URL if is_staging else SEARCH_BASE_URL

def discover_glossaries(project_id: str, user_project: str, is_staging: bool = False) -> list:
    req = _build_glossary_search_request(project_id)
    url = get_search_base_url(is_staging)
    res = api_call_utils.fetch_api_response("POST", url, user_project, req)
    if res.get("error_msg"):
        logger.error(res["error_msg"])
        return []
    results = res.get("json", {}).get("results", [])
    return [f"https:{r['linkedResource']}" for r in results if r.get("searchResultSubtype") == "entry.glossary" and "linkedResource" in r]

def _get_project_url(project_id: str) -> str:
    return f"{CLOUD_RESOURCE_MANAGER_BASE_URL}/projects/{project_id}"

def get_project_number(project_id: str, user_project: str) -> str:
    res = api_call_utils.fetch_api_response("GET", _get_project_url(project_id), user_project)
    if res.get("error_msg"):
        raise Exception(res["error_msg"])
    name = res.get("json", {}).get("name", "")
    return name.split("/")[-1] if "/" in name else ""

def get_dc_base_url(ctx: Context) -> str:
    return DATACATALOG_STAGING_BASE_URL if getattr(ctx, "is_staging", False) else DATACATALOG_BASE_URL

def fetch_and_populate_metadata(ctx: Context) -> None:
    url = f"{get_dc_base_url(ctx)}/projects/{ctx.project}/locations/{ctx.location_id}/entryGroups/{ctx.entry_group_id}/entries/{ctx.dc_glossary_id}"
    res = api_call_utils.fetch_api_response("GET", url, ctx.user_project)
    if res.get("error_msg"):
        raise Exception(f"Failed to fetch glossary from Data Catalog: {res['error_msg']}")
    entry_json = res.get("json", {})
    ctx.display_name = entry_json.get("displayName", ctx.dp_glossary_id)
    ctx.description = entry_json.get("description", "")


def get_dp_base_url(ctx: Context) -> str:
    return DATAPLEX_STAGING_BASE_URL if getattr(ctx, "is_staging", False) else DATAPLEX_BASE_URL

def post_dataplex_glossary(ctx: Context) -> dict:
    url = f"{get_dp_base_url(ctx)}/projects/{ctx.project}/locations/global/glossaries?glossary_id={ctx.dp_glossary_id}"
    return api_call_utils.fetch_api_response("POST", url, ctx.user_project, {"displayName": ctx.display_name})

def get_dataplex_glossary_entry_url(ctx: Context) -> str:
    return f"{get_dp_base_url(ctx)}/projects/{ctx.project}/locations/global/entryGroups/@dataplex/entries/projects/{ctx.project_number}/locations/global/glossaries/{ctx.dp_glossary_id}"

def update_glossary_entry_overview(ctx: Context, description: str) -> bool:
    project_number = STAGING_PROJECT_NUMBER if getattr(ctx, "is_staging", False) else PROD_PROJECT_NUMBER
    url = f"{get_dataplex_glossary_entry_url(ctx)}?updateMask=aspects&aspectKeys={project_number}.global.overview"
    aspect_type_full = f"projects/{project_number}/locations/global/aspectTypes/overview"
    payload = {"aspects": {f"{project_number}.global.overview": {"aspectType": aspect_type_full, "data": {"content": description}}}}
    res = api_call_utils.fetch_api_response("PATCH", url, ctx.user_project, payload)
    return not bool(res.get("error_msg"))

def poll_dataplex_glossary_entry(ctx: Context) -> bool:
    url = f"{get_dataplex_glossary_entry_url(ctx)}?view=FULL"
    for _ in range(5):
        res = api_call_utils.fetch_api_response("GET", url, ctx.user_project)
        res_json = res.get("json")
        if isinstance(res_json, dict) and "name" in res_json:
            return True
        time.sleep(10)
    return False

def complete_glossary_creation(ctx: Context) -> None:
    if poll_dataplex_glossary_entry(ctx):
        if ctx.description:
            update_glossary_entry_overview(ctx, ctx.description)
            logger.info("Updated overview.")

def create_dataplex_glossary(ctx: Context) -> None:
    res = post_dataplex_glossary(ctx)
    error_msg = res.get("error_msg", "")
    if error_msg and "ALREADY_EXISTS" in error_msg:
        logger.info(f"Glossary '{ctx.display_name}' already exists.")
    elif error_msg:
        logger.error(f"Failed to create glossary: {res['error_msg']}")
        return
    else:
        logger.info(f"Glossary creation initiated for '{ctx.display_name}'.")
        time.sleep(10)
    complete_glossary_creation(ctx)
