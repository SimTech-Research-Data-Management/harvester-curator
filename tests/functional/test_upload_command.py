import subprocess
import unittest
from ..common.base_test import BaseTestHarvesterCurator
from pathlib import Path

class TestUploadCommand(BaseTestHarvesterCurator):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parents[1]
        self.test_dir = self.base_dir/"test_data"/"use_case"  
        self.harvest_output = self.base_dir/"output"/"harvested_output.json"
        self.api_endpoints = self.base_dir/"test_data"/"api_end_points"/"darus_md_schema_api_endpoints.json"
        self.curate_output = self.base_dir/"output"/"curated_output.json"
    
        self.harvest_output.parent.mkdir(parents=True, exist_ok=True)
        self.curate_output.parent.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        if self.harvest_output.exists():
            self.harvest_output.unlink()
        if self.curate_output.exists():
            self.curate_output.unlink()
    
        self.assertFalse(self.harvest_output.exists())
        self.assertFalse(self.curate_output.exists())
   

    def test_upload(self):
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

        # Run curate then to ensure the existence of curate output before test run upload
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

        # Run upload
        # upload_result = subprocess.run([
        #     "harvester-curator", "upload",
        #     "--server_url", "https://darus.uni-stuttgart.de/",
        #     "--api_token", "api_token",
        #     "--dataverse_id", "dataverse_id",
        #     "--curated_metadata_filepath", str(self.curate_output)
        # ], capture_output=True, text=True)
        # print("upload output:", upload_result.stdout)
        # print("upload errors:", upload_result.stderr)
        # self.assertEqual(upload_result.returncode, 0)

if __name__ == '__main__':
    unittest.main()

    