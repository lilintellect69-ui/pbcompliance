# PrivateBox SOC 2 Architecture Pack

PB-curated source matrix for authoring `frameworks/soc-2/soc-2.yaml`. Captured 2026-05-11. Mirrors the ISO 42001 / POPIA / King V pack pattern.

Six tables follow:
1. SOC 2 framework structure for PrivateBox (DC + CC + optional categories)
2. PrivateBox SOC 2 master control matrix (full 51-criterion table)
3. Type I design evidence matrix
4. Type II operating effectiveness matrix (frequency + observation period per criterion)
5. (omitted by source)
6. System description requirements for PrivateBox (DC1–DC9)

Authoring approach:
- 33 Common Criteria entries (CC1.1 → CC9.2) as `kind: criterion` with ID prefix `soc-2-cc-X.Y`.
- 18 optional-category entries: 3 Availability (A1.1–A1.3, prefix `a`), 2 Confidentiality (C1.1–C1.2, prefix `c`), 5 Processing Integrity (PI1.1–PI1.5, prefix `pi`), 8 Privacy (P1.1, P2.1, P3.1, P4-bundle, P5-bundle, P6-bundle, P7.1, P8.1, prefix `p`).
- 9 Description Criteria (DC1–DC9) in framework-level `description_criteria[]` block (SOC 2 schema feature per docs/schema-v2.md).
- Each criterion populates `type_i_evidence` (from Table 3) and `type_ii_evidence` / `suggested_observation_period` (from Table 4) — SOC 2-specific schema fields.
- Outgoing crosswalks to ISO 27001 primarily (CC6 ↔ A.5/A.8 security overlap), selective to 27701/42001/POPIA/king-v where alignment is meaningful.
- 5 scenarios for Type I / Type II / subservice treatments.
- 7 OQs for service auditor, additional categories, observation period, etc.
