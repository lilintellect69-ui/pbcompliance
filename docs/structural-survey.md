# PrivateBox GRC OS — Framework Structural Survey

**Purpose.** Compare the structural shape of all 9 frameworks in scope before designing schema v2. This survey is shape-only — native taxonomy, depth, certifiability, audit type, distinctive structural features. Interpretation and content come later, per framework, from PrivateBox's existing research.

**Audience.** Schema v2 designers (you and Claude). Not a framework primer.

**How to read each profile.** Fixed shape per framework: native taxonomy, group structure, total requirement count, certifiability and audit type, roles and scenarios, effective dates, companion standards, what strains the current ISO 27001-shaped schema.

---

## 1. ISO/IEC 27001:2022 — done

| Field | Value |
|---|---|
| Native taxonomy | Clauses (mandatory) + Annex A controls (selected via SoA) |
| Depth | 2 levels (clause → subclause; group → control) |
| Group structure | Clauses 4–10; Annex A.5 / A.6 / A.7 / A.8 |
| Total | 30 clause subclauses + 93 Annex A = 123 |
| Certifiable? | Yes, accredited certification |
| Audit type | Stage 1 + Stage 2 + surveillance + 3-yearly recertification |
| Roles | Single (the certified org) |
| Effective dates | One revision (2022); transition to 2022 from 2013 ended Oct 2025 |
| Companions | None mandatory; 27002 is implementation guidance for Annex A |
| **Strain on current schema** | Baseline — no strain. The schema was designed against this. |

---

## 2. ISO/IEC 27701:2025 — Privacy Information Management

| Field | Value |
|---|---|
| Native taxonomy | Clauses (PIMS extension) + three distinct Annex types |
| Depth | 2 levels |
| Group structure | Clauses 4–10 (mirrors 27001 structure); **Annex A.1 controller controls** (~31 controls); **Annex A.2 processor controls** (~18 controls); **Annex A.3 shared security controls** (29 controls aligned to ISO 27002:2022 themes) |
| Total | ~30 clauses + ~78 Annex controls = ~108 |
| Certifiable? | Yes — extension certification on top of ISO 27001 |
| Audit type | Combined with 27001 audit; cannot certify standalone |
| Roles | **Controller / Processor / Both** — controls activate by role. Same org can be both for different processing activities. |
| Effective dates | 2025 revision is significant restructure from 2019; legacy migration table needed |
| Companions | Built on top of 27001; references GDPR Art 6/9, POPIA s.11/26, etc. |
| **Strain on current schema** | **Three Annex buckets, not one.** Plus the role dimension (Controller vs Processor) is a per-requirement attribute, not a global setting — a single org playing both roles has both columns active. The 2019→2025 migration mapping is itself useful schema metadata (legacy_ref). |

---

## 3. ISO/IEC 42001:2023 — AI Management System (+ 42005, 42006)

| Field | Value |
|---|---|
| Native taxonomy | Clauses (AIMS) + Annex A controls + informative annexes + companion standards |
| Depth | 3 levels in places (e.g. A.6.1.4 Bias, A.6.2.3 Human oversight) |
| Group structure | Clauses 4–10; **Annex A.2 through A.10** (9 groups, 38 controls); **Annex B** informative implementation guidance; **Annex C** informative objectives/risk sources; companion standards 42005 (impact assessment) and 42006 (certification readiness) |
| Total | ~30 clauses + 38 Annex A controls + companion content = ~70+ requirements |
| Certifiable? | Yes — accredited certification (42006 governs accreditation) |
| Audit type | Standard ISO management-system audit, but with AI-specific competence requirements |
| Roles | **AI Provider / AI Producer / AI User / AI Customer / AI Subject / AI Partner** (per ISO 22989). PB is typically Provider+Producer; customers are Users; data subjects are AI Subjects. |
| Effective dates | Published Dec 2023; first certifications mid-2024 onward |
| Companions | **42005** AI System Impact Assessment (separate but tightly bound — referenced from A.5); **42006** AI management system certification body requirements; ISO 22989 (AI concepts/terms); ISO 23894 (AI risk management) |
| **Strain on current schema** | Three-level depth (A.6.1.4 not just A.6); informative-only annexes that are still referenced by core controls; **companion standards that aren't separate frameworks but aren't really in 42001 either** — needs `companion_refs` field; multi-role taxonomy richer than Controller/Processor. |

