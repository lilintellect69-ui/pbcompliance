"""
Build PrivateBox's EU AI Act alignment record against schema v2.

Source: PrivateBox EU AI Act Compliance & Trust Architecture (research doc).
This is the structural torture-test for schema v2: 5 risk tiers, 6 roles,
14 scenarios with role-flips, phased effective dates, source authority levels,
and ~29 articles spanning Provider/Deployer/Importer/Distributor obligations.

Run: python scripts/build_eu_ai_act.py
Output: /mnt/user-data/outputs/eu-ai-act.yaml
"""

import yaml
from pathlib import Path
from collections import OrderedDict


# =============================================================================
# YAML helpers
# =============================================================================

class LiteralStr(str):
    pass


class FoldedStr(str):
    pass


def L(s):
    return LiteralStr(s.strip())


def F(s):
    return FoldedStr(" ".join(s.split()))


yaml.add_representer(
    OrderedDict,
    lambda dumper, data: dumper.represent_mapping(
        "tag:yaml.org,2002:map", data.items()
    ),
)
yaml.add_representer(
    LiteralStr,
    lambda dumper, data: dumper.represent_scalar(
        "tag:yaml.org,2002:str", data, style="|"
    ),
)
yaml.add_representer(
    FoldedStr,
    lambda dumper, data: dumper.represent_scalar(
        "tag:yaml.org,2002:str", data, style=">"
    ),
)


# =============================================================================
# Top-level metadata
# =============================================================================

DATA = OrderedDict()

DATA["schema_version"] = "2.0"
DATA["id"] = "eu-ai-act"
DATA["version"] = "Reg 2024/1689"
DATA["full_name"] = "Regulation (EU) 2024/1689 — Artificial Intelligence Act"
DATA["type"] = "regulation"
DATA["issuer"] = "European Union (Parliament & Council)"
DATA["audit_type"] = "conformity_assessment"
DATA["certifiable"] = False  # CE marking via conformity assessment — not ISO-style certification

DATA["pb_interpretation_version"] = "1.0"
DATA["pb_interpretation_owner"] = None
DATA["pb_interpretation_last_reviewed"] = None

# Risk tiers under the Act
DATA["tiers"] = ["prohibited", "high-risk", "gpai", "limited", "minimal"]

# Roles defined under the Act (Art. 3 + value-chain articles)
DATA["roles"] = [
    "provider",
    "deployer",
    "importer",
    "distributor",
    "authorised_representative",
    "product_manufacturer",
]

# Phased application — Art 113 timeline
DATA["effective_dates"] = [
    OrderedDict([
        ("milestone", "AI literacy + prohibited practices"),
        ("date", "2025-02-02"),
        ("obligations", ["eu-ai-act-art-4", "eu-ai-act-art-5"]),
        ("status", "in_force"),
        ("notes", "Highest-tier penalties for Art 5 breaches (€35M / 7%)."),
    ]),
    OrderedDict([
        ("milestone", "GPAI model provider obligations"),
        ("date", "2025-08-02"),
        ("obligations", [
            "eu-ai-act-art-51", "eu-ai-act-art-52", "eu-ai-act-art-53",
            "eu-ai-act-art-54", "eu-ai-act-art-55",
        ]),
        ("status", "in_force"),
        ("notes", "Legacy GPAI models (placed on market before this date) have until 2 Aug 2027."),
    ]),
    OrderedDict([
        ("milestone", "High-risk Annex III + transparency + most provider/deployer duties"),
        ("date", "2026-08-02"),
        ("obligations", [
            "eu-ai-act-art-6", "eu-ai-act-art-8", "eu-ai-act-art-9",
            "eu-ai-act-art-10", "eu-ai-act-art-11", "eu-ai-act-art-12",
            "eu-ai-act-art-13", "eu-ai-act-art-14", "eu-ai-act-art-15",
            "eu-ai-act-art-16", "eu-ai-act-art-17", "eu-ai-act-art-22",
            "eu-ai-act-art-25", "eu-ai-act-art-26", "eu-ai-act-art-27",
            "eu-ai-act-art-49", "eu-ai-act-art-50",
            "eu-ai-act-art-72", "eu-ai-act-art-73",
        ]),
        ("status", "future"),
        ("notes", "Digital Omnibus (Nov 2025 proposal) may delay this; plan to original date."),
    ]),
    OrderedDict([
        ("milestone", "High-risk Annex I product-embedded systems"),
        ("date", "2027-08-02"),
        ("obligations", []),  # subset of Art 6 + 8-15 for Annex I products
        ("status", "future"),
        ("notes", "Legacy GPAI deadline. Most product-embedded high-risk obligations."),
    ]),
]


# =============================================================================
# PB application
# =============================================================================

DATA["pb_application"] = OrderedDict([
    ("why_chosen", F(
        """
        EU customers in regulated sectors (legal, financial, healthcare, public sector)
        will require AI Act alignment as a procurement gate from mid-2026 onwards.
        On-prem reduces some risks but does not remove provider duties, prohibited-practice
        screening, AI literacy obligations, or transparency duties. Non-compliance penalties
        are the highest of any AI regulation globally (€35M / 7% turnover for Art 5 breaches).
        """
    )),
    ("scope_decisions", OrderedDict([
        ("on_prem", OrderedDict([
            ("coverage", "partial"),
            ("rationale", F(
                """
                Customer hardware in EU customer environments = putting into service in the EU.
                Outputs used in EU = extraterritorial reach (Art 2(1)(c)). PB role: typically
                provider of AI system. Customer role: deployer. Customer-driven Annex III use
                triggers role-flip (Art 25(1)(c)) where customer becomes provider of high-risk system.
                """
            )),
        ])),
        ("ai_factory", OrderedDict([
            ("coverage", "partial"),
            ("rationale", F(
                """
                Partner DC may or may not be in EU jurisdiction. If non-EU PB serves EU customers,
                authorised representative required for high-risk variants (Art 22). PB acts as
                provider; customer as deployer; partner DC as supplier governed contractually.
                """
            )),
        ])),
    ])),
    ("top_risks", [
        "Sales rep saying 'yes you can use it for HR ranking' triggers Art 25(1)(c) role-flip exposure for both PB and customer",
        "Skipping AI literacy programme (Art 4) — already binding since Feb 2025",
        "Failing to screen prohibited practices (Art 5) — €35M / 7% penalty tier",
        "Stripping upstream GPAI documentation when integrating third-party models (Art 53 pass-through)",
        "Telemetry/support access undermining the on-prem story without contractual scoping",
        "Treating on-prem as 'exempt' — Act applies regardless of hosting topology",
        "Missing Art 50(2) machine-readable marking for generative outputs from Aug 2026",
    ]),
])


# =============================================================================
# Open questions — EU AI Act specific + carry over AI Factory
# =============================================================================

