import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import job_mcp_server


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_path = Path(self.temp_dir.name) / "memory.json"
        self.memory_patch = patch.object(
            job_mcp_server, "MEMORY_FILE", self.memory_path
        )
        self.memory_patch.start()

    def tearDown(self):
        self.memory_patch.stop()
        self.temp_dir.cleanup()

    def test_save_and_retrieve_preference(self):
        result = job_mcp_server.save_preference(
            "employment_type", "Part-time"
        )
        self.assertIn("Saved preference", result)
        saved = json.loads(job_mcp_server.get_saved_preferences())
        self.assertEqual(saved["employment_type"], "Part-time")

    def test_remote_is_saved_as_boolean(self):
        result = job_mcp_server.save_preference("remote", "true")
        self.assertIn("Saved preference", result)
        saved = json.loads(job_mcp_server.get_saved_preferences())
        self.assertIs(saved["remote"], True)

    def test_reject_unsupported_key(self):
        result = job_mcp_server.save_preference(
            "api_key", "secret"
        )
        self.assertIn("ERROR", result)
        self.assertEqual(
            json.loads(job_mcp_server.get_saved_preferences()), {}
        )

    def test_reject_invalid_remote_value(self):
        result = job_mcp_server.save_preference(
            "remote", "sometimes"
        )
        self.assertIn("ERROR", result)
        self.assertEqual(
            json.loads(job_mcp_server.get_saved_preferences()), {}
        )

    def test_reject_negative_salary(self):
        result = job_mcp_server.save_preference(
            "minimum_salary", "-5"
        )
        self.assertIn("ERROR", result)
        self.assertEqual(
            json.loads(job_mcp_server.get_saved_preferences()), {}
        )

    def test_clear_preferences(self):
        job_mcp_server.save_preference("employment_type", "Part-time")
        result = job_mcp_server.clear_saved_preferences()
        self.assertIn("cleared", result.lower())
        self.assertEqual(
            json.loads(job_mcp_server.get_saved_preferences()), {}
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
