# Toolkit Readiness — Composio Product Ops investigation

An evidence-first research agent and single-page case study covering the exact 100 assigned apps across ten categories. Author: Harshit Aman. Research snapshot: 23 November 2026.

## What ran, and what did not

The submission dataset was researched by Codex agents using live web search and first-party page opens. Work was partitioned into non-overlapping app ID ranges. Each researcher produced structured claims with actual source URLs and access caveats. The supervising agent consolidates these files, validates identities and evidence structure, challenges ambiguous findings, and builds the HTML report.

This is agent-assisted documentary research, not human collection of 100 rows and not proof of authenticated vendor execution. No paid app account is needed to establish a documented access gate. Public candidate submissions were not reused as data.

The Python CLI additionally implements a separately runnable Aerolink-backed retrieval/extraction pipeline. The initial dataset is **not represented as the output of an Aerolink run** while account-side free-only billing remains unverified. Composio SDK execution is recorded in `data/composio_check.json`: a genuine read-only call returned 1,000 toolkit labels. The build compares exact display labels against the assigned apps, with all nonmatches explicitly unknown because the returned catalogue window is partial. A label match does not establish vendor identity, endpoint coverage or official MCP support.

The 20-app human audit is pending until the author records real observations. No human-accuracy percentage is invented. Agent checks and schema validation are not substitutes for that audit.

## Quick start — no API key needed

Python 3.11+ is required; developed on Python 3.13. Create a virtual environment if desired, then:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python src/research.py check
python src/research.py build
python -m http.server 8086 --directory dist
```

Open `http://localhost:8086`. The generated `dist/index.html` embeds all research data. CSV, JSON and verification records are also exported. The optional `dist/human-audit.html` worksheet stores the reviewer's draft locally and exports observations without submitting them anywhere.

## Fresh research run

Use your own Aerolink account. Confirm its current base URL, Responses protocol, model identifier, free quota and billing behavior in the provider dashboard. Set values in the current process; never commit keys. `.env.example` contains names only and is not automatically loaded.

```powershell
$env:AEROLINK_BASE_URL = 'https://cgapi.aerolink.lat/v1'
$env:AEROLINK_MODEL = '<account-verified-model-id>'
# Configure AEROLINK_API_KEY privately in your process.
# Set this only after verifying free-only enforcement in your account:
$env:FREE_ALLOCATION_CONFIRMED = 'true'
python src/research.py research --limit 5
python src/research.py research
```

The client never calls the model unless the explicit allowance flag, key and model are present. The flag is a user assertion, **not a billing guarantee**: only the account/provider can enforce billing. Do not set it if requests could consume an unauthorised paid balance. The submission author selected free allocation only.

The research pipeline fetches public official hints, discovers relevant same-domain documentation links, extracts typed JSON from fetched text, validates source URLs, and checkpoints per app under `data/live`. Three workers are used, with bounded fetches and retries. Rerunning skips completed records. Fetch failures and review-needed cases are recorded rather than silently dropped. Independent rechecks use a separate output directory and do not read first-pass answers:

```powershell
python src/research.py verify --ids 1 11 21
```

To directly re-fetch cited documentation URLs, run `python src/research.py sources`. It fetches newly added URLs and carries forward dated existing checks; use `--refresh` for a full fresh pass. Reachability is not a semantic accuracy score. The checked-in source-audit record preserves both successful retrievals and access/fetch failures.

The HTTP retriever blocks local/private destinations and credential-bearing URLs. It does not bypass authentication, bot checks or payment gates. Browser-assisted follow-up is separately labelled when documentation cannot be fetched automatically. A successful schema parse does not establish factual correctness.

## Optional Composio catalogue check

```powershell
python -m pip install composio
# Configure COMPOSIO_API_KEY privately and verify free-only allowance.
python src/research.py catalogue
```

This is a catalogue-metadata check, not a claim of successful vendor API access or an official vendor MCP. If not configured, an explicit `not_executed` status is written. Never infer an MCP from toolkit presence.

## Research and verification contracts

- `data/apps.json`: immutable assignment identities and hints.
- `data/research`: original agent records, each with evidence, access conditions and a scoped verdict.
- `data/first_pass.json`: frozen baseline, never overwritten by corrections.
- `data/corrections.json`: explicit changes with reasons and source URLs.
- `data/results.json`: baseline plus documented corrections.
- `data/human_audit.json`: two apps per category, selected with seed 42 plus a lower-confidence pick. Six decision fields per app.

Access conditions overlap: free credentials can coexist with paid production features, admin approval or partner review. `build_now` refers only to the documented narrow scope. `not_established` means the review did not establish a fact; it does not prove absence. CLI tools can be wrapped locally and are not rejected just because they lack REST.

Human accuracy is fully correct fields divided by correct + partial + incorrect adjudicated fields, with pending and unresolved counts displayed separately. The same human reference and sample must be used before and after corrections. A percentage describes that sample, not all 100 apps. Do not label any check human unless the named author actually performs it.

After the author exports observations from the worksheet, import them with `python src/research.py import-audit PATH --reviewer "Harshit Aman"`. Only complete six-field app references are marked reviewed. Importing does not auto-generate correct grades; those must be adjudicated against the recorded reference. The original agent research remains frozen.

## Limitations

Documentation is a dated snapshot. Plan eligibility, pricing, endpoints and MCP availability can change. Some pages are gated, JavaScript-only or inaccessible to automated retrieval. A public API description is not proof that a production credential or partner approval can be obtained. No live vendor calls are claimed. The source records retain those limitations rather than treating them as negative facts.

## Publication

The report is a static site. Public publication and GitHub ownership are checked separately. No API keys are deployed to the browser. The repository includes only this project; unrelated résumés, account files and private preparation notes are excluded.
