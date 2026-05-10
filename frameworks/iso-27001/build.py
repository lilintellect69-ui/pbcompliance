"""
Build PrivateBox's ISO/IEC 27001:2022 alignment record against schema v2.

This re-emits the v1 ISO 27001 data in v2 shape:
- Single requirements[] list (no clauses/annex_a_controls split)
- ID prefixing (iso-27001-cl-4.1, iso-27001-a-5.1)
- kind field per requirement
- crosswalk arrays (empty for now; populated as other frameworks land)
- open_questions[] block seeded with AI Factory unknowns
- owner_by_model on requirements where AI Factory ownership genuinely diverges

Source-of-truth content comes from v1 build script. This transforms; it does
not re-type. Edit v1 if you want to edit content; re-run this to regenerate.
"""

import sys
import yaml
from pathlib import Path
from collections import OrderedDict

# Pull v1 DATA + YAML helpers
sys.path.insert(0, "/home/claude/privatebox-grc/scripts")
import build_iso27001 as v1
from build_iso27001 import LiteralStr, FoldedStr, L, F


# =============================================================================
# Top-level metadata
# =============================================================================

DATA = OrderedDict()

DATA["schema_version"] = "2.0"
DATA["id"] = "iso-27001"
DATA["version"] = "2022"
DATA["full_name"] = (
    "ISO/IEC 27001:2022 Information security management systems — Requirements"
)
DATA["type"] = "management_system_standard"
DATA["issuer"] = "ISO/IEC"
DATA["audit_type"] = "certification"
DATA["certifiable"] = True

DATA["pb_interpretation_version"] = "1.0"
DATA["pb_interpretation_owner"] = None
DATA["pb_interpretation_last_reviewed"] = None

# Single framework, no sub-frameworks or companion standards
# (ISO 27002 is implementation guidance for Annex A but doesn't add requirements)

# Roles: ISO 27001 has a single audited org, no role-splitting
DATA["roles"] = []

# Tiers: not applicable
DATA["tiers"] = []

# No phased application; single revision date
DATA["effective_dates"] = []


# =============================================================================
# PB application (carried over from v1)
# =============================================================================

DATA["pb_application"] = v1.DATA["pb_application"]


# =============================================================================
# SoA guidance (carried over from v1)
# =============================================================================

DATA["soa_guidance"] = v1.DATA["soa_guidance"]


# =============================================================================
# Shared responsibility model (carried over from v1)
# =============================================================================

DATA["shared_responsibility_model"] = v1.DATA["shared_responsibility_model"]


# =============================================================================
# Evidence families (carried over from v1)
# =============================================================================

DATA["evidence_families"] = v1.DATA["evidence_families"]


# =============================================================================
# Scenarios — not used for ISO 27001
# =============================================================================

DATA["scenarios"] = []


# =============================================================================
# Open questions — seed AI Factory unknowns
# =============================================================================

