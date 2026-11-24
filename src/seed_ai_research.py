"""Record the supervising agent's live first-party web investigation (apps 91–100).

This is evidence serialization, not an assertion that Aerolink/Composio ran.
"""
from research import DATA, read, write, now

def ev(url,title,supports,excerpt):
    return dict(url=url,title=title,source_type='first_party',supports=supports,excerpt=excerpt,retrieved_at=now())

def main():
    apps={a['id']:a for a in read(DATA/'apps.json')};records=[]
    def add(ident,description,auth,access,api,breadth,capabilities,mcp,verdict,blockers,confidence,evidence,notes):
        a=apps[ident]
        records.append(dict(id=ident,name=a['name'],category=a['category'],description=description,auth_methods=auth,access=access,api_type=api,api_breadth=breadth,capabilities=capabilities,mcp_status=mcp,composio_status='not_checked',verdict=verdict,blockers=blockers,confidence=confidence,evidence=evidence,notes=notes,researched_at=now(),research_method='Codex agent web search and first-party document opens; no vendor-account/API execution'))
    add(91,'Enterprise notebook research and source-grounded summaries.',
        ['OAuth2 user access token'],['paid_plan','admin_approval'],'REST',
        'Notebook lifecycle and sharing; API preview scoped to licensed enterprise users.',
        ['Create and retrieve notebooks','List notebooks','Share notebooks'],
        'not_established','build_with_constraints',['Enterprise license, Cloud project setup and NotebookLM IAM role required'],'high',[
        ev('https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks','Create and manage notebooks API',['auth_methods','access','api_type','api_breadth','verdict'],'Notebook management uses authenticated licensed users and the discoveryengine notebook API; setup requires the NotebookLM user role.')],
        'Assigned NotebookLM hint refers to the enterprise product. Do not imply that a free consumer NotebookLM account exposes this API. Official MCP support was not established in reviewed sources.')
    add(92,'Meeting transcription and searchable meeting knowledge.',
        ['OAuth2'],['unresolved'],'MCP',
        'Meeting search and transcript retrieval through the vendor MCP; general public REST access not established.',
        ['Search meetings','Retrieve meeting transcripts','Access authorised shared conversations'],
        'vendor_official','build_with_constraints',['Plan eligibility and custom API application access need confirmation'],'medium',[
        ev('https://help.otter.ai/hc/en-us/articles/35287607569687-Otter-MCP-Server','Otter MCP Server',['auth_methods','api_type','api_breadth','mcp_status','verdict'],'Official OAuth-authenticated MCP endpoint supports meeting search and transcripts; the FAQ says a public API key is not available and directs custom application questions to support.')],
        'An existing MCP integration is feasible; creating an independent REST connector is a different access question. No assertion that MCP is free on every Otter plan.')
    add(93,'Meeting recording, transcription, summaries and follow-up automation.',
        ['API key','OAuth2'],['self_serve_free'],'REST; webhooks',
        'Meetings, transcripts, summaries, action items and recording downloads; signed meeting-ready webhooks.',
        ['Retrieve recordings and transcripts','Read summaries and action items','Receive signed webhooks'],
        'vendor_official','build_now',['Per-user visibility; no organisation-wide API key'],'high',[
        ev('https://www.fathom.ai/features/api','Fathom API',['auth_methods','access','api_type','api_breadth','mcp_status','verdict'],'Self-generated user API keys, OAuth apps, webhooks and SDKs are included on all plans including Free; the page distinguishes the vendor MCP from the API.'),
        ev('https://developers.fathom.ai/','Fathom developer introduction',['api_type','api_breadth'],'Developer documentation covers quickstart, API endpoints, webhooks, SDKs and public OAuth apps.')],
        'Buildable for the authorising user’s visible meetings; do not promise access to other users’ unshared recordings. Documentation evidence only, not a tested connection.')
    add(94,'Evidence-based scientific literature search for research workflows.',
        ['OAuth2','API key (Bearer)'],['self_serve_free','paid_plan'],'MCP; API',
        'Scientific search and structured paper findings; plan-dependent monthly pools.',
        ['Search scientific papers','Retrieve structured research findings'],
        'vendor_official','build_with_constraints',['Owner plan limits and monthly API/MCP usage pool apply'],'high',[
        ev('https://docs.consensus.app/consensus-mcp','Consensus MCP setup',['auth_methods','access','api_type','api_breadth','mcp_status','verdict'],'Official MCP supports OAuth or profile-created bearer keys. Free accounts can connect; keys inherit their owner’s plan limits and shared monthly API usage pool.')],
        'OAuth was an assignment hint, not the only supported method. Public documentation now also explains API-key authentication. This research does not establish unlimited free searches.')
    add(95,'Document parsing, extraction, classification and editing for AI pipelines.',
        ['API key','OAuth device flow (local tooling)'],['self_serve_free','paid_plan'],'REST; SDK; MCP',
        'Parse, extract, split, classify, edit and upload documents; hosted and local agent interfaces.',
        ['Parse documents','Extract structured fields','Split and classify','Upload files'],
        'vendor_official','build_with_constraints',['Metered document-processing allowance; hosted MCP cannot read local files directly'],'high',[
        ev('https://docs.reducto.ai/quickstart','Reducto API quickstart',['auth_methods','access','api_type','api_breadth'],'Quickstart offers free account creation and API-key setup for document parsing. Free registration does not establish unlimited processing.'),
        ev('https://docs.reducto.ai/mcp-server','Reducto MCP server',['auth_methods','api_type','api_breadth','mcp_status','verdict'],'Vendor hosts a bearer-key MCP and provides local tooling with browser device login. Hosted upload accepts public URLs; local-file access requires the local server.')],
        'Separate credential self-service from processing cost. API and local-tool credential flows differ.')
    add(96,'Autonomous software engineering sessions and repository knowledge.',
        ['API key','personal access token','service user key'],['paid_plan','admin_approval'],'REST; MCP',
        'Repository documentation plus sessions, playbooks, knowledge, schedules and integrations.',
        ['Query repository documentation','Manage engineering sessions','Manage playbooks and knowledge'],
        'vendor_official','build_with_constraints',['Appropriate Devin account entitlement and organisation-scoped credentials required'],'medium',[
        ev('https://docs.devin.ai/work-with-devin/devin-mcp','Devin MCP',['auth_methods','api_type','api_breadth','mcp_status','verdict'],'Official MCP requires Devin credentials. Current service-user and personal tokens support organisation tools; legacy keys only support repository-documentation tools. Enterprise tokens require an organisation header.')],
        'Devin MCP is authenticated; free public DeepWiki MCP is a separate service, not proof of free Devin platform access. Exact account plan eligibility should be checked before implementation.')
    add(97,'AI image and video generation through account tools and a separate developer API.',
        ['browser sign-in (CLI/MCP)','API key (developer API)'],['paid_plan'],'REST; CLI; MCP',
        'Media generation, status polling, cancellation, uploads and agent tooling.',
        ['Generate images and video','Poll and cancel generation','Upload reference files'],
        'vendor_official','build_with_constraints',['CLI/MCP plan credits differ from a separately funded API balance'],'high',[
        ev('https://higgsfield.ai/blog/higgsfield-cli','Higgsfield CLI integration routes',['auth_methods','access','api_type','api_breadth','mcp_status','verdict'],'CLI and MCP use browser sign-in and plan credits; the developer REST API uses an API key and a separate prepaid balance.'),
        ev('https://open.higgsfield.ai/quick-start','Higgsfield API quickstart',['auth_methods','api_type','api_breadth'],'REST generation uses the full copied API key, returns asynchronous request identifiers, and exposes polling, cancellation and uploads.')],
        'Do not reuse the user’s unrelated Aerolink allowance for media generation or assume free UI generations apply to API/CLI calls.')
    add(98,'Local rendering of Mermaid definitions into diagrams.',
        ['none (local process)'],['local_open_source'],'Local CLI; JavaScript module',
        'Diagram rendering to SVG, PNG and PDF from local source.',
        ['Render diagram files','Convert Mermaid-containing Markdown','Use a local JavaScript rendering interface'],
        'not_established','build_now',['Install the supported Node/browser runtime; isolate untrusted diagram execution'],'high',[
        ev('https://github.com/mermaid-js/mermaid-cli','Mermaid CLI repository',['auth_methods','access','api_type','api_breadth','verdict'],'Maintainer repository documents local CLI rendering and programmatic use. It is open-source local software rather than an authenticated hosted REST service.'),
        ev('https://github.com/mermaid-js/mermaid-cli/blob/master/LICENSE','Mermaid CLI license',['access'],'The official repository publishes an MIT license.')],
        'A local agent tool can wrap the CLI. No official MCP was established in this review; absence of a REST API is not a blocker for local agent-callable skills.')
    add(99,'TranscriptAPI retrieval of YouTube transcripts, search and channel metadata.',
        ['API key (Bearer)'],['self_serve_trial','paid_plan'],'REST; MCP',
        'Transcripts, language metadata, video search, channel feeds and playlist videos.',
        ['Retrieve transcripts','Search videos','List channel and playlist videos'],
        'vendor_official','build_now',['Starter credits are finite; ongoing usage is metered'],'high',[
        ev('https://transcriptapi.com/','TranscriptAPI API and MCP documentation',['auth_methods','access','api_type','api_breadth','mcp_status','verdict'],'Vendor documents bearer-key REST calls, its own MCP endpoint, supported YouTube data tools and 100 initial credits without a card.')],
        'Assigned hint is transcriptapi.com, a third-party provider. Its official MCP is official to TranscriptAPI, not an official Google/YouTube MCP or unrestricted access to every video.')
    add(100,'Meeting recordings, transcripts, notes and workspace insights.',
        ['personal access token','workspace access token','OAuth2'],['self_serve_free','paid_plan','admin_approval'],'REST; MCP',
        'Personal/workspace meeting data and OAuth integrations; MCP uses personal scope.',
        ['Read meeting records','Access transcripts','Build OAuth integrations','Query meeting data through MCP'],
        'vendor_official','build_with_constraints',['Workspace tokens require admin authority and plan entitlement; MCP does not accept workspace-scope tokens'],'high',[
        ev('https://developers.grain.com/authentication.html','Grain authentication',['auth_methods','access','api_type','api_breadth','verdict'],'Personal and workspace tokens plus OAuth are documented. Workspace scope is plan-restricted and admin-only; personal tokens also authenticate the MCP server.'),
        ev('https://developers.grain.com/mcp/','Official Grain MCP',['mcp_status','api_breadth'],'Grain publishes a first-party MCP quickstart for meeting context and analytics.')],
        'This is grain.com meeting software, not the unrelated rungrain.com developer workspace. Personal-scope and organisation-wide connector readiness are different.')
    write(DATA/'research'/'apps_091_100.json',records)
    print('Serialized',len(records),'live-researched app records.')

if __name__=='__main__': main()
