# PrivateBox ISO AI Governance Architecture: Certifier-Grade Alignment Pack
## ISO/IEC 42001:2023 (primary) · ISO/IEC 42005:2025 (impact-assessment companion) · ISO/IEC 42006:2025 (certification-readiness companion)

---

## 1. Executive Summary

PrivateBox is positioned as an **on-prem / locally hosted, single-tenant AI solution** for confidential firms in legal, finance, healthcare, HR, retail, and confidential enterprise search. Its core value proposition — that sensitive client data does not leave the customer environment — materially **reduces** several categories of AI risk (data exfiltration, multi-tenant leakage, third-party model misuse, cross-jurisdictional data transfer exposure) but **does not eliminate** the AI Management System (AIMS) duties imposed by ISO/IEC 42001:2023. On-prem architecture is a *control*, not a *governance system*.

This document provides an **evidence-based alignment** with ISO/IEC 42001:2023, deepened by ISO/IEC 42005:2025 (AI system impact assessment) and ISO/IEC 42006:2025 (certification-body / audit-readiness expectations). It is **not** a claim of certification. PrivateBox can credibly state:

- *"PrivateBox is designed in alignment with ISO/IEC 42001:2023, with an AIMS architecture that implements controls consistent with the standard's requirements, and an impact-assessment methodology aligned with ISO/IEC 42005:2025."*
- *"PrivateBox is preparing for accredited certification under ISO/IEC 42001, with audit-readiness benchmarked against ISO/IEC 42006:2025."*

PrivateBox should **never** state: "ISO 42001 certified", "fully compliant with ISO/IEC 42001", or "guaranteed responsible AI" until and unless an accredited certification body (e.g., Schellman, BSI, DNV, A-LIGN, TÜV) issues a certificate against a defined AIMS scope. Even after certification, language must remain accurate to that scope.

The deliverable is structured to support three audiences simultaneously: **internal control builders** (engineering, security, governance), **external trust/procurement** (legal, finance, healthcare buyers, their CISOs and DPOs), and **certification auditors** (Stage 1 documentation review and Stage 2 implementation effectiveness).

---

## 2. Assumptions and Scoping Notes for PrivateBox

| # | Assumption | Implication |
|---|---|---|
| A1 | PrivateBox is the **AI system provider/producer**; the customer is typically the **AI deployer/user** (in EU AI Act language, often "deployer"; in ISO 42001 language, the "customer" or "user" role) | Roles must be documented per Annex A.10 and per AIMS scope statement |
| A2 | A typical install is **single-tenant, on customer infrastructure**, with optional support layers (remote admin, update delivery, telemetry, monitoring, backup, vendor maintenance, support access, managed connectors) | Each support layer creates a *shared responsibility* surface that must be governed contractually and operationally |
| A3 | PrivateBox typically integrates **third-party foundation/open-weight models** (e.g., Llama-family, Mistral, etc.) and customer/private RAG corpora | Annex A.10.2 (suppliers) and A.7 (data) are always in scope; cannot be excluded from SoA |
| A4 | Primary jurisdictions: **South Africa (POPIA, King V), EU (EU AI Act, GDPR-equivalent), US, UK** | Multi-jurisdictional crosswalk is mandatory; AIMS context (Clause 4) must list all of these |
| A5 | Primary sectors: **legal, finance, healthcare**; supporting: HR, retail, enterprise search | High-impact use cases (clinical decision support, credit, legal advice, hiring) trigger the most demanding A.5 / 42005 impact assessments |
| A6 | PrivateBox's AIMS scope = the *organisation building, distributing and supporting PrivateBox* — not the customer's AI usage | Customer's AI use is governed by *their* AIMS (which PrivateBox should help enable through documentation, but cannot certify) |
| A7 | PrivateBox **does not normally see, train on, or retain customer production data** (this is a core architectural commitment) | This must be evidenced contractually, technically (config), and through telemetry-scope statements |
| A8 | PrivateBox aims to align in parallel with **ISO 27001, ISO 27701, NIST AI RMF, NIST SP 800-218A, EU AI Act, POPIA, King V** | Single integrated control library + crosswalk to avoid duplication |

**Scoping decision**: AIMS scope statement should read (target wording): *"The design, development, packaging, distribution, support, and continual improvement of the PrivateBox on-premises single-tenant AI platform, including its model selection/evaluation pipeline, RAG and connector framework, update and telemetry services, and customer support operations. Excluded: customer-operated deployments after handover, customer fine-tuning of models inside their environment, and customer-provided data — these remain under the customer's own AIMS / governance."*

---

## 3. Source Hierarchy and Standard Status Note

| Standard | Status | Role in this pack | How treated |
|---|---|---|---|
| **ISO/IEC 42001:2023** | Published Dec 2023, normative, certifiable management system standard (Annex SL structure, clauses 4–10, Annex A reference controls A.2–A.10 = 38 controls across 9 objectives, Annex B normative implementation guidance, Annex C informative objectives/risk sources, Annex D informative sector/integration guidance) | **Primary alignment source of truth** for every Clause and Annex A claim | Direct quotation/paraphrase of requirements where authoritative; Annex B used for "what good looks like"; Annex C drives Table 6 |
| **ISO/IEC 42005:2025** | Published May 2025, **guidance** standard (not certifiable on its own); deepens AI system impact assessment (AISIA) — process, thresholds, roles, documentation, monitoring; Annex A maps it to ISO 42001, Annex B relates it to ISO/IEC 23894, Annex C provides harm/benefit taxonomy, Annex E provides AISIA template | **Companion guidance** for impact assessment depth (Tables 5, 9) | Used to deepen Clause 6.1.4 (impact assessment) and Annex A.5 controls |
| **ISO/IEC 42006:2025** | Published Jul 2025, additional requirements to ISO/IEC 17021-1 for **certification bodies** auditing AIMS — auditor competence (≥4 yrs IT/data protection, ≥2 yrs AI; ≥3 days AIMS audit training; supervised audit experience), audit-time calculation, team competence covering all of Annex A | **Companion certification-readiness reference** — tells PrivateBox what auditors will be required to do, and therefore what evidence they will demand | Used for Table 10 (audit-readiness) and Section 14 (case studies) |
| ISO/IEC 22989:2022 | Normatively referenced by ISO 42001 (terminology) | Definitional only | Aligned terminology used throughout |
| ISO/IEC 23894:2023 | AI risk management guidance | Reference for risk methodology | Used to harden Clause 6.1 |

**Source labels used in tables**: `[42001-N]` = ISO 42001 normative; `[42001-Annex B]` = normative implementation guidance; `[42001-Annex C]` = informative; `[42005-G]` = ISO 42005 guidance; `[42006-CB]` = ISO 42006 certification-body expectation; `[CB]` = accredited certification body interpretation (Schellman, BSI, DNV, A-LIGN, TÜV); `[Expert]` = serious implementation guide; `[Market]` = market practice; `[Inf]` = inference / our interpretation.

**Caveat on paywalled wording**: ISO 42001, 42005, 42006 are paywalled; only Clauses 1–3 of 42001 and limited drafts/previews are publicly visible. Where exact normative wording is paywalled, this pack uses authoritative summaries (ISO official explainers, NIST crosswalk PDF, Schellman/BSI/DNV/A-LIGN/Microsoft/Anthropic/AWS/Workday/Cognizant published material) with explicit labelling. Customers, auditors and procurement teams are referred to the official ISO documents for normative reference.

---

## 4. TABLE 1 — Clause-by-Clause AIMS Matrix (Clauses 4–10)

(*Columns condensed for readability: Clause / Title / Source / Requirement summary / PB interpretation / On-prem reading / Practical objective / Implementation checklist / Required artifacts / Evidence example / Test method / Maturity indicator / Failure modes / Marketing-safe wording*)

### Clause 4 — Context of the Organisation

**4.1 Understanding the organisation and its context** `[42001-N]`
- **Requirement summary**: Determine internal/external issues relevant to AIMS purpose and ability to achieve intended outcomes. Determine PrivateBox's *role* in the AI ecosystem (provider, producer, customer, partner — likely **provider + producer**).
- **PB interpretation**: PrivateBox must explicitly position itself as an AI system *provider* (and component *producer*) to confidential firms; not a *deployer* of AI on behalf of those firms.
- **On-prem reading**: Customer environment is *external context*; PrivateBox's R&D/support environment is *internal context*. Both must be captured.
- **Applies?** Yes (PB).
- **Implementation**: Maintain a written *Context of the Organisation* document refreshed at least annually and on material change (new jurisdiction, new sector, new model class, regulatory change).
- **Artifacts**: Context register; PESTLE/SWOT-style register; AI role declaration.
- **Evidence**: Dated, version-controlled context register signed off by top management.
- **Test**: Auditor asks "Why is your AIMS scope what it is?" — answer must trace to context.
- **Maturity**: Reviewed at every management review; tied to objectives.
- **Failures**: Generic boilerplate; not refreshed; ignores POPIA/EU AI Act/King V; doesn't name PB's AI role.
- **Marketing-safe**: *"PrivateBox's AIMS is contextualised for confidential-firm AI in legal, finance and healthcare across ZA, EU, US and UK."*

**4.2 Needs and expectations of interested parties** `[42001-N]`
- **Requirement**: Identify interested parties; their relevant requirements; which become AIMS requirements.
- **PB interpretation**: Customers (legal/finance/healthcare CISOs, DPOs, GCs), data subjects (clients of customers), regulators (Information Regulator ZA, EU AI Office, UK ICO, US sectoral), employees, third-party model providers, support partners, investors.
- **Implementation**: Stakeholder register with documented expectations and how each maps to controls.
- **Artifact**: Interested-Parties Register.
- **Evidence**: Register, interview/feedback logs, requirement-traceability matrix.
- **Failures**: Customer-only view; missing data subjects and regulators; no traceability to controls.
- **Marketing-safe**: *"PrivateBox's AIMS systematically captures and addresses the requirements of customers, data subjects, regulators and supply-chain partners."*