---

## 4. SOC 2 — Trust Services Criteria + Description Criteria

| Field | Value |
|---|---|
| Native taxonomy | Common Criteria (CC1–CC9) mandatory + four optional categories (Availability A1, Confidentiality C1, Processing Integrity PI1, Privacy P1–P8) + Description Criteria (DC1–DC9) |
| Depth | 2 levels (CC1 → CC1.1, etc.) plus Points of Focus under each criterion |
| Group structure | DC1–DC9 (description); CC1–CC9 (common); A1.1–A1.3; C1.1–C1.2; PI1.1–PI1.5; P1.1–P8.1 |
| Total | ~40+ criteria; 9 description criteria; ~20 optional category criteria |
| Certifiable? | **No — attestation**, not certification. CPA firm issues opinion. Cannot self-claim "SOC 2 certified". |
| Audit type | **Type I** (design at point in time) vs **Type II** (operating effectiveness over period of 3–12 months). Same controls, different evidence question. |
| Roles | Single audited org, but with **Subservice Organisations** (carve-out vs inclusive treatment) and **Complementary User Entity Controls (CUECs)** — controls assumed of the customer. CUEC is structurally important for shared-responsibility/on-prem. |
| Effective dates | TSP-100 + DC-200 (2022 revision); points-of-focus refresh 2024 |
| Companions | None within SOC 2; SOC 1 / SOC 3 are separate report types |
| **Strain on current schema** | **Type I/II is a parallel evidence axis** — same control, two evidence templates (designed vs operating-effectiveness-over-period); **CUECs are first-class** — they're customer-side controls the auditor lists in the report; **Description Criteria are meta-criteria** about how the system is described, not control criteria; **Points of Focus** under each criterion are sub-bullet implementation guidance, useful for coaching but not separately auditable; **carve-out vs inclusive subservice treatment** is a per-supplier scoping decision. |

---

## 5. POPIA — Protection of Personal Information Act (South Africa)

| Field | Value |
|---|---|
| Native taxonomy | **8 Conditions for lawful processing** + **Sections of the Act** + **Scenario-based role allocation** |
| Depth | Variable — Conditions are abstract; sections are statutory; scenarios are operational |
| Group structure | 8 Conditions: Accountability, Processing Limitation, Purpose Specification, Further Processing Limitation, Information Quality, Openness, Security Safeguards, Data Subject Participation. Sections (s.8 through s.109) provide the binding text. |
| Total | 8 conditions + ~30 key sections + 14+ scenarios in PB research |
| Certifiable? | **No — legal compliance**, no certification regime. Some industry codes of conduct (s.60–68) provide sector schemes. |
| Audit type | Regulator inspection; complaint-driven; enforcement notices; administrative fines. Information Officer registration required. |
| Roles | **Responsible Party** (controller-equivalent) / **Operator** (processor-equivalent). Roles flip per scenario — PB is Responsible Party for its own corporate processing, Operator when supporting customer environments, may be both simultaneously. |
| Effective dates | Effective July 2021; ongoing regulatory guidance |
| Companions | PAIA (Promotion of Access to Information Act) — interfaces with POPIA s.23–25; sector codes; Regulator guidance notes |
| **Strain on current schema** | **Three orthogonal axes need representation:** (1) Conditions (the abstract obligations), (2) Sections (the binding text), (3) Scenarios (which trigger different role allocations). Same processing activity has different obligations depending on PB's role in that scenario. **Scenario-conditional ownership** is structurally new. |

---

## 6. NIST bundle — AI RMF + SSDF + 800-218A

