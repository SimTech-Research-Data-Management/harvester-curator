import subprocess
import unittest
from ..common.base_test import BaseTestHarvesterCurator
from pathlib import Path

class TestCurateCommand(BaseTestHarvesterCurator):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parents[1]
        self.test_dir = self.base_dir/"test_data"/"use_case"  
        self.harvest_output = self.base_dir/"output"/"harvested_output.json"
        self.api_endpoints = self.base_dir/"test_data"/"api_end_points"/"darus_md_schema_api_endpoints.json"
        self.curate_output = self.base_dir/"output"/"curated_output.json"
        self.default_harvest_output_filepath = self.base_dir.parent / "output" / "harvested_output.json"
        self.default_curate_output_filepath = self.base_dir.parent / "output" / "curated_output.json"

        self.harvest_output.parent.mkdir(parents=True, exist_ok=True)
        self.curate_output.parent.mkdir(parents=True, exist_ok=True)
          
    def tearDown(self):
        if self.harvest_output.exists():
            self.harvest_output.unlink()
        if self.curate_output.exists():
            self.curate_output.unlink()
        if self.default_harvest_output_filepath.exists():
            self.default_harvest_output_filepath.unlink()
        if self.default_curate_output_filepath.exists():
            self.default_curate_output_filepath.unlink()

        self.assertFalse(self.harvest_output.exists())
        self.assertFalse(self.curate_output.exists())
        self.assertFalse(self.default_harvest_output_filepath.exists())
        self.assertFalse(self.default_curate_output_filepath.exists())

    def test_curate(self):
        # Run harvest first to ensure the existence of harvest output before test run curate
        harvest_result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(self.test_dir),
            "--output_filepath", str(self.harvest_output)
        ], capture_output=True, text=True)

        print("harvest output:", harvest_result.stdout)
        print("harvest errors:", harvest_result.stderr)

        self.assertEqual(harvest_result.returncode, 0)
        self.assertTrue(self.harvest_output.exists())
       

        self.assertGreater(self.harvest_output.stat().st_size, 0, "harvested_output.json is empty.")

        # Run curate
        curate_result = subprocess.run([
            "harvester-curator", "curate",
            "--harvested_metadata_filepath", str(self.harvest_output),
            "--output_filepath", str(self.curate_output),
            "--api_endpoints_filepath", str(self.api_endpoints)
        ], capture_output=True, text=True)
        
        print("curate output:", curate_result.stdout)
        print("curate errors:", curate_result.stderr)

        self.assertEqual(curate_result.returncode, 0)
        self.assertTrue(self.curate_output.exists())
     

    def test_curate_with_default_input(self):
        # Remove the default curate output file if it alreay exists   
        if self.default_curate_output_filepath.exists():
            self.default_curate_output_filepath.unlink()

        # Run harvest first to ensure the existence of harvest output before test run curate
        harvest_result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(self.test_dir),
            "--output_filepath", str(self.default_harvest_output_filepath)
        ], capture_output=True, text=True)
        self.assertEqual(harvest_result.returncode, 0)
        self.assertTrue(self.default_harvest_output_filepath.exists())

        # Run curate with default input
        curate_result = subprocess.run([
            "harvester-curator", "curate"
        ], capture_output=True, text=True)

        self.assertEqual(curate_result.returncode, 0)
        self.assertTrue(self.default_curate_output_filepath.exists())

    def test_curate_invalid_harvest_metadata_filepath(self):
        invalid_harvest_metadata_filepath = Path("/invalid/harvest_metadata/dir")
        result = subprocess.run([
            "harvester-curator", "curate",
            "--harvested_metadata_filepath", str(invalid_harvest_metadata_filepath),
            "--output_filepath", str(self.curate_output),
            "--api_endpoints_filepath", str(self.api_endpoints)
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid harvester output filepath", result.stderr)
    

    def test_curate_invalid_harvest_metadata_fileformat(self):
        invalid_harvest_metadata_fileformat = self.base_dir/"output"/"harvested_output.txt"
        result = subprocess.run([
            "harvester-curator", "curate",
            "--harvested_metadata_filepath", str(invalid_harvest_metadata_fileformat),
            "--output_filepath", str(self.curate_output),
            "--api_endpoints_filepath", str(self.api_endpoints)
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid harvester output filepath", result.stderr)
    
    def test_curate_invalid_api_endpoints_filepath(self):

        # Run harvest first to ensure the existence of harvest output before test run curate
        harvest_result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(self.test_dir),
            "--output_filepath", str(self.harvest_output)
        ], capture_output=True, text=True)
        self.assertEqual(harvest_result.returncode, 0)
        self.assertTrue(self.harvest_output.exists())

        invalid_api_endpoints_filepath = Path("/invalid/api_endpoints/dir")
        result = subprocess.run([
            "harvester-curator", "curate",
            "--harvested_metadata_filepath", str(self.harvest_output),
            "--output_filepath", str(self.curate_output),
            "--api_endpoints_filepath", str(invalid_api_endpoints_filepath)
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid api_endpoints filepath", result.stderr)
    
    def test_curate_invalid_api_endpoints_fileformat(self):

        # Run harvest first to ensure the existence of harvest output before test run curate
        harvest_result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(self.test_dir),
            "--output_filepath", str(self.harvest_output)
        ], capture_output=True, text=True)
        self.assertEqual(harvest_result.returncode, 0)
        self.assertTrue(self.harvest_output.exists())

        invalid_api_endpoints_fileformat = self.base_dir/"test_data"/"api_end_points"/"darus_md_schema_api_endpoints.txt"
        result = subprocess.run([
            "harvester-curator", "curate",
            "--harvested_metadata_filepath", str(self.harvest_output),
            "--output_filepath", str(self.curate_output),
            "--api_endpoints_filepath", str(invalid_api_endpoints_fileformat)
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid api_endpoints filepath", result.stderr)
    
    def test_curate_invalid_output_filepath(self):

        # Run harvest first to ensure the existence of harvest output before test run curate
        harvest_result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(self.test_dir),
            "--output_filepath", str(self.harvest_output)
        ], capture_output=True, text=True)
        self.assertEqual(harvest_result.returncode, 0)
        self.assertTrue(self.harvest_output.exists())

        invalid_curate_output_path = Path("/root/output/dir")
        result = subprocess.run([
            "harvester-curator", "curate",
            "--harvested_metadata_filepath", str(self.harvest_output),
            "--output_filepath", str(invalid_curate_output_path),
            "--api_endpoints_filepath", str(self.api_endpoints)
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be created", result.stderr)

    def test_harvest_invalid_output_fileformat(self):
        # Run harvest first to ensure the existence of harvest output before test run curate
        harvest_result = subprocess.run([
            "harvester-curator", "harvest",
            "--dir_path", str(self.test_dir),
            "--output_filepath", str(self.harvest_output)
        ], capture_output=True, text=True)
        self.assertEqual(harvest_result.returncode, 0)
        self.assertTrue(self.harvest_output.exists())

        invalid_curate_output_fileformat = self.base_dir/"output"/"curated_output.txt"
        result = subprocess.run([
            "harvester-curator", "curate",
            "--harvested_metadata_filepath", str(self.harvest_output),
            "--output_filepath", str(invalid_curate_output_fileformat),
            "--api_endpoints_filepath", str(self.api_endpoints)
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid output filepath", result.stderr)

if __name__ == "__main__":
    unittest.main()