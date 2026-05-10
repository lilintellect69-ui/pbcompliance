---
name: compliance-framework-author
description: Use this skill whenever authoring a new compliance framework YAML for the PrivateBox GRC OS, or substantially editing an existing one. Triggers when the user references a framework not yet in frameworks/ (e.g., ISO 42001, NIST SSDF, SOC 2, POPIA, King V, COBIT), asks to "add a framework," or asks to extend the framework set. Also use when materially restructuring existing frameworks. Do NOT use for small fixes to existing frameworks (typos, single-field edits) — direct YAML editing is fine for those.
---

# Authoring a compliance framework YAML

This skill codifies the authoring methodology proven on ISO 27001, ISO 27701, and EU AI Act. Read this skill in full before touching any framework YAML.

## When to use

- Adding a new framework to `frameworks/`
- Substantially restructuring an existing framework (e.g., schema v2 → v3 migration)
- Onboarding a fork or variant (e.g., NIST 800-218A as separate from SSDF)

## Required inputs before authoring

1. **Source standard text** in `frameworks/<id>/source/`. PDF, MD, TXT, HTML are all fine. Don't author from memory or summary; the standard's exact structure matters.
2. **A populated `pb_application` block** in the YAML (or willingness to draft one with the user). This includes `why_chosen`, `scope_decisions` per business model, and `top_risks`.
3. **Knowledge of which frameworks are already in `frameworks/`** to determine crosswalk direction (more-specific/newer → more-general/older; ISO 27001 is target-only).

## Output structure

A complete framework YAML has these top-level fields. Do not invent new top-level fields without updating `docs/schema-v2.md` and `build/validate_framework.py`.

```yaml
schema_version: "2.0"
id: <framework-id>                  # kebab-case, e.g. iso-42001
full_name: "<full standard title>"
version: "<official version>"
issuer: "<ISO|NIST|EU|...>"
type: <enum>                        # see schema-v2.md
audit_type: <enum>                  # certifiable | attestation | regulatory_supervision | ...
certifiable: true|false
companion_standards: []             # other standards that pair with this one
effective_dates: []                 # phased dates (especially for regulations)
roles: []                           # role names defined by the framework
tiers: []                           # risk tiers if framework defines them
shared_responsibility_model: []     # who-does-what across PB / customer / partners
soa_guidance: {}                    # if the framework has a Statement of Applicability concept
pb_interpretation_version: "<x.y>"
pb_interpretation_owner: <person|null>
pb_interpretation_last_reviewed: <date|null>

pb_application:
  why_chosen: |
    <multi-line prose: why this framework matters for PB; market/regulatory driver>
  scope_decisions:
    on_prem:
      coverage: full|partial|none
      rationale: <prose>
    ai_factory:
      coverage: full|partial|none
      rationale: <prose>
  top_risks:                        # ~5-8 risks
    - <prose: risk in 1-2 sentences, ideally with framework refs>

evidence_families:                  # 15-25 typical
  - id: <kebab-case>
    name: <human-readable>
    examples: [<list of 3-7 example artifacts>]
    why_auditor_cares: <one sentence>
    cadence: <Annual / On change / Quarterly / etc.>
    typical_owner: PB|PB-SH|SH|SH-CL|CL

scenarios:                          # 0-15 typical; mostly relevant for risk-tiered frameworks
  - id: <kebab-case>
    framework_specific_id: <e.g. AI-006 for AI Systems Registry>
    name: <one line>
    description: <prose>
    risk_tier: <if framework defines tiers>
    applies_to_business_models: [on-prem, ai-factory]
    triggered_requirements: [<id>, <id>]

open_questions:                     # 0-15 typical; one per unresolved governance/business decision
  - id: <kebab-case starting with oq->
    question: <prose>
    context: <prose>
    blocks_requirements: [<id>, <id>]
    blocks_scenarios: [<id>]
    decision_status: pending|resolved|deferred
    resolution: <if resolved>
    resolution_date: <if resolved>

requirements:                       # the bulk of the file
  - id: <framework-id>-<group>-<native-id>      # e.g. iso-42001-cl-4.1
    native_id: <as in source>                   # e.g. 4.1
    kind: requirement|objective|principle|practice|clause
    group: <native grouping label>              # e.g. "Context of the organization"
    title: <short>
    business_models: [on-prem, ai-factory]      # required
    
    # ONE of these is required (validator enforces):
    requirement: |
      <verbatim or close-paraphrase of the requirement>
    objective: |
      <if framework expresses as an objective rather than a hard requirement>
    
    owner: PB|PB-SH|SH|SH-CL|CL                 # default ownership
    owner_by_model:                             # only if ownership genuinely differs
      on_prem: <owner>
      ai_factory: <owner|{status: pending, open_question: oq-...}>
    applies: <which PB scopes this applies to>
    maturity_target: SA|AR|Cert                 # Self-Asserted, Audit-Ready, Certified
    tier: <if framework has tiers and req is tier-specific>
    role_applicability: [<role-id>, ...]        # if framework has roles
    
    pb_interpretation: |
      <prose: what does PB take this to mean operationally>
    
    documented_evidence: [<list of artifact descriptions>]
    operational_evidence: [<list of process/log/observation descriptions>]
    audit_methods: [Insp, Int, Samp, Obs, Rep]  # one or more
    
    pitfalls: [<common failure modes>]
    good_vs_audit_ready: |
      Good: <prose>
      Audit-ready: <prose what auditors will additionally want>
    
    external_safe_phrasing: |
      <one-paragraph defensible non-overclaiming statement; goes into Trust Packs>
    
    crosswalk:                                  # cross-framework references
      - framework: <other-framework-id>
        refs: [<other-req-id>, ...]
        note: <prose explaining the relationship>
    
    triggered_by_scenarios: [<scenario-id>, ...]
```