| Field | Value |
|---|---|
| Native taxonomy | Three sub-frameworks bundled by PB choice |
| Depth | Variable per sub-framework |
| Group structure | **AI RMF**: 4 Functions (Govern, Map, Measure, Manage) → Categories → Subcategories. ~70 outcomes. **SSDF**: 4 Practices (PO, PS, PW, RV) → Tasks. ~40 tasks. **800-218A**: AI overlay on SSDF — adds tasks (PO.5.3, PS.1.2, PS.1.3) and modifies others. ~20 overlay items. |
| Total | ~70 RMF outcomes + 40 SSDF tasks + 20 218A overlay items = ~130 |
| Certifiable? | **No — voluntary framework**. Reference for self-assessment, procurement, government use. |
| Audit type | Self-attestation; sometimes mapped into FedRAMP / contract requirements. |
| Roles | RMF: AI Actors (developer, deployer, end user, evaluator, etc. — 7+ archetypes). SSDF: software producer. |
| Effective dates | RMF 1.0 (Jan 2023); RMF GenAI Profile (Jul 2024); SSDF 1.1 (Feb 2022); 800-218A (May 2024) |
| Companions | 218A is explicitly an overlay on SSDF, not standalone. Other NIST AI series (AI 100-1, etc.) provide context. |
| **Strain on current schema** | **Three sub-frameworks bundled** — needs `sub_framework` field. **Overlay relationship** — 218A items either add to or modify SSDF tasks; needs `overlay_target_id` field. **Mapping across sub-frameworks** — PB's research already shows the same artefact (e.g. governance pack) covers RMF GOV + SSDF PO; this is the proto-Control-Library. |

---

## 7. EU AI Act — Regulation 2024/1689

| Field | Value |
|---|---|
| Native taxonomy | Articles + Annexes + Risk tiers + Roles |
| Depth | 2 levels (Article → paragraphs/sub-articles) |
| Group structure | 113 articles in 13 chapters; 13 annexes (Annex I product list, Annex III high-risk list, Annex IV technical doc, etc.). Risk tiers: **Prohibited** (Art 5), **High-risk** (Art 6 + Annex III), **GPAI** (Art 51–55), **Limited risk** (Art 50 transparency), **Minimal risk** (no obligations). |
| Total | PB research focuses on ~25 key articles + 14 deployment scenarios + risk classification matrix |
| Certifiable? | **Conformity assessment + CE marking** for high-risk systems (not certification in ISO sense). GPAI Code of Practice is voluntary. Notified Bodies do conformity assessment. |
| Audit type | Pre-market conformity assessment; post-market monitoring; serious incident reporting; market surveillance authorities can inspect. |
| Roles | **Provider / Deployer / Importer / Distributor / Authorised Representative**. **Role-flip rule (Art 25)** — substantial modification turns deployer into provider. PB is typically Provider; customers are Deployers; reseller channels create Importer/Distributor obligations. |
| Effective dates | **Phased application:** Feb 2025 (Art 4 AI literacy + Art 5 prohibited); Aug 2025 (GPAI Art 51–55); Aug 2026 (Annex III high-risk + Art 50 transparency); Aug 2027 (Annex I product-embedded high-risk). Penalties up to €35M / 7% turnover. |
| Companions | Commission Guidelines (non-binding interpretation, e.g. AI System Definition Feb 2025, Prohibited Practices Feb 2025, GPAI Guidelines Jul 2025); GPAI Code of Practice (Jul 2025, voluntary); harmonised standards (when published, give presumption of conformity). |
| **Strain on current schema** | **Risk tier** is a primary classifier — same article applies differently per tier; sometimes only applies to one tier. **14 deployment scenarios** in PB research, each with its own role/tier/applies/legal-basis profile — scenarios are first-class entities, not just an attribute. **Effective dates per article** — must support phased implementation; obligations become live at different dates. **Role-flip** means PB role itself can change per deployment scenario, with cascading consequences across many requirements. **Source authority levels** — PB research tags binding [L], guidance [G], code [C], draft [D], market practice [M]; this is real metadata, not just trivia. |

---

## 8. King V — Corporate Governance (South Africa)

| Field | Value |
|---|---|
| Native taxonomy | Outcomes + Principles + Recommended Practices |
| Depth | 3 levels (Outcome → Principle → Practice) |
| Group structure | ~5 governance outcomes; **17 principles**; recommended practices per principle (~10–30 each). Disclosure framework drives reporting. |
| Total | 17 principles; ~150–200 recommended practices total |
| Certifiable? | **No — disclosure-based**. Uses **"apply and explain"** model (King IV used "apply or explain"; King V is "apply and explain" — explain the application, not just compliance). |
| Audit type | Integrated annual report disclosure; JSE listing requirements for listed entities; not directly applicable to PB as a private company but sets governance benchmark expected by institutional customers. |
| Roles | Board / Sub-committees / CEO / executives. Less about external roles, more about internal governance structure. |
| Effective dates | King V published October 2025; replaces King IV |
| Companions | Companies Act 71 of 2008 (statutory); JSE Listings Requirements (for listed entities); IoDSA guidance. |
| **Strain on current schema** | **Disclosure-driven not control-driven** — the unit of compliance is the public disclosure statement, not an implemented control. **Apply-and-explain text** is the deliverable. **Proportionality** is explicit — practices are scaled to org size; PB applies a "proportionate" subset rather than the full set. **Outcomes layer** above principles is a meta-level not present in any other framework. |

