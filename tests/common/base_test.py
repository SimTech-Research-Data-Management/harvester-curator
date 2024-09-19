import unittest
from pathlib import Path
import shutil

class BaseTestHarvesterCurator(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("tests", "test_data", "use_case")
        self.api_endpoints = Path("tests", "test_data", "api_end_points", "darus_md_schema_api_endpoints.json")
        self.harvest_output = Path("tests", "output", "harvested_output.json")
        self.curate_output = Path("tests", "output", "curated_output.json")
     
        self.harvest_output.parent.mkdir(parents=True, exist_ok=True)
        self.curate_output.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.harvest_output.parent.exists():
            shutil.rmtree(self.harvest_output.parent)
