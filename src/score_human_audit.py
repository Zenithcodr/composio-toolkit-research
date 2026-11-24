"""Reproduce disclosed adjudication against existing author-confirmed references.

This does not perform a human review, create reference answers or award accuracy
for wording changes. The explicit semantic exceptions below are review decisions.
"""
import ast
import hashlib
from research import DATA, read, write, accuracy

SEMANTIC_EQUIVALENTS = {
    (34, 'auth_methods'): 'The same private-integration bearer token, OAuth and interactive hosted-MCP sign-in routes were already identified; the reference clarifies their scopes.',
    (37, 'auth_methods'): 'Both distinct API and MCP keys were identified. Header names add implementation detail without changing the authentication families.',
    (54, 'verdict'): 'Both verdicts permit a toolkit. A constrained overall integration versus a narrow build-now prototype is a conservative scope judgment, not a factual error.',
    (100, 'auth_methods'): 'Personal tokens, workspace tokens and OAuth were already identified. The reference adds bearer, PKCE and token-scope details.',
    (100, 'api_type'): 'REST plus MCP and HTTP/REST API v2 plus MCP describe the same interface families.',
}

def reference_value(value):
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value.strip()
    return value

def main():
    attestation = read(DATA/'human_review_attestation.json')
    assert attestation['personally_checked_official_documentation'] is True
    raw = (DATA/'first_pass.json').read_bytes()
    lf = raw.replace(b'\r\n', b'\n')
    hashes = {hashlib.sha256(value).hexdigest() for value in (raw, lf, lf.replace(b'\n', b'\r\n'))}
    assert (DATA/'first_pass.sha256').read_text().strip() in hashes, 'Original baseline changed'
    baseline = {a['id']:a for a in read(DATA/'first_pass.json')}
    final = {a['id']:a for a in read(DATA/'results.json')}
    audit = read(DATA/'human_audit.json')
    assert len(audit) == attestation['sample_size'] == 20
    unresolved = set(attestation['unresolved_app_ids'])
    for app in audit:
        assert app['reviewer'] == attestation['reviewer'] and app['reviewed_at']
        for field, check in app['checks'].items():
            assert check['reference'], 'Missing actual author reference'
            if app['id'] in unresolved:
                check.update(first_pass_grade='unresolved', final_grade='unresolved',
                             note=attestation['unresolved_reason'])
                continue
            ref = reference_value(check['reference'])
            assert reference_value(final[app['id']][field]) == ref, f'Final answer needs fresh adjudication: {app["id"]}:{field}'
            check['final_grade'] = 'correct'
            if reference_value(baseline[app['id']][field]) == ref:
                check.update(first_pass_grade='correct', note='The preserved first-pass claim and final claim agree with the author-confirmed reference.')
            elif (app['id'],field) in SEMANTIC_EQUIVALENTS:
                check.update(first_pass_grade='correct', note=SEMANTIC_EQUIVALENTS[(app['id'],field)])
            else:
                check.update(first_pass_grade='partial', note='The first pass omitted or insufficiently scoped a material authentication route, access condition, interface or capability established in the reference. The documented final correction resolves that omission; this is not merely a wording comparison.')
    write(DATA/'human_audit.json', audit)
    print({'first_pass':accuracy(audit,'first_pass_grade'), 'final':accuracy(audit,'final_grade')})

if __name__ == '__main__':
    main()
