"""
HISTORICAL / ARCHIVAL SCRIPT — already applied. Do not re-run.

This script was the one-shot applier of the initial Option B crosswalks across
ISO 27001, ISO 27701, and EU AI Act YAMLs. The crosswalks it applied are now
embedded in those YAMLs. Re-running it would either no-op (if rules detect
existing entries) or duplicate.

For new framework authoring, do NOT use this script. Instead:
  1. Run `make crosswalks` to see auto-suggested candidates
  2. Hand-author crosswalks directly in the new framework's YAML
  3. Validate with `make validate`

Kept in build/ as the audit record of what was done. Read-only in spirit.

Original docstring follows for context:

Two sources of crosswalks:
  1. STRUCTURAL — auto-generated from native_id matching:
     - 27701 clauses 4.1-10.2 ↔ 27001 clauses 4.1-10.2 (Annex SL HLS shared)
     - 27701 A.3 shared controls ↔ 27001 Annex A controls (numbering correspondence)
  2. SEMANTIC — hand-authored cross-domain mappings:
     - 27701 A.1/A.2 (privacy-specific) ↔ 27001 (security overlaps)
     - EU AI Act articles ↔ 27001 (risk/security/lifecycle)
     - EU AI Act articles ↔ 27701 (privacy/AI overlaps)

Crosswalk authorship rule (per schema v2 decision):
  - Crosswalks are one-way at write time
  - Author from more-specific/newer toward more-general/older
  - 27701 → 27001 (privacy more specific than security)
  - EU AI Act → 27001 (regulation more specific than baseline)
  - EU AI Act → 27701 (AI regulation more specific than baseline privacy)
  - OS resolves reverse graph at load time
"""

import yaml
from pathlib import Path
from collections import OrderedDict

# Historical path — kept to make the original script readable; not used.
YAML_DIR = Path("/mnt/user-data/outputs")


# =============================================================================
# YAML helpers (keep formatting consistent with build scripts)
# =============================================================================

class LiteralStr(str):
    pass


class FoldedStr(str):
    pass


def F(s):
    return FoldedStr(" ".join(s.split()))


yaml.add_representer(
    OrderedDict,
    lambda d, data: d.represent_mapping("tag:yaml.org,2002:map", data.items()),
)
yaml.add_representer(
    LiteralStr,
    lambda d, data: d.represent_scalar("tag:yaml.org,2002:str", data, style="|"),
)
yaml.add_representer(
    FoldedStr,
    lambda d, data: d.represent_scalar("tag:yaml.org,2002:str", data, style=">"),
)


# =============================================================================
# STRUCTURAL crosswalks — auto-derived from native_id correspondence
# =============================================================================

# 27701 PIMS clauses 4.1-10.2 → 27001 ISMS clauses 4.1-10.2
# Annex SL High-Level Structure — clauses are 1:1 by design across all ISO mgmt-system standards
PIMS_CLAUSE_NIDS = [
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "5.3",
    "6.1", "6.2", "6.3",
    "7.1", "7.2", "7.3", "7.4", "7.5",
    "8.1", "8.2", "8.3",
    "9.1", "9.2", "9.3",
    "10.1", "10.2",
]

# 27701 A.3 shared controls → 27001 Annex A
# Format: (27701 native_id, list of 27001 native_id targets)
# 27701 A.3 explicitly aligns to ISO 27002:2022 themes; numbering correspondence is direct.
A3_TO_27001_ANNEX_A = [
    ("5.7", ["5.7"]),                               # Threat intelligence
    ("5.16-8.5", ["5.16", "8.2", "8.3", "8.4", "8.5"]),  # IAM + privileged access
    ("5.14-5.15", ["5.14", "5.15"]),                # Information transfer
    ("8.15-8.17", ["8.15", "8.16", "8.17"]),        # Logging & monitoring
    ("8.24", ["8.24"]),                             # Cryptography
    ("8.25-8.30", ["8.25", "8.26", "8.27", "8.28", "8.29", "8.30"]),  # Secure development
    ("8.13", ["8.13"]),                             # Backup
    ("5.24-5.27", ["5.24", "5.25", "5.26", "5.27"]),  # Incident management
    ("5.19-5.23", ["5.19", "5.20", "5.21", "5.22", "5.23"]),  # Supplier / cloud
    ("7.x", ["7.1", "7.2", "7.3", "7.4"]),          # Physical (representative)
    ("5.31-5.34", ["5.31", "5.32", "5.33", "5.34"]),  # Compliance / records
]


