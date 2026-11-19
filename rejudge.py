"""One documented protocol repair: supply literal MCP status/results to every critic.
Agent runs are not regenerated. Original critic records are preserved for comparison.
"""
import asyncio,json,csv,statistics
from pathlib import Path
from evaluate import critic,setup_tracing,CASES
from job_agent import HERE,configure_model

async def main():
    folder=HERE/'evaluation/live';old=HERE/'evaluation/initial_critic';old.mkdir(exist_ok=True)
    model=configure_model();provider=setup_tracing(folder);sem=asyncio.Semaphore(3)
    paths=sorted(folder.glob('TC*_run*.json'))
    async def repair(path):
        record=json.loads(path.read_text())
        if not record.get('critic') or not record.get('turns'):return
        async with sem:
            (old/path.name).write_text(json.dumps(record,indent=2))
            record['initial_critic']=record['critic']
            record['protocol_repair']='One rescore with literal raw MCP tool events; no agent rerun or selective retries.'
            record['critic']=await critic(model,record['turns'][-1])
            record['checks']['critic_at_least_four']=min(record['critic'][k] for k in ['accuracy','honesty','usefulness'])>=4
            record['passed']=all(record['checks'].values());path.write_text(json.dumps(record,indent=2))
            print('REJUDGED',record['case_id'],record['repeat'],record['passed'],record['critic'],flush=True)
    await asyncio.gather(*(repair(path) for path in paths));provider.force_flush()
    records=[json.loads(p.read_text()) for p in paths];rows=[]
    for case in CASES:
        runs=[r for r in records if r['case_id']==case['id']];wins=sum(r['passed'] for r in runs)
        scores=[r['critic'][key] for r in runs if r.get('critic') for key in ['accuracy','honesty','usefulness']]
        rows.append({'test_case_id':case['id'],'input':case['input'],'expected_output':case['expected'],
            'actual_output':json.dumps([r['turns'][-1]['final'] if r['turns'] else 'ERROR '+r.get('error_type','unknown') for r in runs]),
            'pass_fail':'PASS' if wins>=2 else 'FAIL','runs_passed':wins,'runs_total':len(runs),
            'critic_mean':round(statistics.mean(scores),3) if scores else '',
            'failed_checks':json.dumps([r['checks'] for r in runs if not r['passed']])})
    with (folder/'evaluation_results.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    summary=json.loads((folder/'summary.json').read_text())
    summary['initial_case_passes']=summary['case_passes'];summary['initial_run_passes']=summary['run_passes']
    summary['case_passes']=sum(r['pass_fail']=='PASS' for r in rows);summary['run_passes']=sum(r['passed'] for r in records)
    summary['case_pass_rate']=summary['case_passes']*10
    summary['critic_scores']=[r['critic'] for r in records if r.get('critic')]
    summary['protocol_repair']='All critic-eligible outputs rescored exactly once with literal raw MCP tool events. Original records retained.'
    (folder/'summary.json').write_text(json.dumps(summary,indent=2));print('REPAIRED SUMMARY',summary['case_passes'],summary['run_passes'],flush=True)

if __name__=='__main__':asyncio.run(main())
