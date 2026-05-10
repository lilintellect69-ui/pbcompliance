# PrivateBox GRC OS — Framework Schema v2

**Status.** Locked. All framework YAML files in `/frameworks/` conform to this spec. The GRC OS reads YAML at load time. Edits go in version control via the build scripts.

**Versioning.** Schema version is recorded in each file as `schema_version: "2.0"`. Backward-incompatible changes bump to 3.0. Additive changes (new optional fields) bump to 2.x.

**Design principles.**
- Single `requirements[]` list, not multiple buckets.
- Most fields are simple strings. Maps and arrays only where the framework structurally requires them.
- Conditional axes (role, tier, scenario, model) are opt-in per-framework. Frameworks that don't use them leave the relevant fields absent.
- Crosswalks are one-way at write time; the OS resolves the reverse graph at load.
- Open Questions and Scenarios are first-class entities, sibling to Requirements.

---

## Top-level structure

```yaml
schema_version: "2.0"

# Identity
id: <framework-id>                    # kebab-case, unique
version: <version>                    # standard's own version, e.g. "2022", "2025"
full_name: <full title>
type: <framework-type>                # see enum below
issuer: <issuer org>

# Audit / certification posture
audit_type: <audit-type-enum>         # see enum below
certifiable: <bool>                   # true if accredited certification exists

# PrivateBox interpretation versioning (separate from standard's version)
pb_interpretation_version: "1.0"
pb_interpretation_owner: <name or null>
pb_interpretation_last_reviewed: <date or null>

# Sub-frameworks (NIST bundle only)
sub_frameworks: [...]                 # see Sub-frameworks section

# Companion standards (ISO 42001 only)
companion_standards: [...]            # see Companions section

# Application to PB
pb_application:
  why_chosen: <text>
  scope_decisions:
    on_prem: {coverage, rationale}
    ai_factory: {coverage, rationale}
  top_risks: [...]

# Roles applicable in this framework
roles: [...]                          # e.g. ["controller", "processor"] for 27701

# Tiers applicable in this framework
tiers: [...]                          # e.g. ["prohibited", "high-risk", "gpai", ...]

# Effective dates / phased application
effective_dates: [...]                # see Effective Dates section

# Optional framework-specific blocks
soa_guidance: ...                     # ISO 27001/27701/42001
description_criteria: [...]           # SOC 2 only
disclosure_framework: ...             # King V only

# Cross-cutting structures
shared_responsibility_model: [...]
evidence_families: [...]
scenarios: [...]                      # POPIA, EU AI Act
open_questions: [...]                 # AI Factory unknowns and other unresolved

# The main requirements list
requirements: [...]
```

---

## Enums

### `type`
- `management_system_standard` — ISO 27001, 27701, 42001
- `attestation` — SOC 2
- `regulation` — POPIA, EU AI Act
- `voluntary_framework` — NIST AI RMF, SSDF, 218A
- `governance_code` — King V

### `audit_type`
- `certification` — accredited 3rd-party certification (ISO standards)
- `attestation` — CPA-issued opinion (SOC 2)
- `conformity_assessment` — CE marking, Notified Body (EU AI Act high-risk)
- `regulatory_inspection` — regulator enforcement (POPIA, EU AI Act)
- `self_attestation` — self-claim against framework (NIST)
- `disclosure` — public disclosure required (King V)

### `kind` (per requirement)
Native taxonomy unit. Determines which optional fields apply.
- `clause` — ISO management-system clauses (4.1, 4.2, ...)
- `control_org` — ISO 27001 Annex A organisational controls
- `control_proc` — ISO 27701 Annex A.2 processor controls
- `control_ctrl` — ISO 27701 Annex A.1 controller controls
- `control_shared` — ISO 27701 Annex A.3 shared security controls
- `control_aims` — ISO 42001 Annex A AIMS controls
- `condition` — POPIA 8 Conditions
- `section` — POPIA statutory section reference
- `criterion` — SOC 2 Common Criteria, Optional Categories
- `principle` — King V principles
- `practice` — King V recommended practices
- `article` — EU AI Act articles
- `function_outcome` — NIST AI RMF outcomes (GOV/MAP/MEASURE/MANAGE)
- `task` — NIST SSDF tasks (PO/PS/PW/RV)
- `overlay` — NIST 218A overlay items

### `applies`
- `Y` — applies, in scope
- `C` — conditional (depends on use case, role, tier, scenario)
- `N` — does not apply, with justification
- `tier_dependent` — applicability driven by `tier` field
- `role_dependent` — applicability driven by `role_applicability` map
- `scenario_dependent` — applicability driven by linked scenario(s)