# =============================================================================
# SEMANTIC crosswalks — hand-authored cross-domain mappings
# =============================================================================

# 27701 A.1 controllers + A.2 processors → 27001 (sparser, requires judgment)
# Only the genuinely overlapping ones; many privacy controls have no security analog.
SEMANTIC_27701_TO_27001 = {
    # Controller controls — most don't crosswalk to 27001 (privacy-specific)
    "iso-27701-a1-6": [  # Contracts with processors
        ("iso-27001-a-5.19", "Supplier relationships — security baseline; privacy adds Art 28 / s.21 specifics"),
        ("iso-27001-a-5.20", "Addressing security in supplier agreements — DPA is privacy-specific instance"),
    ],
    "iso-27701-a1-12": [  # Privacy by design / by default
        ("iso-27001-a-8.25", "Secure development lifecycle — PbD is the privacy lens of secure design"),
        ("iso-27001-a-8.27", "Secure system architecture and engineering principles"),
    ],
    "iso-27701-a1-13": [  # Cross-border transfer basis
        ("iso-27001-a-5.14", "Information transfer rules — privacy adds jurisdictional/legal basis layer"),
    ],
    "iso-27701-a1-16": [  # Records of disclosures incl. law-enforcement
        ("iso-27001-a-5.34", "Privacy and protection of PII — disclosure logging is a privacy-specific evidence"),
    ],
    # Processor controls
    "iso-27701-a2-6": [  # Confidentiality undertakings
        ("iso-27001-a-6.6", "Confidentiality or non-disclosure agreements — same control with privacy emphasis"),
    ],
    "iso-27701-a2-8": [  # Assist controller (DSAR, breach)
        ("iso-27001-a-5.34", "Privacy and protection of PII — assist obligations are operational instance"),
    ],
    "iso-27701-a2-16": [  # Disclosure of subcontractors
        ("iso-27001-a-5.19", "Supplier relationships — sub-processor register is privacy operationalisation"),
        ("iso-27001-a-5.21", "Managing security in the ICT supply chain"),
    ],
    "iso-27701-a2-17": [  # Engagement of subcontractor (flow-down)
        ("iso-27001-a-5.20", "Addressing security in supplier agreements — DPA flow-down is the privacy form"),
    ],
}