**4.3 Determining the scope of the AIMS** `[42001-N]`
- **Requirement**: Documented scope statement covering boundaries, products, services, locations, AI roles.
- **PB interpretation**: See target wording in §2 (assumption A6). Scope must be *narrow enough to be defensible* but *broad enough to be credible*.
- **Implementation**: A 1-page AIMS Scope Statement, top-management-signed, referenced from policy.
- **Failures**: Scope drift in marketing; scope that seems to extend over customer environments (creates legal exposure).
- **Marketing-safe**: *"Our AIMS scope covers the design, build and support of PrivateBox; customer-operated deployments are governed by the customer's own AIMS, which we enable with documentation."*

**4.4 AI management system** `[42001-N]`
- Establish, implement, maintain, continually improve the AIMS.
- **Implementation**: PDCA cycle; integrated with ISO 27001 ISMS and ISO 27701 PIMS where present.
- **Artifact**: AIMS manual / overview describing process architecture and integration.
- **Marketing-safe**: *"AIMS architecture aligned to ISO/IEC 42001, integrated with our existing ISMS."*

### Clause 5 — Leadership

**5.1 Leadership and commitment** `[42001-N]`: Top management accountability — measurable; not delegable. **Artifacts**: Board/Exco minutes; CEO sign-off on AI policy and AIMS scope; budget allocation evidence. **Failures**: AIMS sponsored only at IT manager level — a frequent finding `[CB-Schellman]`.

**5.2 AI Policy** `[42001-N]` + linked to **A.2.2**: Written, approved, communicated, available to interested parties, framed by business strategy, ethics, risk environment, legal requirements, including handling of policy exceptions. **Artifact**: PrivateBox AI Policy v1.x. **Test**: Random employee interviewed by auditor can describe its core principles. **Marketing-safe**: *"Our AI Policy, approved by top management, governs every PrivateBox AI activity."*

**5.3 Roles, responsibilities and authorities** `[42001-N]` + **A.3.2**: Documented assignment for AIMS conformance and reporting. **Artifact**: RACI; AI Governance Charter; named AI Governance Lead, Model Risk Lead, AI Security Lead, Data/RAG Steward, Customer Support AI Liaison; ideally a cross-functional AI Governance Committee meeting on a fixed cadence.

### Clause 6 — Planning

**6.1.1 Actions to address risks and opportunities** `[42001-N]`: Determine risks and opportunities for AIMS to achieve intended outcomes, prevent/reduce undesired effects, and continually improve.

**6.1.2 AI risk assessment** `[42001-N]` (corresponds to Clause 6.1.2): Documented risk-assessment methodology — criteria, acceptance, repeatability — informed by Annex C objectives/risk sources `[42001-Annex C]` and ISO/IEC 23894. **Implementation**: Methodology document + AI Risk Register per system in scope. **Failure**: Using a generic InfoSec risk methodology and renaming it.

**6.1.3 AI risk treatment** `[42001-N]`: Treatment plan; control selection; **Statement of Applicability (SoA)** comparing selected controls against Annex A. Note 3 explicitly permits exclusion *with documented justification*. **Artifact**: SoA (one row per Annex A control: applicability Y/N, implementation status, control owner, evidence pointer, justification — see Table 2). **Failure**: Excluding controls without written justification → major nonconformity `[CB-Schellman / orbit.reconn.io]`.

**6.1.4 AI system impact assessment** `[42001-N]` — **deepened by ISO/IEC 42005:2025** `[42005-G]`: Documented process for assessing AI system impacts on individuals, groups, society. 42005 requires: documented methodology, integration with management system, timing/scope rules, role allocation, thresholds, conduct, analysis, recording/reporting, approval, monitoring/review (10 elements). Must address *intended uses* and *reasonably foreseeable misuses*. **Artifact**: AISIA Methodology + per-system AISIA records. (See Table 9.)

**6.2 AI objectives and planning to achieve them** `[42001-N]`: SMART AI objectives at relevant functions — measurable, time-bound, communicated, monitored, updated. **Failure**: Aspirational statements ("we will be ethical") that cannot be measured.

**6.3 Planning of changes** `[42001-N]`: Changes to AIMS performed in a planned manner. **Artifact**: Change control procedure that explicitly covers model swaps, RAG corpus changes, prompt-template changes, deployment-environment changes.

### Clause 7 — Support

**7.1 Resources** | **7.2 Competence** | **7.3 Awareness** | **7.4 Communication** | **7.5 Documented information** `[42001-N]`.

- Competence: AI ethics, ML risk, secure SDLC for AI, data governance, model evaluation, jurisdictional law (POPIA, EU AI Act, GDPR, HIPAA-equivalent, FCA/SEC/JSE-relevant). Records: training plans, competence matrix, certifications.
- Awareness: All staff (including support engineers) understand AI policy, their role, consequences of non-conformance.
- Communication: Internal and external (customers, regulators) protocols — including incident notification timelines.
- Documented information: Version-controlled, dated, owner-attributed, retention-defined.
- **42006-CB observation**: Auditors sample randomly; documents that exist but no one can find or has read fail this clause.

### Clause 8 — Operation

**8.1 Operational planning and control** `[42001-N]`: Establish, implement, control processes; criteria; documented info to confirm processes carried out as planned; control planned changes; review unintended changes.

**8.2 AI risk assessment (operational)** `[42001-N]`: Perform AI risk assessments at planned intervals and on significant change.

**8.3 AI risk treatment (operational)** `[42001-N]`: Implement the AI risk treatment plan.

**8.4 AI system impact assessment (operational)** `[42001-N]`: Perform AISIA at planned intervals and on significant change. Pre-deployment AISIA is mandatory before any new system or material upgrade. (See Table 5.)

### Clause 9 — Performance Evaluation

**9.1 Monitoring, measurement, analysis, evaluation** `[42001-N]`: What/how/when monitored; methods to ensure valid results; analysis and evaluation of AIMS performance and effectiveness. **Artifact**: KPI dashboard (model performance drift, fairness/bias indicators, incident counts, support-ticket categorisation, concern-reporting volumes, SoA implementation health).

**9.2 Internal audit** `[42001-N]`: Programme; impartial auditors; report to relevant management; corrective actions tracked. Audit team **must be independent** of the AIMS team `[42006-CB]`.

**9.3 Management review** `[42001-N]`: Inputs (audit results, KPI data, nonconformities, status of actions, changes in external/internal issues, feedback from interested parties, opportunities for continual improvement) → Outputs (decisions, resource changes, improvement opportunities). Cadence: at least annual; more often during early maturity.

### Clause 10 — Improvement

**10.1 Continual improvement** `[42001-N]`: Suitability, adequacy, effectiveness of AIMS continuously improved.

**10.2 Nonconformity and corrective action** `[42001-N]`: React, evaluate cause, implement actions, review effectiveness, update AIMS if needed, retain documented information of nature/actions/results. **Failure**: NC log that records issues but never closes them.

---

## 5. TABLE 2 — Annex A Control Matrix (38 controls, granular)

For brevity, columns shown in compact form below: **Ref · Title · Source · Auth summary · PB interpretation · Applies (Y/Shared/Cond/N/A) · Owner · On-prem reading · Practical objective · Checklist · Artifacts · Evidence · Test · SoA note · Maturity · Failures · Safe wording.**

### A.2 — Policies related to AI (3 controls) `[42001-N + Annex B]`

**A.2.2 AI Policy** — Documented AI policy informed by business strategy, values, risk level, legal requirements; principles + exceptions process. **PB**: Mandatory. **Owner**: AI Governance Lead. **Artifact**: PrivateBox AI Policy. **Evidence**: Signed PDF v1.x; dissemination log. **Test**: Random employee interview. **SoA**: Always Applicable. **Maturity**: Versioned, reviewed annually + on trigger. **Failure**: Boilerplate not tailored. **Safe wording**: *"PrivateBox operates under a documented AI Policy aligned to ISO/IEC 42001 A.2.2."*

**A.2.3 Alignment with other organisational policies** — Map intersection with InfoSec (27001), Privacy (27701/POPIA/GDPR), HR, Procurement, Ethics. **PB**: Yes. **Artifact**: Cross-policy alignment map. **Failure**: AI policy contradicts privacy policy on retention.

**A.2.4 Review of the AI policy** — Named owner, scheduled reviews, trigger-based reviews. **Artifact**: Review log. **Test**: Auditor reads minutes.

### A.3 — Internal organisation (2)

**A.3.2 Roles and responsibilities** — Defined and communicated AI roles. **Artifact**: AI RACI; org chart. **Failure**: Same person owns development AND oversight.

**A.3.3 Reporting concerns** — Whistleblower-equivalent for AI concerns; non-retaliation. **Artifact**: Concerns SOP; concern log; staff training. **Test**: Random employee asked "How would you raise an AI concern?" — must answer.

### A.4 — Resources (6)

**A.4.2 Resource documentation** — General resource catalogue. **Artifact**: Resource map per AI system.

**A.4.3 Data resources** — Provenance, categories (train/val/test/prod), labelling, quality, retention, known biases, rights. **PB on-prem reading**: PrivateBox documents *its* training/eval data and the structure expected of *customer* data; customer data itself remains customer-owned. **Critical control**. **Failure**: Training-data provenance undocumented `[Expert-orbit.reconn.io]`.