### `source_authority`
Optional. Defaults to `binding` if absent.
- `binding` — law, regulation, accredited standard
- `guidance` — non-binding interpretation (e.g. Commission Guidelines)
- `code` — voluntary code of practice
- `draft` — published but not finalised
- `market` — market practice / consultancy interpretation

### `owner`
- `PB` — PrivateBox
- `PB/SH` — PrivateBox-led shared
- `SH` — neutrally shared
- `SH/CL` — customer-led shared
- `CL` — customer

### `maturity_target`
- `SA` — situational awareness
- `AR` — audit-ready
- `Cert` — certifiable
- `SA/AR` — between SA and AR

---

## Sub-frameworks (NIST bundle)

Used only when one framework bundles distinct sub-frameworks.

```yaml
sub_frameworks:
  - id: rmf
    name: "AI Risk Management Framework"
    version: "1.0 + GenAI Profile Jul 2024"
    issuer: NIST
  - id: ssdf
    name: "Secure Software Development Framework"
    version: "1.1"
    issuer: NIST
  - id: 218a
    name: "SP 800-218A AI Overlay"
    version: "Final May 2024"
    issuer: NIST
    overlay_on: ssdf
```

Each requirement in NIST framework adds a `sub_framework` field referencing one of these IDs.

---

## Companion standards (ISO 42001)

Used when a framework references companion standards that aren't separately certifiable.

```yaml
companion_standards:
  - id: iso-42005
    name: "AI System Impact Assessment"
    version: "2025"
    role: "Referenced from A.5; provides structured impact-assessment methodology"
  - id: iso-42006
    name: "Requirements for AI management system certification bodies"
    version: "2025"
    role: "Governs accreditation; not directly applicable to PB but shapes auditor expectations"
```

Requirements can reference these via `companion_refs: [iso-42005]`.

---

## Effective dates

Used for phased application (EU AI Act primarily; others typically have a single date).

```yaml
effective_dates:
  - milestone: "AI literacy + prohibited practices"
    date: "2025-02-02"
    obligations: [eu-ai-act-art-4, eu-ai-act-art-5]
  - milestone: "GPAI obligations"
    date: "2025-08-02"
    obligations: [eu-ai-act-art-51, eu-ai-act-art-52, ...]
  - milestone: "High-risk + transparency"
    date: "2026-08-02"
    obligations: [eu-ai-act-art-6, eu-ai-act-art-50, ...]
```

Each requirement may also carry `effective_from` and `effective_until` directly.

---

## Scenarios

First-class navigable entities for POPIA and EU AI Act. Other frameworks may use them optionally.

```yaml
scenarios:
  - id: scn-eu-a
    name: "Pure on-prem enterprise chat assistant, customer-supplied data only"
    framework_specific_id: "Scenario A"
    description: "PrivateBox runs locally inside customer's environment..."
    applies_to_business_models: [on-prem]
    pb_role: provider
    customer_role: deployer
    risk_tier: minimal
    triggered_requirements:
      - requirement_id: eu-ai-act-art-2
        scenario_specific_note: "AI Act applies because product is placed on EU market"
      - requirement_id: eu-ai-act-art-50
        scenario_specific_note: "Transparency obligations may apply when binding"
    legal_basis: "Art 2(1)(a)–(b); Art 3(1) AI system definition"
    notes: ...
```

Scenarios are sibling to requirements. The OS resolves cross-references at load.

---

## Open Questions

First-class entity for unresolved governance/business decisions that block requirement resolution.

```yaml
open_questions:
  - id: oq-partner-dc-selection
    question: "Which DC partner(s) for AI Factory deployments?"
    candidate_answers: ["Teraco", "Africa Data Centres", "Vantage", "TBD"]
    decision_owner: "PrivateBox founders"
    decision_status: pending          # pending | resolved | deferred
    blocks_requirements: [a-7.1, a-7.11, a-7.12, ...]
    blocks_scenarios: []
    notes: ...
    created: "2026-05-04"
    resolved_value: null              # populated when status: resolved
    resolved_at: null
```

Other entities reference open questions via `open_question: oq-...`.

The OS surfaces blocked requirements when filtered to a relevant lens (e.g. AI Factory).

---

## Shared responsibility model

Per-framework, mostly stable across frameworks. Up to 12-15 rows.

```yaml
shared_responsibility_model:
  - area: "Physical security"
    pb_owned: ...
    cl_owned: ...
    shared_note: ...
```

Same shape as v1 schema.

---

## Evidence families

Per-framework. Up to ~15 families.

```yaml
evidence_families:
  - id: governance_documents
    name: "Governance documents"
    examples: [...]
    why_auditor_cares: ...
    cadence: ...
    typical_owner: PB
```

Same shape as v1 schema.

---

## Description criteria (SOC 2 only)