# EU AI Act → 27001 (sparser — security/risk overlaps)
SEMANTIC_EU_AI_ACT_TO_27001 = {
    "eu-ai-act-art-4": [  # AI Literacy
        ("iso-27001-cl-7.2", "Competence — AI literacy is the AI-specific instance of competence requirement"),
        ("iso-27001-cl-7.3", "Awareness — AI literacy programme is the AI awareness instance"),
    ],
    "eu-ai-act-art-9": [  # Risk Management (high-risk)
        ("iso-27001-cl-6.1", "ISMS risk planning — Art 9 RMS is the AI-specific risk discipline"),
        ("iso-27001-a-5.7", "Threat intelligence — feeds AI risk identification"),
    ],
    "eu-ai-act-art-10": [  # Data Governance (high-risk)
        ("iso-27001-a-8.10", "Information deletion — supports data lifecycle obligations"),
        ("iso-27001-a-8.11", "Data masking — supports data minimisation"),
        ("iso-27001-a-8.12", "Data leakage prevention — protects training data integrity"),
    ],
    "eu-ai-act-art-11": [  # Technical Documentation
        ("iso-27001-cl-7.5", "Documented information — Annex IV file is structured technical documentation"),
    ],
    "eu-ai-act-art-12": [  # Record-Keeping / Logs
        ("iso-27001-a-8.15", "Logging — Art 12 logs build on the security logging baseline"),
        ("iso-27001-a-8.16", "Monitoring activities — runtime monitoring overlap"),
        ("iso-27001-a-8.17", "Clock synchronisation — log integrity dependency"),
    ],
    "eu-ai-act-art-15": [  # Accuracy, Robustness, Cybersecurity
        ("iso-27001-a-5.7", "Threat intelligence — adversarial-testing input"),
        ("iso-27001-a-8.7", "Protection against malware — model-poisoning analog"),
        ("iso-27001-a-8.16", "Monitoring activities — drift/anomaly detection"),
        ("iso-27001-a-8.25", "Secure development lifecycle"),
        ("iso-27001-a-8.28", "Secure coding"),
        ("iso-27001-a-8.29", "Security testing in development and acceptance"),
    ],
    "eu-ai-act-art-16": [  # Provider Obligations (high-risk)
        ("iso-27001-cl-9.2", "Internal audit — Art 16 quality discipline mirrors ISMS audit"),
        ("iso-27001-cl-9.3", "Management review — Art 16 management oversight"),
    ],
    "eu-ai-act-art-17": [  # Quality Management System
        ("iso-27001-cl-4.4", "ISMS establishment — QMS scaffolding shares structure with ISMS"),
        ("iso-27001-cl-9.2", "Internal audit"),
        ("iso-27001-cl-9.3", "Management review"),
    ],
    "eu-ai-act-art-23-24": [  # Importers / Distributors
        ("iso-27001-a-5.19", "Supplier relationships — channel partners are suppliers"),
        ("iso-27001-a-5.20", "Addressing security in supplier agreements"),
    ],
    "eu-ai-act-art-25": [  # Role-flips along value chain
        ("iso-27001-a-5.19", "Supplier relationships — Art 25(4) written agreements"),
        ("iso-27001-a-5.20", "Addressing security in supplier agreements"),
    ],
    "eu-ai-act-art-72": [  # Post-Market Monitoring
        ("iso-27001-cl-9.1", "Performance monitoring — PMM extends ISMS monitoring to AI lifecycle"),
        ("iso-27001-a-5.27", "Learning from incidents — feeds PMM data"),
    ],
    "eu-ai-act-art-73": [  # Serious-incident reporting
        ("iso-27001-a-5.24", "Incident management planning — Art 73 has stricter timing"),
        ("iso-27001-a-5.25", "Assessment and decision on information security events"),
        ("iso-27001-a-5.26", "Response to information security incidents"),
        ("iso-27001-a-5.27", "Learning from incidents"),
    ],
}

