"""Team 8 M4: bounded search and local preferences over stdio MCP."""
from mcp.server.fastmcp import FastMCP
import json, math, os, re, tempfile
from pathlib import Path

mcp=FastMCP('Job Search Tools')
DATABASE=Path(os.getenv('JOB_DATABASE',str(Path(__file__).with_name('jobs.json'))))
MEMORY_FILE=Path(os.getenv('JOB_MEMORY_FILE',str(Path(__file__).with_name('memory.json'))))
ALLOWED_PREFERENCES={'keywords','location','remote','employment_type','minimum_salary','skills'}

def normalize_employment(value):
    key=re.sub(r'[\s_-]+','',value.casefold())
    return {'parttime':'part-time','fulltime':'full-time','':''}.get(key,value.strip().casefold())

def load_jobs():
    try:
        with DATABASE.open('r',encoding='utf-8') as stream:jobs=json.load(stream)
    except FileNotFoundError:return 'ERROR: jobs.json was not found.'
    except (json.JSONDecodeError,UnicodeError):return 'ERROR: jobs.json contains invalid JSON.'
    except OSError:return 'ERROR: jobs.json could not be read.'
    if not isinstance(jobs,list):return 'ERROR: jobs.json must contain a list of job records.'
    required={'id','title','company','location','remote','employment_type','salary_min','salary_max','skills'}
    ids=set()
    for job in jobs:
        if (not isinstance(job,dict) or not required<=job.keys() or type(job['id']) is not int
            or job['id'] in ids or type(job['remote']) is not bool
            or not all(isinstance(job[k],str) and job[k].strip() for k in ['title','company','location','employment_type'])
            or not isinstance(job['skills'],list) or not all(isinstance(s,str) for s in job['skills'])):
            return 'ERROR: jobs.json contains an invalid or duplicate job record.'
        for field in ('salary_min','salary_max'):
            if type(job[field]) not in (int,float) or not math.isfinite(job[field]) or job[field]<0:
                return 'ERROR: jobs.json contains an invalid salary.'
        if job['salary_max']<job['salary_min']:return 'ERROR: jobs.json contains an invalid salary range.'
        ids.add(job['id'])
    return jobs

@mcp.tool()
def search_jobs(keywords:str='',location:str='',remote:bool=False,employment_type:str='',
                minimum_salary:float=0,skills:str='',skill_match:str='any',salary_period:str='hour')->str:
    """Search fictional listings, never verified vacancies. Salary is USD/hour unless salary_period='year'
    (2080-hour assumption). employment_type accepts part-time or part time, full-time or full time.
    skills is comma-separated; any requires one skill, all requires each. remote=False is unrestricted.
    """
    if type(minimum_salary) not in (int,float) or not math.isfinite(minimum_salary) or minimum_salary<0:
        return 'ERROR: minimum_salary must be a finite non-negative number.'
    if type(remote) is not bool:return 'ERROR: remote must be true or false.'
    if skill_match not in {'any','all'}:return 'ERROR: skill_match must be any or all.'
    if salary_period not in {'hour','year'}:return 'ERROR: salary_period must be hour or year.'
    jobs=load_jobs()
    if isinstance(jobs,str):return jobs
    threshold=minimum_salary/2080 if salary_period=='year' else minimum_salary
    requested=[s.strip().casefold() for s in skills.split(',') if s.strip()]
    aliases={'developer':['developer','programmer','engineer'],'development':['development','developer','programmer','programming','software engineer'],
             'software':['software','programmer'],'web':['web','frontend','front-end','website'],
             'programming':['programming','programmer','developer']}
    terms=[a for term in re.findall(r'[a-z0-9+#-]+',keywords.casefold()) for a in aliases.get(term,[term])]
    matches=[]
    for job in jobs:
        text=' '.join([job['title'],job['company'],*job['skills']]).casefold()
        if terms and not any(t in text for t in terms):continue
        if location and location.casefold().strip() not in job['location'].casefold():continue
        if remote and not job['remote']:continue
        if employment_type and normalize_employment(job['employment_type'])!=normalize_employment(employment_type):continue
        if job['salary_min']<threshold:continue
        overlap=[any(s in j.casefold() for j in job['skills']) for s in requested]
        if requested and not (all(overlap) if skill_match=='all' else any(overlap)):continue
        matches.append(job)
    return json.dumps(matches,indent=2) if matches else 'No jobs matched the provided criteria.'

def load_memory():
    try:
        data=json.loads(MEMORY_FILE.read_text(encoding='utf-8'))
        return {k:v for k,v in data.items() if k in ALLOWED_PREFERENCES} if isinstance(data,dict) else {}
    except (OSError,ValueError):return {}

def save_memory(data):
    MEMORY_FILE.parent.mkdir(parents=True,exist_ok=True)
    descriptor,path=tempfile.mkstemp(prefix='.preferences-',dir=MEMORY_FILE.parent)
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8') as stream:json.dump(data,stream,allow_nan=False,indent=2)
        os.replace(path,MEMORY_FILE)
    finally:
        if os.path.exists(path):os.unlink(path)

@mcp.tool()
def get_saved_preferences()->str:
    """Read local preferences. Explain each applied preference when searching with it."""
    return json.dumps(load_memory(),indent=2)

@mcp.tool()
def save_preference(key:str,value:str)->str:
    """Save one allowed preference ONLY when the current user explicitly asks to remember/save it."""
    key=key.casefold().strip();value=value.strip()
    if key not in ALLOWED_PREFERENCES:return 'ERROR: Unsupported preference key.'
    if key=='remote':
        if value.casefold() not in {'true','false'}:return 'ERROR: remote must be true or false.'
        value=value.casefold()=='true'
    elif key=='minimum_salary':
        try:value=float(value)
        except ValueError:return 'ERROR: minimum_salary must be a number.'
        if not math.isfinite(value) or value<0:return 'ERROR: minimum_salary cannot be negative or non-finite.'
    elif len(value)>200:return 'ERROR: preference is too long.'
    data=load_memory();data[key]=value
    try:save_memory(data)
    except OSError:return 'ERROR: Could not save preferences.'
    return f"Saved preference '{key}'."

@mcp.tool()
def clear_saved_preferences()->str:
    """Clear local preferences ONLY when the current user asks to clear or forget them."""
    try:save_memory({})
    except OSError:return 'ERROR: Could not clear saved preferences.'
    return 'All saved job-search preferences have been cleared.'

if __name__=='__main__':mcp.run(transport='stdio')
