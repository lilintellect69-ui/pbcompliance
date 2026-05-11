# PrivateBox NIST Bundle Architecture Pack

PB-curated source matrix for `frameworks/nist/nist.yaml` covering three NIST documents authored as one framework with `sub_frameworks[]`:

1. **AI RMF 1.0** + GenAI Profile (Jul 2024) — 72 function outcomes across GOVERN / MAP / MEASURE / MANAGE
2. **SSDF 1.1** (NIST SP 800-218) — 45 tasks across PO / PS / PW / RV
3. **SP 800-218A AI Overlay** (Final May 2024) — 19 overlay items adding model-specific recommendations on top of SSDF

Captured 2026-05-11. Mirrors the ISO 42001 / POPIA / King V / SOC 2 pack pattern.

## Sub-framework split

| Sub-framework | Kind | Count | Prefix |
|---|---|---|---|
| AI RMF | `function_outcome` | 72 | `nist-gov-`, `nist-map-`, `nist-measure-`, `nist-manage-` |
| SSDF | `task` | 45 | `nist-po-`, `nist-ps-`, `nist-pw-`, `nist-rv-` |
| 218A AI Overlay | `overlay` | 19 | `nist-218a-` |

## Unified artefact-family synthesis

The architecture pack identifies 7 unified artefact families that cut across AI RMF / SSDF / 218A:
1. Governance pack
2. System and model inventory
3. Secure SDLC
4. Model and data provenance
5. TEVV and red teaming
6. Runtime and incident operations
7. Customer handoff and shared responsibility

These map to `evidence_families[]` entries in the YAML.

## Authoring approach

- Each outcome / task / overlay item gets a YAML entry with `kind`, `sub_framework`, `native_id`, `requirement`, `pb_interpretation`, `owner`, `documented_evidence`, `audit_methods`, `failure_modes`, `maturity_target`, `external_safe_phrasing`.
- 218A overlay items use `overlay_target_id` (pointing back to the SSDF task being modified) and `overlay_modifies` (describing what 218A adds).
- 218A cross-cutting items (e.g., "Model provenance", "Prompt-injection risk", "Content provenance") use descriptive native IDs since they don't overlay a single SSDF task.
- Outgoing crosswalks: to ISO 27001 (security overlap, esp. SSDF PW), ISO 42001 (AI RMF heavy overlap), SOC 2 (SDLC overlap), POPIA, King V where natural.
- 5 scenarios for AI RMF profile selection, SSDF readiness, 218A activation.
- 6 OQs for profile choice, SBOM tooling, model registry tooling, etc.
