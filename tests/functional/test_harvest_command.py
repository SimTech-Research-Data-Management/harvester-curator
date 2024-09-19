import os
import subprocess
import unittest
from ..common.base_test import BaseTestHarvesterCurator
from pathlib import Path

class TestHarvestCommand(BaseTestHarvesterCurator):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parents[1]
        self.test_dir = self.base_dir/"test_data"/"use_case"  
        self.harvest_output = self.base_dir/"output"/"harvested_output.json"
        self.default_harvest_output_filepath = self.base_dir.parent / "output" / "harvested_output.json"

        self.harvest_output.parent.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        if self.harvest_output.exists():
            self.harvest_output.unlink()
        if self.default_harvest_output_filepath.exists():
            self.default_harvest_output_filepath.unlink()

        self.assertFalse(self.harvest_output.exists())
        self.assertFalse(self.default_harvest_output_filepath.exists())

    def test_harvest(self):
        result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(self.test_dir),
            "--output_filepath", str(self.harvest_output)
        ], capture_output=True, text=True)

        print("harvest output:", result.stdout)
        print("harvest errors:", result.stderr)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(self.harvest_output.exists())
    
    
    def test_harvest_with_default_input(self):
        # Remove the default output file if it alreay exists   
        if self.default_harvest_output_filepath.exists():
            self.default_harvest_output_filepath.unlink()
            
        result = subprocess.run([
            "harvester-curator", "harvest"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(self.default_harvest_output_filepath.exists())

    def test_harvest_invalid_dir_path(self):
        invalid_dir = Path("/invalid/test/dir")
        result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(invalid_dir),
            "--output_filepath", str(self.harvest_output)
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"Invalid directory", result.stderr)

    def test_harvest_invalid_output_fileformat(self):
        invalid_output = self.base_dir/"output"/"harvested_output.txt"
        result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(self.test_dir),
            "--output_filepath", str(invalid_output)
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must end with '.json'", result.stderr)
          
if __name__ == "__main__":
    unittest.main()