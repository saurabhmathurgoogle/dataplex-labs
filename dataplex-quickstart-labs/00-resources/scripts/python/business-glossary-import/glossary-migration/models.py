from dataclasses import dataclass

@dataclass
class Context:
    user_project: str
    project: str
    location_id: str
    entry_group_id: str
    dc_glossary_id: str
    dp_glossary_id: str
    project_number: str = ""
    is_staging: bool = False
    display_name: str = ""
    description: str = ""