**A.4.4 Tooling resources** — ML frameworks, eval libraries, guardrail tools, prompt templates, RAG stack. **Artifact**: Tooling register with versions and licences.

**A.4.5 System and computing resources** — Hardware, hosting type, processing/storage, environmental impact. **PB**: Critical because deployment target = customer hardware → minimum-spec sheet, GPU sizing, energy disclosure.

**A.4.6 Human resources** — Skill matrix, diversity considerations for teams handling sensitive data domains.

(*A.4.1 / A.4.x numbering varies between sources [Expert-cyberzoni vs Expert-reconn]; PrivateBox should map to whichever Annex A numbering ISO publishes — the PECB-aligned numbering above is widely used.*)

### A.5 — Assessing impacts of AI systems (3) — connect to **42005**

**A.5.2 AI system impact assessment process** — Documented, repeatable methodology. **PB**: Mandatory; cannot be excluded even for organisations using only third-party models. **Artifact**: AISIA Methodology aligned with 42005 (10 elements).

**A.5.3 Documentation of AI system impact assessments** — Per-system records. **Artifact**: AISIA records library.

**A.5.4 Assessing AI system impact on individuals or groups** | **A.5.5 Assessing societal impacts** — Coverage of fairness, privacy, safety, autonomy, environment, employment, public trust. **PB-sector**: Healthcare → patient safety; legal → access to justice/privilege; finance → fair lending/POPIA s.71 automated decision-making.

### A.6 — AI system life cycle (10)

**A.6.1.1 Objectives for responsible development** — Translate policy into engineering objectives.

**A.6.1.2 Processes for responsible design and development** — SDLC integrating fairness, transparency, robustness, security; align to **NIST SP 800-218A** for generative/foundation-model practices.

**A.6.1.3 Documentation of AI system development** — Design specs, decisions, test results, sign-offs (AI equivalent of model card + system card + datasheet).

**A.6.1.4 Addressing bias** — Methodology, baselines, retest cadence. **Failure**: Awareness statement instead of method.

**A.6.1.5 AI system robustness / verification & validation** — Adversarial testing, edge cases, red-teaming.

**A.6.2.1 AI system operational concept** — How it is meant to run in customer environment.

**A.6.2.2 AI system testing** — Pre-deployment testing depth proportional to risk.

**A.6.2.3 Human oversight** — *Genuine* override authority, accuracy/consistency monitoring, concern channel, automated-decision appropriateness assessment per use case. **PB-sector criticality**: Legal/finance/healthcare must default to "human-in-the-loop" for any consequential output.

**A.6.2.4 AI system event logs** — Time, date, inputs (or hashes), outputs, anomalies, retention. **PB on-prem reading**: Logs are *customer-owned* by default; PrivateBox only sees what telemetry contracts permit.

**A.6.2.5 AI system deployment** — Documented deployment plan; pre-go-live verification checklist (impact assessment, testing, oversight, ops docs all complete and signed).

### A.7 — Data for AI systems (4)

**A.7.2 Data for development and enhancement** — Operational data governance (quality, provenance, security, transparency).

**A.7.3 Acquisition of data** — Categories, quantities, sources, demographics, prior handling, rights (PII, copyright), labelling metadata, provenance.

**A.7.4 Quality of data** — Defined criteria, measurement, remediation.

**A.7.5 Processing of personal information** — Integration with POPIA / GDPR / UK GDPR / HIPAA-equivalent. **PB**: PrivateBox should default to "no customer PII processing in our environment" and have technical evidence; processing remains in customer's environment.

### A.8 — Information for interested parties (5)

**A.8.2 Characteristics / system documentation** — Intended use, capabilities, limitations, conditions of non-use.

**A.8.3 External reporting / disclosure** — When users interact with AI; aligns with EU AI Act Art. 50.

**A.8.4 Communication of incidents** — Notification procedures (timelines aligned to EU AI Act Art. 73 = 15 days for serious incidents; aligned to POPIA s.22 breach notification where personal info is involved).

**A.8.5 Information for interested parties** — Limitations, known biases, edge cases.

**A.8.6 Communication of changes** — Material changes communicated to affected parties.

### A.9 — Use of AI systems (3)

**A.9.2 Processes for responsible use** — Internal use processes.

**A.9.3 Objectives for responsible use** — Translated into measurable objectives.

**A.9.4 Intended use** — Operational safeguards prevent out-of-scope use; user training. **PB**: Critical for legal/finance/healthcare to scope what PrivateBox is *not* used for (e.g., not the sole basis for clinical, credit, or legal-advice decisions).

### A.10 — Third-party and customer relationships (2)

**A.10.2 Allocating responsibilities** (suppliers and partners) — Due diligence on model providers, contractual AI requirements, ongoing oversight, model-card review.

**A.10.3 Suppliers** | **A.10.4 Customers** — Supplier obligations + customer-facing obligations (intended use, prohibited use, oversight expectations, change notifications, EULA/MSA AI clauses).