---

## Cross-cutting analysis

### What shapes are common

Every framework can be reduced to **a list of requirements**, where each requirement has interpretation, ownership, evidence, and external phrasing. The fields used in the current ISO 27001 schema are mostly transferable: `id`, `title`, `pb_interpretation`, `owner`, `evidence`, `audit_methods`, `cadence`, `pitfall`, `external_safe_phrasing`, `business_models`. These work across all 8.

Every framework also has **groups** that organise the requirements — clauses, annexes, conditions, criteria, principles, articles, functions, practices. The current schema's `group` and `group_name` fields cover this if we accept that groupings are framework-specific strings.

Every framework has **a notion of applicability** — applies / not-applies / conditional, with rationale. The current `applies` and `applies_rationale` fields generalise.

### What varies

**Bucket structure.** ISO 27001 has 2 buckets (clauses + Annex A). ISO 27701 has 4 (clauses + Controller + Processor + Shared). ISO 42001 has 4+ (clauses + Annex A + Annex B + Annex C + companion standards). SOC 2 has 3 (Description Criteria + Common + Optional). POPIA has 3 (Conditions + Sections + Scenarios). NIST has 3 sub-frameworks. EU AI Act has 2 (Articles + Annexes) but with a risk-tier orthogonal axis. King V has 3 (Outcomes + Principles + Practices). **The two-bucket model is the exception, not the rule.**

**Conditional applicability.** ISO 27001 has a single applicability question per control. POPIA has scenario-conditional applicability — same condition, different obligations per scenario. EU AI Act has tier-conditional and role-conditional applicability — same article, different obligations for Provider vs Deployer, for high-risk vs GPAI vs minimal. ISO 27701 has role-conditional applicability — same control, different evidence for Controller vs Processor. **Conditional applicability is the norm; static applicability is the exception.**

**Certifiability and audit type.** ISO 27001/27701/42001 are accredited certifications. SOC 2 is attestation (not certification). POPIA and EU AI Act are legal compliance with regulator enforcement. NIST is self-attestation. King V is disclosure. **One framework cannot have a single "audited / not-audited" status flag; the type matters.**

**Effective dates and phasing.** ISO standards have a single revision date. EU AI Act has staggered application dates for different articles. King V has a publication date and ongoing transitional expectations. POPIA has a single effective date but ongoing Regulator guidance. **Phased application by date is real for at least EU AI Act and probably others.**

**Crosswalk.** Every framework's research already includes a crosswalk to other frameworks. ISO 42001 explicitly maps to ISO 27001 / 27701 / NIST AI RMF / EU AI Act / POPIA / King V. POPIA maps to GDPR. ISO 27701 maps to ISO 27002:2022 themes and to GDPR/POPIA. NIST 218A maps to SSDF. **The crosswalk is structural, not optional.** It's the foundation of the unified Control Library.

**Source authority levels.** EU AI Act research tags every source as binding [L] / guidance [G] / code [C] / draft [D] / market [M]. ISO standards have the standard text + interpretive guidance + auditor commentary. POPIA has the Act + Regulations + Regulator guidance + enforcement notices + case examples. **Source provenance matters per requirement, not just per framework.**

### Structural elements the current schema is missing

1. **More than two requirement buckets.** Replace `clauses` and `annex_a_controls` with a single `requirements[]` list, with a `kind` field for native taxonomy (clause, control_org, control_proc, control_ctrl, control_shared, condition, section, criterion, principle, practice, article, function_outcome, task, overlay).

2. **Role-conditional fields.** Some fields (notably `owner`, `pb_interpretation`, `evidence`, `applies`) need to support per-role variants for ISO 27701 (Controller/Processor) and EU AI Act (Provider/Deployer). Map shape: `{role: value}` instead of single value.

