import unittest
import subprocess

class TestCLIGeneral(unittest.TestCase):
    def test_overall_help(self):
        result = subprocess.run([
            "harvester-curator", "--help"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
    
    def test_harvest_help(self):
        result = subprocess.run([
            "harvester-curator", "harvest", "--help"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage", result.stdout)
        self.assertIn("harvester-curator harvest", result.stdout)
        self.assertIn("--dir_path", result.stdout)
        self.assertIn("--output_filepath", result.stdout)      
    
    def test_curate_help(self):
        result = subprocess.run([
            "harvester-curator", "curate", "--help"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage", result.stdout)
        self.assertIn("harvester-curator curate", result.stdout)
        self.assertIn("--harvested_metadata_filepath", result.stdout)
        self.assertIn("--output_filepath", result.stdout)
        self.assertIn("--api_endpoints_filepath", result.stdout)
    
    def test_upload_help(self):
        result = subprocess.run([
            "harvester-curator", "upload", "--help"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage", result.stdout)
        self.assertIn("harvester-curator upload", result.stdout)
        self.assertIn("--server_url", result.stdout)
        self.assertIn("--api_token", result.stdout)
        self.assertIn("--dataverse_id", result.stdout)
        self.assertIn("--curated_metadata_filepath", result.stdout)

if __name__ == "__main__":
    unittest.main()
