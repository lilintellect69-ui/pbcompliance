"""
Build PrivateBox's ISO/IEC 27701:2025 alignment record against schema v2.

ISO 27701:2025 is the standalone PIMS (no longer an extension of 27001).
Structure: clauses 4-10 (PIMS management system), Annex A.1 (controller controls),
Annex A.2 (processor controls), Annex A.3 (shared security controls aligned to 27002:2022).

This is the third framework in the GRC OS — first real use of:
- role_applicability axis (controller vs processor)
- companion_standards for ISO 27018:2025 (when Teraco hosting activates)

Run: python scripts/build_iso27701.py
Output: /mnt/user-data/outputs/iso-27701.yaml
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
# Top-level metadata
# =============================================================================

DATA = OrderedDict()

DATA["schema_version"] = "2.0"
DATA["id"] = "iso-27701"
DATA["version"] = "2025"
DATA["full_name"] = (
    "ISO/IEC 27701:2025 — Privacy information management — Requirements and guidance"
)
DATA["type"] = "management_system_standard"
DATA["issuer"] = "ISO/IEC"
DATA["audit_type"] = "certification"
DATA["certifiable"] = True

DATA["pb_interpretation_version"] = "1.0"
DATA["pb_interpretation_owner"] = None
DATA["pb_interpretation_last_reviewed"] = None

# Roles axis: PB is dual-role
DATA["roles"] = ["controller", "processor"]

# No tier system
DATA["tiers"] = []

# Single revision date (Edition 2 published 14 Oct 2025; transition deadline Oct 2028)
DATA["effective_dates"] = [
    OrderedDict([
        ("milestone", "ISO 27701:2025 published (Edition 2)"),
        ("date", "2025-10-14"),
        ("obligations", []),
        ("status", "in_force"),
        ("notes", "Supersedes 2019 edition (withdrawn). Transition deadline October 2028 for existing 2019 certificate holders."),
    ]),
]

# Companion standards — referenced but separately certifiable
DATA["companion_standards"] = [
    OrderedDict([
        ("id", "iso-27018"),
        ("name", "Code of practice for protection of PII in public clouds acting as PII processors"),
        ("version", "2025 (Edition 3)"),
        ("role", "Becomes directly applicable when PB activates Teraco hosting (PB acts as PII processor in cloud)."),
    ]),
    OrderedDict([
        ("id", "iso-27001"),
        ("name", "Information security management systems — Requirements"),
        ("version", "2022"),
        ("role", "Information security backbone. 27701 A.3 controls align to 27002:2022 themes; SoA can be combined."),
    ]),
    OrderedDict([
        ("id", "iso-27002"),
        ("name", "Information security controls"),
        ("version", "2022"),
        ("role", "Implementation guidance underlying 27701 A.3."),
    ]),
    OrderedDict([
        ("id", "iso-29100"),
        ("name", "Privacy framework"),
        ("version", "current"),
        ("role", "Privacy framework reference; 27701 maintains an updated mapping."),
    ]),
    OrderedDict([
        ("id", "iso-27706"),
        ("name", "Requirements for bodies providing audit and certification of privacy information management systems"),
        ("version", "2025"),
        ("role", "Certification-body scheme; shapes accredited auditor expectations. Not directly applicable to PB."),
    ]),
]


# =============================================================================
# PB application
# =============================================================================

DATA["pb_application"] = OrderedDict([
    ("why_chosen", F(
        """
        Confidential-firm customer base (legal, financial, professional services) treats privacy
        management as a procurement gate. ISO 27701:2025 is the certifiable PIMS standard against
        which enterprise privacy claims can be tested. On-prem architecture reduces several classes
        of privacy risk (cross-border transfer, multi-tenant leakage, vendor-side telemetry exposure)
        but does NOT eliminate the need for a documented PIMS — PB the company still acts as
        controller (own corporate data) and processor (customer data via support, RAG, hosting).
        """
    )),
    ("scope_decisions", OrderedDict([
        ("on_prem", OrderedDict([
            ("coverage", "full"),
            ("rationale", F(
                """
                On-prem default: customer owns the runtime environment; PB acts as controller for own
                corporate/telemetry/lead data, and as processor for customer data when optional support,
                RAG ingestion, integration help, or update delivery touches client PII. Dual-role posture
                is the design choice; contracts and controls reflect both roles.
                """
            )),
        ])),
        ("ai_factory", OrderedDict([
            ("coverage", "partial"),
            ("rationale", F(
                """
                Future Teraco-hosted single-tenant scenario activates ISO 27018:2025 obligations directly.
                PB acts as processor in full; section-72 POPIA / GDPR Chapter V transfer rules become
                live considerations. Several scope decisions pending (DC partner, jurisdiction, CMK
                support, contract template) — see open questions.
                """
            )),
        ])),
    ])),
    ("top_risks", [
        "Marketing claiming 'ISO 27701 certified' before an accredited certificate is issued",
        "Telemetry pipelines collecting customer content beyond what's contractually permitted (no-train commitment violations)",
        "Standing support access undermining the on-prem privacy promise",
        "Sub-processor register going stale as model API providers / monitoring vendors are added without notice",
        "Backup support performed without verified deletion at end of engagement",
        "Cross-border transfers to non-adequate jurisdictions without lawful basis (SCCs/POPIA s.72 evidence)",
        "Treating PB as 'always processor' or 'always controller' rather than dual-role per activity",
    ]),
])


# =============================================================================
# SoA guidance
# =============================================================================

DATA["soa_guidance"] = OrderedDict([
    ("principles", F(
        """
        SoA covers Annex A.1 (controllers, ~31 controls), A.2 (processors, ~18 controls), and A.3
        (shared security, 29 controls). When 27001:2022 is also held, A.3 SoA can be unified with the
        27001 SoA — the 27701 A.3 controls are the 27002:2022 controls re-tagged with privacy lens.
        """
    )),
    ("na_justification_rules", F(
        """
        Apart from genuinely-N/A controls (e.g., joint controllership when never applicable), default
        is to apply. PIMS principle: if PB processes PII in any capacity, most controls apply. The
        common error is to mark processor controls N/A because 'we don't store customer data on our
        infra' — wrong, because support/telemetry/update flows still process PII on customer behalf.
        """
    )),
    ("honesty_rules", F(
        """
        Where a control is partially applied (e.g., subprocessor register exists but not yet public),
        document the gap and the closing plan. Auditors prefer honest 'in progress' to claimed-but-
        unevidenced 'fully applied'.
        """
    )),
])


# =============================================================================
# Shared responsibility model
# =============================================================================

DATA["shared_responsibility_model"] = [
    OrderedDict([
        ("area", "PII inventory (ROPA)"),
        ("pb_owned", "PB ROPA covers controller-side processing (corp/telemetry/leads) and processor-side activities (support/RAG/hosting)."),
        ("cl_owned", "Customer maintains its own ROPA covering use of PB and the data it processes through PB."),
        ("shared_note", "PB provides processor-side ROPA outputs to customer for incorporation into customer's controller-side ROPA."),
    ]),
    OrderedDict([
        ("area", "Lawful basis"),
        ("pb_owned", "PB establishes lawful basis for its own controller activities."),
        ("cl_owned", "Customer establishes lawful basis for processing PII through PB."),
        ("shared_note", "DPA records PB's processor scope; customer signs off lawful basis for its own use."),
    ]),
    OrderedDict([
        ("area", "DSAR fulfilment"),
        ("pb_owned", "PB fulfils DSARs against own controller-side data. PB assists customer for DSARs against client data."),
        ("cl_owned", "Customer fulfils DSARs against its own data subjects."),
        ("shared_note", "DPA defines assist SLAs and channel."),
    ]),
    OrderedDict([
        ("area", "Privacy impact assessments"),
        ("pb_owned", "PB conducts product-level DPIA per significant feature/scenario."),
        ("cl_owned", "Customer conducts deployment-specific DPIA for its use case."),
        ("shared_note", "PB provides DPIA template + product DPIA inputs to customer."),
    ]),
    OrderedDict([
        ("area", "Sub-processor governance"),
        ("pb_owned", "PB maintains public sub-processor register; provides advance change notice."),
        ("cl_owned", "Customer reviews changes; raises objections under DPA."),
        ("shared_note", "DPA defines notice window and objection mechanism."),
    ]),
    OrderedDict([
        ("area", "Cross-border transfers"),
        ("pb_owned", "PB documents transfers it controls (telemetry destinations, sub-processor locations)."),
        ("cl_owned", "Customer documents transfers from its own use of PB."),
        ("shared_note", "Transfer register annexed to DPA where shared liability."),
    ]),
    OrderedDict([
        ("area", "Incident response"),
        ("pb_owned", "PB IR plan covers product/support incidents; notifies customer per DPA SLA."),
        ("cl_owned", "Customer IR plan covers deployment incidents; notifies PB if PB-side support involved."),
        ("shared_note", "Joint tabletop annually; notification SLA in DPA (e.g., <24h customer, <72h regulator)."),
    ]),
    OrderedDict([
        ("area", "Encryption / KMS"),
        ("pb_owned", "PB documents crypto policy and KMS architecture; supports customer-managed keys."),
        ("cl_owned", "Customer chooses key management posture (customer-managed vs provider-managed)."),
        ("shared_note", "CMK option preferred for confidential firms; documented in deployment guide."),
    ]),
    OrderedDict([
        ("area", "Logging"),
        ("pb_owned", "PB-side logs (support sessions, telemetry, product diagnostics) — minimised, redacted, time-bounded."),
        ("cl_owned", "Customer-side logs (prompts, outputs, RAG queries) — primary on-prem store."),
        ("shared_note", "Log schema documented; PII redaction by default; customer controls retention."),
    ]),
    OrderedDict([
        ("area", "Training & awareness"),
        ("pb_owned", "PB annual privacy training for all staff; specialised training for support engineers."),
        ("cl_owned", "Customer trains its own users on privacy-aware use of PB."),
        ("shared_note", "PB provides deployer-side training pack."),
    ]),
    OrderedDict([
        ("area", "Sub-processor exit / portability"),
        ("pb_owned", "PB sets retention / deletion at end of engagement."),
        ("cl_owned", "Customer instructs deletion or return of data at end of engagement."),
        ("shared_note", "DPA defines deletion-with-certificate workflow."),
    ]),
    OrderedDict([
        ("area", "Physical security"),
        ("pb_owned", "PB office security."),
        ("cl_owned", "Customer datacentre / facility security (on-prem default)."),
        ("shared_note", "When Teraco hosting active, Teraco's ISAE 3402 / PCI DSS attestations inherited; PB documents the inheritance."),
    ]),
]


# =============================================================================
# Evidence families
# =============================================================================

DATA["evidence_families"] = [
    OrderedDict([
        ("id", "pims_governance_charter"),
        ("name", "Privacy governance charter"),
        ("examples", ["Board-signed charter", "Mission and scope statement", "Resourcing commitment"]),
        ("why_auditor_cares", "Sets tone-from-the-top; required for Cl. 5.1 leadership commitment."),
        ("cadence", "Annual review"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "pims_scope_statement"),
        ("name", "PIMS scope statement"),
        ("examples", ["Sites, roles, in-scope products", "Dual-role declaration", "Teraco contingency note"]),
        ("why_auditor_cares", "Cl. 4.3 — defines what is and is not in PIMS scope."),
        ("cadence", "Annual + on change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "privacy_policy"),
        ("name", "Internal privacy policy + public privacy notice"),
        ("examples", ["Internal policy aligned to controls", "Public layered notice", "Dual-role disclosure"]),
        ("why_auditor_cares", "Cl. 5.2 + Annex A.1.10 transparency."),
        ("cadence", "Annual + on change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "privacy_risk_methodology"),
        ("name", "Privacy risk methodology + register"),
        ("examples", ["Methodology document", "Risk register with privacy lens", "Treatment plan", "SoA per Cl. 6.1.3(e)"]),
        ("why_auditor_cares", "Cl. 6.1 — explicit privacy risk methodology required in 2025."),
        ("cadence", "Quarterly review"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "ropa"),
        ("name", "Records of Processing Activities (ROPA)"),
        ("examples", ["Controller-side activities", "Processor-side activities", "Per-activity entries"]),
        ("why_auditor_cares", "Annex A.1.8 + A.2.7 — Article 30 GDPR equivalent. Audit cornerstone."),
        ("cadence", "Quarterly review"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "controller_processor_matrix"),
        ("name", "Controller/Processor scenario matrix"),
        ("examples", ["Per-activity role allocation", "Why role allocation", "Required clauses/controls per scenario"]),
        ("why_auditor_cares", "Demonstrates dual-role discipline; shows PB has thought through every processing flow."),
        ("cadence", "On change / annual"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "dpa_template"),
        ("name", "DPA template (Article 28 + POPIA s.21 + AI no-train + transfers + audit + termination)"),
        ("examples", ["Master DPA", "Per-engagement annexes", "AI-specific clauses (no-train)"]),
        ("why_auditor_cares", "Annex A.1.6 + A.2.x — processor contracts required."),
        ("cadence", "Annual + on regulatory change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "subprocessor_register"),
        ("name", "Public sub-processor register"),
        ("examples", ["Vendor name", "Purpose", "Location", "Change notice channel"]),
        ("why_auditor_cares", "Annex A.2.16 — transparency to customer and customer's data subjects."),
        ("cadence", "Live + advance change notice"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "dsar_sop"),
        ("name", "DSAR SOP (intake / identify / fulfil / log)"),
        ("examples", ["Intake form", "Identity verification", "Fulfilment workflow", "Customer-assist track"]),
        ("why_auditor_cares", "Annex A.1.11 + A.2.8 — data subject rights end-to-end."),
        ("cadence", "Annual"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "incident_response_plan"),
        ("name", "Privacy incident response plan"),
        ("examples", ["Roles + decision tree", "Customer notification SLA <24h", "Regulator SLA <72h", "Tabletop reports"]),
        ("why_auditor_cares", "Annex A.3 incident management; GDPR Art 33-34 / POPIA s.22."),
        ("cadence", "Annual tabletop"),
        ("typical_owner", "PB/SH"),
    ]),
    OrderedDict([
        ("id", "support_access_sop"),
        ("name", "Support access SOP + PAM/JIT configuration"),
        ("examples", ["Per-session approval workflow", "JIT credential issuance", "Session recording", "PAM logs"]),
        ("why_auditor_cares", "Cornerstone of vendor-side privacy posture; failure mode is standing access."),
        ("cadence", "Quarterly review"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "telemetry_minimisation_spec"),
        ("name", "Telemetry minimisation specification"),
        ("examples", ["Allow-listed fields", "Redaction rules", "Opt-out mechanism", "Off-by-default flag"]),
        ("why_auditor_cares", "Demonstrates engineered minimisation, not just policy claim."),
        ("cadence", "Annual + on schema change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "update_integrity_standard"),
        ("name", "Update integrity standard (signed packages + SBOM)"),
        ("examples", ["Signing pipeline", "SBOM publication", "Repository security"]),
        ("why_auditor_cares", "Annex A.3 supply chain; supports integrity claims for on-prem update channel."),
        ("cadence", "Per release"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "backup_decommissioning_sop"),
        ("name", "Backup & decommissioning SOP + deletion certificate template"),
        ("examples", ["Encrypted backup procedure", "Restore tests", "Decommissioning steps", "Deletion certificate"]),
        ("why_auditor_cares", "Annex A.2.10 — return/transfer/disposal at end of contract."),
        ("cadence", "Annual + on engagement end"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "data_flow_diagrams"),
        ("name", "Data flow diagrams (per deployment mode)"),
        ("examples", ["On-prem default flow", "Teraco-hosted variant", "Support flow", "Telemetry flow", "RAG flow"]),
        ("why_auditor_cares", "Visualises dual-role per activity; backbone for DPIAs."),
        ("cadence", "Annual + on change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "dpia_template_and_register"),
        ("name", "DPIA template + per-activity DPIAs"),
        ("examples", ["ICO/EDPS-aligned template", "DPIA register", "DPIA per processing activity"]),
        ("why_auditor_cares", "Annex A.1.5; required for high-risk AI processing."),
        ("cadence", "On project / on significant change"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "transfer_register"),
        ("name", "Cross-border transfer register"),
        ("examples", ["Per-transfer entries", "SCCs/IDTAs", "POPIA s.72 evidence", "Recipient list"]),
        ("why_auditor_cares", "Annex A.1.13/A.2.11; GDPR Ch. V; POPIA s.72."),
        ("cadence", "Live + per transfer"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "training_records"),
        ("name", "Privacy training records + competence matrix"),
        ("examples", ["Curricula per role", "Completion records", "Refresh tracking"]),
        ("why_auditor_cares", "Cl. 7.2/7.3 — competence and awareness."),
        ("cadence", "Annual"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "internal_audit_records"),
        ("name", "Internal audit + management review pack"),
        ("examples", ["Audit plan + findings", "Management review minutes", "CAPA log"]),
        ("why_auditor_cares", "Cl. 9.2/9.3 — required for certification."),
        ("cadence", "Annual"),
        ("typical_owner", "PB"),
    ]),
    OrderedDict([
        ("id", "trust_pack_language_guide"),
        ("name", "Trust-pack language guide"),
        ("examples", ["Approved external claims", "Red-flag list (claims NOT to make)"]),
        ("why_auditor_cares", "Prevents marketing overclaim that triggers regulator/customer pushback."),
        ("cadence", "Annual"),
        ("typical_owner", "PB"),
    ]),
]


# =============================================================================
# Open questions
# =============================================================================

DATA["open_questions"] = [
    OrderedDict([
        ("id", "oq-27701-certification-target"),
        ("question", "Pursue accredited ISO 27701:2025 certification, and on what timeline?"),
        ("candidate_answers", [
            "Yes — within 12 months (alongside or after 27001:2022 cert)",
            "Yes — within 18 months",
            "Defer until first qualified procurement demand",
            "No — operate in alignment without seeking accredited cert",
        ]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", []),
        ("notes", F(
            "Drives investment levels in evidence quality, internal audit independence, and management "
            "review formality. Without a target cert date, there's no forcing function on evidence."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-27701-dpo-appointment"),
        ("question", "Formal Privacy Lead/DPO designation — internal or outsourced?"),
        ("candidate_answers", [
            "Internal full-time DPO",
            "Internal Privacy Lead with outsourced fractional DPO",
            "Outsourced DPO (e.g., DPO-as-a-service vendor)",
            "Defer formal appointment",
        ]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["iso-27701-cl-5.3"]),
        ("blocks_scenarios", []),
        ("notes", F(
            "Required for procurement DDQs. Conflict-free reporting line to management is the discriminator."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-27701-no-train-commitment"),
        ("question", "Is the 'no customer-content training' commitment engineering-true and contractually enforceable?"),
        ("candidate_answers", [
            "Yes — engineering attestation + DPA clause + telemetry inspection on demand",
            "Partial — DPA clause yes, engineering controls in flight",
            "No — currently rely on customer trust without technical enforcement",
        ]),
        ("decision_owner", "PrivateBox technical lead + legal"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["iso-27701-a2-3"]),
        ("blocks_scenarios", []),
        ("notes", F(
            "The 'no-train' claim is the single most procurement-relevant differentiator for AI vendors. "
            "Vague claims here are a red flag in any DDQ."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-27701-cmk-support"),
        ("question", "Customer-managed key (CMK) support — default or option?"),
        ("candidate_answers", [
            "CMK default for confidential-firm tier",
            "CMK as a paid option",
            "Vendor-managed default with CMK upgrade path",
            "No CMK support yet",
        ]),
        ("decision_owner", "PrivateBox technical lead"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", []),
        ("notes", F(
            "Confidential-firm customers (legal, finance) often require CMK. Drives KMS architecture decisions "
            "and customer-facing key-management UX."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-27701-subprocessor-list"),
        ("question", "What goes on the public sub-processor register?"),
        ("candidate_answers", [
            "All upstream model API providers + monitoring + support tooling vendors",
            "Only those that touch customer PII (excluding vendor-internal tooling)",
            "Defer publication until first accredited cert",
        ]),
        ("decision_owner", "PrivateBox founders + legal"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["iso-27701-a2-16"]),
        ("blocks_scenarios", []),
        ("notes", F(
            "Public sub-processor register is procurement-table-stakes. Stale or selectively-maintained "
            "registers fail DDQ scrutiny."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-27701-teraco-activation"),
        ("question", "When does Teraco hosting activate (triggers ISO 27018:2025)?"),
        ("candidate_answers", [
            "Already active",
            "Within 6 months",
            "On first qualified customer demand",
            "Not planned",
        ]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", ["scn-27701-k"]),
        ("notes", F(
            "Teraco-hosted scenario activates 27018:2025 directly. POPIA s.72 + GDPR Ch. V transfer rules "
            "become live for non-SA customers hosted there."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    # Carry-over AI Factory open questions relevant to 27701 context
    OrderedDict([
        ("id", "oq-partner-dc-selection"),
        ("question", "Which DC partner(s) for AI Factory deployments?"),
        ("candidate_answers", ["Teraco", "Africa Data Centres", "Vantage", "EU-based partner", "TBD"]),
        ("decision_owner", "PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", ["scn-27701-k"]),
        ("notes", F(
            "DC partner selection determines which 27018:2025 controls inherit-from-partner vs require "
            "PB-side implementation."
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
        ("blocks_requirements", ["iso-27701-a1-13", "iso-27701-a2-11"]),
        ("blocks_scenarios", ["scn-27701-k"]),
        ("notes", F(
            "Jurisdiction determines applicable transfer regimes (POPIA s.72 in SA, GDPR Ch. V in EU)."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-customer-contract-template"),
        ("question", "What does the customer contract / DPA look like for AI Factory?"),
        ("candidate_answers", [
            "Adapted on-prem template with hosting addendum",
            "New SaaS-style template with 27018-aligned annex",
            "Per-deal bespoke",
        ]),
        ("decision_owner", "Legal + PrivateBox founders"),
        ("decision_status", "pending"),
        ("blocks_requirements", []),
        ("blocks_scenarios", ["scn-27701-k"]),
        ("notes", F(
            "Hosting changes the DPA shape: subprocessor flow-down, data residency commitments, audit rights."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
    OrderedDict([
        ("id", "oq-ai-factory-exit-portability"),
        ("question", "Customer exit / data portability mechanism for AI Factory hosting?"),
        ("candidate_answers", [
            "Encrypted data export + cryptographic disposal + signed certificate",
            "Migration path back to on-prem deployment",
            "Per-deal exit plan",
        ]),
        ("decision_owner", "PrivateBox technical lead"),
        ("decision_status", "pending"),
        ("blocks_requirements", ["iso-27701-a2-10"]),
        ("blocks_scenarios", ["scn-27701-k"]),
        ("notes", F(
            "Annex A.2.10 mandates return/deletion at end of contract; mechanism must be defined and verifiable."
        )),
        ("created", "2026-05-04"),
        ("resolved_value", None),
        ("resolved_at", None),
    ]),
]


# =============================================================================
# Helpers — clause / controller / processor / shared factories
# =============================================================================


def make_clause(*, native_id, group, group_name, title, requirement,
                pb_interpretation, owner, documented_evidence=None,
                operational_evidence=None, audit_methods=None, cadence=None,
                failure_modes=None, maturity_target="AR", remediation=None,
                external_safe_claim=None, scope_note=None, depends_on=None,
                business_models=None, source_refs=None, role_applicability=None):
    cid = f"iso-27701-cl-{native_id}"
    entry = OrderedDict([
        ("id", cid),
        ("kind", "clause"),
        ("native_id", native_id),
        ("group", group),
        ("group_name", group_name),
        ("title", title),
        ("requirement", F(requirement)),
        ("pb_interpretation", F(pb_interpretation)),
        ("owner", owner),
    ])
    if role_applicability:
        entry["role_applicability"] = role_applicability
    if documented_evidence:
        entry["documented_evidence"] = documented_evidence
    if operational_evidence:
        entry["operational_evidence"] = F(operational_evidence)
    if audit_methods:
        entry["audit_methods"] = audit_methods
    if cadence:
        entry["cadence"] = cadence
    if failure_modes:
        entry["failure_modes"] = F(failure_modes)
    entry["maturity_target"] = maturity_target
    if remediation:
        entry["remediation"] = F(remediation)
    if external_safe_claim:
        entry["external_safe_claim"] = F(external_safe_claim)
    if scope_note:
        entry["scope_note"] = F(scope_note)
    if depends_on:
        entry["depends_on"] = depends_on
    entry["business_models"] = business_models or ["on-prem", "ai-factory"]
    entry["crosswalk"] = []
    if source_refs:
        entry["source_refs"] = source_refs
    return entry


def make_control(*, kind, native_id, group, group_name, title, objective,
                 pb_interpretation, owner, applies, applies_rationale,
                 implementation=None, evidence=None, audit_methods=None,
                 cadence=None, depends_on=None, pitfall=None,
                 good_vs_audit_ready=None, maturity_target="AR",
                 remediation=None, external_safe_phrasing=None,
                 business_models=None, role_applicability=None,
                 legacy_ref=None, na_justification_template=None,
                 companion_refs=None, source_refs=None):
    """Generic control factory — used for control_ctrl, control_proc, control_shared.

    `kind` selects ID prefix: control_ctrl→a1, control_proc→a2, control_shared→a3.
    """
    prefix_map = {
        "control_ctrl": "a1",
        "control_proc": "a2",
        "control_shared": "a3",
    }
    prefix = prefix_map[kind]
    cid = f"iso-27701-{prefix}-{native_id}"
    entry = OrderedDict([
        ("id", cid),
        ("kind", kind),
        ("native_id", native_id),
        ("group", group),
        ("group_name", group_name),
        ("title", title),
        ("objective", F(objective)),
    ])
    if applies:
        entry["applies"] = applies
    if applies_rationale:
        entry["applies_rationale"] = F(applies_rationale)
    if na_justification_template:
        entry["na_justification_template"] = F(na_justification_template)
    entry["pb_interpretation"] = F(pb_interpretation)
    entry["owner"] = owner
    if role_applicability:
        entry["role_applicability"] = role_applicability
    if implementation:
        entry["implementation"] = F(implementation)
    if evidence:
        entry["evidence"] = F(evidence)
    if audit_methods:
        entry["audit_methods"] = audit_methods
    if cadence:
        entry["cadence"] = cadence
    if depends_on:
        entry["depends_on"] = depends_on
    if pitfall:
        entry["pitfall"] = F(pitfall)
    if good_vs_audit_ready:
        entry["good_vs_audit_ready"] = good_vs_audit_ready
    entry["maturity_target"] = maturity_target
    if remediation:
        entry["remediation"] = F(remediation)
    if external_safe_phrasing:
        entry["external_safe_phrasing"] = F(external_safe_phrasing)
    entry["business_models"] = business_models or ["on-prem", "ai-factory"]
    entry["crosswalk"] = []
    if companion_refs:
        entry["companion_refs"] = companion_refs
    if legacy_ref:
        entry["legacy_ref"] = legacy_ref  # 2019 → 2025 mapping
    if source_refs:
        entry["source_refs"] = source_refs
    return entry


# =============================================================================
# Scenarios — 11 from Table 4
# =============================================================================


def make_scenario(*, id, name, framework_specific_id, description,
                  applies_to_business_models, pb_role, customer_role,
                  triggered_requirements, why_role_allocation=None,
                  contractual_implication=None, required_clauses_or_terms=None,
                  required_operational_control=None, required_evidence=None,
                  risk_if_misclassified=None, sales_safe_explanation=None,
                  notes=None):
    entry = OrderedDict([
        ("id", id),
        ("name", name),
        ("framework_specific_id", framework_specific_id),
        ("description", F(description)),
        ("applies_to_business_models", applies_to_business_models),
        ("pb_role", pb_role),
        ("customer_role", customer_role),
    ])
    if why_role_allocation:
        entry["why_role_allocation"] = F(why_role_allocation)
    if contractual_implication:
        entry["contractual_implication"] = F(contractual_implication)
    if required_clauses_or_terms:
        entry["required_clauses_or_terms"] = F(required_clauses_or_terms)
    if required_operational_control:
        entry["required_operational_control"] = F(required_operational_control)
    if required_evidence:
        entry["required_evidence"] = required_evidence
    if risk_if_misclassified:
        entry["risk_if_misclassified"] = F(risk_if_misclassified)
    if sales_safe_explanation:
        entry["sales_safe_explanation"] = F(sales_safe_explanation)
    if notes:
        entry["notes"] = F(notes)
    entry["triggered_requirements"] = triggered_requirements
    return entry


DATA["scenarios"] = [
    make_scenario(
        id="scn-27701-a", framework_specific_id="Scenario A",
        name="Pure on-prem, no remote support — vendor never touches client data",
        description="""
            PrivateBox is deployed on customer infrastructure with no support layers active. PB
            has no role for client data; PB is only a controller for its own corporate data.
        """,
        applies_to_business_models=["on-prem"],
        pb_role="controller",  # for own corp data only
        customer_role="controller",
        why_role_allocation="Vendor never accesses customer PII when no support layers active.",
        contractual_implication="Customer-only DPA mostly N/A re client data; standard EULA + PB privacy notice for own data.",
        required_clauses_or_terms="Standard EULA + privacy notice for PB-side data only.",
        required_operational_control="None re client data.",
        risk_if_misclassified="Treating PB as 'always processor' inflates obligations and complicates contracts.",
        sales_safe_explanation="When deployed without optional support, PrivateBox does not process client data on the customer's behalf.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-cl-4.3"), ("scenario_specific_note", "Scope statement should distinguish this baseline mode.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-b", framework_specific_id="Scenario B",
        name="On-prem with vendor update delivery",
        description="""
            Update channel is vendor-driven; metadata may flow back. PB acts as processor (limited)
            for any PII in update telemetry, controller for diagnostics where it sets purposes.
        """,
        applies_to_business_models=["on-prem"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="Update channel is vendor-driven; metadata flow makes PB processor for any PII.",
        contractual_implication="DPA needed if any PII in update telemetry.",
        required_clauses_or_terms="Article 28 + signed updates + telemetry minimisation.",
        required_operational_control="Signed packages; allow-listed channels.",
        required_evidence=["Update integrity standard", "Telemetry specification"],
        risk_if_misclassified="If treated as 'no role', any PII leak becomes silent breach.",
        sales_safe_explanation="Updates are delivered via signed channels under documented terms.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a2-2"), ("scenario_specific_note", "Customer agreement covers update channel.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-3"), ("scenario_specific_note", "Update telemetry must not be repurposed for own use.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-16"), ("scenario_specific_note", "Update infra vendors registered as sub-processors.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-c", framework_specific_id="Scenario C",
        name="On-prem with telemetry",
        description="""
            Telemetry pipeline streams metadata back to PB. PB role depends on telemetry contents:
            controller for diagnostics PB defines purposes for, processor when customer content present.
        """,
        applies_to_business_models=["on-prem"],
        pb_role="processor",  # dual-role really
        customer_role="controller",
        why_role_allocation="Depends on what telemetry contains and who decides purposes.",
        contractual_implication="Dual-role DPA; opt-out mechanism.",
        required_clauses_or_terms="Define purposes; minimisation; opt-out.",
        required_operational_control="Telemetry filter; redaction.",
        required_evidence=["Telemetry minimisation specification", "Sample data"],
        risk_if_misclassified="Misclassifying as controller-only when content present is a breach exposure.",
        sales_safe_explanation="Telemetry is minimised, configurable, and governed by dual-role terms.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a1-2"), ("scenario_specific_note", "Identify and document purposes for telemetry.")]),
            OrderedDict([("requirement_id", "iso-27701-a1-3"), ("scenario_specific_note", "Lawful basis for diagnostic processing.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-2"), ("scenario_specific_note", "Customer instructions where telemetry contains customer data.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-3"), ("scenario_specific_note", "No repurposing of customer content.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-d", framework_specific_id="Scenario D",
        name="On-prem with support access",
        description="""
            PB engineer accesses customer environment to diagnose; sessions may include access to
            prompts, outputs, system parameters, customer data.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="Vendor processes customer data on instruction during support sessions.",
        contractual_implication="DPA with explicit support-access terms; per-session approval.",
        required_clauses_or_terms="Confidentiality, JIT, recording, deletion.",
        required_operational_control="Support access SOP; PAM logs; session recording.",
        required_evidence=["Support access SOP", "PAM logs", "Per-session approval records"],
        risk_if_misclassified="Standing access without DPA = unauthorised processing exposure.",
        sales_safe_explanation="Support sessions are time-boxed, recorded, and approved per request.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a2-2"), ("scenario_specific_note", "Customer instructions cover support sessions.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-6"), ("scenario_specific_note", "Confidentiality undertakings for support engineers.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-8"), ("scenario_specific_note", "DSAR-assist obligations during support.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-14"), ("scenario_specific_note", "Notify on disclosure requests.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-e", framework_specific_id="Scenario E",
        name="Managed deployment support",
        description="""
            PB performs initial deployment configuration touching customer PII (e.g., directory sync,
            initial ingestion).
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="PB performs configuration touching PII on customer instruction.",
        contractual_implication="DPA + specific deployment SOW.",
        required_clauses_or_terms="Article 28 full; deletion at end.",
        required_operational_control="Deployment SOP; deletion certificates.",
        required_evidence=["Deployment SOP", "Deletion certificates"],
        risk_if_misclassified="Treating as 'consulting' with no DPA = silent breach.",
        sales_safe_explanation="Managed deployment is performed under a processor agreement.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a2-2"), ("scenario_specific_note", "DPA covers deployment scope.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-10"), ("scenario_specific_note", "Deletion at end of deployment engagement.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-f", framework_specific_id="Scenario F",
        name="Troubleshooting sessions involving customer data",
        description="""
            Live troubleshooting sessions where PB engineer interactively processes customer PII
            (reading logs, examining outputs).
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="Direct PII processing on customer instruction during session.",
        contractual_implication="Per-session terms; data-minimisation.",
        required_clauses_or_terms="NDA; redaction; case file deletion.",
        required_operational_control="Session log; deletion record; per-session approval.",
        required_evidence=["Session logs", "Deletion records"],
        risk_if_misclassified="Logs retained beyond session purpose = retention violation.",
        sales_safe_explanation="Troubleshooting sessions follow documented privacy controls.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a2-9"), ("scenario_specific_note", "Temp files and session captures must be deleted.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-g", framework_specific_id="Scenario G",
        name="Document ingestion / RAG setup support",
        description="""
            PB structures and ingests customer documents into RAG corpus; potentially involves
            sensitive PII at scale.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="PB processes customer documents on customer instruction; setup is processor activity.",
        contractual_implication="DPA with RAG-specific data-handling annex.",
        required_clauses_or_terms="No-train clause; deletion; minimisation.",
        required_operational_control="RAG ingestion SOP; deletion runbook.",
        required_evidence=["RAG ingestion SOP", "Per-engagement deletion records"],
        risk_if_misclassified="RAG corpus retained for own model improvement = no-train violation.",
        sales_safe_explanation="RAG setup is performed under processor terms with no-train commitment.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a2-2"), ("scenario_specific_note", "Customer instructions define RAG corpus scope.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-3"), ("scenario_specific_note", "No-train commitment for RAG content.")]),
            OrderedDict([("requirement_id", "iso-27701-a1-12"), ("scenario_specific_note", "Privacy by design in RAG architecture.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-h", framework_specific_id="Scenario H",
        name="Backup support",
        description="""
            PB performs backup operations on customer's behalf; storage and handling of backup data
            falls under PB's processor scope.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="PB stores/handles backups containing customer PII.",
        contractual_implication="DPA + storage location + encryption commitments.",
        required_clauses_or_terms="Encrypted backups; tested restore.",
        required_operational_control="Backup procedure; encryption configuration.",
        required_evidence=["Backup procedure", "Restore test records"],
        risk_if_misclassified="Backups offshore without lawful basis = transfer violation.",
        sales_safe_explanation="Backup support is governed by processor terms with regional storage options.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a2-2"), ("scenario_specific_note", "DPA covers backup scope.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-10"), ("scenario_specific_note", "Backup deletion at end of contract.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-i", framework_specific_id="Scenario I",
        name="Integration / connector support",
        description="""
            PB designs and deploys integrations / connectors between PrivateBox and customer systems
            (CRM, email, file shares); connector design touches PII flow.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="PB designs PII flows on customer instruction; connector implementation is processor activity.",
        contractual_implication="DPA with connector annex.",
        required_clauses_or_terms="Per-connector PIA; minimisation.",
        required_operational_control="Connector PIA; design doc.",
        required_evidence=["Connector PIA", "Connector design doc"],
        risk_if_misclassified="Over-broad connector scope = excessive processing.",
        sales_safe_explanation="Connectors are deployed after a privacy review.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a1-12"), ("scenario_specific_note", "Privacy by design in connector architecture.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-2"), ("scenario_specific_note", "Customer instructions define connector scope.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-j", framework_specific_id="Scenario J",
        name="Hosted update repository / model package distribution",
        description="""
            PB hosts an update / model-package repository serving customer deployments; metadata
            (deployment IDs, versions, last-checked timestamps) flows to PB.
        """,
        applies_to_business_models=["on-prem", "ai-factory"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="Processor for any PII in metadata; controller for repo-side telemetry purposes PB defines.",
        contractual_implication="DPA + SCCs/IDTAs if outside region.",
        required_clauses_or_terms="Signed packages; SBOM; transfer basis.",
        required_operational_control="Repo telemetry spec; signed updates.",
        required_evidence=["Repo telemetry specification", "SBOM"],
        risk_if_misclassified="Implicit cross-border transfers without lawful basis.",
        sales_safe_explanation="Update repository operations are governed and disclosed.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a1-13"), ("scenario_specific_note", "Transfer basis for repo telemetry.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-11"), ("scenario_specific_note", "Disclose processing locations to customer.")]),
        ],
    ),
    make_scenario(
        id="scn-27701-k", framework_specific_id="Scenario K",
        name="Future Teraco-hosted single-tenant deployment",
        description="""
            PB activates Teraco hosting; customer deploys into a single-tenant ringfenced footprint
            in Teraco DC. PB acts as processor in full; ISO 27018:2025 obligations attach directly.
            POPIA s.72 + GDPR Ch. V transfer rules become live for non-SA customers.
        """,
        applies_to_business_models=["ai-factory"],
        pb_role="processor",
        customer_role="controller",
        why_role_allocation="PB operates the host (single-tenant) — full processor scope.",
        contractual_implication="Hosting DPA; SLA; section-72 evidence.",
        required_clauses_or_terms="Customer-key option; data residency in SA; audit rights.",
        required_operational_control="27018-aligned controls; Teraco compliance pack inheritance.",
        required_evidence=["Hosting DPA", "27018:2025 SoA delta", "Teraco ISAE 3402 / PCI DSS attestation copies", "Section-72 compliance memo"],
        risk_if_misclassified="Mistreating as 'still on-prem' = inheriting wrong controls.",
        sales_safe_explanation="Teraco-hosted PrivateBox operates as a processor with cloud-PII protections aligned to ISO/IEC 27018:2025.",
        notes="Activates 27018:2025 (companion standard). Cross-references oq-27701-teraco-activation.",
        triggered_requirements=[
            OrderedDict([("requirement_id", "iso-27701-a2-2"), ("scenario_specific_note", "Hosting DPA covers entire processor scope.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-10"), ("scenario_specific_note", "Exit and portability mechanism critical.")]),
            OrderedDict([("requirement_id", "iso-27701-a2-11"), ("scenario_specific_note", "POPIA s.72 + GDPR Ch. V transfer evidence.")]),
        ],
    ),
]


# =============================================================================
# Requirements — populated below via append
# =============================================================================

DATA["requirements"] = []


DATA["requirements"].extend([
    make_clause(
        native_id="4.1", group="4", group_name="Context of the organization",
        title="Understanding the organization and its context",
        requirement="""
            Determine internal and external issues including climate change, regulatory, technological
            context relevant to the PIMS.
        """,
        pb_interpretation="""
            On-prem AI for confidential firms is highly contextual. Document understanding of
            legal-firm/finance customer pressures, SA/Teraco context, AI evolution context, and
            climate change considerations.
        """,
        owner="PB",
        documented_evidence=["Context analysis document", "PESTLE/SWOT", "Regulatory horizon scan", "AI-trend register"],
        operational_evidence="Cite specific regulations and risks; review minutes referencing context; reviewed by leadership ≥1×/year.",
        audit_methods=["Insp", "Int"],
        cadence="Annual + on regulatory or product change",
        failure_modes="Generic context unrelated to AI/privacy; no climate/AI references.",
        external_safe_claim="PrivateBox maintains a documented context analysis aligned with ISO/IEC 27701:2025 Clause 4.1.",
        source_refs=["ISO/IEC 27701:2025 Cl. 4.1"],
    ),
    make_clause(
        native_id="4.2", group="4", group_name="Context of the organization",
        title="Understanding the needs and expectations of interested parties",
        requirement="""
            Identify stakeholders including PII principals; their needs/expectations; legal and
            contractual obligations.
        """,
        pb_interpretation="""
            Customer firms (controllers); regulators (ICO, IR-SA, EDPB); data subjects (employees of
            client firms); partners; certifiers. Customer is itself an interested party as both
            controller and operator of the host environment.
        """,
        owner="PB",
        documented_evidence=["Stakeholder register", "Customer expectation log", "Regulator monitoring log"],
        operational_evidence="Register lists named parties and obligations; cross-checked with sales contract obligations.",
        audit_methods=["Insp", "Int"],
        cadence="On contract / regulatory change",
        failure_modes="Lists only commercial customers; missing data subjects/regulators.",
        external_safe_claim="PrivateBox maintains a documented interested-parties register including data subjects and regulators.",
        source_refs=["ISO/IEC 27701:2025 Cl. 4.2"],
    ),
    make_clause(
        native_id="4.3", group="4", group_name="Context of the organization",
        title="Determining the scope of the PIMS",
        requirement="""
            Determine PIMS boundaries considering 4.1, 4.2, and processing of PII.
        """,
        pb_interpretation="""
            Critical scope decisions: include product engineering, support operations, update infrastructure,
            telemetry pipelines, optional Teraco footprint. Exclude internal-HR-only systems if not
            relevant. Scope statement modelled on Slack/Salesforce/Orbita exemplars; explicit dual-role
            (controller AND processor) declaration.
        """,
        owner="PB",
        documented_evidence=["PIMS scope statement", "SoA reference"],
        operational_evidence="Scope walkthrough with auditor; stable, justified, role-aware.",
        audit_methods=["Insp"],
        cadence="Annual + on change",
        failure_modes="Scope too narrow (excludes support); too broad (includes everything but resourced for nothing).",
        external_safe_claim="Our PIMS covers PrivateBox product, support operations, update delivery and (when active) Teraco-hosted deployments.",
        source_refs=["ISO/IEC 27701:2025 Cl. 4.3"],
    ),
    make_clause(
        native_id="4.4", group="4", group_name="Context of the organization",
        title="Privacy information management system",
        requirement="""
            Establish, implement, maintain, and continually improve the PIMS in accordance with the
            requirements of this document.
        """,
        pb_interpretation="""
            Foundational: PIMS framework integrating ISMS (where 27001 held), AIMS (where 42001 in scope).
            Not a paper-only management system.
        """,
        owner="PB",
        documented_evidence=["Top-level PIMS manual / framework document"],
        operational_evidence="Internal audit verifies integration, not bolt-on.",
        audit_methods=["Insp", "Int"],
        cadence="Annual",
        failure_modes="Paper-only PIMS not integrated with operational reality.",
        external_safe_claim="PrivateBox operates a documented Privacy Information Management System.",
        source_refs=["ISO/IEC 27701:2025 Cl. 4.4"],
    ),
    make_clause(
        native_id="5.1", group="5", group_name="Leadership",
        title="Leadership and commitment",
        requirement="""
            Top management to demonstrate commitment, integrate PIMS into business processes, allocate
            resources.
        """,
        pb_interpretation="""
            New 2025 emphasis: privacy is no longer subordinate to security. Leadership must approve
            on-prem privacy posture and shared-responsibility model.
        """,
        owner="PB",
        documented_evidence=["Privacy charter", "Management endorsement", "Resource commitment", "Board minutes"],
        operational_evidence="Walkthrough with CEO/CTO; visible board engagement on privacy.",
        audit_methods=["Insp", "Int"],
        cadence="Annual",
        failure_modes="Privacy delegated to IT only; leadership disengaged.",
        external_safe_claim="Top management has formally established and resourced a PIMS.",
        source_refs=["ISO/IEC 27701:2025 Cl. 5.1"],
    ),
    make_clause(
        native_id="5.2", group="5", group_name="Leadership",
        title="Privacy policy",
        requirement="""
            Establish a privacy policy with objectives, commitment to legal requirements, and continual
            improvement.
        """,
        pb_interpretation="""
            Internal privacy policy + public privacy notice. Procurement reviewers ask for this first.
            Should explicitly describe on-prem-by-default and shared-responsibility.
        """,
        owner="PB",
        documented_evidence=["Internal privacy policy", "Public privacy notice"],
        operational_evidence="Compare published vs internal version; versioned, reviewed annually, signed by management.",
        audit_methods=["Insp"],
        cadence="Annual",
        failure_modes="Generic privacy policy lifted from a template.",
        external_safe_claim="PrivateBox maintains a documented privacy policy reviewed at least annually.",
        source_refs=["ISO/IEC 27701:2025 Cl. 5.2"],
    ),
    make_clause(
        native_id="5.3", group="5", group_name="Leadership",
        title="Roles, responsibilities and authorities",
        requirement="""
            Assign PIMS roles, including privacy lead/DPO equivalent.
        """,
        pb_interpretation="""
            Required for procurement DDQs. DPO not legally mandatory in all cases but practically
            essential for AI/PII vendor. Independent privacy lead with reporting line to management.
        """,
        owner="PB",
        documented_evidence=["Org chart", "RACI matrix", "DPO appointment letter / role description"],
        operational_evidence="Interview the role-holder; verify reporting line independence.",
        audit_methods=["Insp", "Int"],
        cadence="Annual + on appointment change",
        failure_modes="Privacy 'owned' by CTO with no separation.",
        external_safe_claim="PrivateBox has appointed a privacy lead with documented authority.",
        source_refs=["ISO/IEC 27701:2025 Cl. 5.3"],
    ),
    make_clause(
        native_id="6.1", group="6", group_name="Planning",
        title="Actions to address risks and opportunities (incl. privacy risk)",
        requirement="""
            Privacy risk assessment and treatment, integrated with information security risk. New 2025
            requirement: privacy risk now explicit, with a separate methodology where appropriate.
        """,
        pb_interpretation="""
            Risk register reflects on-prem-specific risks (support access, update channel, RAG ingestion,
            telemetry). Tied to Annex A controls. Updated quarterly.
        """,
        owner="PB",
        documented_evidence=["Privacy risk methodology", "Privacy risk register", "Risk treatment plan", "SoA per Cl. 6.1.3(e)"],
        operational_evidence="Sample risks → traced to controls; treatments evidenced.",
        audit_methods=["Insp", "Samp"],
        cadence="Quarterly review",
        failure_modes="Generic infosec risks rebadged as privacy risks.",
        external_safe_claim="PrivateBox operates a documented privacy risk methodology with a maintained register.",
        source_refs=["ISO/IEC 27701:2025 Cl. 6.1"],
    ),
    make_clause(
        native_id="6.2", group="6", group_name="Planning",
        title="Privacy objectives and planning to achieve them",
        requirement="""
            Establish measurable privacy objectives at relevant functions and levels.
        """,
        pb_interpretation="""
            KPIs include: zero unsanctioned cross-border transfers; DSAR support SLA; support-access
            auditability rate.
        """,
        owner="PB",
        documented_evidence=["Privacy objectives document with KPIs and targets"],
        operational_evidence="Quarterly review report; track objective vs actual; trends improve.",
        audit_methods=["Insp"],
        cadence="Quarterly review",
        failure_modes="Aspirational objectives with no measurement.",
        external_safe_claim="PrivateBox tracks measurable privacy objectives at least quarterly.",
        source_refs=["ISO/IEC 27701:2025 Cl. 6.2"],
    ),
    make_clause(
        native_id="6.3", group="6", group_name="Planning",
        title="Planning of changes",
        requirement="""
            Plan PIMS changes in a controlled way.
        """,
        pb_interpretation="""
            New 2025 explicit clause. Especially relevant for adding Teraco hosting, new connectors,
            new model versions.
        """,
        owner="PB",
        documented_evidence=["Change management procedure including PIMS impact"],
        operational_evidence="Sample changes with PIMS-impact assessment recorded.",
        audit_methods=["Insp", "Samp"],
        cadence="Per change",
        failure_modes="New connector or hosting mode launched with no privacy impact assessment.",
        external_safe_claim="Privacy implications are assessed for material PIMS changes.",
        source_refs=["ISO/IEC 27701:2025 Cl. 6.3"],
    ),
    make_clause(
        native_id="7.1", group="7", group_name="Support",
        title="Resources",
        requirement="""
            Provide resources for the establishment, implementation, maintenance and continual
            improvement of the PIMS.
        """,
        pb_interpretation="Stable funding; budget line for privacy programme distinct from security.",
        owner="PB",
        documented_evidence=["Budget allocation", "GRC tooling licenses"],
        operational_evidence="Compare budget to plan; stable funding visible.",
        audit_methods=["Insp"],
        cadence="Annual",
        failure_modes="Volunteer/best-effort privacy work.",
        external_safe_claim="Privacy programme is resourced as part of operating plan.",
        source_refs=["ISO/IEC 27701:2025 Cl. 7.1"],
    ),
    make_clause(
        native_id="7.2", group="7", group_name="Support",
        title="Competence",
        requirement="""
            Privacy-relevant roles competent on the basis of education, training or experience.
        """,
        pb_interpretation="""
            Critical for support staff and engineering. Support engineers need privacy-aware training
            for customer-data exposure scenarios.
        """,
        owner="PB",
        documented_evidence=["Competence matrix", "Training records"],
        operational_evidence="Sampled training certificates; refresher every 12 months.",
        audit_methods=["Insp", "Samp"],
        cadence="Annual",
        failure_modes="One-off generic training.",
        external_safe_claim="Personnel with privacy responsibilities are demonstrably competent.",
        source_refs=["ISO/IEC 27701:2025 Cl. 7.2"],
    ),
    make_clause(
        native_id="7.3", group="7", group_name="Support",
        title="Awareness",
        requirement="All relevant personnel aware of the privacy policy, their contribution, and consequences.",
        pb_interpretation="Annual awareness program; ≥95% completion target.",
        owner="PB",
        documented_evidence=["Attendance records", "Awareness curriculum"],
        operational_evidence="Random sampling; <80% completion = failure mode.",
        audit_methods=["Insp", "Samp"],
        cadence="Annual",
        failure_modes="<80% completion.",
        external_safe_claim="PrivateBox maintains an annual privacy awareness program.",
        source_refs=["ISO/IEC 27701:2025 Cl. 7.3"],
    ),
    make_clause(
        native_id="7.4", group="7", group_name="Support",
        title="Communication",
        requirement="Determine internal and external communications relevant to the PIMS.",
        pb_interpretation="""
            Should cover support-window incident comms to customers; templates tested in tabletop
            exercises.
        """,
        owner="PB",
        documented_evidence=["Communication plan", "Templates"],
        operational_evidence="Drill exercise; templates tested.",
        audit_methods=["Insp"],
        cadence="Annual + on incident",
        failure_modes="No defined channel for breach communications.",
        external_safe_claim="PrivateBox maintains documented privacy communication procedures.",
        source_refs=["ISO/IEC 27701:2025 Cl. 7.4"],
    ),
    make_clause(
        native_id="7.5", group="7", group_name="Support",
        title="Documented information",
        requirement="Maintain control over policies/procedures (creation, update, retention, distribution).",
        pb_interpretation="Audit-ready always. Document register with version control and retention rules.",
        owner="PB",
        documented_evidence=["Document register", "Document control system"],
        operational_evidence="Sample document with version history; old versions retrievable.",
        audit_methods=["Insp", "Samp"],
        cadence="Continuous",
        failure_modes="Sprawl in shared drives; uncontrolled documents.",
        external_safe_claim="PrivateBox operates documented information control aligned with the PIMS.",
        source_refs=["ISO/IEC 27701:2025 Cl. 7.5"],
    ),
    make_clause(
        native_id="8.1", group="8", group_name="Operation",
        title="Operational planning and control",
        requirement="""
            Plan, implement, and control processes to meet PIMS requirements including privacy risk
            treatment.
        """,
        pb_interpretation="""
            Where most failures occur. Includes support-access, update-delivery, telemetry pipelines,
            RAG ingestion procedures.
        """,
        owner="PB",
        documented_evidence=["SOPs for each operational privacy process", "Runbooks"],
        operational_evidence="Sample SOP; ticket sample; walkthrough.",
        audit_methods=["Insp", "Samp", "Obs"],
        cadence="Per process / annual",
        failure_modes="SOP exists but unused.",
        external_safe_claim="Privacy controls are embedded in operational procedures.",
        source_refs=["ISO/IEC 27701:2025 Cl. 8.1"],
    ),
    make_clause(
        native_id="8.2", group="8", group_name="Operation",
        title="Privacy risk assessment (operational)",
        requirement="Privacy risk assessments for processing activities.",
        pb_interpretation="Operational PIA per processing activity (RAG ingestion, support, telemetry).",
        owner="PB",
        documented_evidence=["PIA register", "Per-activity PIAs"],
        operational_evidence="Sample PIA; each activity has a PIA.",
        audit_methods=["Insp", "Samp"],
        cadence="Per activity / on change",
        failure_modes="Single org-wide PIA only.",
        external_safe_claim="PrivateBox conducts privacy impact assessments for each processing activity.",
        source_refs=["ISO/IEC 27701:2025 Cl. 8.2"],
    ),
    make_clause(
        native_id="8.3", group="8", group_name="Operation",
        title="Privacy risk treatment",
        requirement="Treat privacy risks per the treatment plan.",
        pb_interpretation="Treatments tied to SoA; tracked through to closure.",
        owner="PB",
        documented_evidence=["Treatment plan", "Status tracking"],
        operational_evidence="Sample treatments; treatments completed on schedule.",
        audit_methods=["Insp", "Samp"],
        cadence="Continuous",
        failure_modes="Open treatments unaddressed for long periods.",
        external_safe_claim="Privacy risks are tracked through to treatment.",
        source_refs=["ISO/IEC 27701:2025 Cl. 8.3"],
    ),
    make_clause(
        native_id="9.1", group="9", group_name="Performance evaluation",
        title="Monitoring, measurement, analysis and evaluation",
        requirement="Measure PIMS effectiveness including privacy KPIs.",
        pb_interpretation="""
            KPIs: DSAR turnaround; support-access tickets without consent; telemetry minimisation rate.
            Trends visible and improving.
        """,
        owner="PB",
        documented_evidence=["Metrics catalog", "Dashboard"],
        operational_evidence="Compare metrics over time; trends improve.",
        audit_methods=["Insp"],
        cadence="Quarterly",
        failure_modes="KPIs not collected or not reviewed.",
        external_safe_claim="PrivateBox maintains privacy KPIs and reviews trends.",
        source_refs=["ISO/IEC 27701:2025 Cl. 9.1"],
    ),
    make_clause(
        native_id="9.2", group="9", group_name="Performance evaluation",
        title="Internal audit",
        requirement="Audit PIMS at planned intervals to determine PIMS conformity.",
        pb_interpretation="Required for certification. Independence between auditor and control owner essential.",
        owner="PB",
        documented_evidence=["Annual internal audit plan", "Audit reports"],
        operational_evidence="Independence check; findings closed.",
        audit_methods=["Insp"],
        cadence="Annual",
        failure_modes="Self-audit by control owner.",
        external_safe_claim="PrivateBox conducts annual internal audits of the PIMS.",
        source_refs=["ISO/IEC 27701:2025 Cl. 9.2"],
    ),
    make_clause(
        native_id="9.3", group="9", group_name="Performance evaluation",
        title="Management review",
        requirement="Top management review the PIMS at planned intervals.",
        pb_interpretation="Required for certification. Decisions documented in minutes.",
        owner="PB",
        documented_evidence=["Annual management review meeting", "Minutes (inputs/outputs)"],
        operational_evidence="Walk inputs/outputs; decisions documented.",
        audit_methods=["Insp"],
        cadence="Annual",
        failure_modes="Skipped or rubber-stamped review.",
        external_safe_claim="Top management reviews the PIMS at least annually.",
        source_refs=["ISO/IEC 27701:2025 Cl. 9.3"],
    ),
    make_clause(
        native_id="10.1", group="10", group_name="Improvement",
        title="Continual improvement",
        requirement="Continually improve the suitability, adequacy and effectiveness of the PIMS.",
        pb_interpretation="Improvement log tracks closed items; not stagnant CAPA.",
        owner="PB",
        documented_evidence=["Improvement log"],
        operational_evidence="Sample items traced from finding to fix.",
        audit_methods=["Insp", "Samp"],
        cadence="Continuous",
        failure_modes="Stagnant CAPA list.",
        external_safe_claim="PrivateBox operates a continual improvement process for the PIMS.",
        source_refs=["ISO/IEC 27701:2025 Cl. 10.1"],
    ),
    make_clause(
        native_id="10.2", group="10", group_name="Improvement",
        title="Nonconformity and corrective action",
        requirement="Nonconformities identified, treated, root-cause analysed.",
        pb_interpretation="CAPA procedure with documented root-cause analysis.",
        owner="PB",
        documented_evidence=["NC/CAPA procedure", "NC log"],
        operational_evidence="Sample NCs; closure timing; RCA visible.",
        audit_methods=["Insp", "Samp"],
        cadence="Continuous",
        failure_modes="NCs closed without RCA.",
        external_safe_claim="PrivateBox operates a documented nonconformity and corrective-action process.",
        source_refs=["ISO/IEC 27701:2025 Cl. 10.2"],
    ),
])


DATA["requirements"].extend([
    make_control(
        kind="control_ctrl", native_id="2", group="A.1", group_name="Controller controls",
        title="Identify and document purpose",
        objective="Identify, document, and justify purpose for processing PII.",
        pb_interpretation="""
            On-prem reduces purposes (no analytics-on-customer-content) but PB still has multiple
            controller-side purposes: telemetry, support metadata, leads, marketing comms.
            Each must have a documented purpose.
        """,
        owner="PB", applies="Y",
        applies_rationale="PB acts as controller for own corporate, telemetry, and lead data.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N"),
                                         ("controller_note", "PB's controller scope.")]),
        implementation="Documented purposes register; per data category list purpose, lawful basis, retention.",
        evidence="Purposes register v1.x; auditor samples 5 purposes and traces to controls.",
        audit_methods=["Insp", "Samp"],
        cadence="Annual + on new processing activity",
        pitfall="Purposes vague (e.g., 'for ops').",
        good_vs_audit_ready=OrderedDict([
            ("good", "Purpose register exists with entries."),
            ("audit_ready", "Purposes tied to controls; reviewed annually; each entry traceable to lawful basis and retention rule."),
        ]),
        external_safe_phrasing="Each processing activity has a documented purpose and lawful basis.",
        legacy_ref="A.7.2.1 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.2"],
    ),
    make_control(
        kind="control_ctrl", native_id="3", group="A.1", group_name="Controller controls",
        title="Identify lawful basis",
        objective="Determine and document the lawful basis for each PII processing activity.",
        pb_interpretation="""
            Customer's consent often inapplicable to vendor-side analytics; PB relies on contract
            performance or legitimate interest for support metadata, telemetry. LIA documented where
            legitimate interest used.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required for each controller-side processing activity.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N")]),
        implementation="Lawful-basis register; per processing entry; LIA documented where applicable.",
        evidence="Register; sample entries; auditor cross-checks vs purpose register.",
        audit_methods=["Insp", "Samp"],
        cadence="Per processing activity / annual",
        pitfall="Legitimate interest used without LIA.",
        external_safe_phrasing="Lawful basis is determined and documented for each activity.",
        legacy_ref="A.7.2.2 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.3"],
    ),
    make_control(
        kind="control_ctrl", native_id="4", group="A.1", group_name="Controller controls",
        title="Determine when and how consent is obtained",
        objective="Where consent is the lawful basis, document procedures for obtaining and recording consent.",
        pb_interpretation="""
            Marketing communications and voluntary telemetry rely on consent. Consent must be granular,
            evidenced, and withdrawable.
        """,
        owner="PB", applies="C",
        applies_rationale="Conditional on processing activities relying on consent.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N")]),
        implementation="Consent procedure; consent records system supporting withdrawal.",
        evidence="Consent records sample; verify withdrawal works.",
        audit_methods=["Insp", "Samp", "Obs"],
        cadence="Per consent capture",
        pitfall="Bundled consent; no withdrawal mechanism.",
        external_safe_phrasing="Consent is captured, recorded and revocable.",
        legacy_ref="A.7.2.3 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.4"],
    ),
    make_control(
        kind="control_ctrl", native_id="5", group="A.1", group_name="Controller controls",
        title="Privacy impact assessment (PIA/DPIA)",
        objective="Conduct PIA/DPIA for high-risk processing activities.",
        pb_interpretation="""
            AI + sensitive client data + new technology implies DPIA likely required for most PB
            processing activities. PB conducts own DPIA per material activity AND provides DPIA template
            to assist customer.
        """,
        owner="PB", applies="Y",
        applies_rationale="High-risk processing across multiple PB activities.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "C"),
                                         ("processor_note", "PB assists customer DPIA where customer is controller.")]),
        implementation="DPIA process and register; per-activity DPIAs.",
        evidence="DPIAs sampled; living documents updated on change.",
        audit_methods=["Insp", "Samp"],
        cadence="Per project / on significant change",
        pitfall="One-off generic DPIA used for all activities.",
        good_vs_audit_ready=OrderedDict([
            ("good", "DPIA template exists; DPIAs done for major activities."),
            ("audit_ready", "Living DPIAs updated on change; tied to risk register; deployer-side DPIA aid template provided."),
        ]),
        external_safe_phrasing="PrivateBox conducts DPIAs for high-risk processing.",
        legacy_ref="A.7.2.5 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.5"],
    ),
    make_control(
        kind="control_ctrl", native_id="6", group="A.1", group_name="Controller controls",
        title="Contracts with PII processors",
        objective="Have contracts with processors meeting GDPR Art. 28 / POPIA s.21 equivalents.",
        pb_interpretation="""
            PB's own subprocessors (cloud, monitoring vendors, support tooling) governed by DPAs.
            Subprocessor register links to per-vendor DPAs.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required for each processor PB engages.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N")]),
        implementation="Subprocessor register; signed DPAs aligned with Article 28(3) requirements.",
        evidence="DPA library; register; sample DPA terms.",
        audit_methods=["Insp", "Samp"],
        cadence="Per onboarding / annual review",
        pitfall="Missing or stale DPAs; weak flow-down clauses.",
        external_safe_phrasing="All processors are governed by data-protection agreements.",
        legacy_ref="A.7.2.6 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.6"],
    ),
    make_control(
        kind="control_ctrl", native_id="7", group="A.1", group_name="Controller controls",
        title="Joint controllership",
        objective="Determine and document joint controller arrangements where applicable.",
        pb_interpretation="Rarely PB; possible in specific integrations. Document if discovered.",
        owner="PB", applies="C",
        applies_rationale="Conditional on existence of joint controller arrangements.",
        na_justification_template="N/A where no joint-controller relationships exist after review.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N")]),
        implementation="Arrangement document where applicable.",
        cadence="On change",
        audit_methods=["Insp"],
        pitfall="Unrecognised joint controllership in product integrations.",
        external_safe_phrasing="Joint controller arrangements documented when applicable.",
        legacy_ref="A.7.2.7 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.7"],
    ),
    make_control(
        kind="control_ctrl", native_id="8", group="A.1", group_name="Controller controls",
        title="Records related to processing PII (ROPA)",
        objective="Maintain records of processing activities equivalent to GDPR Art. 30.",
        pb_interpretation="ROPA covers controller-side activities; updated quarterly.",
        owner="PB", applies="Y",
        applies_rationale="Required for any processing of PII.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N")]),
        implementation="ROPA spreadsheet/tool; live entries.",
        evidence="ROPA sample; auditor traces an activity.",
        audit_methods=["Insp", "Samp"],
        cadence="Quarterly",
        pitfall="Stale ROPA.",
        external_safe_phrasing="PrivateBox maintains records of processing activities.",
        legacy_ref="A.7.2.8 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.8"],
    ),
    make_control(
        kind="control_ctrl", native_id="9", group="A.1", group_name="Controller controls",
        title="Determining and fulfilling obligations to PII principals",
        objective="Identify and meet obligations to PII principals.",
        pb_interpretation="Tied to data subject rights process; obligations register.",
        owner="PB", applies="Y",
        applies_rationale="Statutory rights apply.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "C")]),
        implementation="Obligations register tied to rights process.",
        cadence="Annual + on regulation change",
        audit_methods=["Insp"],
        pitfall="Obligations identified but rights process not exercised.",
        external_safe_phrasing="Documented obligations to PII principals.",
        legacy_ref="A.7.3.1 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.9"],
    ),
    make_control(
        kind="control_ctrl", native_id="10", group="A.1", group_name="Controller controls",
        title="Determining information to be provided to PII principals",
        objective="Provide privacy notice meeting transparency obligations (GDPR Art 12-14 etc.).",
        pb_interpretation="""
            Public privacy notice should clearly distinguish PB-as-controller scope vs
            PB-as-processor scope. Reviewed annually.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required for transparency to data subjects.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N")]),
        implementation="Public privacy notice published; layered (summary + detail).",
        evidence="Notice live at public URL.",
        audit_methods=["Insp"],
        cadence="Annual + on change",
        pitfall="Misleading notice that conflates controller and processor scopes.",
        external_safe_phrasing="Provides a privacy notice covering controller-role processing.",
        legacy_ref="A.7.3.2 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.10"],
    ),
    make_control(
        kind="control_ctrl", native_id="11", group="A.1", group_name="Controller controls",
        title="Providing information; modifying purpose; access; correction; erasure; objection; portability; automated decisions",
        objective="End-to-end DSAR fulfilment and data subject rights.",
        pb_interpretation="""
            Critical for credibility. DSARs against PB-controller-side data go to PB; DSARs against
            client data go to customer (PB assists per A.2.8).
        """,
        owner="PB", applies="Y",
        applies_rationale="Statutory rights apply across processing activities.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "C")]),
        implementation="DSAR SOP and tooling; <30-day target.",
        evidence="DSAR ticket queue; sampled tickets.",
        audit_methods=["Insp", "Samp"],
        cadence="Per request + annual review",
        pitfall="No tooling; manual chase; missed timelines.",
        external_safe_phrasing="PrivateBox operates a documented DSAR fulfilment process.",
        legacy_ref="A.7.3.3-9 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.11"],
    ),
    make_control(
        kind="control_ctrl", native_id="12", group="A.1", group_name="Controller controls",
        title="Privacy by design and by default; collection limitation; minimisation; de-identification; deletion at end; temp files",
        objective="Architecture-level privacy protections.",
        pb_interpretation="""
            On-prem helps significantly; reduces vendor exposure. Privacy-by-default still must be
            evidenced (default settings, telemetry minimisation, temp file handling, deletion at
            end of processing).
        """,
        owner="PB", applies="Y",
        applies_rationale="Architectural requirement across processing activities.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="PbD design records; default settings docs; deletion runbook.",
        evidence="Design docs; default configurations.",
        audit_methods=["Insp", "Obs"],
        cadence="Per release",
        pitfall="PbD claimed but not evidenced in design records.",
        good_vs_audit_ready=OrderedDict([
            ("good", "Privacy considered in design discussions."),
            ("audit_ready", "PbD documented across SDLC; default settings evidenced; deletion runbook tested."),
        ]),
        external_safe_phrasing="Privacy by design and default is evidenced in product design records.",
        legacy_ref="A.7.4.1-5 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.12"],
    ),
    make_control(
        kind="control_ctrl", native_id="13", group="A.1", group_name="Controller controls",
        title="Identify basis for transfer of PII between jurisdictions",
        objective="Cross-border transfer basis (GDPR Ch. V; POPIA s.72).",
        pb_interpretation="""
            On-prem in client country = no transfer. Teraco-SA = no transfer for SA-domiciled data.
            Outbound to non-adequate jurisdictions = SCCs/POPIA s.72 basis required.
        """,
        owner="PB", applies="Y",
        applies_rationale="Live for SA clients touching global model APIs; for any cross-border telemetry.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "C")]),
        implementation="Transfer register; SCCs/IDTAs/POPIA s.72 evidence per transfer.",
        evidence="Register; signed SCCs.",
        audit_methods=["Insp", "Samp"],
        cadence="Per transfer + annual review",
        pitfall="Transfers without documented basis.",
        external_safe_phrasing="Cross-border transfers are governed by documented legal bases.",
        legacy_ref="A.7.5.1 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.13"],
    ),
    make_control(
        kind="control_ctrl", native_id="14", group="A.1", group_name="Controller controls",
        title="Countries / international organisations to which PII can be transferred",
        objective="Document recipients of PII transfers.",
        pb_interpretation="Recipient list annexed to privacy notice.",
        owner="PB", applies="Y",
        applies_rationale="Disclosure obligation under transparency rules.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N")]),
        implementation="Recipient list maintained.",
        evidence="Annexed to privacy notice.",
        audit_methods=["Insp"],
        cadence="Annual + on change",
        pitfall="Hidden recipients (e.g., new sub-processor not added).",
        external_safe_phrasing="Recipients of PII transfers are disclosed.",
        legacy_ref="A.7.5.2 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.14"],
    ),
    make_control(
        kind="control_ctrl", native_id="15", group="A.1", group_name="Controller controls",
        title="Records of transfers",
        objective="Maintain a transfer log.",
        pb_interpretation="Live log of transfers with destination, basis, date.",
        owner="PB", applies="Y",
        applies_rationale="Required for accountability of cross-border transfers.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "N")]),
        implementation="Transfer log.",
        evidence="Log; sample entries.",
        audit_methods=["Insp", "Samp"],
        cadence="Continuous",
        external_safe_phrasing="Maintains transfer records.",
        legacy_ref="A.7.5.3 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.15"],
    ),
    make_control(
        kind="control_ctrl", native_id="16", group="A.1", group_name="Controller controls",
        title="Records of disclosures to third parties",
        objective="Maintain a disclosure log including law-enforcement requests.",
        pb_interpretation="""
            Important for confidential firms. Law-enforcement requests reaching PB: narrow processor
            role limits scope, but disclosures still must be logged. Privileged-data escalation path
            critical.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required for accountability and transparency.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "C"),
                                         ("controller_note", "Own data."),
                                         ("processor_note", "PB assists customer with disclosures of customer data per A.2.14.")]),
        implementation="Disclosure log; law-enforcement-request SOP with counsel-review step.",
        evidence="Log; SOP; sample (redacted).",
        audit_methods=["Insp", "Samp"],
        cadence="Per disclosure + annual review",
        pitfall="Silent compliance with overbroad requests.",
        external_safe_phrasing="Maintains records of third-party disclosures.",
        legacy_ref="A.7.5.4 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.1.16"],
    ),
])


DATA["requirements"].extend([
    make_control(
        kind="control_proc", native_id="2", group="A.2", group_name="Processor controls",
        title="Customer agreement",
        objective="Process PII only on customer's documented instructions.",
        pb_interpretation="""
            Cornerstone of processor relationship. Even though customer 'operates' the box, PB
            acts on customer instruction during support, telemetry, and any vendor-touch activity.
            Master DPA + per-engagement annexes covers this.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required for any processor activity.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="DPA / Customer Agreement defining instructions; annexes for specific engagements (deployment, support, RAG setup).",
        evidence="Signed DPA library; sampled DPAs verified.",
        audit_methods=["Insp", "Samp"],
        cadence="Annual review of template",
        pitfall="DPA missing or silent on AI specifics (no-train, RAG, support access).",
        good_vs_audit_ready=OrderedDict([
            ("good", "DPA template exists and is used."),
            ("audit_ready", "Master DPA + per-engagement annexes for all material processing flows; AI-specific clauses included."),
        ]),
        external_safe_phrasing="Processes client PII only on documented customer instructions.",
        legacy_ref="B.8.2.1 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.2"],
    ),
    make_control(
        kind="control_proc", native_id="3", group="A.2", group_name="Processor controls",
        title="Organization's purposes",
        objective="Processor does not process PII for its own purposes beyond the contract.",
        pb_interpretation="""
            Critical for AI vendor: no model training on customer data. Telemetry must be designed
            to NOT capture customer content. The 'no-train' commitment must be engineering-true
            and contractually anchored.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required to prevent unauthorised re-purposing.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Engineering attestation: no customer-data training; telemetry minimisation specification.",
        evidence="Telemetry spec; design doc; engineering attestations.",
        audit_methods=["Insp", "Int", "Obs"],
        cadence="Per release / annual",
        pitfall="Implicit/ambiguous re training; customer expected to trust without technical evidence.",
        external_safe_phrasing="Customer content is not used for model training.",
        legacy_ref="B.8.2.2 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.3"],
    ),
    make_control(
        kind="control_proc", native_id="4", group="A.2", group_name="Processor controls",
        title="Marketing and advertising use",
        objective="No marketing or advertising use of PII unless explicit consent.",
        pb_interpretation="Policy explicitly prohibits.",
        owner="PB", applies="Y",
        applies_rationale="Required to prevent misuse.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Policy prohibiting; technical controls preventing use of customer data for marketing.",
        evidence="Policy text.",
        audit_methods=["Insp"],
        cadence="Annual review",
        pitfall="Hidden marketing flags or inferred uses.",
        external_safe_phrasing="Customer PII is not used for marketing.",
        legacy_ref="B.8.2.3 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.4"],
    ),
    make_control(
        kind="control_proc", native_id="5", group="A.2", group_name="Processor controls",
        title="Infringing instructions",
        objective="Notify controller if instruction may infringe law.",
        pb_interpretation="Customers may request data export PB cannot legally action; documented escalation procedure.",
        owner="PB", applies="Y",
        applies_rationale="Required by Article 28(3)(h) GDPR equivalent.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Procedure to flag illegal instructions; counsel review step.",
        evidence="Procedure document; sample escalations (redacted).",
        audit_methods=["Insp"],
        cadence="Per request",
        pitfall="No procedure; engineers comply without review.",
        external_safe_phrasing="Identifies and notifies customers of potentially infringing instructions.",
        legacy_ref="B.8.2.4 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.5"],
    ),
    make_control(
        kind="control_proc", native_id="6", group="A.2", group_name="Processor controls",
        title="Confidentiality undertakings",
        objective="Persons authorised to process PII committed to confidentiality.",
        pb_interpretation="All support staff and contractors; NDAs and HR records evidence coverage.",
        owner="PB", applies="Y",
        applies_rationale="Required for any persons accessing customer PII.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="NDAs; vetting; HR records.",
        evidence="NDA records; sample.",
        audit_methods=["Insp", "Samp"],
        cadence="Per onboarding",
        pitfall="Contractors uncovered by confidentiality regime.",
        external_safe_phrasing="All personnel processing customer data are under confidentiality.",
        legacy_ref="B.8.2.5 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.6"],
    ),
    make_control(
        kind="control_proc", native_id="7", group="A.2", group_name="Processor controls",
        title="Records related to processing on behalf of customer (Art 30(2))",
        objective="Maintain processor records of processing.",
        pb_interpretation="Per-customer activity log; available to auditor.",
        owner="PB", applies="Y",
        applies_rationale="Article 30(2) equivalent.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Customer-instruction-driven records; per-customer log.",
        evidence="Log live and current.",
        audit_methods=["Insp"],
        cadence="Continuous",
        external_safe_phrasing="Maintains processor records of processing.",
        legacy_ref="B.8.2.6 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.7"],
    ),
    make_control(
        kind="control_proc", native_id="8", group="A.2", group_name="Processor controls",
        title="Obligations to PII principals (assist controller)",
        objective="Assist customer with DSARs, breach notifications, DPIA cooperation.",
        pb_interpretation="""
            Critical. On-prem may give customer direct access for many DSARs, but PB still must
            assist when telemetry/support involved. SLA defined in DPA.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required to support customer's controller-side obligations.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="DSAR-assist runbook; SLAs in DPA.",
        evidence="Runbook; ticket samples.",
        audit_methods=["Insp", "Samp"],
        cadence="Per request + annual review",
        pitfall="Customer left to fend off DSARs alone.",
        external_safe_phrasing="Assists customers in fulfilling data-subject rights requests.",
        legacy_ref="B.8.3.1 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.8"],
    ),
    make_control(
        kind="control_proc", native_id="9", group="A.2", group_name="Processor controls",
        title="Temporary files",
        objective="Manage and delete temporary files containing PII.",
        pb_interpretation="""
            Telemetry, debug bundles, support session captures are common temp-file sources.
            Audit support-bundle / temp-file lifecycle.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required to prevent retention beyond purpose.",
        role_applicability=OrderedDict([("controller", "C"), ("processor", "Y")]),
        implementation="Temp-file deletion runbook; auto-delete configuration.",
        evidence="Runbook; sample.",
        audit_methods=["Insp", "Obs"],
        cadence="Continuous",
        pitfall="Forgotten temp dumps retained indefinitely.",
        external_safe_phrasing="Temporary files are subject to documented deletion procedures.",
        legacy_ref="B.8.4.1 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.9"],
    ),
    make_control(
        kind="control_proc", native_id="10", group="A.2", group_name="Processor controls",
        title="Return, transfer, disposal of PII",
        objective="At end of contract: delete or return PII; certify deletion.",
        pb_interpretation="""
            On-prem: most data is already with customer. Vendor-side artefacts (telemetry, support
            bundles, backups, RAG corpora when PB-managed) must be deleted/returned with certificate.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required at end of every processor engagement.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Decommissioning SOP; deletion certificate template.",
        evidence="SOP; past examples (certificates).",
        audit_methods=["Insp", "Samp"],
        cadence="Per engagement end",
        pitfall="'Yeah we deleted it' verbally without certificate.",
        external_safe_phrasing="Provides return/deletion of customer PII at end of service.",
        legacy_ref="B.8.4.2 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.10"],
    ),
    make_control(
        kind="control_proc", native_id="11", group="A.2", group_name="Processor controls",
        title="Basis for transfer of PII between jurisdictions (processor scope)",
        objective="Document lawful basis for processor-side cross-border transfers.",
        pb_interpretation="Per customer instruction; documented locations.",
        owner="PB", applies="Y",
        applies_rationale="Required for any processor-side transfers.",
        role_applicability=OrderedDict([("controller", "C"), ("processor", "Y")]),
        implementation="Annex with locations; per customer instruction.",
        evidence="Locations document.",
        audit_methods=["Insp"],
        cadence="Per customer / annual",
        pitfall="Hidden transfers via sub-processor relationships.",
        external_safe_phrasing="Processor-side transfers are governed and disclosed.",
        legacy_ref="B.8.5.1 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.11"],
    ),
    make_control(
        kind="control_proc", native_id="12", group="A.2", group_name="Processor controls",
        title="Countries to which PII may be transferred (disclose to customer)",
        objective="Disclose to customer the countries where PII may be processed.",
        pb_interpretation="List of countries annexed to DPA.",
        owner="PB", applies="Y",
        applies_rationale="Required for transparency to customer.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="List of countries; updated as sub-processors change.",
        evidence="DPA annex.",
        audit_methods=["Insp"],
        cadence="Annual + on change",
        external_safe_phrasing="Discloses countries of processing.",
        legacy_ref="B.8.5.2 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.12"],
    ),
    make_control(
        kind="control_proc", native_id="13", group="A.2", group_name="Processor controls",
        title="Records of disclosures (processor)",
        objective="Same as controller side: maintain disclosure log.",
        pb_interpretation="Live processor disclosure log.",
        owner="PB", applies="Y",
        applies_rationale="Required for accountability.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Disclosure log.",
        evidence="Log live.",
        audit_methods=["Insp"],
        cadence="Continuous",
        external_safe_phrasing="Maintains processor disclosure records.",
        legacy_ref="B.8.5.3 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.13"],
    ),
    make_control(
        kind="control_proc", native_id="14", group="A.2", group_name="Processor controls",
        title="Notification of PII disclosure requests",
        objective="Notify controller of law-enforcement disclosure requests where lawful.",
        pb_interpretation="LE-request SOP with counsel review; customer notified per DPA terms.",
        owner="PB", applies="Y",
        applies_rationale="Required to allow controller to take appropriate action.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="LE-request SOP.",
        evidence="SOP; past cases (redacted).",
        audit_methods=["Insp", "Samp"],
        cadence="Per request",
        pitfall="Silent compliance.",
        external_safe_phrasing="Customers are notified of disclosure requests where lawful.",
        legacy_ref="B.8.5.4 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.14"],
    ),
    make_control(
        kind="control_proc", native_id="15", group="A.2", group_name="Processor controls",
        title="Legally binding PII disclosures",
        objective="Comply only when legally binding; counsel review.",
        pb_interpretation="Legal-review step before any compelled disclosure.",
        owner="PB", applies="Y",
        applies_rationale="Required to prevent unauthorised disclosure.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Legal-review step in disclosure workflow.",
        cadence="Per request",
        audit_methods=["Insp"],
        pitfall="Auto-comply without legal review.",
        external_safe_phrasing="Legally binding disclosure requests are reviewed by counsel.",
        legacy_ref="B.8.5.5 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.15"],
    ),
    make_control(
        kind="control_proc", native_id="16", group="A.2", group_name="Processor controls",
        title="Disclosure of subcontractors",
        objective="Disclose sub-processors before use; allow customer to consent or object.",
        pb_interpretation="""
            Critical for AI vendor (model API providers, monitoring vendors). Pure on-prem with no
            remote support → minimal sub-processors. Once telemetry/support added → register grows.
            Public sub-processor register with change-notice channel.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required for transparency to customer.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Sub-processor register published; change-notice channel.",
        evidence="Register URL; change notices archive.",
        audit_methods=["Insp"],
        cadence="Live + per change",
        pitfall="Stealth sub-processors added without notice.",
        external_safe_phrasing="Maintains a published subprocessor register with change notifications.",
        legacy_ref="B.8.5.6 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.16"],
    ),
    make_control(
        kind="control_proc", native_id="17", group="A.2", group_name="Processor controls",
        title="Engagement of a subcontractor (flow-down obligations)",
        objective="Same data-protection obligations flow down to sub-processors.",
        pb_interpretation="Flow-down clauses in sub-processor DPAs are equivalent to customer DPAs.",
        owner="PB", applies="Y",
        applies_rationale="Required to maintain protection chain.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Flow-down clauses in sub-processor DPAs.",
        evidence="DPA library; sample.",
        audit_methods=["Insp", "Samp"],
        cadence="Per onboarding",
        pitfall="Weak flow-down (e.g., processor accepts customer DPA but flows down only generic clauses).",
        external_safe_phrasing="Subprocessor obligations equivalent to customer DPAs.",
        legacy_ref="B.8.5.7 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.17"],
    ),
    make_control(
        kind="control_proc", native_id="18", group="A.2", group_name="Processor controls",
        title="Change of subcontractor (notice and objection)",
        objective="Notify customer of sub-processor changes; allow objection per DPA.",
        pb_interpretation="Defined notice window in DPA; objection mechanism.",
        owner="PB", applies="Y",
        applies_rationale="Required by Article 28(2) GDPR equivalent.",
        role_applicability=OrderedDict([("controller", "N"), ("processor", "Y")]),
        implementation="Change-notice procedure; defined window (e.g., 30 days advance notice).",
        evidence="Change-notice records.",
        audit_methods=["Insp"],
        cadence="Per change",
        external_safe_phrasing="Subprocessor changes are notified in advance.",
        legacy_ref="B.8.5.8 (2019)",
        source_refs=["ISO/IEC 27701:2025 A.2.18"],
    ),
])


DATA["requirements"].extend([
    make_control(
        kind="control_shared", native_id="5.7", group="A.3", group_name="Shared security controls",
        title="Threat intelligence",
        objective="Collect and use threat intelligence to inform privacy and security risk.",
        pb_interpretation="Privacy-aware threat intel feed; integrated with privacy risk register.",
        owner="PB", applies="Y",
        applies_rationale="Standard 27002:2022 control with privacy lens.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="Threat-intel feed; integration with risk register.",
        evidence="Feed sources; reports.",
        audit_methods=["Insp"],
        cadence="Continuous + quarterly review",
        external_safe_phrasing="Threat intelligence feeds privacy risk.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (5.7)", "ISO/IEC 27002:2022 5.7"],
    ),
    make_control(
        kind="control_shared", native_id="5.16-8.5", group="A.3", group_name="Shared security controls",
        title="Identity management & privileged access",
        objective="Strong authentication, privileged-access management for support roles.",
        pb_interpretation="""
            Cornerstone for support-access risk. Support engineers' access to client environments
            must be MFA + JIT + recorded. PAM logs evidence each session.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required for any vendor-side access to customer environments.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="JIT/PAM for support; SSO; MFA; session recording.",
        evidence="PAM logs; configuration documentation.",
        audit_methods=["Insp", "Samp", "Obs"],
        cadence="Continuous",
        pitfall="Shared accounts; standing access.",
        good_vs_audit_ready=OrderedDict([
            ("good", "MFA enabled; some PAM."),
            ("audit_ready", "JIT credential issuance; per-session approval; session recording; quarterly access review."),
        ]),
        external_safe_phrasing="Vendor support access is governed by privileged-access management.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (5.16, 8.2-8.5)", "ISO/IEC 27002:2022 5.16, 8.2-8.5"],
    ),
    make_control(
        kind="control_shared", native_id="5.14-5.15", group="A.3", group_name="Shared security controls",
        title="Information transfer security",
        objective="Secure mechanisms for information transfer.",
        pb_interpretation="""
            Backup support, log shipping, telemetry — all must use encrypted channels with allow-
            listed destinations. Customer-controllable.
        """,
        owner="PB", applies="Y",
        applies_rationale="Required for any vendor↔customer data transfer.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="Encrypted channels; signed packages; allow-listed destinations.",
        evidence="TLS configurations; signed-update infrastructure.",
        audit_methods=["Insp", "Obs"],
        cadence="Continuous",
        pitfall="Telemetry over plain HTTP; unsigned updates.",
        external_safe_phrasing="Vendor↔customer transfers are encrypted and integrity-protected.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (5.14, 5.15)", "ISO/IEC 27002:2022 5.14, 5.15"],
    ),
    make_control(
        kind="control_shared", native_id="8.15-8.17", group="A.3", group_name="Shared security controls",
        title="Logging & monitoring",
        objective="Privacy-aware logging.",
        pb_interpretation="""
            Critical for support-access auditability. Customer keeps primary logs on-prem; PB-side
            logs minimised and PII-redacted by default.
        """,
        owner="PB/SH", applies="Y",
        applies_rationale="Required for accountability and incident response.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="Logging specification including PII minimisation and redaction defaults.",
        evidence="Logging spec; sample logs.",
        audit_methods=["Insp", "Samp"],
        cadence="Per release",
        pitfall="Logs include raw client content (e.g., prompts, outputs).",
        external_safe_phrasing="Logs are designed to minimise PII while retaining auditability.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (8.15-8.17)", "ISO/IEC 27002:2022 8.15-8.17"],
    ),
    make_control(
        kind="control_shared", native_id="8.24", group="A.3", group_name="Shared security controls",
        title="Cryptography (incl. KMS)",
        objective="Cryptographic protection of PII.",
        pb_interpretation="""
            Essential for confidential firms. Customer-managed keys preferred; PB documents key
            management options (CMK vs vendor-managed) in deployment guide.
        """,
        owner="PB/SH", applies="Y",
        applies_rationale="Required for any PII at rest or in transit.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="Crypto policy; KMS architecture; customer-managed keys offered.",
        evidence="Policy; architecture document.",
        audit_methods=["Insp"],
        cadence="Annual + on cryptographic change",
        pitfall="Vendor-controlled keys forced; no CMK option.",
        external_safe_phrasing="Supports customer-managed encryption keys.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (8.24)", "ISO/IEC 27002:2022 8.24"],
    ),
    make_control(
        kind="control_shared", native_id="8.25-8.30", group="A.3", group_name="Shared security controls",
        title="Secure development (SDL incl. PbD)",
        objective="Privacy by design embedded in SDLC.",
        pb_interpretation="Tied to A.1.12. PbD checklist in PR template; privacy review per material change.",
        owner="PB", applies="Y",
        applies_rationale="Required to evidence PbD architectural posture.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="PbD checklist in PR template; SDLC documentation.",
        evidence="Sample PRs; SDLC documentation.",
        audit_methods=["Insp", "Samp"],
        cadence="Per release",
        depends_on=["iso-27701-a1-12"],
        external_safe_phrasing="Privacy by design is embedded in the SDLC.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (8.25-8.30)", "ISO/IEC 27002:2022 8.25-8.30"],
    ),
    make_control(
        kind="control_shared", native_id="8.13", group="A.3", group_name="Shared security controls",
        title="Backup integrity & access",
        objective="Backup operations protect PII.",
        pb_interpretation="""
            When PB performs backups (optional service), full A.2 processor obligations attach.
            Encrypted backups; tested restore.
        """,
        owner="PB/SH", applies="C",
        applies_rationale="Conditional on backup-support service activation.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="Backup procedure; encryption; access control.",
        evidence="Procedure; configuration.",
        audit_methods=["Insp", "Obs"],
        cadence="Per backup cycle + annual restore test",
        pitfall="Untested backups; backups offshore without basis.",
        external_safe_phrasing="Backup operations follow documented privacy-preserving procedures.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (8.13)", "ISO/IEC 27002:2022 8.13"],
    ),
    make_control(
        kind="control_shared", native_id="5.24-5.27", group="A.3", group_name="Shared security controls",
        title="Privacy incident management",
        objective="Privacy incident response capability.",
        pb_interpretation="""
            Privacy track within IR plan; notification SLA in DPAs (e.g., <24h customer, <72h regulator);
            coordination with customer.
        """,
        owner="PB/SH", applies="Y",
        applies_rationale="Required for accountability and regulatory compliance.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="IR plan with privacy track; notification SLAs in DPAs.",
        evidence="IR plan; tabletop exercise reports.",
        audit_methods=["Insp", "Int"],
        cadence="Annual tabletop + per incident",
        pitfall="72h+ silence to customer.",
        external_safe_phrasing="Privacy incidents trigger documented notification SLAs.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (5.24-5.27)", "ISO/IEC 27002:2022 5.24-5.27"],
    ),
    make_control(
        kind="control_shared", native_id="5.19-5.23", group="A.3", group_name="Shared security controls",
        title="Supplier / cloud security",
        objective="Third-party / cloud security with privacy lens.",
        pb_interpretation="All optional support layers introduce supplier dependencies; subject to privacy-aware due diligence.",
        owner="PB", applies="Y",
        applies_rationale="Required for any sub-processor relationship.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="Supplier management including privacy.",
        evidence="Supplier register; reviews.",
        audit_methods=["Insp"],
        cadence="Annual reviews",
        pitfall="Stale supplier register; no privacy review on renewal.",
        external_safe_phrasing="Suppliers are subject to privacy-aware due diligence.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (5.19-5.23)", "ISO/IEC 27002:2022 5.19-5.23"],
    ),
    make_control(
        kind="control_shared", native_id="7.x", group="A.3", group_name="Shared security controls",
        title="Physical security",
        objective="Physical security of PII processing facilities.",
        pb_interpretation="""
            On-prem default: less directly applicable (customer-owned facility). Teraco scenario:
            inherits Teraco's ISAE 3402 / PCI DSS attestations; PB documents the inheritance.
        """,
        owner="SH", applies="C",
        applies_rationale="Customer-owned in on-prem default; inherited from host in Teraco scenario.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="Physical-security mapping document; Teraco compliance pack inheritance for hosted scenario.",
        evidence="Mapping doc; Teraco attestation copies.",
        audit_methods=["Insp"],
        cadence="Annual",
        pitfall="Asserted but not documented; claiming Teraco's certifications as PB's own.",
        external_safe_phrasing="Physical security relies on customer-owned facility or Teraco-attested colocation.",
        companion_refs=["iso-27002", "iso-27018"],
        source_refs=["ISO/IEC 27701:2025 A.3 (7.x)", "Teraco ISAE 3402 / PCI DSS"],
    ),
    make_control(
        kind="control_shared", native_id="5.31-5.34", group="A.3", group_name="Shared security controls",
        title="Compliance / records (legal compliance)",
        objective="Track legal and regulatory compliance obligations.",
        pb_interpretation="Compliance register tracking GDPR, POPIA, AI Act, sectoral regulations.",
        owner="PB", applies="Y",
        applies_rationale="Required for accountability across jurisdictions.",
        role_applicability=OrderedDict([("controller", "Y"), ("processor", "Y")]),
        implementation="Compliance register.",
        evidence="Register; sample.",
        audit_methods=["Insp"],
        cadence="Annual + on regulatory change",
        external_safe_phrasing="Legal/regulatory obligations are tracked.",
        companion_refs=["iso-27002"],
        source_refs=["ISO/IEC 27701:2025 A.3 (5.31-5.34)", "ISO/IEC 27002:2022 5.31-5.34"],
    ),
])


