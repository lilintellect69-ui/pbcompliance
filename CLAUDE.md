# CLAUDE.md — PrivateBox GRC OS

This file orients you (Claude) at the start of every session. Read it before doing anything else, including before reading any uploaded files. It captures methodology, current state, and conventions accumulated across many prior sessions.

## What this project is

PrivateBox is a South African on-prem AI vendor (privatebox.co.za) selling sovereign AI infrastructure to legal, medical, and financial customers. Three founders. Hardware: NVIDIA Spark plus open-source Onyx orchestration. Pre-certification phase — framing is "alignment not compliance."

This repo is **PrivateBox's internal Governance, Risk & Compliance Operating System** — an auditable, lens-aware tracker spanning nine compliance frameworks. Frameworks are unified through a single schema (v2) and an explicit cross-framework graph. The end state is a system that turns compliance work into a graph of reusable assets, then renders that graph into different surfaces: internal dashboard, customer DD pack, board posture report, regulatory technical documentation, audit-ready SoA.

## Two business models

Every entity carries a `business_models` enum: `on-prem`, `ai-factory`, or `both`. The lens toggle in the OS UI propagates through everything.

- **On-prem**: customer hardware, PB-managed appliance + management plane. Production today.
- **AI Factory**: partner DC ringfenced, multi-tenant. Aspirational. Blocked on ~10 open questions (`oq-partner-dc-*`, `oq-ai-factory-*`).

When ownership genuinely differs between models, the requirement carries `owner_by_model: { on_prem: 'SH', ai_factory: { status: 'pending', open_question: 'oq-...' } }`. The 12 ISO 27001 A.7 physical controls are the canonical example — on-prem owner is the customer (SH), AI Factory owner is unknown until partner-DC is selected.

## Repo layout

```
privatebox-grc-os/
├── CLAUDE.md                  # This file
├── MIGRATION.md               # First-10-minutes setup
├── Makefile                   # validate / dev / build / data
├── docs/
│   ├── schema-v2.md           # Schema spec (authoritative)
│   ├── structural-survey.md   # How each framework's structure maps to schema
│   └── crosswalk-candidates-report.md
├── frameworks/
│   ├── iso-27001/             # Each framework is self-contained
│   │   ├── iso-27001.yaml     # The output (123 reqs)
│   │   ├── build.py           # Generates the YAML from source
│   │   └── source/            # Source standard text
│   ├── iso-27701/             # 66 reqs
│   ├── eu-ai-act/             # 27 articles
│   └── (6 more to come)
├── build/                     # Cross-framework tooling
│   ├── validate_framework.py  # Schema v2 validator (12 rules)
│   ├── crosswalk_candidates.py
│   ├── apply_crosswalks.py
│   └── build_os_data.py       # Combines all YAMLs into os/src/data.json
├── os/                        # Vite-served React OS
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx            # 7-view OS prototype
│   │   ├── data.json          # Built artifact (do not hand-edit)
│   │   └── ...
└── .claude/
    └── skills/
        ├── compliance-framework-author/   # Authoring methodology for new YAMLs
        └── os-development/                # React OS architecture & extension patterns
```

## Schema v2 essentials

Read `docs/schema-v2.md` for the full spec. Key rules:

- One `requirements[]` list per framework, with `kind` enum (`requirement`, `objective`, `principle`, `practice`, `clause`).
- Either `requirement` or `objective` must be present (validator enforces). Not both, not neither.
- `tier`, `role_applicability`, `owner_by_model` are optional; default behavior covers most cases.
- `crosswalk[]` per requirement: list of `{ framework, refs[], note }` groups. Option B authoring rule: one entry per `(ref, note)` pair when semantically distinct; structural matches keep shared notes.
- ISO 27001 has no outgoing crosswalks — it's the foundational target only. More-specific/newer frameworks reference into it.
- `effective_dates[]`, `evidence_families[]`, `pb_application{}`, `roles[]`, `tiers[]`, `companion_standards[]` at framework level.
- `business_models` required on every requirement (enforced by validator).
- `external_safe_phrasing` is the Trust Pack composer engine — defensible, non-overclaiming statements per requirement.

## Build pipeline

