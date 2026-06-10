import unittest
import migration_utils

class TestMigrationUtils(unittest.TestCase):
    def test_normalize_id(self):
        self.assertEqual(migration_utils.normalize_id("My_Glossary!"), "my-glossary")
        self.assertEqual(migration_utils.normalize_id("123-Glossary"), "g123-glossary")
        self.assertEqual(migration_utils.normalize_id("   "), "g")

    def test_parse_glossary_url(self):
        url = "projects/my-proj/locations/us/entryGroups/my-eg/glossaries/my-glos"
        expected = {"project": "my-proj", "location_id": "us", "entry_group_id": "my-eg", "glossary_id": "my-glos"}
        self.assertEqual(migration_utils.parse_glossary_url(url), expected)

    def test_parse_glossary_ids_list(self):
        val = "projects/p/locations/l/entryGroups/eg/glossaries/g1, projects/p/locations/l/entryGroups/eg/glossaries/g2"
        expected = ["projects/p/locations/l/entryGroups/eg/glossaries/g1", "projects/p/locations/l/entryGroups/eg/glossaries/g2"]
        self.assertEqual(migration_utils.parse_glossary_ids_list(val), expected)

if __name__ == "__main__":
    unittest.main()