(Some references count 38, others 39, others 42; ISO Annex A is the authoritative count. PrivateBox's SoA must reflect the published count and numbering. Number mismatch in market literature is a known issue `[Expert]`.)

### Annex A — On-prem-specific summary (per-control distinctions)

For every control above, the on-prem architecture pattern follows this discipline:
- **Risk reduced by on-prem**: Data egress, multi-tenant leakage, jurisdictional data transfer, third-party prompt logging.
- **AIMS duty that remains**: Policy, governance, impact assessment, lifecycle, supplier governance (model providers), transparency, oversight design, incident handling, continual improvement.
- **PrivateBox must implement**: Everything in Tables 1–5 (its AIMS is for *its product and operations*).
- **Customer-owned**: Data, environment-level access control, deployment-time decisions, end-user training, customer-side AISIA for *their* use cases.
- **Shared responsibility**: Update delivery, telemetry boundaries, support access, incident detection, RAG corpus design assistance.
- **Evidence proving the distinction**: Contractual responsibility matrix; technical-architecture diagram with trust boundaries; telemetry data-dictionary; support-access logs; SoC/SOC-2-style attestation language.

---

## 6. TABLE 3 — Evidence Pack Matrix (top artefacts)

For each artefact: clause/control link · what good looks like · minimum acceptable v1 · example contents · owner · cadence · auditor test · customer test · weaknesses · external-safe claim.

| Artefact | Linked to | Owner | Cadence | "Good" looks like | Common weaknesses | Safe claim |
|---|---|---|---|---|---|---|
| **AIMS Scope Statement** | 4.3 | Top mgmt | Annual + on change | 1 page; explicit role; explicit exclusions; matches certificate boundary | Scope drift; vague | "AIMS aligned to ISO/IEC 42001 with documented scope" |
| **AI Policy** | 5.2 / A.2.2 | AI Gov Lead | Annual | Principles, scope, prohibited uses, exceptions, owner, version | Boilerplate; not communicated | "Documented AI policy approved by top management" |
| **Governance Charter / RACI** | 5.3 / A.3.2 | AI Gov Lead | Annual | Named roles, AI Governance Committee TOR, escalation path | Single-person ownership | "Cross-functional AI governance" |
| **AI Risk Methodology** | 6.1.2 | Risk Lead | Annual | Criteria, scoring, treatment options, integration with InfoSec/Privacy risk | Reuse of generic InfoSec method | "AI-specific risk methodology consistent with ISO 42001 / 23894" |
| **AI Risk Register** | 6.1.2 / 8.2 | Risk Lead | Quarterly | Per-system; sources include Annex C; treatments traceable to SoA | Static; no link to controls | (Internal only — don't publish) |
| **AISIA Methodology** | 6.1.4 / A.5.2 | AI Gov Lead | Annual | 10 elements per 42005; thresholds; templates (42005 Annex E) | Hand-wave; one-size-fits-all | "AISIA methodology aligned with ISO/IEC 42005:2025" |
| **AISIA Records (per system)** | 6.1.4 / A.5.3 | Product owner | Pre-deployment + on change + scheduled | Foreseeable misuse covered; harms/benefits taxonomy used | No misuse coverage | (Share extracts under NDA) |
| **Model / AI System Inventory** | A.4 | AI Gov Lead | Continuous | Every model, version, dataset, owner, status, deployment locations | Spreadsheet drift | "Maintained inventory of in-scope AI systems" |
| **Intended-use & Prohibited-use Register** | A.8.5, A.9.4 | Product | Per release | Sector-specific; disclosed to customers | Marketing-driven, not engineering-driven | "Documented intended and prohibited uses" |
| **Data Provenance / Datasheets** | A.4.3, A.7.3 | Data Steward | Per dataset | Provenance, rights, demographics, labelling, prior handling | Missing for older datasets | "Datasheets for development data" |
| **V&V / Robustness Records** | A.6.1.5, A.6.2.2 | ML Eng | Per release | Adversarial, edge, drift, fairness, security tests | Functional only | "Pre-release V&V against documented criteria" |
| **Lifecycle SOP** | A.6 | Eng Lead | Annual | Cradle-to-grave; integrates NIST SSDF / 800-218A | Missing decommission | "AI lifecycle aligned to ISO 42001 A.6 and NIST SP 800-218A" |
| **Deployment Approval Record (gate)** | A.6.2.5 | Change Board | Per deploy | Checklist with all preconditions ticked + signatures | Verbal sign-off | "Documented pre-deployment approval gate" |
| **Monitoring / Incident SOP** | A.8.4, 9.1, 10.2 | Ops Lead | Annual | KPI list; thresholds; runbooks; notification timelines | No thresholds | "Continuous monitoring and incident handling consistent with ISO 42001" |
| **Nonconformity / CAPA Log** | 10.2 | QA | Continuous | Each NC: cause, action, effectiveness review, closure date | Open forever | (Internal) |
| **Supplier / Model Vendor Reviews** | A.10.2 | Procurement + Risk | Per onboarding + annual | Model card review; bias/safety eval; licence compliance; contractual AI clauses | None for open-weight models | "Documented supplier and model-vendor due diligence" |
| **Third-Party Model Approval Record** | A.10.2 / A.6 | Risk Lead | Per model | Eval results, accepted residual risks, approver | Pulled-from-Hugging-Face syndrome | (Internal) |
| **RAG / Data-Ingestion Controls Doc** | A.7 | Data Steward | Annual | Source vetting, quality gates, sensitive-data handling, customer-facing config | Implicit only | "Documented RAG governance controls" |
| **Human Oversight SOP** | A.6.2.3 | Product | Annual | Override authority, monitoring, escalation | Rubber-stamp | "Genuine human oversight per A.6.2.3" |
| **Transparency / User Information Pack** | A.8 | Product Marketing under Legal review | Per release | Capabilities, limitations, conditions of non-use, change log | Sales-driven inflation | "Customer-facing transparency documentation" |
| **Audit Logging Standard** | A.6.2.4 | Eng | Annual | Schema, retention, integrity, customer-controlled | Logs in customer env without spec | "Auditable event-logging standard" |
| **Internal Audit Programme + Reports** | 9.2 | Internal Audit | At least annual | Independent of AIMS team; tracked findings | Same team auditing itself | "Independent internal audit programme" |
| **Management Review Records** | 9.3 | Top mgmt | At least annual | All required inputs/outputs documented | Lunch meeting only | "Documented management review of the AIMS" |
| **SoA** | 6.1.3 | AI Gov Lead | At least annual | Every Annex A control with applicability + justification + status + evidence pointer | Empty justifications | "Documented Statement of Applicability" |
| **Trust-Pack Language Guide** | A.8 + this pack §17,18 | Comms + Legal | Quarterly | Pre-approved phrasing; red-flag list | Marketing freelances | (Internal control) |

---

## 7. TABLE 4 — AI Role / Shared Responsibility Matrix for PrivateBox

| Scenario | PB role | Customer role | Why | Clause/Annex | Contract term | Operational control | Evidence | Risk if misclassified | Sales-safe explanation |
|---|---|---|---|---|---|---|---|---|---|
| Pure on-prem, no remote support | Provider/Producer | Deployer + operator | Customer alone runs system | A.10.3/4 | "Customer responsible for operation, monitoring, oversight, AISIA of customer use" | Documented handover; runbook | Signed handover record | PB inherits operational liability | "PrivateBox provides; you operate — fully on your infrastructure" |
| On-prem + vendor update delivery | Provider | Deployer | PB still controls model/code supply chain | A.6 / A.10 | Update integrity, signing, change-notification, rollback | Signed updates; CHANGELOG; staged rollout | Cryptographic signing; audit logs | Hidden change management | "Updates delivered with cryptographic integrity and change notification" |
| On-prem + telemetry | Shared | Shared | Telemetry crosses trust boundary | A.6.2.4, A.7.5, A.8 | Data dictionary; opt-in/out; PII-free guarantee; jurisdiction | Field-level data dictionary; telemetry policy | Telemetry sampling logs | Hidden personal data egress (POPIA/GDPR risk) | "Telemetry is opt-in, scoped to operational metadata only, never customer content" |
| On-prem + support access | Shared | Customer-owned data | Engineer access creates risk | A.6.2.3, A.10 | Just-in-time access, customer approval per session, full session recording | Bastion logs; ticketing audit | Session recording; access reviews | Insider data exposure | "Just-in-time, customer-approved, fully logged support access" |
| Managed deployment support | Shared | Deployer | PB hands-on during install | A.6.2.5 | Scope, time-box, data-handling rules | Engagement record; scope statement | Sign-off | PB perceived as joint controller | "Time-boxed deployment support under defined scope" |
| Troubleshooting with customer data | Conditional / Avoid | Customer | Customer data viewing must be exception | A.7.5, A.10 | Default no; explicit case-by-case approval; data minimisation | Authorisation record; data-handling protocol | Per-incident approvals | Privacy / privilege breach (legal: confidentiality) | "Customer-data access only with explicit, case-by-case customer authorisation" |
| Document ingestion / RAG setup support | Shared | Customer | PB helps shape corpus, customer owns content | A.7 | Customer attests rights and PII handling; PB provides controls | Ingestion guidance; integrity/quality checks | RAG config baseline | Copyright / privilege issues | "We help configure RAG; you own the corpus and its rights" |
| Backup support | Shared | Customer | Backups carry data | A.7.5, ISO 27001 A.8.13 | Encryption, location, retention, customer-key | KMS/HSM evidence | Backup configs | Cross-jurisdictional storage | "Encrypted, customer-keyed backups in customer-controlled location" |
| Integration / connector support | Shared | Customer | Connector security is shared | A.10 | Connector security baseline; least-privilege | Connector inventory; perm matrix | Pen-test evidence | Excess privilege | "Least-privilege connectors with documented permission scope" |
| Hosted update repository / model package distribution | Provider | Customer pulls | PB serves software supply chain | A.10.2, NIST SSDF | SBOM, signing, vulnerability disclosure, SLSA-equivalent | SBOM; signature manifests | Supply-chain attestation | Tampering, dependency risk | "Signed updates with SBOM and vulnerability disclosure" |
| Customer fine-tuning / adaptation | Customer | Customer | Customer changes model behaviour | A.6, A.10.4 | Customer responsibility; PB provides safe-tuning guidance and guardrails | Tuning guide; safe defaults | Post-tune eval template | PB blamed for customer-induced bias | "Fine-tuning is customer-owned; we provide guardrails and guidance" |
| Customer use of third-party models within PB | Shared | Customer chooses | PB hosts integration, customer chooses model | A.10.2 | Approved-models list; model addition workflow | Model approval log | SOA evidence | Unsanctioned models | "Customers may add approved third-party models under documented governance" |

---

## 8. TABLE 5 — AI Risk, Impact Assessment, and Lifecycle Matrix (42001 + 42005)

| Stage | Reference | PB interpretation | Control objective | Checklist (key) | Evidence | Shared responsibility | Pitfalls |
|---|---|---|---|---|---|---|---|
| Ideation / justification | 4.1, 6.2 | Use-case justified, sector legal scan | "Should we build/serve this?" | Business case; sector legal review (POPIA/EU AI Act tiers/HIPAA-equiv) | Memo + approval | PB-led | "Solutionism" |
| Requirements / specification | A.6.1.1 | Translate policy + risk into specs | Engineering objectives derived from policy | Requirements doc with non-functional governance reqs | Spec | PB | Missing fairness/robustness reqs |
| Design | A.6.1.2 | Privacy/safety/fairness by design | Design that supports controls | Design doc; threat model; human oversight design | Design doc + sign-off | PB | Retro-fitting |
| Development | A.6.1.3, NIST SP 800-218A | Secure SDLC + AI specifics | Auditable build pipeline | SBOM; signed builds; secrets mgmt; AI-specific tasks | SDLC evidence | PB | "Just like normal code" |
| Training / tuning | A.4.3, A.6.1.4 | PB-side training; customer-side tuning separately | Provenance + bias controls | Datasheets; bias eval; reproducible runs | Training records | PB primary; customer for fine-tune | Black-box training |
| Testing / V&V | A.6.1.5, A.6.2.2 | Functional + adversarial + drift + fairness | Risk-proportionate test depth | Test plan; results; sign-off | Test reports | PB | Functional only |
| Deployment | A.6.2.5 | Pre-deployment gate | Verify all preconditions | Deployment checklist; AISIA signed; oversight in place | Approval record | Shared (PB ships, customer accepts) | Deploying without AISIA |
| Operation | A.6.2.1, A.9 | Customer operates within intended use | Operate within envelope | Ops manual; intended-use docs | Customer ops logs | Customer | Drift outside envelope |
| Monitoring | A.6.2.4, 9.1 | Continuous performance + drift + bias | Detect/respond | KPI dashboard; drift detectors; thresholds | Monitoring reports | Shared (telemetry boundary) | Lagging detection |
| Incident handling | 10.2, A.8.4 | Detect, classify, contain, notify, learn | Timely structured response | IR plan; severity tiers; notification timelines (15-day EU AI Act serious-incident) | IR records | Shared | Late notification |
| Change management | 6.3, A.6 | All material AI changes go through CR | Controlled change | CR templates; AISIA refresh; rollback plan | CR records | PB primary | Silent retrains |
| Retraining / update | A.6 + 42005 §6.x | Re-AISIA, re-test | Maintain assurance | Trigger criteria; re-eval | Updated AISIA + test records | PB primary | "Just an update" |
| Retirement / decommissioning | A.6, NIST AI RMF Govern 1.7 | Safe phase-out | No residual harm | Sunset plan; data disposal; customer migration | Sunset records | Shared | Forgotten systems |
| Support access | A.10 | Just-in-time, recorded | Auditable assistance | Access workflow | Session logs | Shared | Standing access |
| Telemetry | A.7.5 | Bounded operational metadata | No content egress | Data dictionary; opt-in | Sampling proof | Shared | Hidden payloads |
| RAG / KB ops | A.7 | Customer-owned content; PB-provided controls | Quality + provenance + rights | Ingestion SOP | Ingestion logs | Shared | Garbage corpus |
| Third-party model/data acquisition | A.10.2 | Approved-list discipline | Supplier-quality assurance | Vendor due-diligence pack | Approval records | PB | Pull-from-internet |
| Impact assessment (42005) | 6.1.4, A.5 | 10-element process | Assess intended + foreseeable misuse | AISIA template; harm/benefit taxonomy | AISIA records | PB primary; customer for own use cases | Generic |
| Risk reassessment | 8.2 | Periodic + on change | Live risk picture | Risk register cadence | Updated register | PB | Annual-only |

---

## 9. TABLE 6 — Annex C Objectives / Risk Sources Matrix `[42001-Annex C, informative]`

(Annex C is informative; PrivateBox's risk methodology must consider these but adapt to context.)

| Objective / risk source | Why it matters for PB | Example PB scenario | Control objective | Evidence | Monitoring | Pitfalls | Cross-link |
|---|---|---|---|---|---|---|---|
| **Accountability** (C.2.1) | Confidential firms expect named accountability | Legal AI gives wrong precedent → who is responsible | Clear RACI; logged decisions | Charter; logs | Quarterly review | Diffused accountability | A.3.2, A.6.2.3 |
| **AI expertise** (C.2.2) | PB must demonstrate competence | Healthcare AI without clinical input | Skill matrix; SME engagement | Competence records | Annual review | "Pure tech team" | 7.2, A.4.6 |
| **Availability/quality of training data** (C.2.3) | Sector-skewed data → bias | Finance dataset under-representing SMEs | Datasheets; quality gates | Datasheets | Per dataset | Convenience sampling | A.4.3, A.7.4 |
| **Environmental impact** (C.2.4) | GPU-heavy on-prem | Inference energy in healthcare | Efficiency metrics; Right-sizing guidance | Energy estimates | Annual | Ignored | A.4.5 |
| **Fairness** (C.2.5) | Sector-critical (hiring, credit, health) | Biased hiring AI for HR sector | Bias methodology; pre-prod gates | Bias reports | Per release + drift | Awareness ≠ method | A.6.1.4 |
| **Maintainability** (C.2.6) | Long deployments on customer hardware | Stale on-prem install | Patch policy; lifecycle commitments | Patch logs | Continuous | Abandonware | A.6 |
| **Privacy** (C.2.7) | POPIA, GDPR, sector | Health data in RAG | Default no PII; minimisation; encryption | DPIA; PIA | Per change | Conflating with InfoSec | A.7.5 |
| **Robustness** (C.2.8) | Adversarial / prompt injection | Legal AI attacked through doc | Adversarial testing | Red-team reports | Per release | Functional-only tests | A.6.1.5 |
| **Safety** (C.2.9) | Healthcare especially | Clinical decision misuse | Intended-use enforcement; oversight | Safety case | Continuous | Rubber-stamp oversight | A.6.2.3, A.9.4 |
| **Security** (C.2.10) | Confidential firms baseline | Model file theft | Integration with ISO 27001 controls | Sec architecture | Continuous | Gap with ISMS | ISO 27001 |
| **Transparency / explainability** (C.2.11) | EU AI Act + King V | Black-box credit decision | Explainability appropriate to risk | XAI artefacts | Per release | One-size XAI | A.8 |
| **Risk source: Lack of human oversight** (C.3.x) | Cross-sector | Auto-finalised legal answer | Human-in-loop default | Oversight design | Sampling | Cosmetic oversight | A.6.2.3 |
| **Risk source: System-life-cycle flaws** (C.3.x) | Long on-prem life | Forgotten model | Lifecycle SOP | Lifecycle records | Annual | None | A.6 |
| **Risk source: ML-specific (data quality, bias, drift)** (C.3.4) | Drift in customer environment | RAG corpus stale | Drift detectors | Drift telemetry | Continuous | No drift KPI | A.6.1.4, A.7.4 |
| **Risk source: Complexity of environment** (C.3.x) | Customer integrations | Connector misconfig | Least-privilege | Connector audit | Per release | Over-broad creds | A.10 |
| **Risk source: Automation / autonomy level** (C.3.x) | Sector-dependent | Auto-execution in finance | Autonomy controls + kill-switch | Design + tests | Per release | Hidden auto behaviour | A.6.2.3 |
| **Risk source: Foreseeable misuse** (C.3.x) | Compulsory in 42005 | Legal AI for unauthorised practice | Misuse list per AISIA | AISIA | Per release | Intent-only thinking | A.5, 42005 |

---

## 10. TABLE 7 — External Claims / Trust Pack / Sales Language (brutally honest)

| Topic | Safe to say | Do NOT say | Why | Evidence required | Website wording | Procurement wording | Security-pack wording |
|---|---|---|---|---|---|---|---|
| ISO 42001 status (pre-cert) | "Designed in alignment with ISO/IEC 42001:2023" | "ISO 42001 certified" / "ISO 42001 compliant" | Certification requires accredited body audit | AIMS scope, SoA, control evidence | "PrivateBox is designed in alignment with ISO/IEC 42001:2023 and is preparing for accredited certification" | "AIMS architecture aligned to ISO/IEC 42001; certification roadmap available under NDA" | "AIMS aligned to ISO/IEC 42001; full SoA and control evidence available under NDA" |
| ISO 42005 | "Impact-assessment methodology aligned with ISO/IEC 42005:2025" | "ISO 42005 certified" (it's not a certification standard) | 42005 is guidance | AISIA methodology + records | "We perform AI System Impact Assessments aligned with ISO/IEC 42005:2025" | Same | Same + sample AISIA template |
| ISO 42006 | "Audit-readiness benchmarked to ISO/IEC 42006:2025 expectations" | "We meet ISO 42006" | 42006 is for *certification bodies*, not orgs | Audit-readiness tracker | "Our certification preparation is benchmarked to the auditor expectations in ISO/IEC 42006:2025" | Same | Same |
| Responsible AI | "We implement responsible-AI controls and document them" | "Guaranteed responsible AI" | No such guarantee exists | Policy + controls + AISIA | "Responsible-AI principles are operationalised through documented controls" | Same | Same |
| Data residency / on-prem | "Customer data does not leave the customer environment by default" | "Your data never leaves" (without telemetry caveat) | Telemetry, support access can move metadata | Telemetry data dictionary; access controls | "By default, customer data remains within your environment; metadata telemetry is opt-in and PII-free" | Same + telemetry dictionary | Full data-flow diagram |
| Bias-free | "We assess and address bias according to documented methodology" | "Bias-free AI" | Impossible | Bias methodology + reports | "Bias is assessed pre-release and during operation against documented criteria" | Same | Bias methodology + sample report |
| Hallucination / accuracy | "Hallucination controls (RAG grounding, citations, guardrails) reduce risk; outputs require human review for consequential decisions" | "Hallucination-free" / "100% accurate" | Untrue | Eval results | "Outputs of consequential queries should be reviewed by qualified humans" | Same | Eval methodology |
| EU AI Act | "Designed to support customer compliance with EU AI Act obligations" | "EU AI Act compliant" | Compliance is system + deployer specific | Mapping doc | "PrivateBox is designed to support customer compliance with applicable EU AI Act obligations" | Mapping table | Same |
| POPIA | "Designed to support customer POPIA obligations including s.71 automated decision-making safeguards" | "POPIA compliant" | Customer is the responsible party (controller equivalent) | Mapping doc | Same | Same | Same |
| King V | "Designed to support board-level AI oversight per King V" | "King V compliant" | King V applies to the *organisation/board*, not a product | Mapping doc | Same | Same | Same |
| HIPAA / financial regs | "Suitable for use in HIPAA / FCA / SEC / JSE-regulated environments when deployed under customer governance" | "HIPAA certified" (no such thing) | HIPAA has no certification | Reference architecture | Same | Same + ref arch | Same |
| ISO 27001/27701 | Use only the certificates you actually hold (or "in progress"); state scope | "All ISO certified" | Misrepresentation | Actual certificates | "PrivateBox holds [list]; pursuing [list]" | Same | Certificates attached |

---

## 11. TABLE 8 — Crosswalk: ISO 42001 × ISO 27001 × ISO 27701 × NIST AI RMF × EU AI Act × POPIA × King V

| 42001 ref | Theme | ISO 27001 link | ISO 27701 link | NIST AI RMF link | EU AI Act link | POPIA link | King V link | Shared artefact | Why for PB |
|---|---|---|---|---|---|---|---|---|---|
| 4 (Context) | Org context | 4 | 5 | GOVERN 1 | Art. 3 (definitions), recitals | s.4 (PoPI scope) | Principle 4 (Strategy) | Context register | Multi-jurisdictional positioning |
| 5 (Leadership) | Tone from top | 5 | 5 | GOVERN 2 | Art. 26 (deployer obligations) | Accountability principle | Principle 1 (Ethical leadership) | AI policy | Board-level accountability |
| 6.1 (Risk) | AI risk | 6.1 | 6.1 | MAP, MEASURE | Art. 9 (risk mgmt for high-risk) | s.19 (security safeguards) | Principle 4 (Risk) | Integrated risk register | One register, multiple labels |
| 6.1.4 (AISIA) | Impact assessment | 8.2 | 7.2 (PIA/DPIA) | MAP | Art. 9, Art. 27 (FRIA) | s.71 (automated decisions); DPIA equivalent | Principle 4 | AISIA + DPIA combined template | Reuse one template |
| 7 (Support) | Resources | 7 | 7 | GOVERN 3 | Art. 4 (AI literacy) | Operator training | Principle 5 (Resources) | Competence matrix | One training programme |
| 8 (Operation) | Operations | 8 | 8 | MANAGE | Art. 8–15 (high-risk obligations) | Operational safeguards | Principle 6 (Performance) | Lifecycle SOP | Single SDLC |
| 9 (Performance) | Monitoring | 9 | 9 | MEASURE | Art. 72 (post-market monitoring); Art. 73 (incidents 15-day) | Breach notification s.22 | Principle 8 (Assurance) | KPI dashboard + IR plan | Single monitoring stack |
| 10 (Improvement) | Improvement | 10 | 10 | MANAGE 4 | — | — | Principle 13 (Disclosure) | NC/CAPA log | One log |
| A.2 Policies | Policy | A.5.1 | A.5.1 | GOVERN 1 | Art. 9 risk policy | Info security policy | — | Integrated policy | Avoid policy proliferation |
| A.3 Internal org | Roles | A.5.2–5.4 | A.5.2 | GOVERN 2.1 | Art. 26.2 (designated humans) | Information Officer | Principle 1 | Charter + RACI | One charter |
| A.4 Resources / Inventory | AI inventory | A.5.9 (asset inventory) | — | GOVERN 1.6 | Art. 11 (technical doc), Art. 60 (DB registration) | — | Principle 12 (IT mgmt) | Unified inventory | Avoid asset/AI silo |
| A.5 Impact assessment | Impact | — | A.7.2 (PIA) | MAP | Art. 9, 27 | s.71 / DPIA | Principle 4 | AISIA framework | Big reuse |
| A.6 Lifecycle | SDLC | A.8.25–8.31 | — | MAP-MEASURE-MANAGE | Art. 9, 10, 13, 14, 15 | Security s.19 | Principle 12 | Unified lifecycle | Avoid duplicate SDLCs |
| A.6.1.4 Bias | Bias | — | — | MEASURE 2.11 | Art. 10 (data governance) | Fairness inferred | Principle 4 | Bias methodology | EU AI Act gap area |
| A.6.2.3 Human oversight | Oversight | — | — | MANAGE | Art. 14 (human oversight) | s.71(2) human review | Principle 12 | Oversight SOP | Critical for high-risk |
| A.6.2.4 Logs | Logging | A.8.15–8.17 | — | MEASURE 3 | Art. 12 (record-keeping) | s.14 records | Principle 8 | Logging standard | Reuse 27001 logging |
| A.7 Data | Data quality | A.5.12, A.8.10 | A.7.4 | MAP 4 | Art. 10 (data governance) | Conditions for processing s.8–25 | Principle 12 | Data governance framework | Critical privacy linkage |
| A.7.5 PII | Privacy in AI | — | A.7 (entire) | — | Art. 10.5 | s.71, ch.3 | Principle 12 | PIMS extension | Reuse 27701 |
| A.8 Information for parties | Transparency | A.5.34 | A.7.3 | MAP 3, MANAGE 4.3 | Art. 13, 50, 52 | s.18 notification | Principle 13 (Disclosure) | Transparency pack | Single disclosure pack |
| A.9 Use | Responsible use | A.5.10–11 | — | GOVERN 4 | Art. 26 (deployer), Art. 50 | Lawful processing | Principle 4 | AUP + intended-use | One AUP |
| A.10 Third party | Suppliers | A.5.19–5.23 | A.7.5 | GOVERN 6, MAP 4.1 | Art. 25 (responsibilities along value chain) | Operator obligations s.20–21 | Principle 11 (Stakeholders) | Supplier programme | Single supplier register |

(Crosswalk validated against NIST official `NIST_AI_RMF_to_ISO_IEC_42001_Crosswalk.pdf` and consensus mapping work `[42001-N + NIST + EU AI Act + POPIA + King V]`. Industry estimates suggest ~70–80% operational overlap between 42001 and NIST AI RMF, and 40–50% overlap with EU AI Act high-risk obligations `[Expert: glacis.io, euaicompass.com, surecloud.com]`.)

---

## 12. TABLE 9 — ISO/IEC 42005 AI System Impact Assessment Matrix

| Area | 42005 ref | Authoritative summary | Why for PB | Trigger | Required step | Artefact | Evidence example | Lifecycle stage | Shared responsibility | Pitfalls |
|---|---|---|---|---|---|---|---|---|---|---|
| Process documentation | 5.1, 5.1.4 | Document the AISIA process incl. methodology, roles, inputs, outputs, decision flow | Auditor entry-point | Always | Maintain methodology doc | AISIA Methodology v1 | Versioned PDF | All | PB defines, customer adapts | One-size-fits-all |
| Integration with mgmt system | 5.x, Annex A | Embed AISIA in AIMS / risk mgmt; reuse 42001 inputs | Avoid duplicate work | Always | Cross-references in methodology | Annex A mapping in methodology | Mapping table | All | PB | Standalone document |
| Timing & scope | 6.x | When to do it, what to cover | Sector-risk-driven | Pre-deployment + on change + scheduled | Trigger criteria | Trigger SOP | Decision log | Pre-deploy + ongoing | PB sets, customer follows | Late assessment |
| Roles & responsibilities | 6.x | Who conducts, reviews, approves, updates | Cross-functional | Per AISIA | RACI per AISIA | RACI in template | Template | All | PB primary | One-person assessment |
| Thresholds | 6.x | Risk levels, sensitivity, deployment context that mandate AISIA | Sector-specific | Always | Threshold table | Threshold SOP | Documented thresholds | Pre-deploy | PB | No thresholds |
| Conduct of assessment | 6.5–6.7 | Identify intended uses, foreseeable applications, affected parties | Compulsory | Per system | Use the template | Per-system AISIA | Completed AISIA | Pre-deploy + on change | PB primary; customer for their use cases | Intended-use only |
| Actual & foreseeable impacts | 6.8 (with sub-clauses 6.8.1–6.8.3 inc. failures and reasonably foreseeable misuse) | Benefits, harms, AI-system failures, reasonably foreseeable misuse | Sector-critical | Per AISIA | Harm/benefit taxonomy (Annex C) | Taxonomy applied | Filled taxonomy | Pre-deploy | PB | Misuse omitted |
| Measures to address | 6.9 | Mitigations and acceptances | Per AISIA | Mitigation register | Linked to A.x controls | Treatment plan | Pre-deploy | PB | Vague mitigations |
| Recording & reporting | 5.x | Document outcomes; transparent format | Audit trail | Per AISIA | Standard report | AISIA report | Signed report | Pre-deploy | PB | Inaccessible records |
| Approval | 6.x | Formal decision authority | Sign-off control | Per AISIA | Approval workflow | Approval matrix | Signature record | Pre-deploy | PB | Verbal approval |
| Monitoring & review | 6.x | Update as systems / context evolve | Long deployments | Per cadence + on change | Review cadence | Review log | Updated AISIA | Operational + change | Shared | Static AISIA |
| Use of harm/benefit taxonomy | Annex C | Accountability, transparency, fairness, reliability, security, privacy, environmental | Comprehensive | Per AISIA | Apply taxonomy | Annex C checklist | Filled checklist | Pre-deploy | PB | Selective use |
| Template use | Annex E | Provided template | Speeds adoption | Per AISIA | Use Annex-E-style template | PB AISIA template | Per-system AISIA | Pre-deploy | PB | Reinventing template |

`[42005-G; SAP community; ISACA atisaca v15; CMS LawNow]`

---

## 13. TABLE 10 — ISO/IEC 42006 Certification-Readiness / Auditor-Expectation Matrix

| Theme | 42006 ref | Why certifiers care | What PB should have ready | Evidence quality | Likely audit test | Common weakness | Remediation priority | Safe wording |
|---|---|---|---|---|---|---|---|---|
| Auditor knowledge of *all* Annex A controls | 7.1.3.x | Audit team must collectively cover Annex A | Map every Annex A control to evidence + owner | Pre-mapped evidence library | Sampling across all controls | Some controls evidenceless | High | "We can produce evidence for every Annex A control in scope" |
| Audit-time calculation | 9.1.x | CB must size the audit accurately based on scope, locations, AI complexity | Crisp scope statement; system count; data-domain count | Stable scope | Scope vs reality reconciliation | Scope creep | High | "Stable, narrowly defined AIMS scope" |
| Initial certification audit (Stage 1 + Stage 2) | 9.x | Stage 1 = doc/design review; Stage 2 = effectiveness | Stage-1-ready doc set + Stage-2 evidence pack | All Section 6 artefacts | Document review then onsite/remote interviews and sampling | Stage 1 NCs found in Stage 2 | High | "Audit-ready against Stage 1 and Stage 2 expectations" |
| Surveillance audits | 9.x | Annual partial audits | Continuous evidence; sampling fairness | Evergreen evidence | Sampling | Stale evidence | Medium | "Continuous-evidence model for surveillance readiness" |
| Re-certification | 9.x | Every 3 years | Retrospective trail | All cycles preserved | Full re-audit | Lost history | Medium | "3-year evidence retention discipline" |
| Auditor competence (≥4 yr IT/data protection, ≥2 yr AI; 3-day AIMS training) | 7.2.x | Auditors must demonstrate AI competence | Be ready to be tested by qualified auditors | n/a | Q&A depth | n/a | n/a | "We engage accredited certification bodies whose auditors meet ISO/IEC 42006 competence requirements" |
| Impartiality | 5.x | CBs must be impartial | Choose CB without conflicts (e.g., consulted you on implementation = conflict) | CB selection record | n/a | Same firm did consulting AND audit | High | "We separate implementation advisory from certification audit" |
| Incident-traceability competence | 7.x | CB team must trace incident → AIMS element | Robust IR + audit trail | Linked logs | Walk-through of an example incident | Logs that don't link | High | "Traceable incident-to-AIMS audit trail" |
| Certification decision | 9.x | Reviewer must be independent of audit team | n/a (CB-side) | n/a | n/a | n/a | n/a | n/a |
| Witness audit (accreditation body observes CB) | (related) | Accreditation bodies (ANAB, UKAS) periodically observe | Be prepared for ANAB/UKAS observers; your evidence quality reflects on the CB too | Polished evidence | Live audit observed | Evidence rough on the day | Medium | "Audit-ready posture supports accredited certification body's own accreditation" |

`[42006-CB; ISO official explainer; ANAB; iteh.ai FDIS sample; A-LIGN/Synthesia witness-audit case]`

---

## 14. Case-Study / Market-Practice Analysis (10+ public examples)

| # | Org | Status | Sector | Cert body | Scope | Public artefacts | Lessons for PB | What NOT to copy |
|---|---|---|---|---|---|---|---|---|
| 1 | **Anthropic** (Jan 2025) | Accredited certification | Frontier AI | Schellman | Claude LLMs on API, Claude Enterprise, Bedrock & Vertex deployments | Public announcement; ISO certificate referenced; Responsible Scaling Policy | RSP-style escalation policy + ISO 42001 = strong external signal | Don't conflate frontier-model policy with on-prem product scope |
| 2 | **AWS** (Nov 2024) | Accredited (Schellman/ANAB) | Cloud AI | Schellman | Bedrock, Q Business, Textract, Transcribe | FAQ page, certificate | Service-by-service scope = honest scoping | Don't overstate scope to "AWS AI" — they didn't |
| 3 | **Google** (Dec 2024) | Accredited | Cloud AI | — | 10 products incl. Vertex AI, Gemini for Workspace | Press releases | Product-scoped certs are credible | Same |
| 4 | **Microsoft 365 Copilot** (Mar 2025) and **Azure AI Foundry + Security Copilot** (later) | Accredited | Productivity / Security AI | Mastermind (IAS-accredited) for Foundry/Copilot; per-product CBs | Specific Copilot products | Service Trust Portal certificates and reports; public RAI Standard, Responsible AI Transparency Report; EY case study | Public Trust Portal model; tie to Responsible AI Standard; impact assessments at engineering level | Don't claim "Microsoft is ISO 42001 certified" — *specific products* are |
| 5 | **IBM** (Sep 2025) | Accredited | Foundation models / Granite | — | Granite-related AIMS | Product launch tying ISO 42001 to model release | ISO 42001 narrative tied to flagship product launch | n/a |
| 6 | **Workday** (Jun 2025) | Accredited (Schellman) + NIST AI RMF attestation | HR/Finance enterprise SaaS | Schellman | Workday products | Public consolidated ISO 42001 report on workday.com/trust | Trust Centre with downloadable consolidated report = procurement gold | Don't promise more than the report covers |
| 7 | **Cognizant** (Dec 2024) | First IT services firm certified | IT services | DNV | AI management system | Press release | Cross-functional change mgmt described publicly | Don't replicate Big-IT scope to a product-scope certification |
| 8 | **Synthesia** (Sep 2024 unaccredited → accredited via A-LIGN) | First AI video co. | AI video | A-LIGN | AI video platform | Detailed blog "Our journey..."; A-LIGN witness-audit detail (18 days Stage 2, ANAB observer) | Honest documentation of the *process* (incl. unaccredited→accredited transition) builds trust | Don't claim accredited status while unaccredited |
| 9 | **KPMG Australia** | First org globally cert'd (BSI) | Advisory | BSI | Advisory practice scope | Press / CIO Influence | Accredited consulting org adds credibility | Don't replicate consulting scope to product scope |
| 10 | **Zendesk** (Sep 2025) | Accredited | Customer support AI | — | "Entire AI core" with named exclusions | Press | Honest exclusion of recently-acquired products | Excluding products is fine if disclosed |
| 11 | **Cohere** (Jun 2025) | Accredited | Foundation models | — | Cohere AI | Public | Foundation-model maker example | n/a |
| 12 | **OneAdvanced** | Accredited | Sector SaaS (esp. legal/professional) | — | AI-powered SaaS portfolio incl. sovereign AI | Press | "Sovereign AI" + ISO 42001 messaging is close to PB's narrative | Don't claim "sovereign" without architectural backup |
| 13 | **Integral Ad Science / Quality Attention** | Accredited | AdTech | — | Quality Attention product | — | Single-product scope, narrow and defensible | n/a |
| 14 | **Changi Airport Group** (Feb 2025, SGS) | Accredited | Public infrastructure | SGS | AI use across airport | Press | Operator (deployer) scope, not provider | Different role from PB |
| 15 | **Microsoft × EY case study** | Public methodology | Big productivity AI | n/a | Methodology | EY case study describing structured impact assessment at engineering level | Translate policy into engineering-applicable impact assessment | Don't underestimate cost (not a doc exercise) |

**Common lessons for PB**:
1. **Narrow, named-product scope** beats broad organisational scope.
2. **Trust-Centre-style** public documentation (Workday, Microsoft Service Trust Portal) is the dominant procurement-friendly pattern.
3. **CB selection matters**: Schellman, A-LIGN, BSI, DNV, SGS, Mastermind/IAS are visible accredited bodies; PB's choice is partly geographic (UK, EU, ZA, US presence).
4. **Tie ISO 42001 to a public Responsible-AI policy** (Anthropic RSP, Microsoft RAI Standard).
5. **Be honest about transitions** (Synthesia's unaccredited → accredited story improved trust, didn't damage it).

**What NOT to copy**:
- Overbroad scope claims;
- Generic press releases without certificate excerpts/scope statements;
- Conflating product certification with organisational certification;
- Treating ISO 42001 as a substitute for EU AI Act or POPIA compliance (it is not).

---

## 15. Top 30 Evidence Artefacts PrivateBox Should Prepare First (priority order)

1. AIMS Scope Statement (1 page; product-scoped)
2. AI Policy (top-management approved)
3. AI Governance Charter + RACI
4. Statement of Applicability (SoA) — every Annex A control
5. AI Risk Methodology + AI Risk Register
6. AI System Impact Assessment Methodology aligned with ISO/IEC 42005:2025 (incl. harm/benefit taxonomy and template)
7. AI System Inventory (with versions, datasets, owners, status)
8. Intended-use / Prohibited-use Register (sector-specific)
9. Data Provenance / Datasheets (training, eval, evaluation harnesses)
10. Bias Assessment Methodology + latest reports
11. V&V / Robustness / Adversarial Test Plan + reports
12. AI Lifecycle SOP (cradle-to-grave; integrates NIST SP 800-218A)
13. Pre-Deployment Approval Gate Checklist + record template
14. Human Oversight SOP (with override authority and concern-channel)
15. AI Event-Logging Standard (schema + retention + integrity)
16. Monitoring & KPI Dashboard Specification
17. Incident Response Plan (including 15-day serious-incident workflow for EU AI Act + 72-hour POPIA breach pathway)
18. Nonconformity / CAPA Log
19. Supplier / Model-Vendor Due-Diligence Pack (incl. for open-weight models)
20. Approved-Models List with approval workflow
21. RAG / Data-Ingestion Controls SOP (rights, quality, sensitive-data handling)
22. Transparency / User Information Pack (per release, customer-facing)
23. Customer Shared-Responsibility Matrix (Table 4 productised)
24. Telemetry Data Dictionary + Default-Off / Opt-In statement
25. Support-Access SOP (just-in-time, recorded, customer-approved)
26. Update-Delivery Standard (signing, SBOM, change-notification)
27. Internal Audit Programme + first-year report
28. Management Review Pack (inputs/outputs template + first review minutes)
29. Crosswalk Pack (ISO 42001 × 27001 × 27701 × NIST AI RMF × EU AI Act × POPIA × King V)
30. External-Claims & Trust-Pack Language Guide (Table 7 productised)

---

## 16. Priority Implementation Roadmap — Now / Next / Later

**NOW (0–3 months) — Establish governance baseline**
- A.2 + A.3 controls: AI Policy, alignment, review cycle, roles, concern-reporting
- AIMS scope statement signed
- AI Governance Lead and Committee stood up
- AI risk methodology published
- AI System Inventory v0
- Initial SoA draft (every Annex A control)
- AI Policy alignment with existing ISMS (ISO 27001) and PIMS (ISO 27701)
- POPIA s.71 + EU AI Act tiering quick-screen for current PB use cases

**NEXT (3–9 months) — Build operational AIMS**
- Full A.4–A.7 build (resources, AISIA process aligned to 42005, lifecycle, data)
- AISIA performed for *every* in-scope AI feature
- A.8 transparency pack v1
- A.9 responsible-use processes
- A.10 supplier programme + approved-models list
- Internal audit programme launch
- Monitoring/incident SOPs operational
- Trust Centre v1 (public)
- Customer Shared-Responsibility Matrix in MSA

**LATER (9–18 months) — Certification readiness and scale**
- Stage 1 readiness review (with implementation partner separate from chosen CB)
- Stage 1 audit → Stage 2 audit by accredited body (Schellman / BSI / DNV / A-LIGN / TÜV / SGS as appropriate to geography)
- Annual surveillance plan
- Sector-specific extensions (healthcare safety case templates, finance fairness reports, legal privilege handling)
- Multi-jurisdictional crosswalk extensions (POPIA, EU AI Act high-risk, UK regulator-specific guidance, US sectoral)
- Continuous-evidence automation (GRC tooling, e.g., Drata/Vanta/Sprinto/ISMS.online — *as evidence aggregators only, not as compliance substitutes*)

**Benchmarks that should *change* the roadmap**
- A customer in healthcare/finance/legal demands certification before procurement → accelerate to "Now" on Stage 1.
- EU AI Act enforcement date for high-risk systems (Aug 2026) creates a hard deadline for any high-risk PB use case.
- A regulatory change in ZA (e.g., a finalised SA AI Act) changes context (Clause 4) and forces SoA review.
- PB onboards a new third-party model (e.g., a frontier model with terms restricting on-prem) → A.10.2 supplier review cycle triggered.
- A serious incident (EU AI Act Art. 73) → triggers re-AISIA and management review.

---

## 17. External-Safe Messaging Examples

**Website (homepage one-liner)**
> *"PrivateBox is an on-premises, single-tenant AI platform for confidential firms. Designed in alignment with ISO/IEC 42001:2023, with an AI System Impact Assessment methodology aligned with ISO/IEC 42005:2025, and a certification roadmap benchmarked to ISO/IEC 42006:2025."*

**Website (trust page)**
> *"Customer data does not leave your environment by default. Telemetry is opt-in and limited to operational metadata. Support access is just-in-time, customer-approved, and fully logged. Our AI Management System is designed in alignment with ISO/IEC 42001:2023; we publish our scope statement, AI Policy summary, and Statement-of-Applicability summary in our Trust Centre. Detailed control evidence is available under NDA."*

**Procurement response (boilerplate)**
> *"PrivateBox operates an AI Management System (AIMS) architected to ISO/IEC 42001:2023. We can provide: (1) AIMS scope statement, (2) AI Policy, (3) Statement of Applicability covering Annex A controls, (4) AI System Impact Assessment methodology aligned with ISO/IEC 42005:2025, (5) representative AISIA for the use case under evaluation, (6) Shared-Responsibility Matrix, and (7) crosswalks to ISO 27001, ISO 27701, NIST AI RMF, EU AI Act, POPIA, and King V. Accredited ISO/IEC 42001 certification is on our roadmap; we do not currently claim certified status."*

**Security pack (executive summary line)**
> *"AIMS designed in alignment with ISO/IEC 42001:2023. ISO 27001 and ISO 27701 alignment in parallel. Accredited certification for ISO/IEC 42001 is in progress, benchmarked to ISO/IEC 42006:2025 audit-readiness expectations."*

**Board narrative (CEO talking points)**
> *"On governance: PrivateBox runs a documented AIMS with named accountability at executive level, an AI Policy, a risk register, impact assessments per system, a Statement of Applicability covering all 38 Annex A controls of ISO/IEC 42001, and a 12–18 month roadmap to accredited certification. On architecture: on-premises by default — sensitive data does not leave customer environments. On regulation: our crosswalk shows substantive coverage of NIST AI RMF, the EU AI Act, POPIA, and the new King V code, with explicit gaps and treatments. On honesty: we do not claim certification we have not earned, nor compliance we cannot evidence."*

---

## 18. Red-Flag Claim List (NEVER make)

1. ❌ "ISO 42001 certified" (until accredited certificate is in hand and within scope)
2. ❌ "Fully compliant with ISO/IEC 42001"
3. ❌ "Guaranteed responsible AI"
4. ❌ "Bias-free / hallucination-free / 100% accurate"
5. ❌ "Your data never leaves" (without telemetry/support-access caveat)
6. ❌ "EU AI Act compliant" / "POPIA compliant" / "GDPR compliant" / "HIPAA certified" (none are product-level certifications; compliance is system-and-deployer specific)
7. ❌ "ISO 42005 certified" / "ISO 42006 certified" (neither is a certification standard for a product or organisation in this sense)
8. ❌ "Sovereign AI" without architectural and contractual evidence
9. ❌ "Audited by [Big Four firm]" if it was an advisory, not an attestation/certification engagement
10. ❌ Implying *the customer* is automatically compliant by using PrivateBox
11. ❌ Claiming Annex A "100% covered" without showing the SoA exclusion justifications
12. ❌ "Drop-in replacement for cloud AI" without acknowledging customer governance duties
13. ❌ "Zero-trust AI" as marketing without zero-trust architectural evidence
14. ❌ "On-prem = compliant" — explicitly false; on-prem is a control, not a governance system
15. ❌ Reusing certificates from upstream providers (e.g., "We use Llama, which is ISO certified") — none of this transfers to PrivateBox

---

## 19. Final Unified ISO AI Governance Architecture for PrivateBox

```
┌──────────────────────────────────────────────────────────────────┐
│  TOP MANAGEMENT (Clause 5 / King V Principle 1)                  │
│  CEO + Board AI accountability, AI Policy ownership, resourcing  │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  AIMS FOUNDATION (Clause 4 + 6 + 7)                              │
│  Context · Scope · Interested parties · Risks/objectives/        │
│  AISIA methodology (42005) · Resources · Competence · Awareness  │
│  Cross-mapped to ISO 27001 ISMS + ISO 27701 PIMS                 │
└──────────────────────────────────────────────────────────────────┘
        │                  │                    │
        ▼                  ▼                    ▼
┌──────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│ POLICY LAYER │ │ ANNEX A CONTROLS │ │ EVIDENCE LAYER       │
│ A.2 / A.3    │ │ A.4–A.10 (38)    │ │ Inventory · SoA ·    │
│              │ │ + 42005 AISIA    │ │ AISIA records ·      │
│              │ │ + NIST SSDF for  │ │ Datasheets · Test    │
│              │ │ build pipeline   │ │ reports · Logs ·     │
│              │ │                  │ │ NC/CAPA · Reviews    │
└──────────────┘ └──────────────────┘ └──────────────────────┘
        │                  │                    │
        ▼                  ▼                    ▼
┌──────────────────────────────────────────────────────────────────┐
│  OPERATIONAL LAYER (Clause 8)                                    │
│  Lifecycle · Change mgmt · Deployment gate · Monitoring ·        │
│  Incident response · Update delivery · Telemetry · Support       │
│  access · RAG ops · Supplier mgmt · Customer enablement docs     │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  SHARED-RESPONSIBILITY INTERFACE (Tables 4 + 7)                  │
│  Contractual matrix · Customer enablement pack · Trust Centre    │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  ASSURANCE LAYER (Clauses 9–10 + 42006-benchmarked readiness)    │
│  Internal audit · Management review · Continual improvement ·    │
│  Stage 1 / Stage 2 / Surveillance / Recertification readiness    │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  REGULATORY CROSSWALK (Table 8)                                  │
│  POPIA · King V · EU AI Act · UK · US sectoral · NIST AI RMF ·   │
│  NIST SP 800-218A · ISO 27001/27701 (one evidence library)       │
└──────────────────────────────────────────────────────────────────┘
```

**Operating principles**
1. **Single source of truth, multiple labels**: one risk register, one impact-assessment template, one evidence library — labelled to multiple frameworks.
2. **Scope discipline**: PrivateBox's AIMS scope is its product and operations; customers' AIMS scopes cover *their* use of PrivateBox.
3. **Honest claims**: aligned ≠ certified; designed for ≠ guarantees.
4. **Risk-proportionate depth**: a high-risk healthcare deployment gets deeper AISIA, more bias testing, stricter human oversight than an internal enterprise-search use case.
5. **Continuous-evidence model**: every artefact has owner, cadence, retention, and is generated as a by-product of operations rather than for an audit.
6. **Procurement-ready**: every external claim has internal evidence; every customer ask maps to a prepared artefact.
7. **Auditor-ready**: every Annex A control mapped, every exclusion justified, every NC closed, every review minuted.

---

## Caveats

1. **ISO standards are paywalled**. Exact normative wording for ISO/IEC 42001, 42005, and 42006 must be sourced from ISO directly. This pack uses authoritative summaries from ISO official explainers, NIST's published 42001 crosswalk, accredited certification bodies (Schellman, BSI, DNV, A-LIGN, SGS, TÜV), and serious implementation guides; specific clause numbers and Annex A control numbers may vary slightly across secondary sources (the most common figure is 38 controls across A.2–A.10, but some sources cite 39 or 42; PrivateBox must align its SoA to the *published* numbering).
2. **42001 is a management-system standard, not a product certification**. Even after certification, no product is "certified" in the conformance-assessment sense — only the AIMS within a defined scope is.
3. **42005 is guidance, not a certification standard**. Claims of "ISO 42005 certification" are not meaningful.
4. **42006 governs certification bodies**, not the orgs they certify. PrivateBox's audit-readiness can be *benchmarked* to 42006 expectations but PB does not "comply with" 42006.
5. **EU AI Act, POPIA, King V, NIST AI RMF, NIST SSDF/SP 800-218A** are independent obligations. ISO 42001 supports them but does not satisfy them. Estimates of overlap (e.g., ~40–50% with EU AI Act high-risk; ~70–80% with NIST AI RMF) are *industry estimates*, not authoritative legal positions.
6. **South Africa's National AI Policy Framework was provisional** and was reportedly pulled in 2026 for citation issues `[CNBC Africa]`; PB should track the official ZA policy trajectory closely. POPIA s.71 (automated decision-making) is the primary current binding constraint along with King V (effective 1 January 2026).
7. **King V** brings AI explicitly into the SA corporate governance code from financial years starting on/after 1 Jan 2026. PB's board-level talking points should reflect this.
8. **Foreseeable misuse coverage** (per ISO 42005 6.8.3) is one of the most commonly under-implemented elements; PB should treat it as a mandatory section in every AISIA, not a best-practice add-on.
9. **Some industry "ISO 42001 certified" claims are unaccredited** (notably during 2024 when accredited CBs were rare); PB must verify any peer claim's accreditation status (ANAB, UKAS, SANAS, etc.) before benchmarking against it.
10. **This pack is informational and implementation-oriented**, not legal advice. Final claim language, contractual responsibility allocation, and jurisdictional compliance positions should be reviewed by qualified legal counsel in each target jurisdiction (ZA, EU, UK, US).

— *End of architecture document.*