3. **Tier / classification axis.** EU AI Act needs a `tier` field per requirement (prohibited / high-risk / GPAI / limited / minimal). For frameworks without tiers, the field is empty.

4. **Scenarios as a first-class entity.** POPIA and EU AI Act both organise around scenarios. A scenario references multiple requirements with scenario-specific role/tier/applies values. New top-level entity: `scenarios[]`.

5. **Effective dates per requirement.** Each requirement gets `effective_from` and `effective_until` fields, optional. EU AI Act phasing requires this; other frameworks just leave it null.

6. **Source authority tags.** Each requirement can have a `source_authority` tag — binding, guidance, code, draft, market. Defaults to "binding" for ISO/legal frameworks; matters explicitly for EU AI Act and POPIA.

7. **Crosswalk anchors.** Each requirement gets a `crosswalk[]` array with entries like `{framework: iso-27001, refs: ["a-5.7", "cl-6.1.2"]}`. This is the seed data for the unified Control Library — the OS reads crosswalks and builds the cross-framework graph.

8. **Companion / overlay relationships.** ISO 42001 references companion standards (42005, 42006); NIST 218A is an overlay on SSDF. Two new fields: `companion_refs[]` for "this requirement is supplemented by external content", `overlay_target_id` for "this requirement modifies another requirement".

9. **Audit type and certifiability per framework.** Not per requirement — per framework metadata. Add `audit_type` enum (certification, attestation, conformity_assessment, regulatory_inspection, self_attestation, disclosure) and `certifiable: bool` at the framework level.

10. **Disclosure text for King V.** King V's deliverable is the "apply and explain" disclosure statement. Add an optional `disclosure_text` field for principle-level requirements; for non-King-V frameworks, leaves null.

### What stays single-string

Most fields stay simple strings, not maps. The model-divergence Open Question we raised earlier still applies — `owner` and a few others become `{on_prem, ai_factory}` maps **only when they actually diverge**. Same logic now extends to roles: `{controller, processor}` map for ISO 27701 fields **only when Controller and Processor obligations actually differ**. Default is single value; map shape only when the framework genuinely requires it.

---

## Schema v2 implications — proposed shape

```yaml
# Framework-level metadata
id: <framework-id>
version: <version>
full_name: <full name>
type: management_system_standard | attestation | regulation | voluntary_framework | governance_code | overlay
issuer: <issuer>
audit_type: certification | attestation | conformity_assessment | regulatory_inspection | self_attestation | disclosure
certifiable: bool
sub_frameworks: []  # for NIST bundle
companion_standards: []  # for ISO 42001
effective_dates:  # for phased application
  - milestone: ...
    date: ...
    obligations: [requirement_ids]
roles: [list of roles applicable in this framework]
tiers: [list of tiers, if applicable]

# Conceptual content
pb_application:
  why_chosen: ...
  scope_decisions: {on_prem: ..., ai_factory: ...}
  top_risks: [...]

# Optional, framework-specific
soa_guidance: ...           # ISO 27001/27701/42001
description_criteria: [...]  # SOC 2 only
disclosure_framework: ...    # King V only

# Cross-cutting structures
shared_responsibility_model: [...]
evidence_families: [...]
scenarios: [...]    # NEW: POPIA, EU AI Act
open_questions: [...]  # NEW: AI Factory unknowns and other unresolved items

# Single requirements list, replacing clauses + annex_a_controls
requirements:
  - id: <framework>-<kind>-<native_id>
    kind: clause | control_org | control_proc | control_ctrl | control_shared |
          condition | section | criterion | principle | practice | article |
          function_outcome | task | overlay
    group: A.5
    group_name: Organisational controls
    native_id: "5.1"
    title: ...

    # Core interpretation
    requirement: ...
    auditor_intent: ...           # optional, mostly for clause-style
    pb_interpretation: ...
    objective: ...                # optional, mostly for control-style
    points_of_focus: [...]        # SOC 2 only

    # Conditional applicability
    applies: Y | C | N | tier_dependent | role_dependent
    applies_rationale: ...
    na_justification_template: ...
    tier: high-risk | gpai | limited | minimal | n/a   # EU AI Act
    role_applicability:           # ISO 27701, EU AI Act
      controller: Y | C | N
      processor: Y | C | N

    # Ownership — single string, or map only where divergent
    owner: PB | PB/SH | SH | SH/CL | CL
    owner_by_model:               # OPTIONAL — only when on-prem and ai-factory diverge
      on_prem: ...
      ai_factory:
        status: pending
        open_question: <open_question_id>

    # Evidence + execution
    documented_evidence: [...]
    operational_evidence: ...
    evidence: ...                 # legacy combined field, when not split
    audit_methods: [...]
    cadence: ...

    # Type I / II split for SOC 2
    type_i_evidence: ...          # SOC 2 only
    type_ii_evidence: ...         # SOC 2 only

    # Coaching content
    failure_modes: ...
    pitfall: ...
    good_vs_audit_ready:
      good: ...
      audit_ready: ...

    # Targets and improvement
    maturity_target: SA | AR | Cert
    remediation: ...

    # External-facing
    external_safe_claim: ...
    disclosure_text: ...          # King V only

    # Relationships
    depends_on: []
    overlay_target_id: ...        # NIST 218A → SSDF
    companion_refs: []            # ISO 42001 → 42005/42006
    crosswalk:
      - framework: iso-27001
        refs: ["a-5.7", "cl-6.1.2"]
      - framework: iso-27701
        refs: ["a-1.5"]

    # Source provenance
    source_authority: binding | guidance | code | draft | market
    source_refs: [...]

    # Phasing (mostly for EU AI Act)
    effective_from: <date>
    effective_until: <date>

    # Standard
    business_models: [on-prem, ai-factory]
    scope_note: ...
```

