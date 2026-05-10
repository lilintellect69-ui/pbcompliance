# PrivateBox POPIA Architecture Pack

PB-curated source matrix for authoring `frameworks/popia/popia.yaml`. Captured from session 2026-05-10. Mirrors the structure of the ISO 42001 pack at `frameworks/iso-42001/source/`.

Eight tables follow:
1. Master Obligation Matrix (statutory thematic areas)
2. Eight Conditions for Lawful Processing
3. Responsible Party / Operator / Shared Responsibility Matrix (10 deployment scenarios)
4. Special PI / Children / Prior Authorisation Matrix
5. Security Safeguards / Incident / Access Control Matrix
6. Data Lifecycle / Purpose / Retention / Cross-Border Matrix
7. Data Subject Rights / Notice / PAIA Interface Matrix
8. External Claims / Trust Pack / Sales Language Matrix

(Full text follows in the YAML build's authoring; rather than duplicating tables here, the YAML's `pb_interpretation`, `documented_evidence`, `failure_modes`, `external_safe_phrasing` and scenario records are derived directly from these tables. See `frameworks/popia/popia.yaml`.)

## Table 1 — Master Obligation Matrix

Rows cover: scope/definitions, accountability, processing limitation, purpose specification & retention, further processing limitation, information quality, openness/documentation/notice, security safeguards, operator duties, breach notification, data subject participation, special PI, children, prior authorisation, direct marketing & automated decisions & cross-border, information officers, enforcement.

## Table 2 — Eight Conditions

1. Accountability (s 8)
2. Processing limitation — lawful/reasonable/minimal (ss 9–10)
3. Processing limitation — consent/justification/objection (s 11)
4. Processing limitation — direct collection (s 12)
5. Purpose specification (ss 13–14)
6. Further processing limitation (s 15)
7. Information quality (s 16)
8. Openness (ss 17–18)
9. Security safeguards (ss 19–22)
10. Data subject participation (ss 23–25)

(Note: POPIA's eight conditions canonically are #1, #2 [aggregating processing limitation sub-rules], #5, #6, #7, #8, #9, #10 above. The pack splits #2 into 3 sub-rows for granularity. Authored YAML uses 8 condition entries per the canonical structure with sub-rules captured as `documented_evidence` / `pb_interpretation` detail.)

## Table 3 — Responsible Party / Operator / Shared Responsibility (10 scenarios)

1. Pure on-prem deployment, no remote support, no telemetry
2. On-prem with signed offline / pull-only updates
3. On-prem with remote admin
4. On-prem with telemetry
5. Support-access troubleshooting using live customer prompts or documents
6. Managed RAG / document-ingestion assistance
7. Hosted update repository or model package distribution
8. Vendor-run backup support involving customer data copy
9. Offshore support engineer accesses incident data
10. PrivateBox website, CRM, bids, billing, staff data (PB's own corporate processing)

## Table 4 — Special PI / Children / Prior Authorisation

Categories: health, biometrics, criminal behaviour, children's PI, unique identifiers across responsible parties, profiling/automated decision-making, foreign transfer of special/children PI, pharmacy/healthcare deployments.

## Table 5 — Security Safeguards / Incident / Access Control

CIA safeguards, risk identification, least privilege, admin access, operator oversight, support access, logging & audit trails, update integrity, telemetry minimisation, incident response & section 22 workflows, decommissioning & disposal, RAG stores / prompt / output handling.

## Table 6 — Data Lifecycle / Purpose / Retention / Cross-Border

Stages: collection, ingestion/import, storage, use/query, further processing/analytics, retrieval/export, output handling, retention, deletion/decommission, cross-border access / remote support.

## Table 7 — Data Subject Rights / Notice / PAIA Interface

Rights: access/confirmation, correction, deletion/destruction, objection, privacy notices, PAIA manual, information officer duties, complaints/regulator engagement.

## Table 8 — External Claims / Trust Pack / Sales Language

Topics: POPIA alignment, on-prem benefit, vendor access, cross-border, security, operator role, direct marketing, healthcare sensitivity. Pre-approved phrasing per topic for website / procurement / security pack.

## Authoring approach

- 8 condition entries (`popia-cond-1` through `popia-cond-8`) cover Chapter 3 conditions (ss 8–25 scaffolding).
- ~13 section entries (`popia-s-*`) cover obligations outside or beneath the 8 conditions: special PI (ss 26–33), children (ss 34–35), IO (ss 55–56), prior auth (ss 57–58), enforcement (ss 60–68), direct marketing (s 69), automated decisions (s 71), cross-border (s 72), offences (ss 89–109).
- 10 scenarios from Table 3 → schema `scenarios[]` with role allocation in POPIA terms (responsible party / operator / shared).
- Evidence families consolidated from Tables 5–7 (~15 families).
- External-safe phrasing taken directly from Table 8 (per-topic procurement / security pack / website variants).
- Crosswalks Phase A: popia.yaml outgoing only to ISO 27001 where POPIA s 19 maps to 27001 Annex A security controls.
- Crosswalks Phase B: retroactive edits to iso-42001.yaml (per existing PENDING-CROSSWALKS.md), iso-27701.yaml, eu-ai-act.yaml to add POPIA crosswalks where standards support POPIA compliance.
