"""Capture a REAL external testing session, with transcript and facilitator notes.
Never prefill observations or participant answers. Files stay local and are git-ignored.
"""
import argparse,asyncio,json,time
from datetime import datetime,timezone
from pathlib import Path
from job_agent import configure_model,EvidenceServer,run_turn

async def main(args):
    args.output.mkdir(parents=True,exist_ok=True)
    print('Explain: fictional listings; no applications; participation voluntary; no names/passwords needed.')
    if input('Tester consents to anonymized session notes? [yes/no]: ').strip().lower()!='yes':return
    data={'tester_id':args.tester,'synthetic':False,'date_utc':datetime.now(timezone.utc).isoformat(),
          'role_context':input('Role/context (no full name): '),'format':input('Format (in-person/video/async): '),
          'external_to_team':input('Outside your team? [yes/no]: ').strip().lower()=='yes','turns':[]}
    if not data['external_to_team']:raise ValueError('The milestone requires external testers.')
    model=configure_model()
    async with EvidenceServer(memory=args.output/(args.tester+'_memory.json')) as server:
        print('Task 1: Find a job matching your real situation. Task 2: explicitly save a preference and reuse it.')
        print('Task 3: choose a listing using the analyst output. Enter DONE when tasks end.')
        started=time.perf_counter()
        while True:
            request=await asyncio.to_thread(input,'Tester request: ')
            if request.strip().upper()=='DONE':break
            result=await run_turn(server,model,request);data['turns'].append(result)
        data['total_seconds']=round(time.perf_counter()-started,2)
    for key,prompt in [
        ('task_given','Task given (exact wording): '),('what_they_did','What actually happened, step by step: '),
        ('stuck_moments','Specific confusion or hesitation; write none if not observed: '),
        ('surprise','Observed surprise; do not infer: '),('would_use_again','Would they use it again, and what would help? '),
        ('specific_analyst_insight','Specific analyst insight they identified: '),
        ('relevance','Relevance rating 1-5 (tester response): '),('trust','Trust rating 1-5: '),
        ('use_again_rating','Use-again rating 1-5: '),('task1_unassisted','Task 1 completed without help? yes/no: '),
        ('first_useful_seconds','Observed seconds to first useful result: ')]:
        data[key]=input(prompt)
    path=args.output/(args.tester+'.json');path.write_text(json.dumps(data,indent=2)+'\n')
    print('Saved locally:',path,'Review and anonymize before sharing; do not invent missing observations.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tester',required=True)
    p.add_argument('--output',type=Path,default=Path('.local_sessions'));asyncio.run(main(p.parse_args()))