```yaml
description_criteria:
  - id: dc-1
    title: "Types of services provided"
    requirement: "Describe the services provided"
    pb_interpretation: ...
    mandatory: true
    on_prem_note: ...
    evidence: ...
```

Sibling to requirements, not part of `requirements[]`.

---

## Disclosure framework (King V only)

```yaml
disclosure_framework:
  reporting_model: "apply and explain"
  primary_artefact: "Integrated Annual Report disclosure section"
  proportionality_rules: ...
  jse_listing_overlap: ...
```

---

## SoA guidance (ISO 27001/27701/42001)

```yaml
soa_guidance:
  principles: <text>
  na_justification_rules: <text>
  honesty_rules: <text>
```

Same shape as v1 schema.

---

## The `requirements[]` list

This is the main content. One entry per native unit (clause, control, condition, criterion, etc.).

### Required fields (every requirement)

```yaml
requirements:
  - id: <framework>-<kind-prefix>-<native_id>    # globally unique within framework
    kind: <kind-enum>
    native_id: <id as used in standard>          # e.g. "5.1", "Article 6", "GOV 1.6"
    title: <title>
    pb_interpretation: <PB-specific interpretation>
    owner: <owner-enum>
    business_models: [...]                       # at minimum [on-prem]
```

**Plus at least ONE of:**
- `requirement: <text>` — natural-language requirement text. Used by clause-style kinds (clause, condition, section, article, principle, criterion, function_outcome, task, overlay).
- `objective: <text>` — short purpose statement. Used by control-style kinds (control_org, control_proc, control_ctrl, control_shared, control_aims, practice).

The validator enforces "at least one of requirement/objective" and warns on kind-mismatch (e.g. `kind: clause` with only `objective`).

### Standard optional fields (most requirements)

```yaml
    # Grouping
    group: <native group code>                   # e.g. "A.5", "CC1", "GOV"
    group_name: <readable group name>

    # Interpretation depth
    auditor_intent: <text>                       # mostly clause-style
    objective: <text>                            # mostly control-style
    points_of_focus: [...]                       # SOC 2 only

    # Applicability
    applies: <applies-enum>
    applies_rationale: <text>
    na_justification_template: <text>

    # Evidence and execution
    documented_evidence: [...]                   # list of artefacts
    operational_evidence: <text>                 # how it's evidenced in operation
    evidence: <text>                             # combined when not split
    audit_methods: [Insp, Int, Samp, Obs, Rep]
    cadence: <text>

    # Coaching content
    failure_modes: <text>
    pitfall: <text>
    good_vs_audit_ready:
      good: <text>
      audit_ready: <text>

    # Targets and improvement
    maturity_target: <maturity-enum>
    remediation: <text>

    # External
    external_safe_claim: <text>                  # clause-style
    external_safe_phrasing: <text>               # control-style
    scope_note: <text>

    # Relationships
    depends_on: [...]                            # other requirement IDs
    crosswalk:
      - framework: iso-27001
        refs: ["a-5.7", "cl-6.1.2"]
      - framework: iso-27701
        refs: ["a-1-5"]

    # Source provenance
    source_authority: <source-authority-enum>
    source_refs: [...]
```

### Conditional axes (framework-specific optional fields)

#### Tier (EU AI Act)
```yaml
    tier: high-risk
    tier_obligations:
      high-risk: "Full obligations under Arts 8-15"
      gpai: "Subset under Arts 51-55"
      minimal: "No obligations"
```

#### Role (ISO 27701, EU AI Act)
```yaml
    role_applicability:
      controller: Y
      processor: C
      controller_note: "Full obligations apply"
      processor_note: "Only when PB processes on customer instructions"
```

#### Scenario references
```yaml
    triggered_by_scenarios: [scn-eu-e, scn-eu-f, scn-eu-g]
```

#### Type I / II evidence (SOC 2)
```yaml
    type_i_evidence: <design evidence>
    type_ii_evidence: <operating-effectiveness evidence>
    suggested_observation_period: "6-12 months"
```

#### Disclosure text (King V)
```yaml
    disclosure_text: <apply-and-explain statement template>
    proportionality_note: <text>
```

#### Sub-framework (NIST bundle)
```yaml
    sub_framework: rmf
```

#### Overlay relationships (NIST 218A)
```yaml
    overlay_target_id: ssdf-task-po-5
    overlay_modifies: "Adds AI-specific monitoring requirement to PO.5"
```

#### Companion references (ISO 42001)
```yaml
    companion_refs: [iso-42005]
    companion_note: "Use 42005 methodology for impact assessment"
```

#### Effective dates (per requirement)
```yaml
    effective_from: "2026-08-02"
    effective_until: null
```

