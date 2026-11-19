"""Reproducible direct-tool before/after checks against the actual M3 Git commit.
These are engineering regression measurements, not human user tests or live agent pass rates.
"""
import importlib.util,json,subprocess,tempfile,csv
from pathlib import Path
import job_mcp_server as current
from grounding import SearchReply,Assessment,AnalystReply,validate_search,validate_analyst

HERE=Path(__file__).resolve().parent
def ids(text):
    try:return sorted(j['id'] for j in json.loads(text))
    except (ValueError,TypeError):return []

def main():
    directory=HERE/'evaluation';directory.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'baseline.py'
        path.write_bytes(subprocess.check_output(['git','show','8a6d910:job_mcp_server.py'],cwd=HERE))
        spec=importlib.util.spec_from_file_location('m3_baseline',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
        old.DATABASE=HERE/'jobs.json'
        cases=[
          ('keyword_punctuation',{'keywords':'software developer, software engineer, programmer','remote':True,'employment_type':'Part-time','minimum_salary':18},{'keywords':'software developer, software engineer, programmer','remote':True,'employment_type':'Part-time','minimum_salary':18},[5]),
          ('employment_part_time',{'employment_type':'part time'},{'employment_type':'part time'},[1,4,5,6,8]),
          ('employment_full_time',{'employment_type':'full time'},{'employment_type':'full time'},[2,3,7]),
          ('annual_salary',{'minimum_salary':40000},{'minimum_salary':40000,'salary_period':'year'},[2,3]),
          ('all_skills',{'skills':'Python,React'},{'skills':'Python,React','skill_match':'all'},[])]
        rows=[]
        for name,before_args,after_args,expected in cases:
            before=old.search_jobs(**before_args);after=current.search_jobs(**after_args)
            rows.append({'change':name,'expected':json.dumps(expected),'before_actual':json.dumps(ids(before)),
                         'after_actual':json.dumps(ids(after)),'before_pass':ids(before)==expected,'after_pass':ids(after)==expected})
        records=current.load_jobs()[:1]
        mutants=[('fabricated_finder_id',lambda:validate_search(SearchReply(kind='search',job_ids=[999],message=''),records)),
                 ('fabricated_analyst_id',lambda:validate_analyst(AnalystReply(assessments=[Assessment(job_id=999,fit_score=5,matched_skills=[],missing_information=[])]),records)),
                 ('unsupported_skill',lambda:validate_analyst(AnalystReply(assessments=[Assessment(job_id=1,fit_score=5,matched_skills=['Python'],missing_information=[])]),records))]
        for name,fn in mutants:
            rows.append({'change':name,'expected':'reject','before_actual':'no programmatic check in M3',
                         'after_actual':'rejected' if not fn() else 'accepted','before_pass':False,'after_pass':not fn()})
    with (directory/'improvement_results.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    print(json.dumps(rows,indent=2))

if __name__=='__main__':main()
