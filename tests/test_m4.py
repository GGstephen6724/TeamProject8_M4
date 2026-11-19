import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import job_mcp_server as server
from grounding import SearchReply,Assessment,AnalystReply,validate_search,validate_analyst,render

class M4RegressionTests(unittest.TestCase):
    def test_comma_separated_keyword_aliases(self):
        result=server.search_jobs(keywords='software developer, software engineer, programmer',remote=True,employment_type='part time',minimum_salary=18)
        self.assertEqual({j['id'] for j in json.loads(result)},{5})
    def test_employment_variants(self):
        for value in ['part time','PART_TIME','Part-time']:
            records=json.loads(server.search_jobs(employment_type=value))
            self.assertEqual({j['id'] for j in records},{1,4,5,6,8})
    def test_annual_salary(self):
        records=json.loads(server.search_jobs(minimum_salary=40000,salary_period='year'))
        self.assertEqual({j['id'] for j in records},{2,3})
    def test_all_skills_not_any(self):
        self.assertIn('No jobs matched',server.search_jobs(skills='Python,React',skill_match='all'))
        self.assertEqual({j['id'] for j in json.loads(server.search_jobs(skills='Python,React'))},{3,5,6})
    def test_nonfinite_salary_rejected(self):
        for value in [float('nan'),float('inf'),-1]:self.assertTrue(server.search_jobs(minimum_salary=value).startswith('ERROR:'))
    def test_invalid_schema_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'jobs.json';path.write_text('[{"id":1}]')
            with patch.object(server,'DATABASE',path):self.assertTrue(server.search_jobs().startswith('ERROR:'))
    def test_duplicate_id_rejected(self):
        records=server.load_jobs()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'jobs.json';path.write_text(json.dumps([records[0],records[0]]))
            with patch.object(server,'DATABASE',path):self.assertIn('duplicate',server.search_jobs())
    def test_search_fabrication_caught(self):
        self.assertFalse(validate_search(SearchReply(kind='search',job_ids=[999],message='Fake'),server.load_jobs()[:1]))
    def test_analyst_fabrication_caught(self):
        reply=AnalystReply(assessments=[Assessment(job_id=999,fit_score=5,matched_skills=[],missing_information=[])])
        self.assertFalse(validate_analyst(reply,server.load_jobs()[:1]))
    def test_unsupported_skill_caught(self):
        reply=AnalystReply(assessments=[Assessment(job_id=1,fit_score=5,matched_skills=['Python'],missing_information=[])])
        self.assertFalse(validate_analyst(reply,server.load_jobs()[:1]))
    def test_renderer_copies_facts(self):
        records=server.load_jobs()[:1];text=render(records)
        self.assertIn('IT Help Desk Technician | SunCoast Technology',text)
        self.assertIn('USD 18-22/hour',text);self.assertIn('fictional',text)
    def test_no_match_offers_explicit_options(self):
        text=render([])
        self.assertIn('No jobs matched',text);self.assertIn('not relax it silently',text)
        self.assertIn('does not mean no such jobs exist elsewhere',text)
    def test_memory_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as d,patch.object(server,'MEMORY_FILE',Path(d)/'memory.json'):
            self.assertTrue(server.save_preference('minimum_salary','nan').startswith('ERROR:'))
            self.assertEqual(server.load_memory(),{})
    def test_corrupt_memory_is_empty(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'memory.json';path.write_text('{bad')
            with patch.object(server,'MEMORY_FILE',path):self.assertEqual(server.load_memory(),{})
    def test_preference_mutation_needs_current_consent(self):
        from job_agent import mutation_authorized
        self.assertFalse(mutation_authorized('save_preference','Find remote jobs.'))
        self.assertFalse(mutation_authorized('save_preference','Do not save my preference.'))
        self.assertTrue(mutation_authorized('save_preference','Please remember that I prefer remote jobs.'))
        self.assertTrue(mutation_authorized('clear_saved_preferences','Please clear my saved preferences.'))

if __name__=='__main__':unittest.main()