DATA["open_questions"] = [
    OrderedDict([
        ("id", "oq-partner-dc-selection"),
        ("question", "Which DC partner(s) for AI Factory deployments?"),
        ("candidate_answers", ["Teraco", "Africa Data Centres", "Vantage", "TBD"]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", [
            "iso-27001-a-7.1", "iso-27001-a-7.2", "iso-27001-a-7.3",
            "iso-27001-a-7.4", "iso-27001-a-7.5", "iso-27001-a-7.6",
            "iso-27001-a-7.8", "iso-27001-a-7.11", "iso-27001-a-7.12",
            "iso-27001-a-7.13",
        ]),
        ("blocks_scenarios", []),
        ("notes", F(
            "Partner DC selection cascades into physical perimeter, entry, monitoring, "
            "environmental, equipment siting, utilities, cabling, and maintenance controls. "
            "Until selected, AI Factory ownership of A.7 controls is pending."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-jurisdiction"),
        ("question", "Which legal jurisdiction(s) for AI Factory hosting?"),
        ("candidate_answers", ["South Africa only", "SA + EU", "SA + US", "Multi-region"]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", [
            "iso-27001-a-5.31", "iso-27001-a-5.34",
        ]),
        ("blocks_scenarios", []),
        ("notes", F(
            "Jurisdiction determines applicable laws (POPIA only vs POPIA+GDPR+others), "
            "cross-border transfer rules, and data residency commitments to customers."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-tenancy-model"),
        ("question", "Tenancy isolation posture for AI Factory?"),
        ("candidate_answers", [
            "Single-tenant ringfenced (1 customer per ringfenced infra)",
            "Multi-tenant ringfenced (multiple customers, strong isolation)",
            "Hybrid (single-tenant for high-sensitivity, multi-tenant for others)",
        ]),
        ("decision_owner", "PrivateBox founders + technical lead"),
        ("decision_status", "pending"),
        ("blocks_requirements", [
            "iso-27001-a-8.31", "iso-27001-a-8.33",
        ]),
        ("blocks_scenarios", []),
        ("notes", F(
            "Tenancy model determines multi-tenant isolation control posture, "
            "test data handling, and environment separation requirements."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-subprocessor-governance"),
        ("question", "How is the partner DC governed contractually as a sub-processor?"),
        ("candidate_answers", [
            "DPA flow-down with audit rights",
            "Master agreement with security schedule",
            "Joint controllership for some functions",
        ]),
        ("decision_owner", "Legal + PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", [
            "iso-27001-a-5.19", "iso-27001-a-5.20", "iso-27001-a-5.21",
            "iso-27001-a-5.22",
        ]),
        ("blocks_scenarios", []),
        ("notes", F(
            "Partner DC becomes a sub-processor under AI Factory model. Contractual posture "
            "determines supplier governance controls applicable to that relationship."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-data-residency"),
        ("question", "Data residency commitments to AI Factory customers?"),
        ("candidate_answers", [
            "Strict in-country only",
            "In-region (Africa)",
            "Customer choice with surcharge",
        ]),
        ("decision_owner", "PrivateBox founders + sales"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", []),
        ("notes", F(
            "Residency commitments shape customer-facing claims, contract templates, "
            "and constrain DC partner selection. Cross-references oq-partner-dc-selection."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-incident-response-split"),
        ("question", "Who handles which incidents in the AI Factory operational stack?"),
        ("candidate_answers", [
            "PB owns all incidents, partner DC notifies PB",
            "Layered: partner DC owns physical/network, PB owns app/AI",
            "Joint incident command for sev-1",
        ]),
        ("decision_owner", "PrivateBox technical lead"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", []),
        ("notes", F(
            "Incident response split affects shared-responsibility documentation, "
            "incident playbooks, and customer-facing incident notification commitments."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-customer-contract-template"),
        ("question", "What does the customer contract look like for AI Factory?"),
        ("candidate_answers", [
            "Adapted on-prem template with hosting addendum",
            "New SaaS-style template",
            "Per-deal bespoke",
        ]),
        ("decision_owner", "Legal + PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", []),
        ("notes", F(
            "Contract template determines what PB commits to, what's customer-owned, "
            "what's the partner DC's obligation, and how regulatory/legal duties allocate."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-offering-definition"),
        ("question", "What exactly is the AI Factory product?"),
        ("candidate_answers", [
            "Ringfenced seats on shared partner DC infra",
            "Dedicated server(s) per customer at partner DC",
            "Customer-owned hardware co-located at partner DC",
        ]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", []),
        ("notes", F(
            "The AI Factory product definition cascades into nearly every framework. "
            "Until defined, AI Factory scope decisions are placeholders."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-exit-portability"),
        ("question", "Customer exit / data portability mechanism for AI Factory?"),
        ("candidate_answers", [
            "Hardware shipment to customer + decom",
            "Encrypted data export + cryptographic disposal",
            "Migration to on-prem deployment",
        ]),
        ("decision_owner", "PrivateBox technical lead"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", []),
        ("notes", F(
            "Exit/portability affects continuity, deletion controls, customer trust, "
            "and contract termination clauses."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-hardware-lifecycle"),
        ("question", "Hardware lifecycle for AI Factory (procurement, sizing, disposal)?"),
        ("candidate_answers", [
            "PB procures and owns; partner DC operates",
            "Partner DC procures; PB pays operating fee",
            "Per-deal procurement",
        ]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", [
            "iso-27001-a-7.10", "iso-27001-a-7.14",
        ]),
        ("blocks_scenarios", []),
        ("notes", F(
            "Hardware lifecycle determines secure disposal posture, equipment maintenance "
            "responsibilities, and storage media controls."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
]


# =============================================================================
# Transform v1 clauses + annex_a_controls into v2 requirements[]
# =============================================================================

# AI Factory ownership overrides — only applied to requirements where ownership
# genuinely diverges between on-prem and AI Factory pending resolution of an
# open question. Most A.7 physical controls are in this category.
AI_FACTORY_PENDING = {
    "iso-27001-a-7.1": "oq-partner-dc-selection",
    "iso-27001-a-7.2": "oq-partner-dc-selection",
    "iso-27001-a-7.3": "oq-partner-dc-selection",
    "iso-27001-a-7.4": "oq-partner-dc-selection",
    "iso-27001-a-7.5": "oq-partner-dc-selection",
    "iso-27001-a-7.6": "oq-partner-dc-selection",
    "iso-27001-a-7.8": "oq-partner-dc-selection",
    "iso-27001-a-7.11": "oq-partner-dc-selection",
    "iso-27001-a-7.12": "oq-partner-dc-selection",
    "iso-27001-a-7.13": "oq-partner-dc-selection",
    "iso-27001-a-7.10": "oq-ai-factory-hardware-lifecycle",
    "iso-27001-a-7.14": "oq-ai-factory-hardware-lifecycle",
}


def _v1_clause_to_v2(clause):
    """Transform a v1 clause entry into a v2 requirement entry."""
    cid = f"iso-27001-{clause['id']}"  # cl-4.1 → iso-27001-cl-4.1
    return OrderedDict([
        ("id", cid),
        ("kind", "clause"),
        ("native_id", clause["subclause"]),
        ("group", clause["clause"]),
        ("group_name", clause["clause_title"]),
        ("title", clause["title"]),
        ("requirement", clause["requirement"]),
        ("auditor_intent", clause["auditor_intent"]),
        ("pb_interpretation", clause["pb_interpretation"]),
        ("owner", clause["owner"]),
        ("documented_evidence", clause["documented_evidence"]),
        ("operational_evidence", clause["operational_evidence"]),
        ("audit_methods", clause["audit_methods"]),
        ("cadence", clause["cadence"]),
        ("failure_modes", clause["failure_modes"]),
        ("maturity_target", clause["maturity_target"]),
        ("remediation", clause["remediation"]),
        ("external_safe_claim", clause["external_safe_claim"]),
        ("scope_note", clause.get("scope_note")),
        ("business_models", clause["business_models"]),
        ("crosswalk", []),
    ])


def _v1_annex_to_v2(annex):
    """Transform a v1 Annex A control entry into a v2 requirement entry."""
    cid = f"iso-27001-{annex['id']}"  # a-5.1 → iso-27001-a-5.1
    entry = OrderedDict([
        ("id", cid),
        ("kind", "control_org"),
        ("native_id", annex["control_id"]),
        ("group", annex["group"]),
        ("group_name", annex["group_name"]),
        ("title", annex["title"]),
        ("objective", annex["objective"]),
        ("applies", annex["applies"]),
        ("applies_rationale", annex["applies_rationale"]),
        ("na_justification_template", annex["na_justification_template"]),
        ("pb_interpretation", annex["pb_interpretation"]),
        ("owner", annex["owner"]),
        ("implementation", annex["implementation"]),
        ("evidence", annex["evidence"]),
        ("audit_methods", annex["audit_methods"]),
        ("cadence", annex["cadence"]),
        ("depends_on", annex["depends_on"]),
        ("pitfall", annex["pitfall"]),
        ("good_vs_audit_ready", annex["good_vs_audit_ready"]),
        ("maturity_target", annex["maturity_target"]),
        ("remediation", annex["remediation"]),
        ("external_safe_phrasing", annex["external_safe_phrasing"]),
        ("business_models", annex["business_models"]),
        ("crosswalk", []),
    ])

    # Apply AI Factory pending override where applicable
    if cid in AI_FACTORY_PENDING:
        oq_id = AI_FACTORY_PENDING[cid]
        entry["owner_by_model"] = OrderedDict([
            ("on_prem", annex["owner"]),
            ("ai_factory", OrderedDict([
                ("status", "pending"),
                ("open_question", oq_id),
            ])),
        ])

    return entry


# Build the unified requirements list
DATA["requirements"] = []
for clause in v1.DATA["clauses"]:
    DATA["requirements"].append(_v1_clause_to_v2(clause))
for annex in v1.DATA["annex_a_controls"]:
    DATA["requirements"].append(_v1_annex_to_v2(annex))


# =============================================================================
# Emit
# =============================================================================

if __name__ == "__main__":
    out_path = Path("/mnt/user-data/outputs/iso-27001.yaml")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = """# ISO/IEC 27001:2022 — PrivateBox alignment record (schema v2)
# Source-of-truth file for the GRC OS. Edits go in version control.
# Regenerate via: python scripts/build_iso27001_v2.py
#
# Schema: see /docs/framework-schema-v2.md
# Linked PB controls and evidence are resolved by the GRC OS at load time
# from the unified control library — they are not stored in this file.
"""

    with open(out_path, "w") as f:
        f.write(header + "\n")
        yaml.dump(
            DATA,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=100,
            indent=2,
        )

    # Sanity output
    print(f"Wrote {out_path}")
    print(f"  schema_version: {DATA['schema_version']}")
    print(f"  requirements: {len(DATA['requirements'])}")
    print(f"  open_questions: {len(DATA['open_questions'])}")
    print(f"  shared_responsibility_model: {len(DATA['shared_responsibility_model'])}")
    print(f"  evidence_families: {len(DATA['evidence_families'])}")

    # Count by kind
    from collections import Counter
    kinds = Counter(r["kind"] for r in DATA["requirements"])
    print(f"  by kind: {dict(kinds)}")

    # Count requirements with owner_by_model
    with_override = sum(1 for r in DATA["requirements"] if "owner_by_model" in r)
    print(f"  requirements with owner_by_model: {with_override}")
