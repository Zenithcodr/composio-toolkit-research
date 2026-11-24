"""Build one self-contained case study plus machine-readable exports."""
from pathlib import Path
from html import escape
import csv, io, json
from research import ROOT, DATA, read, write, summarize, accuracy, now, catalogue_observations

def build():
    records=read(DATA/'results.json');summary=summarize(records)
    audit=read(DATA/'human_audit.json') if (DATA/'human_audit.json').exists() else []
    corrections=read(DATA/'corrections.json') if (DATA/'corrections.json').exists() else []
    automated=read(DATA/'automated_audit.json') if (DATA/'automated_audit.json').exists() else {'status':'pending','checks':[]}
    catalogue=read(DATA/'composio_check.json') if (DATA/'composio_check.json').exists() else {'status':'not_executed','reason':'No configured SDK key; no catalogue/API execution claimed.'}
    catalogue['observations']=catalogue_observations(records,catalogue.get('catalogue',[])) if catalogue.get('status')=='executed' else []
    catalogue['exact_label_matches']=sum(x['status']=='label_match' for x in catalogue['observations'])
    source_audit=read(DATA/'source_audit.json') if (DATA/'source_audit.json').exists() else {'status':'pending'}
    publication=read(ROOT/'publication.json') if (ROOT/'publication.json').exists() else {}
    human_review=read(DATA/'human_review_attestation.json') if (DATA/'human_review_attestation.json').exists() else {}
    payload={'records':records,'summary':summary,'audit':audit,'accuracy':{'first':accuracy(audit,'first_pass_grade'),'final':accuracy(audit,'final_grade')},'corrections':corrections,'automated':automated,'catalogue':catalogue,'source_audit':source_audit,'publication':publication,'human_review':human_review,'built_at':now()}
    encoded=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template=(ROOT/'src'/'report.html').read_text(encoding='utf-8')
    output=template.replace('__RESEARCH_DATA__',encoded)
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    (dist/'index.html').write_text(output,encoding='utf-8')
    write(dist/'results.json',records);write(dist/'verification.json',{'human_audit':audit,'human_review':human_review,'automated_audit':automated,'source_audit':source_audit,'corrections':corrections,'accuracy':payload['accuracy']})
    write(dist/'catalogue-observations.json',{'checked_at':catalogue.get('checked_at'),'returned_toolkits':catalogue.get('returned_toolkits'),'catalogue_partial':True,'observations':catalogue['observations']})
    catalogue_by_id={x['id']:x for x in catalogue['observations']}
    columns=['id','name','category','auth_methods','access','api_type','mcp_status','verdict','blockers','confidence','evidence_urls','composio_catalogue_observation']
    with (dist/'results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        for record in records:
            row={k:record.get(k,'') for k in columns};row['evidence_urls']=' | '.join(e['url'] for e in record['evidence'])
            row['composio_catalogue_observation']=catalogue_by_id.get(record['id'],{}).get('status','not_checked')
            for k,v in row.items():
                if isinstance(v,list):row[k]=' | '.join(v)
            writer.writerow(row)
    # No model answers in the checklist: the reviewer must read sources first.
    cards=[]
    for app in audit:
        sources=''.join(f'<li><a target="_blank" rel="noopener" href="{escape(u,quote=True)}">{escape(u)}</a></li>' for u in app['evidence_urls'])
        fields=''.join(f'<label>{escape(field)}<textarea data-id="{app["id"]}" data-field="{field}" placeholder="What does the official evidence establish? Note uncertainties."></textarea></label>' for field in app['checks'])
        cards.append(f'<section><h2>{app["id"]}. {escape(app["name"])}</h2><p>{escape(app["category"])}</p><ul>{sources}</ul>{fields}</section>')
    checklist='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Human verification worksheet</title><style>body{font:17px Georgia,serif;max-width:900px;margin:40px auto;padding:20px;background:#fafafa;color:#18212b}section{border-top:2px solid #18212b;padding:20px 0}label{display:block;margin:15px 0}textarea{display:block;width:95%;min-height:70px;font:16px sans-serif}button{padding:15px;font:16px sans-serif;background:#18212b;color:white;border:0;cursor:pointer}a{overflow-wrap:anywhere}header{position:sticky;top:0;background:#fafafa;padding:12px 0}</style><header><h1>20-app human evidence audit</h1><p>Read the sources. Record your own findings before viewing the model answer. This worksheet does not mark anything verified automatically.</p><button id="export">Download my observations</button> <span id="saved"></span></header>'''+''.join(cards)+'''<script>const key='composio-human-audit-v1';let saved={};try{saved=JSON.parse(localStorage.getItem(key)||'{}')}catch{}document.querySelectorAll('textarea').forEach(t=>{const k=t.dataset.id+':'+t.dataset.field;t.value=saved[k]||'';t.addEventListener('input',()=>{saved[k]=t.value;try{localStorage.setItem(key,JSON.stringify(saved));document.querySelector('#saved').textContent='Saved in this browser'}catch{document.querySelector('#saved').textContent='Use Download to save'}})});document.querySelector('#export').onclick=()=>{const data={reviewed_at:new Date().toISOString(),observations:saved};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='human-observations.json';a.click();URL.revokeObjectURL(a.href)};</script></html>'''
    (dist/'human-audit.html').write_text(checklist,encoding='utf-8')
    print('Built',dist/'index.html','with',len(records),'records and',len(audit),'human-review worksheets.')

if __name__=='__main__':build()