# EU AI Act → 27701 (medium density — privacy/AI overlaps)
SEMANTIC_EU_AI_ACT_TO_27701 = {
    "eu-ai-act-art-4": [  # AI Literacy
        ("iso-27701-cl-7.2", "Competence — AI literacy programme parallels privacy competence"),
        ("iso-27701-cl-7.3", "Awareness — AI literacy and privacy awareness share form"),
    ],
    "eu-ai-act-art-9": [  # Risk Management
        ("iso-27701-cl-6.1", "Privacy + security risk methodology — Art 9 RMS aligns to integrated risk discipline"),
        ("iso-27701-cl-8.2", "Operational privacy risk assessment"),
    ],
    "eu-ai-act-art-10": [  # Data Governance
        ("iso-27701-a1-2", "Identify and document purpose — training data must have documented purpose"),
        ("iso-27701-a1-3", "Identify lawful basis — applies to training data collection"),
        ("iso-27701-a1-12", "Privacy by design — data governance is core PbD principle"),
        ("iso-27701-a2-3", "No re-purposing — 'no training on customer data' is the operational form"),
    ],
    "eu-ai-act-art-11": [  # Technical Documentation
        ("iso-27701-cl-7.5", "Documented information — Annex IV file structure"),
    ],
    "eu-ai-act-art-12": [  # Logs
        ("iso-27701-a3-8.15-8.17", "Logging & monitoring — Art 12 builds on privacy-aware logging baseline"),
    ],
    "eu-ai-act-art-15": [  # Accuracy, Robustness, Cybersecurity
        ("iso-27701-a3-8.24", "Cryptography — protects model and customer data"),
        ("iso-27701-a3-8.25-8.30", "Secure development including PbD"),
    ],
    "eu-ai-act-art-16": [  # Provider Obligations
        ("iso-27701-cl-9.2", "Internal audit"),
        ("iso-27701-cl-9.3", "Management review"),
    ],
    "eu-ai-act-art-17": [  # QMS
        ("iso-27701-cl-4.4", "PIMS establishment — QMS scaffolding shares structure"),
        ("iso-27701-cl-9.2", "Internal audit"),
        ("iso-27701-cl-9.3", "Management review"),
    ],
    "eu-ai-act-art-22": [  # Authorised Representatives (high-risk)
        ("iso-27701-a1-6", "Contracts with processors — AR mandate is contractual instrument"),
    ],
    "eu-ai-act-art-23-24": [  # Importers / Distributors
        ("iso-27701-a3-5.19-5.23", "Supplier / cloud security — channel partners as suppliers"),
    ],
    "eu-ai-act-art-25": [  # Role-flips
        ("iso-27701-a1-6", "Contracts with processors — Art 25(4) written agreements"),
        ("iso-27701-a1-7", "Joint controllership — analogous role-allocation discipline"),
        ("iso-27701-a3-5.19-5.23", "Supplier security"),
    ],
    "eu-ai-act-art-26": [  # Deployer Obligations
        ("iso-27701-a2-2", "Customer agreement / instructions — deployer-as-controller direction-giving"),
        ("iso-27701-a2-8", "Assist controller — analogous to deployer support obligations"),
    ],
    "eu-ai-act-art-27": [  # FRIA
        ("iso-27701-a1-5", "PIA/DPIA — FRIA extends DPIA with fundamental-rights layer"),
    ],
    "eu-ai-act-art-50": [  # Transparency
        ("iso-27701-a1-10", "Privacy notice — Art 50 disclosure parallels privacy transparency principle"),
    ],
    "eu-ai-act-art-53": [  # GPAI Documentation
        ("iso-27701-a1-13", "Transfer basis — Annex XII downstream documentation"),
        ("iso-27701-a2-11", "Transfer basis (processor scope)"),
    ],
    "eu-ai-act-art-72": [  # Post-Market Monitoring
        ("iso-27701-cl-9.1", "Monitoring, measurement, analysis and evaluation"),
        ("iso-27701-cl-10.1", "Continual improvement"),
    ],
    "eu-ai-act-art-73": [  # Serious-incident reporting
        ("iso-27701-a3-5.24-5.27", "Privacy incident management — Art 73 has stricter timing for high-risk AI"),
    ],
}


# =============================================================================
# Build the full crosswalk index per source framework
# =============================================================================


def build_iso27701_crosswalks():
    """Return dict: 27701-req-id -> list of crosswalk entries."""
    crosswalks = {}

    # PIMS clauses 4.1-10.2 → 27001 clauses 1:1
    for nid in PIMS_CLAUSE_NIDS:
        src = f"iso-27701-cl-{nid}"
        crosswalks[src] = [
            OrderedDict([
                ("framework", "iso-27001"),
                ("refs", [f"iso-27001-cl-{nid}"]),
                ("note", F("Annex SL High-Level Structure — clauses 4-10 are 1:1 across ISO management-system standards.")),
            ]),
        ]

    # 27701 A.3 shared controls → 27001 Annex A
    for a3_nid, target_nids in A3_TO_27001_ANNEX_A:
        src = f"iso-27701-a3-{a3_nid}"
        crosswalks[src] = [
            OrderedDict([
                ("framework", "iso-27001"),
                ("refs", [f"iso-27001-a-{n}" for n in target_nids]),
                ("note", F("ISO/IEC 27701:2025 A.3 controls explicitly align to ISO/IEC 27002:2022 themes — same numbering, privacy lens.")),
            ]),
        ]

    # Semantic 27701 A.1/A.2 → 27001 — Option B: one entry per (ref, note) pair
    # Each semantic mapping has its own substantive note; collapsing them into a
    # single entry lost per-target context. Structural entries above keep shared
    # notes because the relationship really is one shared interpretation.
    for src_id, targets in SEMANTIC_27701_TO_27001.items():
        for target_id, note in targets:
            crosswalks.setdefault(src_id, []).append(
                OrderedDict([
                    ("framework", "iso-27001"),
                    ("refs", [target_id]),
                    ("note", F(note)),
                ])
            )

    return crosswalks


