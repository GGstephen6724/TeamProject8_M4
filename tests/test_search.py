
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from unittest.mock import patch, mock_open

import job_mcp_server


class JobSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database_path = Path(__file__).resolve().parents[1] / "jobs.json"
        with database_path.open("r", encoding="utf-8") as file:
            cls.jobs = json.load(file)

    def run_search(self, **filters):
        with patch.object(job_mcp_server, "DATABASE") as database:
            database.open.return_value.__enter__.return_value = None

            # Supply the real sample listings without changing jobs.json.
            with patch("builtins.open", create=True):
                from unittest.mock import mock_open
                database.open.return_value = mock_open(
                    read_data=json.dumps(self.jobs)
                ).return_value

            # Patch the file-opening method used by the search function.
            with patch.object(
                Path,
                "open",
                return_value=mock_open(
                    read_data=json.dumps(self.jobs)
                ).return_value,
            ):
                return job_mcp_server.search_jobs(**filters)

    def test_remote_part_time_minimum_salary(self):
        result = json.loads(self.run_search(
            keywords="developer",
            remote=True,
            employment_type="Part-time",
            minimum_salary=18,
        ))
        self.assertTrue(result)
        self.assertTrue(all(job["remote"] for job in result))
        self.assertTrue(all(job["employment_type"] == "Part-time" for job in result))
        self.assertTrue(all(job["salary_min"] >= 18 for job in result))

    def test_software_development_keyword(self):
        result = json.loads(self.run_search(
            keywords="software development",
            remote=True,
            employment_type="Part-time",
            minimum_salary=18,
        ))
        self.assertTrue(any(job["title"] == "Junior Web Developer" for job in result))

    def test_local_it_support_minimum_salary(self):
        result = json.loads(self.run_search(
            keywords="IT Support",
            location="Fort Myers",
            employment_type="Full-time",
            minimum_salary=20,
        ))
        self.assertTrue(all("Fort Myers" in job["location"] for job in result))
        self.assertTrue(all(job["salary_min"] >= 20 for job in result))

    def test_remote_filter(self):
        result = json.loads(self.run_search(remote=True))
        self.assertTrue(result)
        self.assertTrue(all(job["remote"] for job in result))

    def test_employment_type_filter(self):
        result = json.loads(self.run_search(employment_type="Part-time"))
        self.assertTrue(result)
        self.assertTrue(all(job["employment_type"] == "Part-time" for job in result))

    def test_minimum_salary_filter(self):
        result = json.loads(self.run_search(minimum_salary=24))
        self.assertTrue(result)
        self.assertTrue(all(job["salary_min"] >= 24 for job in result))

    def test_skill_filter(self):
        result = json.loads(self.run_search(skills="Python"))
        self.assertTrue(result)
        self.assertTrue(any(
            any("python" in skill.lower() for skill in job["skills"])
            for job in result
        ))

    def test_no_matching_jobs(self):
        result = self.run_search(
            keywords="unicorn aerospace",
            remote=True,
            minimum_salary=1000,
        )
        self.assertIn("No jobs matched", result)


    def test_invalid_database_json(self):
        invalid_file = mock_open(read_data="{invalid json")

        with patch.object(
            job_mcp_server,
            "DATABASE",
            Path("fake_jobs.json"),
        ):
            with patch.object(
                Path,
                "open",
                invalid_file,
            ):
                result = job_mcp_server.search_jobs()

        self.assertIn("invalid JSON", result)


    def test_missing_database(self):
        with patch.object(
            Path,
            "open",
            side_effect=FileNotFoundError,
        ):
            result = job_mcp_server.search_jobs()
        self.assertIn("not found", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
