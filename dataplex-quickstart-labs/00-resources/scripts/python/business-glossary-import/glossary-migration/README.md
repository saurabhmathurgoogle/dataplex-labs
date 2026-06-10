# Glossary Migration Script

This script migrates Business Glossaries from Google Cloud Data Catalog to Dataplex.

## Setup

1. Install dependencies:
   ```bash
   pip install google-auth requests
   ```
2. Authenticate:
   ```bash
   gcloud auth application-default login
   ```

## Usage

Migrate all glossaries in a project:
```bash
python run.py --project="my-source-project" --user-project="my-billing-project"
```

To migrate specific glossaries, provide a comma-separated list of glossary URLs:
```bash
python run.py --project="my-source-project" --user-project="my-billing-project" --glossaries="projects/my-source-project/locations/us/entryGroups/eg/glossaries/g1,projects/my-source-project/locations/us/entryGroups/eg/glossaries/g2"
```