def build_eu_ai_act_crosswalks():
    """Return dict: eu-ai-act-req-id -> list of crosswalk entries."""
    crosswalks = {}

    # EU AI Act → 27001 — Option B: one entry per (ref, note) pair
    for src_id, targets in SEMANTIC_EU_AI_ACT_TO_27001.items():
        for target_id, note in targets:
            crosswalks.setdefault(src_id, []).append(
                OrderedDict([
                    ("framework", "iso-27001"),
                    ("refs", [target_id]),
                    ("note", F(note)),
                ])
            )

    # EU AI Act → 27701 — Option B: one entry per (ref, note) pair
    for src_id, targets in SEMANTIC_EU_AI_ACT_TO_27701.items():
        for target_id, note in targets:
            crosswalks.setdefault(src_id, []).append(
                OrderedDict([
                    ("framework", "iso-27701"),
                    ("refs", [target_id]),
                    ("note", F(note)),
                ])
            )

    return crosswalks


# =============================================================================
# Apply crosswalks to YAML files
# =============================================================================


def apply_crosswalks_to_file(yaml_path, crosswalks):
    """Load YAML, populate crosswalk arrays, write back."""
    with open(yaml_path) as f:
        # Preserve top-level header comments
        header_lines = []
        for line in f:
            if line.startswith("#") or not line.strip():
                header_lines.append(line)
            else:
                break
    header = "".join(header_lines)

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    # Convert to OrderedDict for stable output
    if not isinstance(data, OrderedDict):
        # safe_load returns dict; we need to reconstruct order
        # Standard top-level order:
        ordered = OrderedDict()
        for k in data:
            ordered[k] = data[k]
        data = ordered

    # Populate crosswalks for each requirement that has a target
    populated = 0
    for req in data["requirements"]:
        rid = req["id"]
        if rid in crosswalks:
            req["crosswalk"] = crosswalks[rid]
            populated += 1

    # Write back
    with open(yaml_path, "w") as f:
        f.write(header)
        if not header.endswith("\n"):
            f.write("\n")
        yaml.dump(
            data, f,
            default_flow_style=False, sort_keys=False, allow_unicode=True,
            width=100, indent=2,
        )

    return populated


def main():
    iso27701_xw = build_iso27701_crosswalks()
    eu_ai_act_xw = build_eu_ai_act_crosswalks()

    print(f"# ISO 27701 source crosswalks: {len(iso27701_xw)}")
    total_27701_targets = sum(
        sum(len(entry["refs"]) for entry in entries)
        for entries in iso27701_xw.values()
    )
    print(f"  Total target refs: {total_27701_targets}")

    print(f"# EU AI Act source crosswalks: {len(eu_ai_act_xw)}")
    total_eu_targets = sum(
        sum(len(entry["refs"]) for entry in entries)
        for entries in eu_ai_act_xw.values()
    )
    print(f"  Total target refs: {total_eu_targets}")

    # Apply to YAML files
    print()
    n = apply_crosswalks_to_file(YAML_DIR / "iso-27701.yaml", iso27701_xw)
    print(f"# Applied to iso-27701.yaml: {n} requirements got crosswalks")
    n = apply_crosswalks_to_file(YAML_DIR / "eu-ai-act.yaml", eu_ai_act_xw)
    print(f"# Applied to eu-ai-act.yaml: {n} requirements got crosswalks")
    print(f"# iso-27001.yaml: unchanged (target only — OS resolves reverse graph)")


if __name__ == "__main__":
    main()
