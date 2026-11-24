import copy, importlib.util, json, os, sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from research import validate_record, apply_corrections, summarize, audit_sample, accuracy, assert_public_url, AeroLink, toolkit_metadata, catalogue_observations

@pytest.fixture
def record():
    return {'id':1,'name':'Example','category':'CRM','description':'Example API','auth_methods':['OAuth2'],'access':['self_serve_free'],'api_type':'REST','api_breadth':'Read records','capabilities':['Read records'],'mcp_status':'not_established','composio_status':'not_checked','verdict':'build_now','blockers':[],'confidence':'high','evidence':[{'url':'https://example.com/docs','title':'Docs','source_type':'first_party','supports':['auth_methods','access','api_type','api_breadth','verdict'],'excerpt':'Developer credentials are self-service.','retrieved_at':'2026-11-23'}],'notes':'Documentation assessment only.','researched_at':'2026-11-23','research_method':'Test fixture, not a research result'}

def test_official_mcp_needs_specific_first_party_support(record):
    record['mcp_status']='vendor_official'
    with pytest.raises(ValueError,match='evidence mapping|MCP evidence'):validate_record(record)
    record['evidence'][0]['supports'].append('mcp_status')
    assert validate_record(record)['mcp_status']=='vendor_official'

def test_unresolved_access_cannot_be_build_now(record):
    record['access']=['unresolved']
    with pytest.raises(ValueError,match='build-now'):validate_record(record)

def test_correction_does_not_mutate_baseline(record):
    before=copy.deepcopy(record)
    corrected=apply_corrections([record],[{'id':1,'reason':'Plan gate documented','evidence_urls':['https://example.com/docs'],'changes':{'access':['paid_plan'],'verdict':'build_with_constraints'}}])
    assert record==before and corrected[0]['access']==['paid_plan']

def test_correction_requires_evidence(record):
    with pytest.raises(ValueError,match='reason and evidence'):apply_corrections([record],[{'id':1,'changes':{'confidence':'low'}}])

def test_correction_cannot_rename_assigned_app(record):
    with pytest.raises(ValueError,match='identity'):apply_corrections([record],[{'id':1,'reason':'x','evidence_urls':['https://example.com'],'changes':{'name':'Another'}}])

def test_access_counts_are_overlapping(record):
    record['access']=['self_serve_free','paid_plan'];record['verdict']='build_with_constraints'
    summary=summarize([record]);assert summary['total']==1 and sum(summary['access'].values())==2

def test_auth_counts_each_method_once_per_app(record):
    record['auth_methods']=['OAuth2','OAuth 2.0','API key'];assert summarize([record])['auth']=={'OAuth':1,'API keys / client credentials':1}

def test_sample_deterministic_two_per_category(record):
    records=[]
    for i in range(1,101):
        r=copy.deepcopy(record);r.update(id=i,name=f'App {i}',category=f'Category {(i-1)//10}',confidence='low' if i%10==0 else 'high');records.append(r)
    sample=audit_sample(records)
    assert len(sample)==20 and len({r['id'] for r in sample})==20 and sample==audit_sample(records)

def test_no_audit_means_no_fake_accuracy():
    result=accuracy([],'final_grade');assert result['fully_correct_fraction'] is None and result['adjudicated']==0

def test_accuracy_denominator_excludes_pending_and_reports_unresolved():
    checks={str(i):{'final_grade':g} for i,g in enumerate(['correct','partial','incorrect','unresolved','pending'])}
    result=accuracy([{'checks':checks}],'final_grade');assert result['adjudicated']==3 and result['fully_correct_fraction']==pytest.approx(1/3) and result['pending']==1 and result['unresolved']==1

@pytest.mark.parametrize('url',['http://localhost/a','file:///etc/passwd','https://user:secret@example.com'])
def test_fetch_rejects_non_public_or_credential_urls(url):
    with pytest.raises(ValueError):assert_public_url(url)

def test_model_calls_gated_before_any_request(monkeypatch):
    monkeypatch.delenv('FREE_ALLOCATION_CONFIRMED',raising=False)
    with pytest.raises(RuntimeError,match='No model request'):AeroLink()

def test_model_endpoint_restricted(monkeypatch):
    monkeypatch.setenv('FREE_ALLOCATION_CONFIRMED','true');monkeypatch.setenv('AEROLINK_API_KEY','test-value');monkeypatch.setenv('AEROLINK_MODEL','test-model');monkeypatch.setenv('AEROLINK_BASE_URL','https://untrusted.example/v1')
    with pytest.raises(RuntimeError,match='Unapproved'):AeroLink()

def test_secret_not_allowed_in_evidence_url(record):
    record['evidence'][0]['url']='https://example.com/docs?api_key=private'
    with pytest.raises(ValueError,match='Credential'):validate_record(record)

def test_catalogue_export_keeps_only_public_labels():
    response=[{'slug':'example','name':'Example','api_key':'should-never-export','private_config':{'x':'y'}}]
    assert toolkit_metadata(response)==[{'slug':'example','name':'Example'}]

def test_populated_claim_requires_specific_evidence_mapping(record):
    record['evidence'][0]['supports'].remove('api_breadth')
    with pytest.raises(ValueError,match='api_breadth claim'):validate_record(record)

def test_catalogue_label_match_does_not_merge_different_products():
    records=[{'id':1,'name':'Salesforce'},{'id':44,'name':'Salesforce Commerce Cloud'}]
    observed=catalogue_observations(records,[{'name':'Salesforce','slug':'salesforce'}])
    assert observed[0]['status']=='label_match'
    assert observed[1]['status']=='not_in_returned_window'
    assert 'absence' in observed[1]['caveat']