```
source standard text  →  build.py (per framework)  →  framework.yaml
                                                          ↓
                                        validate_framework.py (12 rules)
                                                          ↓
                                        crosswalk_candidates.py (auto)
                                                          ↓
                                        apply_crosswalks.py (manual + auto)
                                                          ↓
                                        build_os_data.py (combine + reverse graph)
                                                          ↓
                                        os/src/data.json
                                                          ↓
                                        vite dev / build → renders OS
```

`make validate` runs validator on every YAML.
`make data` rebuilds data.json.
`make dev` serves OS at localhost:5173.
`make all` runs validate + crosswalks + data + babel-parse OS in sequence.

## Current state

**Done (3 frameworks, 216 requirements):**
- ISO/IEC 27001:2022 — 123 requirements (mandatory clauses 4-10 + 93 Annex A controls)
- ISO/IEC 27701:2025 — 66 requirements (privacy extension; controllers + processors split)
- EU AI Act (Reg 2024/1689) — 27 articles (risk tiers, role obligations, GPAI)

**Crosswalks:** 59 source crosswalks → 133 cross-framework target refs (Option B: 108 entries). All validate clean.

**Open questions registry:** 23 unique. 10 are AI Factory carry-overs blocking partner-DC selection.

**Scenarios:** 25 across the three frameworks. Distribution: 19 both-models, 5 on-prem-only, 1 ai-factory-only.

**Evidence families:** 55 across the three frameworks (15 + 20 + 20).

**OS:** 6-view prototype + lens toggle. Views: Home, Framework detail (4-section user-journey spine), Requirement detail, Scenario detail, Open questions, Cross-framework graph.

**Pending (6 frameworks):**
1. ISO 42001 (AI management system) — natural next; extends 27001's HLS pattern; sets up AI Systems Registry path
2. NIST bundle (RMF + SSDF + 800-218A + AI RMF) — possibly three or four separate frameworks
3. SOC 2 Trust Services Criteria — different audit type (attestation, not certification)
4. POPIA (SA privacy law) — statutory, not a standard
5. King V (SA corporate governance, Oct 2025) — principle-based, not control-based
6. COBIT 2019 — governance + management objectives

## Methodology — minimum-viable-loop

The first three frameworks were built using a "prove the foundation works on the hardest parts before scaling" approach:

1. **Three structurally-different frameworks first** (clause-style management standard / dual-role privacy extension / regulatory act) to stress-test schema v2.
2. **Validator and crosswalk pipeline before scaling** to ensure drift is caught immediately.
3. **End-to-end OS prototype** rendering all three together, to surface integration problems early.
4. **Read-only first**, write/edit later, so the read model is right before write paths complicate things.

This methodology stays. Don't break it. Don't propose authoring six frameworks before re-running the validator. Don't propose the Trust Pack composer before the Controls library exists.

## Conventions

- The user prefers terse, structured responses. "Go", "B works", "Continue" are typical. Don't over-explain.
- The user pushes back on consensus-seeking reasoning. Take positions; defend them.
- The user values methodology rigor. Don't shortcut steps. If a sequence is wrong, say so.
- Three-framework build YAMLs are large (100-150KB each). Don't try to read them whole; use the validator's output and `view` with line ranges.
- The OS template is large (~87KB). Use grep + `view` with ranges, not full reads.
- When changing schema or build pipeline, run `make all` afterwards to confirm nothing breaks downstream.
- Wireframes and design intent live in transcripts of prior sessions; if you need them and they're not in the repo, ask before guessing.

## What to read next

- Authoring a new framework YAML? Open `.claude/skills/compliance-framework-author/SKILL.md`.
- Extending the React OS (new view, new entity type, lens system changes)? Open `.claude/skills/os-development/SKILL.md`.
- Schema confused? `docs/schema-v2.md`.
- Adding a new entity type (Controls, Risks, AI Systems)? Read both skills, then propose schema additions and validate against existing data.
- OS UI work? `os/src/App.jsx` is the entry point; lens system at the top; views below.

## What NOT to do

- Don't reproduce copyrighted standard text in YAMLs. Cite clause numbers; paraphrase requirements; never quote substantial passages from ISO, NIST, EU AI Act, etc.
- Don't author crosswalks without running `crosswalk_candidates.py` first to see what's auto-detected.
- Don't add fields to schema v2 without updating `docs/schema-v2.md` AND `validate_framework.py` AND a one-line note in this file's "current state" section.
- Don't commit `os/src/data.json` after every YAML edit — it's a build artifact. Either gitignore it or commit it on a deliberate cadence.