## Authoring workflow

### Step 1: Plan

Before writing any YAML, produce a build plan covering:

- **Estimated requirement count** (look at the source standard: count clauses, articles, control items)
- **Group structure** (the source's native grouping — clauses 4-10 + Annex A for ISO 27001-style; chapters for regulations; trust services criteria for SOC 2)
- **Audit type** (certifiable, attestation, regulatory supervision, advisory)
- **Whether it has tiers** (risk classes, criticality levels)
- **Whether it has roles** (controller/processor; provider/deployer)
- **Phased effective dates** (for regulations)
- **Known crosswalks** (which existing frameworks does it relate to; in which direction)
- **Open questions surfaced during reading** (governance/business decisions PB hasn't made)

Show this plan to the user. Don't proceed to authoring without sign-off.

### Step 2: Skeleton

Write the framework-level metadata + `pb_application` block + `evidence_families` first. Validate it with `make validate` (the validator allows a partial file at this stage; requirements list can be empty).

### Step 3: Requirements — one group at a time

For each native group of the source standard:

1. Author all requirements in that group as a batch.
2. Each requirement gets every applicable field from the schema. Don't skip `pb_interpretation`, `pitfalls`, or `external_safe_phrasing` — those are the productivity multiplier for downstream uses.
3. Use `kind: clause` for management-system-style mandatory clauses; `kind: requirement` for control-style items; `kind: principle` for principle-based frameworks (King V); `kind: practice` for NIST SSDF-style practices; `kind: objective` for outcome-based items.
4. After each group, run `make validate`. Fix errors before continuing.

### Step 4: Crosswalks

Once all requirements exist:

1. Run `make crosswalks`. This generates auto-suggested matches based on overlap signals (id similarity, title similarity, requirement-text overlap).
2. Review the candidates report. For each:
   - **Accept** if structurally aligned (e.g., 27701 inherits 27001 clause structure).
   - **Refine** if the relationship is real but the auto note is wrong.
   - **Reject** if the candidate is a false positive.
3. Author additional semantic crosswalks the auto-pipeline missed. Use Option B authoring rules (`docs/schema-v2.md`): one entry per `(ref, note)` pair when semantically distinct; structural matches keep shared notes.
4. Crosswalk direction: more-specific/newer references the more-general/older. ISO 27001 is target-only — never carries outgoing crosswalks.

### Step 5: Scenarios + open questions

Scenarios are framework-applicability vignettes: "PB customer X uses Y feature; what obligations apply." Mostly relevant for risk-tiered frameworks (EU AI Act has 14; ISO 27001 has 0). Open questions surface unresolved governance/business decisions blocking requirement resolution.

Don't fabricate scenarios. If the framework doesn't have rich vignette structure, leave the list empty.

### Step 6: Verify end-to-end

```bash
make validate    # schema check
make data        # rebuild data.json — fails if any framework breaks the combiner
make dev         # eyeball in OS — does the framework detail page render correctly with all 4 sections?
```

If the framework lacks the data needed to render Section 1 (plain English summary, key concepts), add it to `os/src/App.jsx`'s `FRAMEWORK_OVERVIEW` map. (Long-term, this should move to YAML; short-term, inline is fine.)

### Step 7: Commit

```bash
git add frameworks/<id>/ os/src/data.json docs/crosswalk-candidates-report.md
git commit -m "Add <framework name>: <N> requirements; <key structural notes>"
```

## Field guidance

### `business_models` (required on every requirement)

Almost every requirement applies to both `on-prem` and `ai-factory`. Few requirements are model-exclusive. If unsure, use `[on-prem, ai-factory]`. Use `owner_by_model` to express divergent *ownership* rather than narrowing `business_models`.

### `owner` enum

- `PB`: PrivateBox owns and operates fully
- `PB-SH`: PB-led, shared with customer for some part
- `SH`: neutral shared responsibility, often documented in shared_responsibility_model
- `SH-CL`: customer-led, PB supports
- `CL`: customer-only

The most distinctive field; drives the implementation roadmap. Sortable, filterable in the OS.

### `maturity_target`

- `SA` = Self-Asserted (we say it's true; we have evidence to back it)
- `AR` = Audit-Ready (we'd pass an external audit on this today)
- `Cert` = Certified (a formal certificate exists for this)

Target, not current state. Don't conflate with implementation status.

### `external_safe_phrasing`

This is the Trust Pack composer engine. Every requirement gets a defensible non-overclaiming statement that PrivateBox can include in customer-facing documents.

- Don't overclaim ("certified" only when literally certified)
- Don't underclaim either ("aligned with" is fine when accurate)
- Avoid future tense unless paired with a date
- One paragraph. Multiple sentences fine. Reads like marketing collateral that survives legal review.

### `audit_methods`

Standard audit method codes:
- `Insp`: Inspection (look at the artifact)
- `Int`: Interview (ask the operator)
- `Samp`: Sampling (pull a random subset of records)
- `Obs`: Observation (watch the process)
- `Rep`: Re-performance (do the procedure with the auditor watching)

Most requirements will have 2-4 of these. The combination tells the auditor how they'll test it.

### `pitfalls`

Common failure modes auditors fail people for. Examples: "boilerplate policy with no PB-specific content," "no evidence of management review actually happening," "scope statement too narrow to be defensible." Level-1 coaching content.

### `good_vs_audit_ready`

Two-step rubric:
- **Good**: PB has the artifact and operates it.
- **Audit-ready**: PB has the artifact, operates it, has evidence of operation, and has the documentation an auditor will additionally want (typically: who reviews it, when, with what cadence, signed by whom).

## Common errors and how to avoid them

**Error: "Requirement <id> has neither `requirement` nor `objective` field"**
Pick one. `requirement` for hard requirements ("the organization shall..."); `objective` for outcome-based items ("the system should achieve...").

**Error: "Requirement <id> has both `requirement` and `objective`"**
Schema enforces XOR. Pick one. If you genuinely need both, the source has a structure problem — flag it to the user.

**Error: "Crosswalk references requirement that doesn't exist"**
Either the target framework hasn't been authored yet (remove the crosswalk; add a comment), or the reference id is wrong. Check the target YAML.

**Error: "Validation rule R7 failed: business_models field missing"**
Add `business_models: [on-prem, ai-factory]` to the requirement.

**Error: data.json doesn't include the new framework**
`build/build_os_data.py` reads framework paths from its arguments. Check the Makefile's `FRAMEWORKS` variable includes the new one.

## What this skill won't do

- It won't author the YAML for you in one shot. Compliance frameworks are complex; the workflow above is iterative on purpose.
- It won't tell you what's in the source standard. You need the actual text.
- It won't decide PB business model questions for you. If a requirement's owner depends on whether AI Factory is using Teraco vs Africa Data Centres, that's an open question, not a guess.

## Reference

- `docs/schema-v2.md` — full schema spec
- `docs/structural-survey.md` — how each framework type maps to schema v2
- `frameworks/iso-27001/iso-27001.yaml` — clause-style management standard exemplar
- `frameworks/iso-27701/iso-27701.yaml` — extension/dual-role exemplar
- `frameworks/eu-ai-act/eu-ai-act.yaml` — regulatory act with phased dates exemplar
