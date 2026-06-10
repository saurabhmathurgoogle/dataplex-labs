import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock google auth before importing our code
sys.modules['google'] = MagicMock()
sys.modules['google.auth'] = MagicMock()
sys.modules['google.auth.transport'] = MagicMock()
sys.modules['google.auth.transport.requests'] = MagicMock()

import api_layer
from models import Context

class TestApiLayer(unittest.TestCase):
    @patch("api_call_utils.fetch_api_response")
    def test_get_project_number(self, mock_fetch):
        mock_fetch.return_value = {"error_msg": None, "json": {"name": "projects/12345"}}
        self.assertEqual(api_layer.get_project_number("my-proj", "u-proj"), "12345")

    @patch("api_call_utils.fetch_api_response")
    def test_discover_glossaries(self, mock_fetch):
        res = {"results": [{"searchResultSubtype": "entry.glossary", "linkedResource": "//x/projects/1/locations/l/entryGroups/eg/entries/g"}]}
        mock_fetch.return_value = {"error_msg": None, "json": res}
        self.assertEqual(api_layer.discover_glossaries("p", "u", False), ["https://x/projects/1/locations/l/entryGroups/eg/entries/g"])

    @patch("api_call_utils.fetch_api_response")
    def test_fetch_glossary_display_name(self, mock_fetch):
        ctx = Context("u", "p", "l", "eg", "dc", "dp", "")
        mock_fetch.return_value = {"error_msg": None, "json": {"displayName": "My Glossary"}}
        self.assertEqual(api_layer.fetch_glossary_display_name(ctx), "My Glossary")

if __name__ == "__main__":
    unittest.main()