---

## Open design decisions before schema v2 lands

1. **Scenario entity scope.** Scenarios are clearly first-class for POPIA and EU AI Act. Should they also exist for other frameworks (e.g. ISO 27001 deployment-pattern scenarios), or are they a per-framework optional structure? *Lean: optional per framework, lives at framework level.*

2. **Crosswalk direction.** Should crosswalks be one-way (each requirement points at others) or two-way (auto-resolved by the OS at load time)? *Lean: one-way in YAML, two-way in OS — the OS builds the reverse index when it loads.*

3. **Sub-framework granularity for NIST bundle.** Treat NIST as one framework with three `sub_framework` values (rmf, ssdf, 218a)? Or treat them as three separate frameworks with cross-references? *Lean: one bundle, sub_framework field — matches how PB's research already organises them.*

4. **ISO 42001 companion standards.** 42005 and 42006 as separate frameworks, or as `companion_standards` content embedded in 42001? *Lean: companions embedded — they're not certifiable separately and don't add requirements, they elaborate them.*

5. **King V disclosure model.** The unit of compliance for King V is a public disclosure statement, not an implemented control. Should the schema treat principles+practices as requirements with a `disclosure_text` field, or build a parallel "disclosures[]" entity? *Lean: requirements with disclosure_text — simpler, keeps the unified shape.*

6. **EU AI Act scenarios as primary or secondary.** PB's research has 14 scenarios (A–N) that drive everything. Are scenarios the entry point users navigate ("I want to deploy a credit scoring tool — what applies?"), with article requirements derived from scenario? Or are articles the entry point, with scenarios as a filter? *Lean: scenarios are first-class navigable entities; the OS supports both navigation paths.*

7. **Per-requirement source_authority for ISO frameworks.** Worth tagging at all? ISO standards are uniformly binding. *Lean: optional field; defaults to "binding" for ISO/legal; matters explicitly for EU AI Act and code-level frameworks.*

8. **Description Criteria for SOC 2.** Are these requirements with `kind: description_criterion`, or a separate top-level `description_criteria[]` block at framework level (parallel to `requirements[]`)? *Lean: separate block — they're meta-criteria about the system description, not control requirements per se.*

---

## Recommended next moves

1. Resolve the 8 open design decisions above (you and Claude — not all need detailed answers, some have obvious leans).
2. Lock schema v2 spec as `framework-schema.md`.
3. Re-emit `iso-27001.yaml` against schema v2 — should be largely mechanical given the existing build script.
4. Validate: load the new YAML in a small Python loader that exercises every field type. Find schema bugs before they propagate to 8 more files.
5. Decision gate: continue YAML population, or pivot to building the OS with one proven framework.