#### Per-business-model owner divergence
```yaml
    owner_by_model:                              # OPTIONAL — only when divergent
      on_prem: "SH"
      ai_factory:
        status: pending
        open_question: oq-partner-dc-selection
```

---

## ID conventions

Globally unique within a framework. Pattern: `<framework-id>-<kind-prefix>-<native_id>`.

| Framework | Kind | Prefix | Example |
|---|---|---|---|
| iso-27001 | clause | cl | iso-27001-cl-4.1 |
| iso-27001 | control_org | a | iso-27001-a-5.1 |
| iso-27701 | clause | cl | iso-27701-cl-5.2 |
| iso-27701 | control_ctrl | a1 | iso-27701-a1-5 |
| iso-27701 | control_proc | a2 | iso-27701-a2-3 |
| iso-27701 | control_shared | a3 | iso-27701-a3-12 |
| iso-42001 | clause | cl | iso-42001-cl-6.1 |
| iso-42001 | control_aims | a | iso-42001-a-6.1.4 |
| soc-2 | criterion | cc | soc-2-cc-1.1 |
| soc-2 | criterion | a | soc-2-a-1.1 |
| popia | condition | cond | popia-cond-7 |
| popia | section | s | popia-s-19 |
| nist | function_outcome | gov | nist-gov-1.1 |
| nist | task | po | nist-po-1.1 |
| nist | overlay | 218a | nist-218a-ps-1.2 |
| eu-ai-act | article | art | eu-ai-act-art-6 |
| king-v | principle | p | king-v-p-1 |
| king-v | practice | rp | king-v-rp-1.5 |

For backward compatibility with v1 ISO 27001 IDs (`cl-4.1`, `a-5.1`), the OS accepts both forms. New files use the prefixed form.

---

## Validation rules

A v2-compliant framework YAML must:

1. **Have schema_version: "2.0"** at top level.
2. **Have all required top-level fields:** id, version, full_name, type, issuer, audit_type, certifiable, pb_interpretation_version, pb_application, requirements.
3. **Each requirement must have:** id, kind, native_id, title, requirement, pb_interpretation, owner, business_models.
4. **kind must be valid enum value.** ID prefix must match kind (e.g. kind=clause requires `-cl-` in id).
5. **owner must be valid enum value.** owner_by_model is optional; if present, on_prem and ai_factory keys both required.
6. **Crosswalk targets must exist.** OS validates at load (warning, not failure, since other frameworks may not be loaded yet).
7. **Open question references must resolve.** Any `open_question: oq-...` reference must match an entry in open_questions[].
8. **Scenario references must resolve.** Any `triggered_by_scenarios: [...]` must reference scenarios[].
9. **Tier values must match framework's tiers[].** If `tier: high-risk` is used, framework's tiers[] must contain "high-risk".
10. **Role values must match framework's roles[].** Same logic.
11. **No duplicate requirement IDs within a framework.**
12. **Counts shouldn't drift.** If framework has known canonical counts (e.g. ISO 27001 = 30 clauses + 93 Annex A), validator can warn on mismatch.

---

## What the OS does at load time

1. Parses each framework YAML, validates against schema.
2. Resolves crosswalks into a bidirectional graph: every requirement knows what it points to AND what points to it.
3. Resolves scenario→requirement and requirement→scenario links.
4. Resolves open_question references; computes the "blocked-by" view.
5. Computes per-framework statistics (alignment %, by group, by owner, by status).
6. Caches the resolved graph; rebuilds only on file change (git hook or filesystem watch).

---

## Migration from v1

v1 ISO 27001 schema had `clauses[]` and `annex_a_controls[]`. v2 collapses to `requirements[]`. Migration is mechanical:

1. Each entry in v1 `clauses[]` becomes a `requirements[]` entry with `kind: clause`.
2. Each entry in v1 `annex_a_controls[]` becomes a `requirements[]` entry with `kind: control_org`.
3. ID prefixing: v1 used `cl-4.1` and `a-5.1`; v2 uses `iso-27001-cl-4.1` and `iso-27001-a-5.1` for new files. v1 IDs continue to work via OS-side normalisation.
4. Field name changes:
   - `clause` and `subclause` collapse to `native_id` (kept full subclause id, e.g. "4.1")
   - `clause_title` → `group_name`
   - `external_safe_claim` and `external_safe_phrasing` both kept (different kinds use different ones)
5. New fields default to absent: `tier`, `role_applicability`, `triggered_by_scenarios`, `effective_from`, `effective_until`, `source_authority`, `companion_refs`, `overlay_target_id`, `sub_framework`.
6. Crosswalk added per requirement (initially empty `[]`; populated as other frameworks land).

The build script changes are small. The YAML output expands modestly (mostly because of crosswalk arrays).
