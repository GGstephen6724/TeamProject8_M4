"""M4 output contracts and renderer: listing facts always come from raw MCP records."""
from typing import Literal
from pydantic import BaseModel,Field,ConfigDict

class SearchReply(BaseModel):
    model_config=ConfigDict(extra='forbid')
    kind:Literal['search','clarification','preference','error']
    job_ids:list[int]
    message:str

class Assessment(BaseModel):
    model_config=ConfigDict(extra='forbid')
    job_id:int
    fit_score:int=Field(ge=1,le=5)
    matched_skills:list[str]
    missing_information:list[Literal['schedule','posting_freshness','qualifications','commute']]

class AnalystReply(BaseModel):
    model_config=ConfigDict(extra='forbid')
    assessments:list[Assessment]

class CriticReply(BaseModel):
    model_config=ConfigDict(extra='forbid')
    accuracy:int=Field(ge=1,le=5)
    honesty:int=Field(ge=1,le=5)
    usefulness:int=Field(ge=1,le=5)
    rationale:str

def validate_search(reply,records):
    ids=[j['id'] for j in records]
    return reply.kind=='search' and len(reply.job_ids)==len(set(reply.job_ids)) and set(reply.job_ids)==set(ids)

def validate_analyst(reply,records):
    by_id={j['id']:j for j in records};ids=[a.job_id for a in reply.assessments]
    if len(ids)!=len(set(ids)) or set(ids)!=set(by_id):return False
    return all(all(s.casefold() in {x.casefold() for x in by_id[a.job_id]['skills']} for s in a.matched_skills) for a in reply.assessments)

def render(records,analyst=None,filters=None,error=None):
    lines=['EDUCATIONAL PROTOTYPE - fictional sample listings, not verified vacancies.']
    if filters:
        lines+=['Applied filters: '+str(filters),'Skills use '+filters.get('skill_match','any')+'-match; remote=False means no remote restriction.']
        if filters.get('salary_period')=='year':lines+=['Annual/hourly comparison assumes 2,080 hours/year, not a guaranteed annual salary.']
    if error:return '\n'.join(lines+['Database unavailable: '+error])
    if not records:return '\n'.join(lines+['No jobs matched the provided criteria in this small sample.'])
    assessments={a.job_id:a for a in analyst.assessments} if analyst else {}
    for j in records:
        lines += [f"[{j['id']}] {j['title']} | {j['company']}",
                  f"{j['location']} | {j['employment_type']} | USD {j['salary_min']:g}-{j['salary_max']:g}/hour",
                  'Listing skills: '+', '.join(j['skills'])]
        if j['id'] in assessments:
            a=assessments[j['id']]
            lines += [f'Analyst fit judgment: {a.fit_score}/5 (assessment, not an employer decision).',
                      'Supported skill overlap: '+(', '.join(a.matched_skills) or 'none identified'),
                      'Not verified: '+', '.join(a.missing_information)]
    return '\n'.join(lines+['Confirm schedule, qualifications, availability and pay with the actual employer before acting.'])