DATA["open_questions"] = [
    OrderedDict([
        ("id", "oq-eu-customer-base"),
        ("question", "Do we have or actively pursue EU customers?"),
        ("candidate_answers", [
            "Yes — EU is a primary target market",
            "Yes — opportunistic, not primary",
            "Not currently, but possible",
            "No — SA/Africa only",
        ]),
        ("decision_owner", "PrivateBox founders + sales"),
        ("decision_status", "pending"),
        ("blocks_requirements", [
            "eu-ai-act-art-2", "eu-ai-act-art-22", "eu-ai-act-art-49",
        ]),
        ("blocks_scenarios", ["scn-eu-n"]),
        ("notes", F(
            "Determines applicability scope. Even one EU customer brings entire framework into scope. "
            "Outputs used in EU also count under Art 2(1)(c) extraterritorial reach."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-eu-ar-appointment"),
        ("question", "Will we appoint an EU Authorised Representative?"),
        ("candidate_answers", [
            "Yes — for any high-risk variant (mandatory under Art 22)",
            "Yes — for GPAI provider role (mandatory under Art 54 if triggered)",
            "Voluntary EU contact for non-high-risk customer expectation",
            "Not until needed",
        ]),
        ("decision_owner", "PrivateBox founders + legal"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["eu-ai-act-art-22", "eu-ai-act-art-54"]),
        ("blocks_scenarios", ["scn-eu-n"]),
        ("notes", F(
            "Required for non-EU providers shipping high-risk systems or GPAI models to EU. "
            "Even where not legally required, EU customers expect an EU contact."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-eu-high-risk-sku"),
        ("question", "Will we offer a high-risk-ready SKU/variant?"),
        ("candidate_answers", [
            "Yes — productise a high-risk-ready configuration with full Art 8-15 compliance",
            "Yes — bespoke, per-deal high-risk readiness",
            "No — explicitly out of scope; route customers to refusal or contractual carve-out",
            "Defer until first qualified demand",
        ]),
        ("decision_owner", "PrivateBox founders + product"),
        ("decision_status", "pending"),
        ("blocks_requirements", [
            "eu-ai-act-art-6", "eu-ai-act-art-9",
            "eu-ai-act-art-10", "eu-ai-act-art-11", "eu-ai-act-art-12",
            "eu-ai-act-art-13", "eu-ai-act-art-14", "eu-ai-act-art-15",
            "eu-ai-act-art-16", "eu-ai-act-art-17", "eu-ai-act-art-49",
        ]),
        ("blocks_scenarios", ["scn-eu-e", "scn-eu-f", "scn-eu-g"]),
        ("notes", F(
            "Determines whether Articles 8-17 + 49 are in scope as binding obligations or "
            "as aspirational scaffolding. Strong commercial decision; impacts AUP, MSA, and product roadmap."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-eu-gpai-cop-signing"),
        ("question", "Will we sign the GPAI Code of Practice if we trigger GPAI provider status?"),
        ("candidate_answers", [
            "Yes — sign at first GPAI provider trigger",
            "No — demonstrate compliance by other adequate means",
            "Decide per case based on upstream supplier signatures",
        ]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["eu-ai-act-art-53", "eu-ai-act-art-56"]),
        ("blocks_scenarios", ["scn-eu-d"]),
        ("notes", F(
            "GPAI CoP is voluntary but creates presumption of compliance. Non-signatories must "
            "demonstrate compliance 'by other adequate means' — heavier evidence burden."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-eu-fine-tune-policy"),
        ("question", "Will we ship fine-tuned models, and if so, who owns the GPAI provider duties?"),
        ("candidate_answers", [
            "We do not fine-tune; only ship third-party models unmodified",
            "We fine-tune below the one-third compute threshold (no GPAI provider role)",
            "We fine-tune above threshold and assume GPAI provider duties",
            "Customer fine-tunes, customer owns GPAI provider role for modifications",
        ]),
        ("decision_owner", "PrivateBox founders + technical lead"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["eu-ai-act-art-25", "eu-ai-act-art-53"]),
        ("blocks_scenarios", ["scn-eu-d"]),
        ("notes", F(
            "One-third compute threshold from Commission GPAI Guidelines (Jul 2025). "
            "Determines whether PB triggers GPAI provider role for modifications."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-eu-art-50-marking-tech"),
        ("question", "What technical approach for Art 50(2) machine-readable output marking?"),
        ("candidate_answers", [
            "Metadata-only (text outputs)",
            "Watermark + metadata (image/audio/video)",
            "C2PA/SynthID-style provenance preservation from upstream",
            "Wait for final Code of Practice (June 2026) and adopt then",
        ]),
        ("decision_owner", "PrivateBox technical lead"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["eu-ai-act-art-50"]),
        ("blocks_scenarios", ["scn-eu-h", "scn-eu-i"]),
        ("notes", F(
            "Art 50(2) binding from Aug 2026. Code of Practice on Marking and Labelling — "
            "first draft Dec 2025, second draft Mar 2026, final June 2026."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-eu-aup-template"),
        ("question", "What is the AUP template for EU deployments?"),
        ("candidate_answers", [
            "Single global AUP with EU-specific addendum",
            "EU-specific AUP separate from RoW",
            "Per-deal AUP",
        ]),
        ("decision_owner", "PrivateBox founders + legal"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["eu-ai-act-art-5", "eu-ai-act-art-6", "eu-ai-act-art-25"]),
        ("blocks_scenarios", ["scn-eu-e", "scn-eu-f", "scn-eu-g"]),
        ("notes", F(
            "AUP is the primary contractual mechanism for excluding Annex III use, "
            "preventing Art 25(1)(c) role-flip surprises, and screening Art 5 prohibited practices."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    # Carry-over AI Factory questions relevant to EU AI Act context
    OrderedDict([
        ("id", "oq-partner-dc-selection"),
        ("question", "Which DC partner(s) for AI Factory deployments?"),
        ("candidate_answers", ["Teraco", "Africa Data Centres", "Vantage", "EU-based partner", "TBD"]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", ["scn-eu-n"]),
        ("notes", F(
            "If AI Factory is hosted at EU-based DC partner, AR requirement may be relaxed. "
            "If non-EU partner, full Art 22 AR mandate applies for high-risk variants."
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
        ("blocks_requirements", ["eu-ai-act-art-2", "eu-ai-act-art-22"]),
        ("blocks_scenarios", ["scn-eu-n"]),
        ("notes", F(
            "EU jurisdiction simplifies Art 2 scope; non-EU triggers extraterritorial reach for EU customers/outputs."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
]


# =============================================================================
# Evidence families — from Section 9 of source research (20 artefacts)
# =============================================================================

DATA["evidence_families"] = [
    OrderedDict([
        ("id", "ai_act_scope_memo"),
        ("name", "AI Act Scope Memo"),
        ("examples", ["Per-customer EU nexus determination", "Output-used-in-EU mapping"]),
        ("why_auditor_cares", "Anchor for whether the framework applies at all."),
        ("cadence", "Per customer / annual"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "role_allocation_memo"),
        ("name", "Role Allocation Memo"),
        ("examples", ["Per-scenario role determination", "Article 25 role-flip analysis"]),
        ("why_auditor_cares", "Establishes who carries which obligations under the Act."),
        ("cadence", "Per scenario / per significant deal"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "risk_classification_register"),
        ("name", "Risk Classification Register"),
        ("examples", ["SKU-by-SKU classification", "Annex III screening per customer"]),
        ("why_auditor_cares", "Determines whether Art 8-15 obligations apply."),
        ("cadence", "Quarterly + on change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "prohibited_use_screening"),
        ("name", "Prohibited-Use Screening Checklist"),
        ("examples", ["Art 5 screening per feature", "Customer onboarding screening"]),
        ("why_auditor_cares", "Article 5 carries highest penalty tier; screening is the defence."),
        ("cadence", "Per feature release / per customer"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "ai_literacy_programme"),
        ("name", "AI Literacy Programme"),
        ("examples", ["Curriculum tiers", "Completion records", "Customer training pack"]),
        ("why_auditor_cares", "Art 4 binding since Feb 2025. Already in scope."),
        ("cadence", "Induction + annual refresh"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "model_inventory"),
        ("name", "Model Inventory (per-SKU, per-version)"),
        ("examples", ["Approved model registry", "GPAI/non-GPAI classification per model"]),
        ("why_auditor_cares", "Foundation for GPAI documentation pass-through and Art 53 compliance."),
        ("cadence", "Per release"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "intended_purpose_register"),
        ("name", "Intended Purpose Register & Instructions for Use"),
        ("examples", ["IPS per SKU", "Annex III exclusion language", "Deployer pack"]),
        ("why_auditor_cares", "Defines the scope against which Art 25 role-flip is measured."),
        ("cadence", "Per release"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "tech_doc_skeleton"),
        ("name", "Technical Documentation Skeleton (Annex IV)"),
        ("examples", ["Annex IV mapping", "Architecture docs", "Validation results"]),
        ("why_auditor_cares", "Required for high-risk; readiness baseline for non-high-risk."),
        ("cadence", "Per release"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "human_oversight_design"),
        ("name", "Human-Oversight Design Note"),
        ("examples", ["Override paths", "Escalation logic", "UI controls"]),
        ("why_auditor_cares", "Art 14 high-risk requirement; good practice for all systems."),
        ("cadence", "Per release"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "data_governance_standard"),
        ("name", "Data Governance Standard"),
        ("examples", ["Training data documentation", "Bias examination methodology", "'No training' assurance"]),
        ("why_auditor_cares", "Art 10 high-risk requirement; defensible posture for all systems."),
        ("cadence", "Per significant data change / annual"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "output_marking_spec"),
        ("name", "Output-Marking / Labelling Specification (Article 50(2))"),
        ("examples", ["Marking technical spec", "Verification path", "Export-format support"]),
        ("why_auditor_cares", "Binding from Aug 2026 for all generative AI providers."),
        ("cadence", "Per release"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "logging_traceability"),
        ("name", "Logging & Traceability Spec"),
        ("examples", ["Log schema", "Retention configuration", "Log export interface"]),
        ("why_auditor_cares", "Art 12 high-risk + Art 26(6) deployer 6-month minimum."),
        ("cadence", "Per release"),
        ("typical_owner", "PB/SH"),
    ]),
    OrderedDict([
        ("id", "pmm_plan"),
        ("name", "Post-Market Monitoring Plan"),
        ("examples", ["PMM plan template", "Telemetry feeds", "Customer feedback channels"]),
        ("why_auditor_cares", "Art 72 obligation for high-risk; good practice for all."),
        ("cadence", "Annual / on incident"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "incident_response_decision_tree"),
        ("name", "Incident Response & Serious-Incident Decision Tree"),
        ("examples", ["Severity matrix with timing buckets (2/10/15 days)", "Authority liaison list"]),
        ("why_auditor_cares", "Art 73 reporting timing rules; failure = visible non-compliance."),
        ("cadence", "Per incident / annual drill"),
        ("typical_owner", "PB/SH"),
    ]),
    OrderedDict([
        ("id", "qms_materials"),
        ("name", "Quality Management Materials"),
        ("examples", ["QMS manual", "Procedure register", "Internal audit reports"]),
        ("why_auditor_cares", "Art 17 high-risk requirement; ISO 42001 alignment."),
        ("cadence", "Annual / on change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "supplier_due_diligence"),
        ("name", "Supplier / Model-Provider Due Diligence Pack"),
        ("examples", ["Per-model supplier file", "GPAI documentation pass-through"]),
        ("why_auditor_cares", "Art 53 documentation chain; prevents inheriting upstream gaps."),
        ("cadence", "Per supplier onboarding / annual"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "change_control_records"),
        ("name", "Change-Control Records"),
        ("examples", ["Change tickets", "Release notes", "Substantial-modification analysis"]),
        ("why_auditor_cares", "Art 18 record-keeping; substantial-modification triggers re-conformity."),
        ("cadence", "Per change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "deployer_pack"),
        ("name", "Customer Deployment Guidance / Deployer Pack"),
        ("examples", ["Instructions for use", "FRIA template", "Workers' info template"]),
        ("why_auditor_cares", "Enables customer to discharge Art 26-27 deployer duties."),
        ("cadence", "Per release"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "trust_pack_language_guide"),
        ("name", "Trust-Pack Language Guide"),
        ("examples", ["Approved sales-safe wording", "Red-flag claim list"]),
        ("why_auditor_cares", "Prevents marketing overclaim that triggers regulatory exposure."),
        ("cadence", "Annual / per release"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "acceptable_use_policy"),
        ("name", "Acceptable Use Policy (AUP)"),
        ("examples", ["AUP text", "Annex III exclusions", "Art 5 prohibited-practice exclusions"]),
        ("why_auditor_cares", "Primary contractual defence against Art 25(1)(c) role-flip."),
        ("cadence", "Annual / per release"),
        ("typical_owner", "PB"),
    ]),
]


# Helper: scenario factory
def make_scenario(
    *,
    id, name, framework_specific_id, description,
    applies_to_business_models,
    pb_role, customer_role,
    risk_tier,
    triggered_requirements,
    legal_basis,
    on_prem_note=None,
    shared_responsibility=None,
    common_misclassification=None,
    sales_safe_wording=None,
    required_evidence_summary=None,
    next_step_assessment=None,
    notes=None,
):
    entry = OrderedDict([
        ("id", id),
        ("name", name),
        ("framework_specific_id", framework_specific_id),
        ("description", F(description)),
        ("applies_to_business_models", applies_to_business_models),
        ("pb_role", pb_role),
        ("customer_role", customer_role),
        ("risk_tier", risk_tier),
        ("legal_basis", F(legal_basis)),
    ])
    if on_prem_note:
        entry["on_prem_note"] = F(on_prem_note)
    if shared_responsibility:
        entry["shared_responsibility"] = F(shared_responsibility)
    if common_misclassification:
        entry["common_misclassification"] = F(common_misclassification)
    if sales_safe_wording:
        entry["sales_safe_wording"] = F(sales_safe_wording)
    if required_evidence_summary:
        entry["required_evidence_summary"] = required_evidence_summary
    if next_step_assessment:
        entry["next_step_assessment"] = F(next_step_assessment)
    if notes:
        entry["notes"] = F(notes)
    entry["triggered_requirements"] = triggered_requirements
    return entry


# Helper: article requirement factory
def make_article(
    *,
    article_num, title, requirement, pb_interpretation, owner,
    applies, applies_rationale,
    business_models=None,
    auditor_intent=None,
    objective=None,
    tier=None,
    role_applicability=None,
    triggered_by_scenarios=None,
    documented_evidence=None,
    operational_evidence=None,
    evidence=None,
    audit_methods=None,
    cadence=None,
    failure_modes=None,
    pitfall=None,
    good_vs_audit_ready=None,
    maturity_target="AR",
    remediation=None,
    external_safe_claim=None,
    scope_note=None,
    depends_on=None,
    crosswalk=None,
    source_authority="binding",
    source_refs=None,
    effective_from=None,
    effective_until=None,
    na_justification_template=None,
):
    """Build a single eu-ai-act-art-N requirement entry."""
    cid = f"eu-ai-act-art-{article_num}"
    entry = OrderedDict([
        ("id", cid),
        ("kind", "article"),
        ("native_id", f"Article {article_num}"),
        ("group", "Articles"),
        ("group_name", "EU AI Act Articles"),
        ("title", title),
    ])
    if requirement:
        entry["requirement"] = F(requirement)
    if auditor_intent:
        entry["auditor_intent"] = F(auditor_intent)
    if objective:
        entry["objective"] = F(objective)
    entry["pb_interpretation"] = F(pb_interpretation)
    entry["owner"] = owner
    entry["applies"] = applies
    entry["applies_rationale"] = F(applies_rationale)
    if na_justification_template:
        entry["na_justification_template"] = F(na_justification_template)
    if tier:
        entry["tier"] = tier
    if role_applicability:
        entry["role_applicability"] = role_applicability
    if triggered_by_scenarios:
        entry["triggered_by_scenarios"] = triggered_by_scenarios
    if documented_evidence:
        entry["documented_evidence"] = documented_evidence
    if operational_evidence:
        entry["operational_evidence"] = F(operational_evidence)
    if evidence:
        entry["evidence"] = F(evidence)
    if audit_methods:
        entry["audit_methods"] = audit_methods
    if cadence:
        entry["cadence"] = cadence
    if failure_modes:
        entry["failure_modes"] = F(failure_modes)
    if pitfall:
        entry["pitfall"] = F(pitfall)
    if good_vs_audit_ready:
        entry["good_vs_audit_ready"] = good_vs_audit_ready
    if maturity_target:
        entry["maturity_target"] = maturity_target
    if remediation:
        entry["remediation"] = F(remediation)
    if external_safe_claim:
        entry["external_safe_claim"] = F(external_safe_claim)
    if scope_note:
        entry["scope_note"] = F(scope_note)
    if depends_on:
        entry["depends_on"] = depends_on
    entry["crosswalk"] = crosswalk or []
    entry["source_authority"] = source_authority
    if source_refs:
        entry["source_refs"] = source_refs
    if effective_from:
        entry["effective_from"] = effective_from
    if effective_until:
        entry["effective_until"] = effective_until
    entry["business_models"] = business_models or ["on-prem", "ai-factory"]
    return entry


# =============================================================================
# Scenarios — populated below via append
# =============================================================================

DATA["scenarios"] = []

# =============================================================================
# Requirements — populated below via append
# =============================================================================

DATA["requirements"] = []


DATA["scenarios"].extend([
    make_scenario(
        id="scn-eu-a", framework_specific_id="Scenario A",
        name="Pure on-prem enterprise chat assistant, customer-supplied data only",
        description="""
            PrivateBox runs locally inside customer's environment. Customer's employees use it
            for general drafting, Q&A, summarisation. No third-party model invoked over the
            internet at runtime. No customer data leaves the customer environment.
        """,
        applies_to_business_models=["on-prem"],
        pb_role="provider",
        customer_role="deployer",
        risk_tier="minimal",
        legal_basis="Art 2(1)(a)–(b); Art 3(1) AI system definition; Commission Guidelines on AI System Definition (Feb 2025).",
        on_prem_note="On-prem deployment does not change 'placing on the market' / 'putting into service'. Act applies.",
        shared_responsibility="""
            PrivateBox: Art 4 literacy, Art 5 prohibited-use screening, AI system documentation,
            Art 50 transparency by design. Customer: deployer-side Art 4 literacy, lawful use,
            workplace consultation if applicable.
        """,
        common_misclassification="Believing 'on-prem means out of scope'. Wrong.",
        sales_safe_wording="""
            PrivateBox is an AI system within the meaning of Article 3(1) of the EU AI Act and
            is placed on the market in the EU when delivered to EU customers, regardless of the
            on-prem deployment topology.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-2"),
                         ("scenario_specific_note", "Putting into service in the EU.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-4"),
                         ("scenario_specific_note", "Both PB and customer have AI literacy duty.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-5"),
                         ("scenario_specific_note", "Prohibited-use screening at customer onboarding.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-50"),
                         ("scenario_specific_note", "Persistent disclosure that user is interacting with AI.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-b", framework_specific_id="Scenario B",
        name="On-prem enterprise search / RAG over customer documents",
        description="""
            Same as A but with retrieval-augmented generation over customer's own documents.
            Customer corpus stays local; no internet retrieval.
        """,
        applies_to_business_models=["on-prem"],
        pb_role="provider",
        customer_role="deployer",
        risk_tier="minimal",
        legal_basis="Art 2(1)(a)–(b); Art 3(1).",
        on_prem_note="Same as A — RAG over local corpus does not change scope or topology analysis.",
        shared_responsibility="""
            PrivateBox: same as A plus document-source citation, retrieval guardrails. Customer:
            same as A plus corpus quality (Art 16 deployer's input-data appropriateness duty
            applies if high-risk variant).
        """,
        common_misclassification="Treating RAG as 'just search' — outputs are still AI generation under Art 50(2).",
        sales_safe_wording="""
            PrivateBox supports retrieval-augmented generation over customer-supplied documents
            within the customer environment, with citations preserved at point of use.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-2"), ("scenario_specific_note", "Same as A.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-4"), ("scenario_specific_note", "Same as A.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-5"), ("scenario_specific_note", "Same as A.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-50"), ("scenario_specific_note", "Same as A; output marking applies to generated summaries.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-c", framework_specific_id="Scenario C",
        name="PrivateBox embeds a third-party GPAI model unmodified",
        description="""
            PrivateBox bundles an unmodified third-party GPAI model (e.g., Llama, Mistral) as
            the runtime LLM. Model is shipped to customer environment via the PrivateBox installer.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",
        customer_role="deployer",
        risk_tier="gpai",  # GPAI provider duties pass through; PB is downstream integrator
        legal_basis="Art 2; Art 3(63) GPAI model definition; Art 53 GPAI provider documentation; Art 25(4) supplier agreements.",
        on_prem_note="Topology irrelevant — GPAI obligations attach to model layer.",
        shared_responsibility="""
            PrivateBox: due diligence on upstream GPAI provider, preserve Annex XII downstream
            documentation, pass through to customer, do not strip provenance. Upstream GPAI provider:
            Art 53 documentation duties (their problem, not PB's). Customer: deployer duties.
        """,
        common_misclassification="Confusing GPAI **model** obligations with GPAI **system** obligations. PB ships a system; the model is upstream.",
        sales_safe_wording="""
            PrivateBox documents the third-party general-purpose AI models it integrates and
            preserves the downstream documentation those providers supply under Article 53.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-3"), ("scenario_specific_note", "Confirm model is GPAI under Art 3(63) (≥10²³ FLOP + generative).")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-53"), ("scenario_specific_note", "Pass-through duty: preserve and forward Annex XII docs.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-25"), ("scenario_specific_note", "Art 25(4) written-agreement template for upstream supplier.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-d", framework_specific_id="Scenario D",
        name="PrivateBox fine-tunes / substantially modifies a model and ships modified weights",
        description="""
            PrivateBox takes a base GPAI model, fine-tunes or substantially modifies it,
            and ships the modified model as part of the platform.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",  # PB also becomes GPAI provider in respect of modifications
        customer_role="deployer",
        risk_tier="gpai",
        legal_basis="Art 25(1)(b) substantial modification; Art 53 (own GPAI duties for modifications); Annex XI, XII; Commission GPAI Guidelines (Jul 2025) one-third compute threshold.",
        on_prem_note="Irrelevant to model-layer obligations.",
        shared_responsibility="""
            PrivateBox: documentation of fine-tune dataset, copyright policy for fine-tune data,
            training-data summary covering the fine-tune, evaluation results, intended purpose;
            decide whether to sign GPAI Code of Practice. Customer: deployer obligations.
        """,
        common_misclassification="Assuming 'we just fine-tuned' means 'we have no GPAI duties'. Threshold is one-third of compute used to train base.",
        sales_safe_wording="""
            PrivateBox-modified models are accompanied by documentation describing the modifications,
            the data used for fine-tuning, and a copyright policy applicable to those modifications.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-25"), ("scenario_specific_note", "Art 25(1)(b) substantial modification triggers GPAI provider role.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-53"), ("scenario_specific_note", "Annex XI internal docs + Annex XII downstream pack + copyright policy + training-data summary, all specific to the fine-tune.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-54"), ("scenario_specific_note", "AR required if PB is non-EU and triggers GPAI provider role.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-56"), ("scenario_specific_note", "Decide whether to sign GPAI CoP.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-e", framework_specific_id="Scenario E",
        name="Customer uses PrivateBox to build an HR screening / ranking tool",
        description="""
            Customer uses PrivateBox to ingest CVs and produce candidate rankings, sift, scoring,
            or interview questions personalised to candidates.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",  # of underlying system; customer becomes provider of high-risk system
        customer_role="provider",  # customer is now provider under Art 25(1)(c) for the high-risk redesignation
        risk_tier="high-risk",
        legal_basis="Annex III(4)(a)–(b) recruitment/selection; Art 6(2); Art 6(3) profiling carve-out unavailable; Art 25(1)(c) role-flip.",
        on_prem_note="On-prem does not lower the risk class.",
        shared_responsibility="""
            PrivateBox: clear instructions stating the system is **not intended** for high-risk
            Annex III use without further deployer assessment; technical preconditions (logging,
            oversight) for high-risk operation; pass-through GPAI documentation. Customer: full
            Article 9-15 compliance, Art 49 registration, Art 27 FRIA, Art 26(7) worker information.
        """,
        common_misclassification="Letting the customer slip into Annex III use without acknowledging it; PB pulled into Art 25(1)(c) provider status because a salesperson said 'yes you can use it for that'.",
        sales_safe_wording="""
            PrivateBox is not intended to be used as a high-risk AI system under Annex III of the
            EU AI Act, including for HR screening, ranking, or selection. Customers who choose to
            operate PrivateBox in such a use case become providers of a high-risk AI system under
            Article 25(1)(c) and must independently meet the obligations in Articles 9-15, 16, 26, 27, and 49.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-6"), ("scenario_specific_note", "Annex III(4) classification.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-25"), ("scenario_specific_note", "Art 25(1)(c) role-flip: customer becomes provider of high-risk system.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-26"), ("scenario_specific_note", "Customer-side deployer duties.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-27"), ("scenario_specific_note", "FRIA required.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-49"), ("scenario_specific_note", "Customer registers in EU database.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-f", framework_specific_id="Scenario F",
        name="Customer uses PrivateBox for credit scoring / insurance pricing decisions",
        description="""
            Customer (bank or insurer) uses PrivateBox to support creditworthiness decisions or
            pricing of life/health insurance for natural persons.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",
        customer_role="provider",  # under Art 25(1)(c)
        risk_tier="high-risk",
        legal_basis="Annex III(5)(b)/(c) creditworthiness, life/health insurance pricing; Art 25(1)(c); DORA in parallel.",
        on_prem_note="Reduces sub-processor and DORA-third-party risks but does not lower AI Act class.",
        shared_responsibility="""
            PrivateBox: instructions excluding such use without sign-off; logging hooks; deployer
            oversight tooling. Customer: full provider obligations, FRIA (financial actors listed
            in Art 27), registration.
        """,
        common_misclassification="Same as E. Customer may try to claim 'fraud detection' carve-out incorrectly — narrow.",
        sales_safe_wording="""
            PrivateBox is not intended to be used to evaluate the creditworthiness of natural persons
            or to assess risk and price life or health insurance. Customers who use PrivateBox for
            those purposes assume provider obligations for a high-risk AI system.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-6"), ("scenario_specific_note", "Annex III(5)(b)/(c).")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-25"), ("scenario_specific_note", "Role-flip same as E.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-27"), ("scenario_specific_note", "FRIA required for financial actors.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-g", framework_specific_id="Scenario G",
        name="Healthcare / medical decision support",
        description="""
            Customer (hospital, clinic, pharma) uses PrivateBox for clinical decision support,
            triage, or patient-facing chat.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",
        customer_role="deployer",  # or device manufacturer if integrated as MDR safety component
        risk_tier="high-risk",  # if MDR/IVDR safety component or Annex III(5)(d)
        legal_basis="Art 6(1) + Annex I (MDR/IVDR safety components); Annex III(5)(d) eligibility for essential public services.",
        on_prem_note="Reduces patient-data exposure. Does not by itself lower risk class.",
        shared_responsibility="""
            PrivateBox: written instructions for use, AUP excluding medical-device incorporation
            absent contractual route, logging hooks. Customer: clinical validation, MDR/IVDR
            conformity if applicable. Note Art 25(3): if customer integrates into a regulated
            medical device, the device manufacturer becomes the provider of the AI system.
        """,
        common_misclassification="Underestimating MDR/IVDR overlap. Treating 'administrative' hospital tools as not high-risk when in fact they touch eligibility decisions.",
        sales_safe_wording="""
            PrivateBox is not a medical device and is not intended to be a safety component of any
            product subject to EU medical-device legislation. Use cases requiring conformity under
            MDR/IVDR or under Annex III(5)(d) require a separate scoping discussion.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-6"), ("scenario_specific_note", "Annex I + Annex III(5)(d).")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-25"), ("scenario_specific_note", "Art 25(3) device-manufacturer-as-provider rule.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-27"), ("scenario_specific_note", "FRIA where public-sector patient services.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-h", framework_specific_id="Scenario H",
        name="Public-facing chatbot / customer-service assistant",
        description="""
            PrivateBox is exposed to end-users (customers, citizens) as a chatbot or assistant.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",
        customer_role="deployer",
        risk_tier="limited",  # Art 50 transparency-triggering, not high-risk unless Annex III also applies
        legal_basis="Art 50(1) provider duty; Art 50(2) synthetic-output marking; Art 50(4) deepfake/public-interest text (deployer side).",
        on_prem_note="Irrelevant to Art 50: duty travels with system and deployer's use, not hosting model.",
        shared_responsibility="""
            PrivateBox: in-product disclosure UI; machine-readable marking of generated outputs;
            persistent disclosure surface; technical guidance for deployer. Customer: deepfake
            labelling (Art 50(4)); ensuring users informed at first interaction (Art 50(5)).
        """,
        common_misclassification="Treating 'obvious it's AI' as universal carve-out — burden of proof is on the provider.",
        sales_safe_wording="""
            PrivateBox surfaces a clear and persistent indication that users are interacting with
            an AI system, and where it generates synthetic content, marks outputs in a machine-readable
            format. The product is designed in alignment with Article 50, applicable from 2 August 2026.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-50"), ("scenario_specific_note", "Art 50(1) provider duty + Art 50(2) marking.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-i", framework_specific_id="Scenario I",
        name="Content generation / synthetic media features",
        description="""
            PrivateBox produces drafts, summaries, images, audio, or video.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",
        customer_role="deployer",
        risk_tier="limited",
        legal_basis="Art 50(2) machine-readable marking; Art 50(4) deepfakes/public-interest text; Code of Practice on Marking and Labelling (voluntary).",
        on_prem_note="Marking duty applies regardless of hosting topology.",
        shared_responsibility="""
            PrivateBox: marking pipeline (metadata, watermark, fingerprint depending on modality);
            provenance preservation; configurable export-time options. Customer: deepfake labelling
            at publication; editorial review for public-interest text.
        """,
        common_misclassification="Stripping upstream provenance metadata. Skipping marking for 'low-risk' modalities. Misusing the assistive-editing carve-out.",
        sales_safe_wording="""
            PrivateBox marks AI-generated outputs in a machine-readable manner, in line with Article
            50(2) of the EU AI Act and the technical approach reflected in the European Commission's
            draft Code of Practice on marking and labelling of AI-generated content (currently voluntary).
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-50"), ("scenario_specific_note", "Art 50(2) provider duty for synthetic outputs.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-j", framework_specific_id="Scenario J",
        name="PrivateBox-hosted model packaging / update delivery",
        description="""
            PrivateBox ships periodic updates: model upgrades, fine-tunes, security patches,
            prompt-template changes. Updates are pushed (with customer consent) over a managed channel.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",
        customer_role="deployer",
        risk_tier="minimal",  # inherits underlying scenario's tier
        legal_basis="Art 16 provider obligations; Art 18 record-keeping; Art 20 corrective actions; Art 72 post-market monitoring.",
        on_prem_note="On-prem update channels often use signed packages and outbound-only fetch — *reduces* attack surface but creates evidence requirement: integrity, provenance, change-control traceability.",
        shared_responsibility="""
            PrivateBox: change-control pipeline, signed releases, release notes describing
            AI-functional changes, regression tests, rollback. Customer: receive, test, deploy, log.
        """,
        common_misclassification="Silent 'improvement' pushes that change behaviour without notice. Treating prompt-template changes as not material.",
        sales_safe_wording="""
            PrivateBox uses a controlled, signed update channel. Each release includes versioned
            release notes that describe AI-functional changes, supporting deployer-side change-control
            and post-market obligations under Article 72 of the AI Act where applicable.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-72"), ("scenario_specific_note", "Update channel is part of post-market monitoring.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-k", framework_specific_id="Scenario K",
        name="Remote support / temporary access by PrivateBox personnel",
        description="""
            A PrivateBox engineer remotely accesses a customer's environment to diagnose. Access
            may include logs, prompts, outputs, system parameters.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",  # also data processor under GDPR if accessing personal data
        customer_role="deployer",  # also data controller
        risk_tier="minimal",  # inherits
        legal_basis="Art 4 (literacy for support staff); Art 20 (corrective actions); Art 21 (cooperation with authorities); Art 72 (post-market monitoring); GDPR Art 28.",
        on_prem_note="Strongest selling point of on-prem is undermined if support access is broad and routine. Build narrow, audited, time-limited, customer-initiated access.",
        shared_responsibility="""
            PrivateBox: support access is opt-in, just-in-time, logged, scoped, masked-by-default for
            prompts/outputs; AI literacy training for support staff; DPA with customer. Customer:
            approves each session; reviews logs.
        """,
        common_misclassification="'Support staff are background contractors so AI literacy doesn't apply' — wrong; Art 4 covers persons dealing with operation/use on behalf. Allowing standing access.",
        sales_safe_wording="""
            Remote support access to a PrivateBox deployment is opt-in, time-bounded, customer-initiated,
            and audit-logged. PrivateBox personnel involved in supporting the system receive AI literacy
            training in line with Article 4.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-4"), ("scenario_specific_note", "Support staff in scope of literacy duty.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-72"), ("scenario_specific_note", "Support data feeds PMM; preserve evidence.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-l", framework_specific_id="Scenario L",
        name="Optional cloud telemetry / monitoring",
        description="""
            Customer enables anonymous telemetry / health monitoring that streams metadata to
            PrivateBox-hosted services.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",  # possibly controller of own telemetry
        customer_role="deployer",
        risk_tier="minimal",
        legal_basis="Art 72 post-market monitoring; Art 20 corrective-action duty (non-high-risk); GDPR.",
        on_prem_note="Default-off telemetry preserves the on-prem promise.",
        shared_responsibility="""
            PrivateBox: telemetry inventory, schema, retention, off-by-default switch.
            Customer: opt-in.
        """,
        common_misclassification="Sneaking prompt/output telemetry into 'anonymous' feed.",
        sales_safe_wording="""
            Telemetry is off by default. When enabled by the customer, telemetry is limited to
            system-health metadata; prompts and outputs are not transmitted.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-72"), ("scenario_specific_note", "Telemetry feeds PMM.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-m", framework_specific_id="Scenario M",
        name="Optional web search / external retrieval (RAG over the live web)",
        description="""
            Customer enables an optional connector that lets the assistant fetch live web content.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",
        customer_role="deployer",
        risk_tier="minimal",  # connector adds transparency/copyright considerations
        legal_basis="Art 13 transparency (high-risk); Art 50 transparency duties; Art 53(1)(c) copyright (GPAI providers, not runtime web fetch — but customers will ask).",
        on_prem_note="Web access is the **biggest single dilution** of the on-prem story. Treat as opt-in, with explicit purpose.",
        shared_responsibility="""
            PrivateBox: domain allow-list, citation surfacing, robots.txt observance, no scraping
            bypass, audit logs. Customer: opt-in, lawful use.
        """,
        common_misclassification="Treating web RAG as harmless because outputs are 'summaries'. Stripping citations.",
        sales_safe_wording="""
            Web retrieval is an opt-in, explicitly enabled connector. When enabled, retrieved content
            is cited at the point of use to preserve provenance, and access is restricted by allow-list.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-50"), ("scenario_specific_note", "Citations surface output provenance.")]),
        ],
    ),
    make_scenario(
        id="scn-eu-n", framework_specific_id="Scenario N",
        name="Cross-border support and EU market placement (PrivateBox vendor outside the EU)",
        description="""
            PrivateBox is a non-EU entity. EU customers buy and deploy. Support is delivered from
            outside the EU.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="provider",
        customer_role="deployer",
        risk_tier="minimal",  # determined per scenario
        legal_basis="Art 2(1)(a) provider placing on EU market; Art 2(1)(c) outputs used in EU; Art 22 AR for high-risk; Art 54 AR for GPAI.",
        on_prem_note="Irrelevant to extraterritoriality.",
        shared_responsibility="""
            PrivateBox: appoint AR; preserve technical documentation; cooperate with market
            surveillance authorities. Customer: deployer obligations.
        """,
        common_misclassification="Believing EU rules don't apply because PB is HQ'd elsewhere.",
        sales_safe_wording="""
            PrivateBox treats EU customer deployments as in scope of the EU AI Act regardless of
            where PrivateBox itself is established. Where a high-risk variant is delivered, PrivateBox
            appoints an authorised representative under Article 22.
        """,
        triggered_requirements=[
            OrderedDict([("requirement_id", "eu-ai-act-art-2"), ("scenario_specific_note", "Extraterritorial reach explicit.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-22"), ("scenario_specific_note", "AR mandate required if any high-risk variant.")]),
            OrderedDict([("requirement_id", "eu-ai-act-art-54"), ("scenario_specific_note", "AR for GPAI provider role if triggered.")]),
        ],
    ),
])


DATA["requirements"].extend([
    make_article(
        article_num="2", title="Scope",
        requirement="""
            The Regulation applies to providers placing AI systems on the EU market or putting them
            into service in the EU; deployers established or located in the EU; providers and deployers
            in third countries where output is used in the EU; importers, distributors, product
            manufacturers under their name; authorised representatives of non-EU providers; affected
            persons in the EU.
        """,
        pb_interpretation="""
            EU geography is not what matters; EU presence of the system, the deployer, or the output
            is what matters. Being headquartered outside the EU is not a defence. PB almost certainly
            has EU customers, EU outputs, or both. Extraterritorial reach is presumed.
        """,
        owner="PB", applies="Y",
        applies_rationale="Treats EU as in scope by default; verifies per customer.",
        documented_evidence=["Customer register with EU flag", "Scope memo", "AR mandate (where applicable)"],
        operational_evidence="EU customer list maintained current; AR mandate text reachable in EU.",
        audit_methods=["Insp", "Int"],
        cadence="Per significant product change",
        failure_modes="'We're not EU; we're not in scope.' Excluding EU output cases.",
        pitfall="Treating non-EU HQ as exempting status.",
        maturity_target="AR",
        remediation="Customer register exists, current, reviewed at every significant product change.",
        external_safe_claim="""
            PrivateBox treats EU deployments and EU-bound outputs as fully in scope of Regulation
            (EU) 2024/1689.
        """,
        triggered_by_scenarios=[f"scn-eu-{c}" for c in "abcdefghijklmn"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 2"],
    ),
    make_article(
        article_num="3", title="Definitions",
        requirement="""
            Defined terms include: AI system (Art 3(1)) — software with autonomy and adaptiveness
            producing outputs from inputs; GPAI model (Art 3(63)) — model with significant generality,
            capable of competently performing a wide range of distinct tasks (Commission threshold
            ≥10²³ FLOP plus generative output for text/image/video); provider (Art 3(3)) — places
            on market under own name; deployer (Art 3(4)) — uses on its own responsibility; intended
            purpose (Art 3(12)); substantial modification (Art 3(23)).
        """,
        pb_interpretation="""
            Almost every other duty under the Act flips on these definitions. Maintain a Definition
            Register that maps every PB SKU and every customer scenario to the relevant defined terms.
            Each model packaged classified as GPAI / not-GPAI. Each scenario tagged with intended-purpose.
            Substantial-modification policy documents what counts as 'substantial'.
        """,
        owner="PB", applies="Y",
        applies_rationale="Foundational classification work for all subsequent articles.",
        documented_evidence=["Definitions register", "Intended-purpose statements", "Substantial-modification policy"],
        operational_evidence="Register reviewed quarterly; tied to release process.",
        audit_methods=["Insp", "Int"],
        cadence="Quarterly + on release",
        pitfall="Loosely calling everything 'AI' without checking the definition; treating the GPAI threshold as a compliance threshold rather than a classification threshold.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox classifies its components as AI systems and (where applicable) general-purpose
            AI models in line with the definitions in Article 3 of Regulation (EU) 2024/1689 and the
            European Commission's guidelines on the AI system definition (February 2025) and on GPAI
            scope (July 2025).
        """,
        triggered_by_scenarios=["scn-eu-c", "scn-eu-d"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 3", "Commission AI System Definition Guidelines Feb 2025 [G]", "Commission GPAI Scope Guidelines Jul 2025 [G]"],
    ),
    make_article(
        article_num="4", title="AI Literacy",
        requirement="""
            Providers and deployers shall take measures to ensure, to their best extent, a sufficient
            level of AI literacy of their staff and other persons dealing with the operation and use
            of AI systems on their behalf, taking into account technical knowledge, experience,
            education, training, the context of use, and the persons or groups on whom the systems are used.
        """,
        pb_interpretation="""
            Already binding since 2 February 2025. People using or running AI on PB's behalf must be
            educated about it. 'On behalf' includes contractors, support staff, integration partners.
            Tier the training by role. Easy to fail because it requires PB's own programme,
            not just customer-facing materials.
        """,
        owner="PB/SH", applies="Y",
        applies_rationale="Provider duty (PB staff) AND deployer duty (customer staff). Each side owns its own.",
        role_applicability=OrderedDict([
            ("provider", "Y"), ("deployer", "Y"),
            ("provider_note", "PB's own internal literacy programme."),
            ("deployer_note", "Customer's literacy programme; PB provides supporting materials."),
        ]),
        documented_evidence=["AI literacy programme document", "Curriculum tiers", "Training material", "Completion records", "Deployer-facing training pack"],
        operational_evidence="Pick a random PB employee in scope; verify they completed the appropriate tier within 12 months.",
        audit_methods=["Insp", "Samp"],
        cadence="Induction + annual refresh",
        pitfall="Treating Art 4 as customer duty only; one-off training without refresh; ignoring contractors and support engineers.",
        maturity_target="AR",
        remediation="Curriculum integrated into onboarding; refresh tracked; deployer-facing version maintained.",
        external_safe_claim="""
            PrivateBox operates an AI literacy programme for its own personnel and provides training
            resources to customers, in line with Article 4 of the EU AI Act, applicable since
            2 February 2025.
        """,
        triggered_by_scenarios=["scn-eu-a", "scn-eu-b", "scn-eu-k"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 4", "AI Office Q&A on AI Literacy [G]", "Commission Living Repository of AI Literacy Practices [G]"],
        effective_from="2025-02-02",
    ),
    make_article(
        article_num="5", title="Prohibited AI Practices",
        requirement="""
            Article 5 prohibits, inter alia: (a) subliminal/manipulative/deceptive techniques materially
            distorting behaviour and causing significant harm; (b) exploitation of vulnerabilities;
            (c) social-scoring by public authorities; (d) predictive policing based solely on profiling;
            (e) untargeted scraping of facial images for facial-recognition databases; (f) emotion-
            recognition in workplace and education contexts (with narrow safety/medical exceptions);
            (g) biometric categorisation inferring sensitive attributes; (h) real-time remote biometric
            identification in publicly accessible spaces for law enforcement (with strict carve-outs).
        """,
        pb_interpretation="""
            Already binding since 2 February 2025. Highest penalty tier (€35M / 7%). Even an apparently
            benign assistant can be configured by a customer to support a prohibited practice (e.g.,
            emotion-recognition in workplace setting through 'sentiment analysis' of e-mails). Must be
            screened in design AND in deployer guidance.
        """,
        owner="PB/SH", applies="Y",
        applies_rationale="Provider duty (do not place such a system on market) and deployer duty (do not use).",
        role_applicability=OrderedDict([
            ("provider", "Y"), ("deployer", "Y"),
        ]),
        tier="prohibited",
        documented_evidence=["Article 5 screening checklist", "AUP", "Sales-intake form", "Design-review template", "Customer onboarding form"],
        operational_evidence="Pick a recent feature release and trace the Article 5 review. Pick a customer and check the onboarding screening.",
        audit_methods=["Insp", "Samp"],
        cadence="Per feature release / per customer",
        pitfall="Treating Art 5 as solely a 'biometrics' issue. Failing to flag features that *enable* a prohibited use even if PB doesn't itself perform it. Missing the workplace + education emotion-recognition prohibition.",
        maturity_target="AR",
        remediation="Article 5 review is a stage gate, not a checkbox.",
        external_safe_claim="""
            PrivateBox's Acceptable Use Policy and onboarding screening expressly exclude the prohibited
            AI practices defined in Article 5 of the EU AI Act, applicable since 2 February 2025.
        """,
        triggered_by_scenarios=[f"scn-eu-{c}" for c in "abcdefghijklmn"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 5", "Commission Guidelines on Prohibited AI Practices Feb 2025 [G]"],
        effective_from="2025-02-02",
    ),
    make_article(
        article_num="6", title="Classification of high-risk AI systems",
        requirement="""
            A system is high-risk if (1) it is a safety component of a product covered by Annex I
            Union harmonisation legislation that is required to undergo third-party conformity assessment;
            or (2) it falls within Annex III, unless the Article 6(3) carve-out applies (narrow procedural
            task; improves prior human activity; detects patterns/deviations not meant to replace human
            assessment; preparatory task) — and the system does not perform profiling, in which case it
            is always high-risk.
        """,
        pb_interpretation="""
            High-risk = product-safety route (Annex I) OR listed use-case (Annex III). The narrow
            Article 6(3) exit door exists, but profiling kills it. PB does not naturally land in Annex I.
            Annex III risk is driven by the customer's intended purpose, not PB's design. The role-flip
            mechanism in Article 25(1)(c) is the dominant scenario.
        """,
        owner="PB/SH", applies="C",
        applies_rationale="Conditional — high-risk classification typically attaches to customer-driven use, with role-flip consequences.",
        tier="high-risk",
        na_justification_template="N/A only where intended purpose is provably non-Annex-III and AUP enforces this contractually.",
        documented_evidence=["Intended-purpose statement", "AUP", "High-risk routing decision tree", "Classification memo per customer"],
        operational_evidence="Audit a sample of customer deployments. Are any inadvertently in Annex III categories without contractual acknowledgement?",
        audit_methods=["Insp", "Samp"],
        cadence="Per customer onboarding + annual",
        pitfall="'Article 6(3) means we're never high-risk.' Ignoring profiling. Letting customers assume Annex III use without flipping role.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox is not intended for use as a high-risk AI system under Annex III of the EU AI Act.
            Customers proposing such use will be routed through a separate contract and configuration;
            otherwise such use is contractually out of scope and subject to the role-flip rules in Art 25(1)(c).
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 6 + Annex III", "Commission Article 6 Guidelines (forthcoming) [G]"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="22", title="Authorised Representatives of Providers (high-risk)",
        requirement="""
            Non-EU providers of high-risk systems must, prior to placing on the market, appoint an
            authorised representative in the EU by written mandate. AR keeps documentation, declaration
            of conformity, conformity-assessment certificate; cooperates with authorities; can terminate
            if provider non-compliant.
        """,
        pb_interpretation="""
            Required only if/when PB provides a high-risk system from outside the EU. Note: GPAI
            providers also need an AR under Article 54.
        """,
        owner="PB", applies="C",
        applies_rationale="Triggers if (and only if) PB ships a high-risk variant from outside the EU.",
        documented_evidence=["AR mandate template", "AR contact register"],
        cadence="On high-risk-variant launch",
        audit_methods=["Insp"],
        pitfall="Forgetting the GPAI-specific AR under Art 54 if PB triggers GPAI provider status.",
        maturity_target="SA/AR",
        triggered_by_scenarios=["scn-eu-n"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 22"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="23-24", title="Importers and Distributors",
        requirement="""
            Importers verify CE marking, conformity declaration, technical documentation, AR appointment,
            instructions for use, before placing on EU market. Distributors verify CE marking and that
            provider/importer have done their job. Both must keep records and act on non-conformities.
        """,
        pb_interpretation="""
            PB can become an 'importer' if it imports an upstream third-party model packaged as a
            separate AI product. Or PB's resellers/MSPs become distributors of PB.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional on channel structure.",
        documented_evidence=["Channel map", "Reseller agreements with distributor verification clauses"],
        cadence="On channel change / annual",
        audit_methods=["Insp"],
        maturity_target="SA",
        triggered_by_scenarios=[],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 23, Art 24"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="25", title="Responsibilities along the AI value chain (role-flips)",
        requirement="""
            A distributor, importer, deployer, or other third party becomes a provider of a high-risk
            system if it (a) puts its name/trademark on it, (b) makes a substantial modification, or
            (c) modifies the intended purpose of an AI system (including a GPAI system) into a high-risk
            Annex III use. The original provider is then relieved of obligations for that new system but
            must cooperate. For Annex I safety-component cases, the product manufacturer is the provider.
            Providers and third parties must agree in writing on the information and technical access
            necessary for compliance.
        """,
        pb_interpretation="""
            Single most important article for PB's commercial posture. Whenever a customer turns PB
            into a high-risk Annex III tool, Art 25(1)(c) flips the customer to provider — but only
            IF PB has been clear in instructions/contract that its system is not for that use. If PB
            is loose, both PB and customer can wind up co-liable. One sentence from a salesperson can
            flip the analysis.
        """,
        owner="PB/SH", applies="Y",
        applies_rationale="Rule applies to PB's contractual posture even when no high-risk use is happening.",
        documented_evidence=["MSA/Order Form clause set", "AUP", "Article 25 cooperation playbook", "Supplier contract templates"],
        operational_evidence="Contract review; legal sign-off; sample customer file.",
        audit_methods=["Insp", "Samp"],
        cadence="Per contract / annual",
        pitfall="Sales saying 'yes, you can use this for HR ranking' — that single sentence can flip role allocation.",
        maturity_target="AR",
        remediation="Standard contract language; sales staff trained on Article 25.",
        external_safe_claim="""
            PrivateBox is not placed on the market as a high-risk AI system. Customers who change the
            intended purpose of the system to a high-risk use case as defined in Annex III assume the
            provider obligations under Article 25(1)(c) of the EU AI Act, and PrivateBox provides
            reasonable cooperation in line with Article 25(2).
        """,
        triggered_by_scenarios=["scn-eu-d", "scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 25"],
        effective_from="2026-08-02",
    ),
])

# Batch 2 — high-risk requirements (Arts 9–17) + deployer (26, 27) + EU database (49)
DATA["requirements"].extend([
    make_article(
        article_num="9", title="Risk Management System (high-risk)",
        requirement="""
            Establish, implement, document, and maintain a risk-management system as a continuous,
            iterative process across the lifecycle: identify and analyse known and reasonably
            foreseeable risks; estimate and evaluate risks emerging from intended use and reasonably
            foreseeable misuse; evaluate other potentially arising risks based on post-market
            monitoring data; adopt risk-management measures; eliminate/reduce risks where possible;
            give clear information to the deployer.
        """,
        pb_interpretation="""
            Required only when high-risk; strongly recommended as scaffolding regardless. LLM-based
            products face known risk classes (prompt injection, hallucination, data leakage, model
            drift) that customers will ask about. PB maintains a living risk register tied to the
            release cycle, even outside high-risk scope.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional (binding) for high-risk variants; good practice for all SKUs.",
        tier="high-risk",
        documented_evidence=["RMS document", "Risk register", "Foreseeable-misuse register", "Mitigation map", "Release-time risk-review records"],
        operational_evidence="Pick a recent release; verify risk-review record; trace one risk from identification to mitigation to deployer disclosure.",
        audit_methods=["Insp", "Samp"],
        cadence="Per release + on incident",
        pitfall="RMS that is a one-off; missing foreseeable-misuse coverage; no link to post-market monitoring.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox maintains a documented risk-management process across the AI lifecycle, covering
            identified risks, foreseeable misuse, mitigation measures, and deployer-facing residual-risk
            information, in alignment with Article 9 of the EU AI Act for any high-risk variant.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 9", "ISO/IEC 23894 [C]"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="10", title="Data and Data Governance (high-risk)",
        requirement="""
            Training, validation, and testing data sets shall be subject to data-governance and management
            practices: design choices; data-collection processes and data origin; relevant data-preparation
            (annotation, labelling, cleaning, updating, enrichment, aggregation); assumptions; assessment
            of availability, quantity, suitability; bias examination; mitigation; gap analysis. Datasets
            must be relevant, sufficiently representative, free of errors, complete, and have appropriate
            statistical properties.
        """,
        pb_interpretation="""
            Article 10 is high-risk-only on its face, but PB's posture toward fine-tuning data and customer
            RAG corpora needs to be defensible. If PB does not train on customer data, that is a powerful,
            evidenceable claim — subject to highest penalty tier (€35M / 7%) for breaches.
        """,
        owner="PB/SH", applies="C",
        applies_rationale="Conditional (binding) for high-risk; defensible posture for all SKUs.",
        tier="high-risk",
        documented_evidence=["Data governance standard", "Per-dataset data card", "Bias-evaluation reports", "'No training on customer data' technical/contractual assurance"],
        operational_evidence="Walk through dataset-card index; trace bias-examination methodology; check controls preventing customer-data leakage into training.",
        audit_methods=["Insp", "Int"],
        cadence="Per dataset release / per fine-tune",
        pitfall="Inheriting a third-party model whose training data is opaque without flagging the dependency. Vague 'no training' claims without contractual or technical anchors.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox documents the provenance, processing, and bias examination of any training or
            fine-tuning data it controls, and provides technical and contractual assurances that customer
            data is not used for model training, in alignment with Article 10 of the EU AI Act.
        """,
        triggered_by_scenarios=["scn-eu-d", "scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 10"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="11", title="Technical Documentation (high-risk)",
        requirement="""
            Technical documentation shall be drawn up before placing on the market and kept up to date;
            it shall demonstrate compliance with Articles 9-15. Annex IV specifies contents: general
            description, detailed description (development methods, design choices, system architecture,
            computational resources), description of monitoring/control/oversight, validation and testing
            procedures, risk-management documentation, list of harmonised standards/common specifications
            applied, EU declaration of conformity, post-market monitoring plan.
        """,
        pb_interpretation="""
            Required for high-risk; an Annex IV-aligned skeleton is best practice for non-high-risk too —
            speeds customer due-diligence and any future high-risk SKU.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional (binding) for high-risk; recommended for all SKUs.",
        tier="high-risk",
        documented_evidence=["Annex IV mapping", "Architecture diagrams", "Per-model documentation", "Testing/validation results", "DoC template", "PMM plan"],
        operational_evidence="Annex IV checklist walk-through with assessor; show a sample technical-documentation file.",
        audit_methods=["Insp"],
        cadence="Per release / on substantial modification",
        pitfall="'It's all in the wiki' — unstructured, inconsistent, not version-controlled.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox maintains technical documentation aligned with Annex IV of the EU AI Act for any
            high-risk variant, and an Annex-IV-aligned skeleton for the standard product to support
            customer due diligence.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 11", "Annex IV"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="12", title="Record-Keeping / Logs (high-risk)",
        requirement="""
            High-risk systems shall technically allow for the automatic recording of events ('logs') over
            their lifetime. Logging capabilities shall enable identification of situations that may result
            in the system presenting a risk or causing a substantial modification, facilitate post-market
            monitoring, and (for biometric ID) record specified parameters. Providers keep logs under their
            control. Deployers keep logs at least 6 months (Art 26(6)).
        """,
        pb_interpretation="""
            PB ships with comprehensive, configurable logging by default — even outside high-risk:
            prompt timestamps, model identifiers, response identifiers, session metadata, retrieval
            citations. On-prem means logs sit with deployer, which is privacy-positive AND satisfies
            Art 26(6) deployer duty.
        """,
        owner="PB/SH", applies="C",
        applies_rationale="Conditional (binding) for high-risk; default-on for all SKUs.",
        tier="high-risk",
        documented_evidence=["Log schema", "Default-on configuration", "Retention guidance", "Log-export interface", "Tamper-evident option"],
        operational_evidence="Inspect a deployment's log schema; verify ≥6-month retention configurable; review log-export interface.",
        audit_methods=["Insp", "Obs"],
        cadence="Per release / on schema change",
        pitfall="Logs that auto-rotate at 30 days. Log volume so high that retention becomes infeasible.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox provides default-on, structured logging with configurable retention of at least
            six months, and a documented log schema, in alignment with Articles 12 and 26(6) of the EU AI Act.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 12", "Art 19", "Art 26(6)"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="13", title="Transparency and Provision of Information to Deployers (high-risk)",
        requirement="""
            High-risk systems shall be designed and developed in such a way as to ensure their operation
            is sufficiently transparent to enable deployers to interpret the system's output and use it
            appropriately. Instructions for use must accompany the system, providing concise, complete,
            correct, clear information including: provider identity; characteristics, capabilities, and
            limitations; foreseeable misuse; technical capabilities; specifications of input data;
            performance metrics; risks; circumstances that may affect output reliability; human oversight
            measures; computational and hardware resources; expected lifetime; maintenance and care; logs.
        """,
        pb_interpretation="""
            'Instructions for use' is the central deployer-facing artifact. PB ships an Instructions
            for Use pack covering Art 13(3) topics. Even non-high-risk deployments benefit from this
            shape — it doubles as customer onboarding material.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional (binding) for high-risk; recommended structure for all SKUs.",
        tier="high-risk",
        documented_evidence=["Instructions for Use pack", "Per-model performance metrics summary", "Foreseeable-misuse list", "Human-oversight description"],
        operational_evidence="Pick a recent release; verify Instructions for Use cover all Art 13(3) topics; trace deployer-facing changes since prior release.",
        audit_methods=["Insp"],
        cadence="Per release",
        pitfall="Instructions written for compliance, not for the deployer's actual operational reality.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox ships with Instructions for Use that cover the topics required under Article 13(3)
            of the EU AI Act, and that enable deployers to interpret the system's output and use it appropriately.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g", "scn-eu-h"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 13"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="14", title="Human Oversight (high-risk)",
        requirement="""
            High-risk systems shall be designed and developed in such a way that they can be effectively
            overseen by natural persons during the period in which they are in use. Human oversight measures
            shall enable understanding of the system's capacities and limitations; awareness of automation
            bias; correct interpretation of output; ability to decide not to use the system or to override
            output; ability to intervene or interrupt operation. For remote biometric ID systems, two-person
            verification.
        """,
        pb_interpretation="""
            PB designs oversight controls (sampling, override, escalation, refusal) into the product
            regardless of risk class. For high-risk variants, these are formalised; for standard SKUs,
            they support good operational hygiene and give deployers somewhere to plug in.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional (binding) for high-risk; built-in for all SKUs.",
        tier="high-risk",
        documented_evidence=["Human-oversight design note", "Override paths documentation", "Escalation logic", "UI controls inventory"],
        operational_evidence="Walk through a deployment's oversight UI; verify override paths function; review escalation playbook.",
        audit_methods=["Insp", "Obs"],
        cadence="Per release",
        pitfall="Treating oversight as a UX afterthought rather than a core design requirement. Oversight that depends on monitoring volumes a human cannot realistically sustain.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox provides human-oversight controls — including override paths, intervention, and
            interruption — designed into the product to support Article 14 of the EU AI Act.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 14"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="15", title="Accuracy, Robustness, and Cybersecurity (high-risk)",
        requirement="""
            High-risk systems shall be designed and developed to achieve appropriate level of accuracy,
            robustness, and cybersecurity, and to perform consistently throughout their lifecycle. Accuracy
            metrics declared in Instructions for Use. Resilience to errors, faults, inconsistencies. Resilience
            against unauthorised attempts to alter use, output, or performance, exploiting system vulnerabilities
            (data poisoning, model poisoning, adversarial examples, model evasion, confidentiality attacks).
        """,
        pb_interpretation="""
            For high-risk variants, accuracy/robustness/cyber are formal commitments declared in
            Instructions for Use. For all SKUs, PB maintains evaluation harness covering hallucination,
            prompt-injection resilience, jailbreak resistance, and data-leakage probes.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional (binding) for high-risk; engineered baseline for all SKUs.",
        tier="high-risk",
        documented_evidence=["Per-model evaluation report", "Adversarial-testing record", "Cyber posture (security controls inventory crosswalked to ISO 27001)"],
        operational_evidence="Inspect evaluation harness; verify recent adversarial test results; cross-reference cyber controls to ISO 27001.",
        audit_methods=["Insp", "Int"],
        cadence="Per release / per significant model change",
        pitfall="Declaring accuracy metrics that the system does not actually meet under real deployment conditions. Confusing 'we use TLS' with cybersecurity for an AI system.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox declares accuracy and robustness metrics for any high-risk variant in its Instructions
            for Use, and maintains an adversarial-testing programme covering prompt injection, jailbreak,
            and data-leakage resistance, in alignment with Article 15 of the EU AI Act.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 15"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="16", title="Obligations of Providers of high-risk AI systems",
        requirement="""
            A high-risk provider must: ensure compliance with Articles 9-15; have a quality-management
            system (Art 17); keep documentation (Art 18); keep automatic logs (Art 19); take corrective
            actions (Art 20); cooperate with authorities (Art 21); appoint AR if non-EU (Art 22); affix
            CE marking and draw up EU declaration of conformity (Art 47, 48); register in EU database (Art 49).
        """,
        pb_interpretation="""
            Triggers only if PB knowingly provides a high-risk system. Right now: not the default product.
            But the Article 16 regime is the destination for any future PB-Annex-III SKU. Design QMS
            scaffolding now to ease the transition.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional — full applicability only on high-risk variant launch.",
        tier="high-risk",
        documented_evidence=["QMS manual", "Technical documentation file", "DoC template", "CE marking workflow", "EU database registration playbook"],
        operational_evidence="Walk an external assessor through the QMS; show sample technical documentation; show DoC template.",
        audit_methods=["Insp"],
        cadence="Annual / on high-risk variant launch",
        pitfall="Believing CE marking is always self-declared — true for Annex III by default (internal control under Annex VI), but biometrics require notified body under Annex VII.",
        maturity_target="SA/AR",
        external_safe_claim="""
            PrivateBox maintains internal documentation and quality-management practices that support
            Article 16 obligations should a high-risk variant be required for a specific deployment.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 16, 17, 18, 19, 20, 21, 22, 47, 48, 49"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="17", title="Quality Management System",
        requirement="""
            Providers of high-risk systems must operate a documented QMS covering at least: regulatory
            strategy; design and development controls; quality control; testing and validation; technical
            documentation; data governance; record-keeping; risk management; post-market monitoring;
            serious-incident reporting; communication with authorities; human resources / accountability;
            resource management.
        """,
        pb_interpretation="""
            Even non-high-risk operation benefits from a QMS that mirrors Article 17. ISO/IEC 42001 is
            strong scaffolding. PB targets ISO 42001 alignment as the QMS reference architecture, which
            gives Article 17 coverage by construction.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional (high-risk); useful management discipline regardless.",
        tier="high-risk",
        documented_evidence=["QMS manual", "Procedure register", "Internal audit reports", "Management-review minutes"],
        operational_evidence="ISO 42001 internal audit covers the Article 17 areas; management-review records exist.",
        audit_methods=["Insp", "Int"],
        cadence="Annual + on change",
        pitfall="Mistaking ISO 27001 alone for a sufficient QMS — the AI lifecycle pieces are missing.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox operates a quality-management system aligned with Article 17 of the EU AI Act and
            structured around ISO/IEC 42001 principles.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 17", "ISO/IEC 42001 [C]"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="26", title="Deployer Obligations (high-risk)",
        requirement="""
            Deployers must: (1) use the system per instructions; (2) assign human oversight to competent
            natural persons; (3) ensure relevance/appropriateness of input data they control; (4) monitor
            operation and notify provider/authorities of risks or serious incidents; (5) keep automatically
            generated logs at least 6 months; (6) inform workers' representatives and affected workers
            before workplace use; (7) public authorities register in EU database; (8) use Art 13 information
            for DPIAs; (9) inform affected natural persons subject to a high-risk AI system; (10) cooperate
            with authorities. Article 27 layers a Fundamental Rights Impact Assessment for specific deployer categories.
        """,
        pb_interpretation="""
            Customer obligation, but PB must enable it — Instructions for Use, oversight tooling, log
            retention, worker-information templates. PB ships a Deployer Pack that gives the customer
            everything they need to discharge Art 26 with documented support.
        """,
        owner="SH/CL", applies="C",
        applies_rationale="Customer is the addressee; PB enables.",
        tier="high-risk",
        role_applicability=OrderedDict([
            ("provider", "C"), ("deployer", "Y"),
            ("provider_note", "PB enables but is not the addressee."),
            ("deployer_note", "Customer is the legal addressee for high-risk variants."),
        ]),
        documented_evidence=["Instructions for use", "Deployer onboarding pack", "FRIA template", "Worker-information template", "Affected-person notification template"],
        operational_evidence="Sample customer can produce all artifacts on request; deployer pack version-controlled and updated per release.",
        audit_methods=["Insp", "Samp"],
        cadence="Per release",
        pitfall="Logs that auto-rotate at 30 days. Forgetting workers'-information duty (Art 26(7)).",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox supplies an Instructions for Use pack and configurable logging, oversight, and
            notification controls that enable deployers of high-risk variants to meet their obligations
            under Article 26 of the EU AI Act.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 13, 14, 26, 27"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="27", title="Fundamental Rights Impact Assessment (deployer)",
        requirement="""
            Before deploying certain high-risk systems, deployers that are bodies governed by public law,
            private operators providing public services, or operators of certain Annex III systems
            (incl. credit/insurance for natural persons) must perform a FRIA covering: deployer's processes,
            period and frequency of use, categories of natural persons affected, specific risks of harm,
            human oversight measures, internal governance, complaint procedures.
        """,
        pb_interpretation="""
            PB does not perform a FRIA (it is not the deployer). But PB provides a deployer-FRIA aid
            template pre-filled with PB's stated intended purpose, foreseeable risks, oversight controls,
            so customers can adapt rather than start from zero.
        """,
        owner="SH/CL", applies="C",
        applies_rationale="Customer obligation; PB supports.",
        tier="high-risk",
        role_applicability=OrderedDict([
            ("provider", "C"), ("deployer", "Y"),
            ("provider_note", "PB provides FRIA scaffolding."),
            ("deployer_note", "Customer carries out and signs FRIA."),
        ]),
        documented_evidence=["FRIA template", "Example FRIA for a fictional deployer", "PB-side risk and oversight description (input to FRIA)"],
        cadence="Per significant deployment",
        audit_methods=["Insp"],
        pitfall="Providing only a generic template that ignores the AI-specific risks customers actually face.",
        maturity_target="SA",
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 27"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="49", title="Registration in the EU database",
        requirement="""
            Providers (and certain public-authority deployers) of Annex III high-risk systems must register
            the system in the EU database before placing on the market or putting into service. Information
            per Annex VIII.
        """,
        pb_interpretation="""
            Triggers only if a high-risk variant is shipped. Database registration is a public-facing
            artifact that must be kept current — non-trivial post-launch obligation.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional on high-risk-variant launch.",
        tier="high-risk",
        documented_evidence=["EU database registration record", "Annex VIII content per registered system"],
        cadence="On registration / on substantial modification",
        audit_methods=["Insp"],
        pitfall="Registering once and not maintaining the entry as the system evolves.",
        maturity_target="SA",
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 49", "Annex VIII"],
        effective_from="2026-08-02",
    ),
])

# Batch 3 — transparency (Art 50) + GPAI (51-55) + Codes (56) + post-market (72-73)
DATA["requirements"].extend([
    make_article(
        article_num="50", title="Transparency Obligations (chat, synthetic content, deepfakes, public-interest text)",
        requirement="""
            (1) Providers must inform persons interacting with the AI system that they are interacting
            with AI, unless this is obvious or use is for permitted criminal-law purposes. (2) Providers
            of generative AI systems must mark synthetic outputs in a machine-readable format and detectable
            as artificially generated, with technical solutions effective, interoperable, robust, reliable
            as far as technically feasible — except where the system performs only assistive editing or
            does not substantially alter input. (3) Deployers of emotion-recognition or biometric-categorisation
            systems must inform exposed natural persons. (4) Deployers of deepfake-generating systems must
            disclose; deployers of AI-generated text published with the purpose of informing the public on
            matters of public interest must disclose, with editorial-review carve-out. (5) Information must
            be provided in a clear and distinguishable manner at the latest at first interaction.
        """,
        pb_interpretation="""
            Article 50 is the obligation that DOES apply broadly — including to PB's typical office
            assistant. Persistent in-product disclosure, machine-readable marking of generated content,
            and deployer guidance for deepfake and public-interest text are all PB-side workstreams.
            Binding from 2 August 2026.
        """,
        owner="PB/SH", applies="Y",
        applies_rationale="Provider duties under 50(1) and 50(2); customer-side under 50(3)/(4)/(5).",
        tier="limited",
        role_applicability=OrderedDict([
            ("provider", "Y"), ("deployer", "Y"),
            ("provider_note", "50(1) AI disclosure + 50(2) machine-readable marking are provider duties."),
            ("deployer_note", "50(3) emotion/biometric disclosure + 50(4) deepfake/public-interest text labelling are deployer duties."),
        ]),
        documented_evidence=["Article 50 design document", "UI screenshots", "Marking technical specification", "Deployer transparency manual", "Sample disclosures in supported languages"],
        operational_evidence="Live demonstration of marking and verification; UX review against accessibility standards.",
        audit_methods=["Insp", "Obs"],
        cadence="Per release",
        pitfall="Treating disclosure as a one-time pop-up. Stripping upstream provenance metadata in pipelines. Skipping marking for 'assistive' features that actually do generate substantial content. Confusing the provider duty (50(2)) with the deployer duty (50(4)).",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox surfaces a persistent indication that users are interacting with AI and marks
            generative outputs in a machine-readable format, in alignment with Article 50(1)-(2) of
            the EU AI Act, applicable from 2 August 2026, and the technical approaches reflected in
            the European Commission's voluntary draft Code of Practice on marking and labelling of
            AI-generated content.
        """,
        triggered_by_scenarios=["scn-eu-a", "scn-eu-b", "scn-eu-h", "scn-eu-i", "scn-eu-m"],
        source_authority="binding",
        source_refs=[
            "Reg 2024/1689 Art 50",
            "Code of Practice on Marking and Labelling of AI-generated Content (1st draft Dec 2025; 2nd draft Mar 2026; final June 2026) [C]",
            "Commission Article 50 Guidelines (forthcoming) [G]",
        ],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="51-52-55", title="GPAI models with systemic risk — classification, notification, additional duties",
        requirement="""
            Article 51 classifies GPAI models with 'systemic risk' (presumption when training compute
            exceeds 10²⁵ FLOP or by Commission designation under Annex XIII). Article 52: notification
            procedure; provider can rebut presumption. Article 55: GPAI-with-systemic-risk additional
            duties — model evaluations including adversarial testing, mitigation of systemic risks,
            serious-incident reporting to AI Office, cybersecurity protection.
        """,
        pb_interpretation="""
            PB extremely unlikely to train a model crossing 10²⁵ FLOP. Systemic-risk regime applies to
            frontier-lab providers. Relevant to PB only as upstream-supplier diligence — verify whether
            any GPAI model PB integrates is itself a systemic-risk model, since systemic-risk models
            carry their own transparency and reporting cascade downstream.
        """,
        owner="PB", applies="C",
        applies_rationale="PB is downstream integrator; systemic-risk obligations attach to upstream providers. Upstream-provider diligence remains.",
        tier="gpai",
        documented_evidence=["Per-model upstream supplier file flagging systemic-risk status"],
        operational_evidence="For each integrated GPAI model: capture systemic-risk flag, link to upstream provider's compliance posture.",
        audit_methods=["Insp"],
        cadence="Per integrated model",
        pitfall="Misreading the threshold as compliance-obligating rather than classification-triggering.",
        maturity_target="SA",
        external_safe_claim="""
            PrivateBox tracks whether the third-party general-purpose AI models it integrates fall under
            the systemic-risk regime in Articles 51-52 and 55 of the EU AI Act and preserves the upstream
            provider's compliance documentation accordingly.
        """,
        triggered_by_scenarios=["scn-eu-c", "scn-eu-d"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 51, 52, 55", "Annex XIII"],
        effective_from="2025-08-02",
    ),
    make_article(
        article_num="53", title="GPAI Provider Obligations — documentation, copyright, training summary",
        requirement="""
            Every GPAI provider must keep technical documentation (Annex XI), provide downstream-provider
            documentation (Annex XII), have a copyright-compliance policy under EU copyright law, and
            publish a sufficiently detailed summary of training content using the AI Office's published
            template. Free-and-open-licence models are partially exempt (only copyright + summary), unless
            they are systemic-risk.
        """,
        pb_interpretation="""
            Two sub-cases for PB: (i) downstream integrator of unmodified third-party GPAI (Scenarios A,
            B, C) — pass-through duty plus diligence on upstream provider; (ii) PB crosses the modification
            threshold (Scenario D) and becomes GPAI provider in respect of modifications — limited but real
            duties (Annex XI internal docs + Annex XII downstream pack + copyright policy + training-data
            summary, all specific to the fine-tune). Binding since 2 August 2025 for new GPAI models.
        """,
        owner="PB", applies="C",
        applies_rationale="Pass-through duty in all GPAI-touching scenarios; full GPAI-provider duty only in Scenario D.",
        tier="gpai",
        documented_evidence=[
            "Per-model upstream supplier file (Annex XII pass-through)",
            "Copyright-compliance policy",
            "Training-data summary (where PB triggers GPAI provider role)",
            "Annex XI internal documentation (where PB triggers GPAI provider role)",
        ],
        operational_evidence="Pick a model; trace the chain: upstream provider → PB pass-through → customer deployer pack.",
        audit_methods=["Insp"],
        cadence="Per integrated model + per fine-tune",
        pitfall="Confusing GPAI **model** obligations (Articles 51-55) with AI **system** obligations. Over-claiming open-source exemption (does not apply if systemic-risk).",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox documents the third-party GPAI models it integrates, preserves the downstream
            documentation those providers supply under Article 53 of the EU AI Act, and where it materially
            modifies a model, prepares its own GPAI documentation in respect of the modifications.
        """,
        triggered_by_scenarios=["scn-eu-c", "scn-eu-d"],
        source_authority="binding",
        source_refs=[
            "Reg 2024/1689 Art 53",
            "Annex XI", "Annex XII",
            "Commission GPAI Scope Guidelines Jul 2025 [G]",
            "GPAI Code of Practice Jul 2025 [C]",
        ],
        effective_from="2025-08-02",
    ),
    make_article(
        article_num="54", title="Authorised Representatives for non-EU GPAI Providers",
        requirement="""
            Non-EU GPAI providers must, prior to placing a GPAI model on the EU market, appoint an
            authorised representative in the EU by written mandate. AR keeps the technical documentation,
            cooperates with the AI Office and competent authorities, can terminate if provider non-compliant.
        """,
        pb_interpretation="""
            Triggers only if PB itself becomes a GPAI provider (Scenario D — fine-tunes above threshold)
            AND PB is non-EU. Distinct from Article 22 (which is for high-risk-system AR). Both ARs needed
            if both roles trigger.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional on Scenario D + non-EU PB establishment.",
        tier="gpai",
        documented_evidence=["GPAI AR mandate (where applicable)"],
        cadence="On Scenario D triggering",
        audit_methods=["Insp"],
        pitfall="Forgetting that high-risk AR (Art 22) and GPAI AR (Art 54) are separate; one AR may satisfy both, by design.",
        maturity_target="SA",
        triggered_by_scenarios=["scn-eu-d", "scn-eu-n"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 54"],
        effective_from="2025-08-02",
    ),
    make_article(
        article_num="56", title="Codes of Practice (legal status)",
        requirement="""
            The AI Office facilitates codes of practice. The Commission may approve a code by implementing
            act. Adherence is voluntary. Non-signatories must demonstrate compliance by other adequate means.
        """,
        pb_interpretation="""
            Codes are a route to compliance, not the compliance itself. PB can choose to align with codes
            (GPAI CoP if Scenario D triggers; Marking and Labelling CoP for Article 50(2)/(4)). Not legally
            required. Trade-off: signing creates presumption of compliance but binds PB to the code's terms;
            non-signing keeps flexibility but puts evidence burden on 'demonstrate by other means'.
        """,
        owner="PB", applies="Y",
        applies_rationale="Governance article; signing decisions are PB-strategic.",
        documented_evidence=["Code-of-Practice signature decision memo (per code)"],
        cadence="On code finalisation / annual review",
        audit_methods=["Insp"],
        maturity_target="SA",
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 56"],
    ),
    make_article(
        article_num="72", title="Post-Market Monitoring (high-risk)",
        requirement="""
            Providers of high-risk systems must operate a post-market monitoring system, with a documented
            plan, that actively and systematically collects, documents, and analyses data on system performance
            throughout its lifetime. Evidence used to update the risk-management system, the system itself,
            and to enable corrective actions.
        """,
        pb_interpretation="""
            Conditional on high-risk status. Even non-high-risk products need a de-facto incident response
            process covering AI-specific failure modes (model degradation, prompt injection, hallucinated
            outputs leading to harm, data leakage). PB designs PMM as default operational discipline.
        """,
        owner="PB", applies="C",
        applies_rationale="Binding for high-risk; recommended as default operational discipline.",
        tier="high-risk",
        documented_evidence=["PMM plan template (per Art 72(3); Commission template forthcoming under Art 96/98)", "Telemetry and customer-feedback channels feeding PMM"],
        operational_evidence="Inspect PMM plan; verify telemetry feeds reach risk register; review last-quarter PMM cycle.",
        audit_methods=["Insp", "Int"],
        cadence="Continuous + annual review",
        pitfall="Treating PMM as a 'v1.1 feature' rather than a day-1 process.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox operates a post-market monitoring process with documented telemetry and feedback
            channels feeding a living risk register, in alignment with Article 72 of the EU AI Act for
            any high-risk variant.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g", "scn-eu-j", "scn-eu-k", "scn-eu-l"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 72", "Commission PMM-plan template (forthcoming) under Art 98 [G]"],
        effective_from="2026-08-02",
    ),
    make_article(
        article_num="73", title="Serious-Incident Reporting (high-risk)",
        requirement="""
            Providers of high-risk systems must report serious incidents to market surveillance authorities
            of the Member State where the incident occurred. Timing: immediately and at most 15 days after
            the provider becomes aware of the serious incident or of the causal link; 2 days for widespread
            infringement or serious malfunction of critical infrastructure; 10 days for incidents resulting
            in death.
        """,
        pb_interpretation="""
            Conditional on high-risk status. Decision tree with the four timing buckets is a small but
            critical artifact; failure of timing is visible non-compliance. PB drills the decision tree
            annually even outside high-risk scope.
        """,
        owner="PB/SH", applies="C",
        applies_rationale="Binding for high-risk; deployer also reports under Art 26(5).",
        tier="high-risk",
        documented_evidence=["Serious-incident decision tree", "Communication templates per timing bucket", "Liaison list per Member State market surveillance authority"],
        operational_evidence="Run a tabletop exercise; verify timing decisions match the four buckets (2/10/15 days, plus 'immediately').",
        audit_methods=["Insp", "Int"],
        cadence="Per incident + annual drill",
        pitfall="Confusing the timing buckets. Treating 'serious malfunction' too narrowly.",
        maturity_target="AR",
        external_safe_claim="""
            PrivateBox maintains a serious-incident decision tree and reporting playbook aligned with the
            timing requirements of Article 73 of the EU AI Act for any high-risk variant.
        """,
        triggered_by_scenarios=["scn-eu-e", "scn-eu-f", "scn-eu-g"],
        source_authority="binding",
        source_refs=["Reg 2024/1689 Art 73"],
        effective_from="2026-08-02",
    ),
])


# =============================================================================
# Emit
# =============================================================================

if __name__ == "__main__":
    out_path = Path("/mnt/user-data/outputs/eu-ai-act.yaml")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = """# EU AI Act (Reg 2024/1689) — PrivateBox alignment record (schema v2)
# Source-of-truth file for the GRC OS. Edits go in version control.
# Regenerate via: python scripts/build_eu_ai_act.py
#
# Schema: see /docs/framework-schema-v2.md
# Phased application: Feb 2025 (Art 4, 5), Aug 2025 (GPAI), Aug 2026 (high-risk + Art 50), Aug 2027 (Annex I)
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

    from collections import Counter
    print(f"Wrote {out_path}")
    print(f"  schema_version: {DATA['schema_version']}")
    print(f"  scenarios: {len(DATA['scenarios'])}")
    print(f"  requirements: {len(DATA['requirements'])}")
    print(f"  open_questions: {len(DATA['open_questions'])}")
    print(f"  evidence_families: {len(DATA['evidence_families'])}")
    print(f"  effective_dates: {len(DATA['effective_dates'])}")

    if DATA["requirements"]:
        kinds = Counter(r["kind"] for r in DATA["requirements"])
        print(f"  by kind: {dict(kinds)}")
        tiers = Counter(r.get("tier", "—") for r in DATA["requirements"])
        print(f"  by tier: {dict(tiers)}")