# =============================================================================
# Emit
# =============================================================================

if __name__ == "__main__":
    out_path = Path("/mnt/user-data/outputs/iso-27701.yaml")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = """# ISO/IEC 27701:2025 — PrivateBox alignment record (schema v2)
# Source-of-truth file for the GRC OS. Edits go in version control.
# Regenerate via: python scripts/build_iso27701.py
#
# Schema: see /docs/framework-schema-v2.md
# 2025 standalone PIMS; supersedes 2019 (withdrawn). Transition deadline October 2028.
"""

    with open(out_path, "w") as f:
        f.write(header + "\n")
        yaml.dump(
            DATA, f,
            default_flow_style=False, sort_keys=False, allow_unicode=True,
            width=100, indent=2,
        )

    from collections import Counter
    print(f"Wrote {out_path}")
    print(f"  schema_version: {DATA['schema_version']}")
    print(f"  scenarios: {len(DATA['scenarios'])}")
    print(f"  requirements: {len(DATA['requirements'])}")
    print(f"  open_questions: {len(DATA['open_questions'])}")
    print(f"  evidence_families: {len(DATA['evidence_families'])}")
    print(f"  companion_standards: {len(DATA['companion_standards'])}")

    if DATA["requirements"]:
        kinds = Counter(r["kind"] for r in DATA["requirements"])
        print(f"  by kind: {dict(kinds)}")
