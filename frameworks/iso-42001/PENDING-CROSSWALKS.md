# ISO 42001 — Pending Crosswalks

Crosswalk targets that cannot be authored yet because the target frameworks are not in `frameworks/`. Source: §11 of `source/privatebox-iso-ai-governance-architecture.md` (PB Architecture Pack).

When the target framework is authored, wire these crosswalks into the **42001** YAML (more-specific/newer references the older/foundational; ISO 27001 is the only target-only framework — see CLAUDE.md).

Format: `<42001 native_id> → <target framework> <target ref(s)> | <theme>`. Resolve the exact target IDs against the new framework's `requirements[]` when wiring.

---

## To NIST AI RMF (when `nist-ai-rmf` is authored)

| 42001 ref | Target | Theme |
|---|---|---|
| cl-4 (all) | GOVERN 1 | Org context |
| cl-5 (all) | GOVERN 2 | Tone from top |
| cl-6.1 | MAP, MEASURE | AI risk |
| cl-6.1.4 | MAP | Impact assessment |
| cl-7 | GOVERN 3 | Resources |
| cl-8 | MANAGE | Operations |
| cl-9 | MEASURE | Monitoring |
| cl-10 | MANAGE 4 | Improvement |
| a-2 (all) | GOVERN 1 | Policy |
| a-3 (all) | GOVERN 2.1 | Roles |
| a-4 (all) | GOVERN 1.6 | Inventory |
| a-5 (all) | MAP | Impact assessment |
| a-6 (all) | MAP, MEASURE, MANAGE | Lifecycle |
| a-6.1.4 | MEASURE 2.11 | Bias |
| a-6.2.4 | MEASURE 3 | Logs |
| a-7 (all) | MAP 4 | Data |
| a-8 (all) | MAP 3, MANAGE 4.3 | Transparency |
| a-9 (all) | GOVERN 4 | Use |
| a-10 (all) | GOVERN 6, MAP 4.1 | Suppliers |

Industry estimates: ~70-80% operational overlap (per §11 caveat).

---

## To POPIA (when `popia` is authored)

| 42001 ref | Target | Theme |
|---|---|---|
| cl-4 | s.4 (PoPI scope) | Org context |
| cl-5 | Accountability principle | Tone from top |
| cl-6.1 | s.19 (security safeguards) | AI risk |
| cl-6.1.4 | s.71 (automated decisions); DPIA equivalent | Impact assessment |
| cl-7 | Operator training | Resources |
| cl-8 | Operational safeguards | Operations |
| cl-9 | Breach notification s.22 | Monitoring |
| a-2 | Info security policy | Policy |
| a-3 | Information Officer | Roles |
| a-5 | s.71 / DPIA | Impact |
| a-6 | Security s.19 | Lifecycle |
| a-6.2.3 | s.71(2) human review | Human oversight |
| a-6.2.4 | s.14 records | Logging |
| a-7 | Conditions for processing s.8-25 | Data |
| a-7.5 | s.71, ch.3 | PII in AI |
| a-8 | s.18 notification | Transparency |
| a-9 | Lawful processing | Use |
| a-10 | Operator obligations s.20-21 | Suppliers |

PB position: customer is responsible party (controller equivalent); PrivateBox is operator. POPIA s.71 (automated decision-making) is the primary current binding constraint per §6 of source.

---

## To King V (when `king-v` is authored)

| 42001 ref | Target | Theme |
|---|---|---|
| cl-4 | Principle 4 (Strategy) | Org context |
| cl-5 | Principle 1 (Ethical leadership) | Tone from top |
| cl-6.1 | Principle 4 (Risk) | AI risk |
| cl-6.1.4 | Principle 4 | Impact assessment |
| cl-7 | Principle 5 (Resources) | Resources |
| cl-8 | Principle 6 (Performance) | Operations |
| cl-9 | Principle 8 (Assurance) | Monitoring |
| cl-10 | Principle 13 (Disclosure) | Improvement |
| a-3 | Principle 1 | Roles |
| a-4 | Principle 12 (IT mgmt) | Inventory |
| a-5 | Principle 4 | Impact assessment |
| a-6 | Principle 12 | Lifecycle |
| a-6.1.4 | Principle 4 | Bias |
| a-6.2.3 | Principle 12 | Human oversight |
| a-6.2.4 | Principle 8 | Logging |
| a-7 | Principle 12 | Data |
| a-7.5 | Principle 12 | PII in AI |
| a-8 | Principle 13 (Disclosure) | Transparency |
| a-9 | Principle 4 | Responsible use |
| a-10 | Principle 11 (Stakeholders) | Suppliers |

King V brings AI explicitly into SA corporate governance from financial years starting on/after 2026-01-01 (see source §6 caveats; tracked in `oq-42001-king-v-trigger`).

---

## Notes

- Crosswalk direction: 42001 references INTO these frameworks (more-specific → more-general / domain-specific). Per CLAUDE.md, ISO 27001 is the only target-only framework — but 42001 is also expected to BE a target for sector frameworks (e.g., a future SA AI Act).
- When resolving target IDs, run `make crosswalks` after wiring; the auto-suggester may surface additional matches based on title/text overlap.
- The pre-built crosswalks below are PB-curated (not auto-detected). Treat them as the seed; do not delete entries without checking the source pack §11.
