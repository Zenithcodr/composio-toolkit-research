"""Apply explicitly reviewed evidence refinements; never invent human accuracy."""
from research import DATA, read, write, now, apply_corrections
import hashlib

def main():
    baseline=read(DATA/'first_pass.json');original={r['id']:r for r in baseline}
    independent=[]
    for path in sorted((DATA/'independent').glob('recheck_*.json')):independent.extend(read(path))
    refs={r['id']:r for r in independent}
    assert len(refs)==20
    definitions={
      10:('access_entitlement_and_surface_refinement',['access','auth_methods','api_breadth'],
          'Specific DealCloud MCP docs resolve Celeste licensing and roles, distinguish REST token exchange from per-user MCP OAuth, and document separately enabled write tools.'),
      61:('surface_completeness',['api_type'],
          'The first pass omitted the separately documented GitHub GraphQL API; REST and MCP remain supported.'),
      62:('stale_restriction',['blockers'],
          'Current Vercel documentation permits CIMD-based MCP clients without a prior vendor review. The older approved-client-only blocker was too restrictive. The verdict remains conservative because product entitlements still vary.'),
      78:('resolved_evidence_gap',['auth_methods','api_type','api_breadth','notes'],
          'Official Coda API material and the vendor Postman introduction establish REST authentication and resource families despite a failed direct-reference redirect. This resolves an evidence gap rather than proving a live credential.'),
      34:('resolved_access_and_scope_gap',['access','auth_methods','api_type','api_breadth','notes'],
          'Current HighLevel pricing and technical docs resolve trial/paid subscription context and separate operational MCP sign-in from REST tokens and the Developer MCP.'),
      37:('scope_narrowing_and_auth_refinement',['access','auth_methods','api_type','api_breadth','notes'],
          'Systeme.io developer and help docs disagree about MCP breadth. The final answer keeps their common confirmed subset, records that conflict, and specifies the actual API/MCP headers.'),
      44:('resolved_mcp_gap',['auth_methods','api_type','api_breadth','mcp_status','notes'],
          'Salesforce publishes a B2C-specific MCP with operational SCAPI Admin tooling. General CRM MCP evidence was not substituted; tenant credentials and admin entitlements remain required.'),
      53:('architecture_constraint',['auth_methods','api_breadth','notes'],
          'Ahrefs documents MCP authentication and restricts repurposing its hosted MCP as a generic backend bridge. A new toolkit should use the documented REST API.'),
      54:('resolved_mcp_gap',['auth_methods','api_type','api_breadth','mcp_status','verdict','notes'],
          'The directly opened vendor MCP guide documents a current seven-tool server and supported authentication. This resolves the unestablished MCP finding and supports a scoped prototype.'),
      92:('resolved_rest_and_access_gap',['auth_methods','access','api_type','api_breadth','notes'],
          'Otter’s Enterprise Public API is documented separately from its OAuth MCP. A missing generic MCP key is not evidence that REST is unavailable; plan-specific access is now explicit.'),
      100:('scope_and_entitlement_completeness',['auth_methods','api_type','api_breadth','notes'],
          'A dedicated Grain API article explicitly establishes free personal access, while workspace-wide REST and premium MCP features have separate gates.'),
    }
    corrections=[]
    for ident,(kind,fields,reason) in definitions.items():
        ref=refs[ident];findings=ref['findings'];old=original[ident]
        changes={field:(ref['notes'] if field=='notes' else findings[field]) for field in fields if field!='blockers'}
        if ident==62:
            changes['blockers']=['MCP clients must support CIMD or use a reviewed Vercel client; CIMD clients do not need review.','Hobby and paid product entitlements and usage limits differ.']
        if ident==10:
            changes['blockers']=['DealCloud with Celeste license required for vendor MCP.','Admins configure MCP; users need Celeste Member and MCP Access.','MCP write tools must be separately enabled.']
            changes['notes']='REST token exchange and MCP per-user OAuth are separate credential routes. The public documentation establishes a licensed tenant integration, not a free developer tenant or public partner enrollment.'
        if ident==53:changes['blockers']=old['blockers']+['Vendor hosted MCP is not a general-purpose bridge for custom backend scripts; use REST for a new programmatic connector.']
        if ident==92:changes['blockers']=['Direct Public API requires Enterprise entitlement; MCP and REST access are different products/scopes.']
        merged={e['url']:e for e in old['evidence']}
        for e in ref['evidence']:merged[e['url']]=e
        changes['evidence']=list(merged.values())
        corrections.append({'id':ident,'kind':kind,'field':', '.join(f for f in changes if f!='evidence'),'reason':reason,
          'evidence_urls':[e['url'] for e in ref['evidence']],'changes':changes,
          'before':{f:old.get(f) for f in changes if f!='evidence'},'adjudicated_by':'Supervising AI agent; not a human audit','adjudicated_at':now()})
    # Supervising source-map audit: add explicit protocol evidence and remove
    # a plan gate that the original Devin source did not actually establish.
    for ident,changes,reason,evidence in [
      (33,{},'The LinkedIn API type was correct but lacked an explicit field-to-source mapping. The current versioning guide demonstrates the HTTPS REST base path and headers.',
       [{'url':'https://learn.microsoft.com/en-us/linkedin/marketing/versioning?view=li-lms-2026-11','title':'LinkedIn Marketing API Versioning','source_type':'first_party','supports':['api_type'],'excerpt':'Vendor versioning docs show the HTTPS /rest API base path, HTTP version headers and a campaign-creation request.','retrieved_at':now()}]),
      (96,{'access':['unresolved'],'blockers':['Devin account credentials and appropriate organisation permissions are required.','Exact API/MCP entitlement on current Free versus paid plans was not established from the public comparison.'],
           'notes':'Devin MCP is authenticated; free DeepWiki is a separate service. Current pricing includes a Free product tier but the extracted comparison does not establish whether its API is included. Do not infer that every Devin account is paid or that Free grants API access.'},
       'The original paid-plan/admin classification exceeded its cited evidence. Authentication and current pricing verify account/role distinctions but leave exact Free API entitlement unresolved, so remove the unsupported mandatory gates.',
       [{'url':'https://docs.devin.ai/api-reference/authentication','title':'Devin API Authentication','source_type':'first_party','supports':['auth_methods','access'],'excerpt':'Service-user keys and personal tokens inherit their principal’s roles and organisation membership; using a personal token is distinct from provisioning a service user.','retrieved_at':now()},
        {'url':'https://devin.ai/pricing','title':'Devin Plans and Pricing','source_type':'first_party','supports':['access'],'excerpt':'Current pricing lists Free and paid product plans. The extracted comparison does not unambiguously establish Free API entitlement.','retrieved_at':now()}])]:
        old=original[ident];changes=dict(changes)
        merged={e['url']:e for e in old['evidence']}
        for e in evidence:merged[e['url']]=e
        changes['evidence']=list(merged.values())
        corrections.append({'id':ident,'kind':'source_mapping_refinement' if ident==33 else 'unsupported_gate_removed','field':', '.join(f for f in changes if f!='evidence') or 'evidence mapping','reason':reason,'evidence_urls':[e['url'] for e in evidence],'changes':changes,'before':{f:old.get(f) for f in changes if f!='evidence'},'adjudicated_by':'Supervising AI source-map audit; not human verification','adjudicated_at':now()})
    write(DATA/'corrections.json',corrections)
    write(DATA/'results.json',apply_corrections(baseline,corrections))
    changes={c['id']:c for c in corrections if c['id'] in refs}
    write(DATA/'automated_audit.json',{
      'status':'completed','method':'Independent AI-agent re-research of a stratified 20-app sample; each verifier saved findings before viewing the first pass. Supervising AI reviewed disagreements. This is not human verification.',
      'checked_at':now(),'sample_size':20,'sample_ids':sorted(refs),'sample_apps_refined':len(changes),'additional_supervising_audit_refinements':2,
      'accuracy_percentage':None,'accuracy_note':'No semantic accuracy percentage is inferred from wording differences or agent agreement; human reference decisions are pending.',
      'checks':[{'id':ident,'name':ref['name'],'outcome':changes[ident]['kind'] if ident in changes else ('publisher_identity_still_unresolved' if ident==50 else 'substantially_corroborated'),
        'notes':ref['notes'],'evidence_urls':[e['url'] for e in ref['evidence']]} for ident,ref in sorted(refs.items())],
      'judgment_differences_excluded':[{'id':25,'note':'Pumble narrow-prototype versus constrained verdict is a scope judgment, not a factual error.'},{'id':62,'note':'Vercel verdict was kept constrained; only the outdated approved-client restriction was corrected.'}],
      'unaccepted_refinements':[{'id':50,'reason':'Rendered FanBasis-branded demo docs clarify a narrow checkout interface, but first-party linkage and merchant API eligibility remain unverified. Keep unresolved and do not upgrade the demo to conclusive first-party authority.'}]
    })
    checksum=hashlib.sha256((DATA/'first_pass.json').read_bytes()).hexdigest()
    checksum_file=DATA/'first_pass.sha256'
    if checksum_file.exists():assert checksum_file.read_text().strip()==checksum,'Frozen baseline changed'
    else:checksum_file.write_text(checksum+'\n',encoding='ascii')
    print('Preserved baseline; applied',len(corrections),'refinement groups from the independent20-app recheck and additional supervising audit. Human accuracy remains pending.')

if __name__=='__main__':main()
