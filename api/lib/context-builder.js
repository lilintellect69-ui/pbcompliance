// Context builder for the compliance assistant.
//
// Builds a tier-weighted system prompt per route type, per the design brief §1
// and §3. The data.json from `make data` is the substrate — see
// docs/schema-v2.md for field definitions. This is pure read-only inference
// over the GRC graph; no LLM call happens here. The LLM is invoked downstream
// in api/chat.js with the assembled system prompt + user message.
//
// Tier weights (informally, by char count not token count):
//   home          → app 25% + cross-cutting 65% + dynamic 10%
//   framework     → app 5% + framework 70% + framework-cross-cutting 15% + dynamic 10%
//   requirement   → app 3% + framework 17% + page 65% + page-cross-cutting 5% + dynamic 10%
//   scenario      → app 3% + framework 15% + page 60% + related 12% + dynamic 10%
//   oq            → app 3% + framework 15% + page 60% + related 12% + dynamic 10%
//   graph         → app 10% + page 30% + cross-cutting 50% + dynamic 10%
//   oq-index      → app 10% + page 80% + dynamic 10%
//
// Output modes (per design brief §4) — applied as a post-build prompt-shaping
// directive at the END of the system prompt:
//   explain     — default conversational
//   procurement — emit external_safe_claim verbatim, refuse to invent
//   audit       — emphasise documented_evidence + audit_methods + cadence + failure_modes
//   crosswalk   — emphasise crosswalk graph traversal

// ─── Indices (built once at first call, cached per-module) ────────────────────

let indices = null;
let cachedDataRef = null;

function buildIndices(data) {
  if (indices && cachedDataRef === data) return indices;
  cachedDataRef = data;

  const frameworks = data.frameworks || {};
  const byId = {};
  const scenarioById = {};
  const oqById = {};
  const evidenceFamilyById = {};
  const scenarioTriggers = {};    // reqId → [scnId]
  const oqBlockers = {};          // reqId → [oqId]
  const overlayTarget = {};       // targetReqId → [overlayReqId]
  const evidenceFamilyByName = {}; // family-name → [{frameworkId, family}]
  const reverseGraph = data.reverse_graph || {};
  const forwardGraph = data.forward_graph || {};

  for (const [fwId, fw] of Object.entries(frameworks)) {
    for (const req of fw.requirements || []) {
      byId[req.id] = { ...req, _framework: fwId };

      // Scenario reverse-index
      for (const scnId of req.triggered_by_scenarios || []) {
        if (!scenarioTriggers[req.id]) scenarioTriggers[req.id] = [];
        scenarioTriggers[req.id].push(scnId);
      }

      // 218A overlay reverse-index
      if (req.overlay_target_id) {
        if (!overlayTarget[req.overlay_target_id]) overlayTarget[req.overlay_target_id] = [];
        overlayTarget[req.overlay_target_id].push(req.id);
      }
    }

    for (const scn of fw.scenarios || []) {
      scenarioById[scn.id] = { ...scn, _framework: fwId };
      // Reverse-index: scenario.triggered_requirements → req
      for (const t of scn.triggered_requirements || []) {
        const reqId = t.requirement_id;
        if (!scenarioTriggers[reqId]) scenarioTriggers[reqId] = [];
        if (!scenarioTriggers[reqId].includes(scn.id)) scenarioTriggers[reqId].push(scn.id);
      }
    }

    for (const oq of fw.open_questions || []) {
      oqById[oq.id] = { ...oq, _framework: fwId };
      for (const reqId of oq.blocks_requirements || []) {
        if (!oqBlockers[reqId]) oqBlockers[reqId] = [];
        oqBlockers[reqId].push(oq.id);
      }
    }

    for (const ef of fw.evidence_families || []) {
      evidenceFamilyById[`${fwId}:${ef.id}`] = { ...ef, _framework: fwId };
      const key = ef.name.toLowerCase().trim();
      if (!evidenceFamilyByName[key]) evidenceFamilyByName[key] = [];
      evidenceFamilyByName[key].push({ frameworkId: fwId, family: ef });
    }
  }

  // Anchor reqs = reqs with 3+ incoming crosswalks (computed by build_os_data).
  // anchor_stats is { reqId: incomingCount }. Sort desc, take 3+.
  const anchorReqs = Object.entries(data.anchor_stats || {})
    .filter(([, count]) => count >= 3)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 30)
    .map(([reqId, count]) => {
      const req = byId[reqId];
      return req ? { ...req, _incomingCount: count } : null;
    })
    .filter(Boolean);

  indices = {
    byId,
    scenarioById,
    oqById,
    evidenceFamilyById,
    evidenceFamilyByName,
    scenarioTriggers,
    oqBlockers,
    overlayTarget,
    reverseGraph,
    forwardGraph,
    anchorReqs,
    frameworks,
  };

  return indices;
}

// ─── Top-level dispatch ───────────────────────────────────────────────────────

export function buildSystemPrompt({ route, lens, data, mode, frameworkMentions }) {
  buildIndices(data);
  const safeMode = mode || 'explain';
  const safeLens = lens || 'both';
  const safeRoute = route || { type: 'home' };

  let body;
  switch (safeRoute.type) {
    case 'framework':
      body = buildFrameworkPrompt(safeRoute, safeLens, safeMode);
      break;
    case 'requirement':
      body = buildRequirementPrompt(safeRoute, safeLens, safeMode);
      break;
    case 'scenario':
      body = buildScenarioPrompt(safeRoute, safeLens, safeMode);
      break;
    case 'oq':
      body = buildOQPrompt(safeRoute, safeLens, safeMode);
      break;
    case 'graph':
      body = buildGraphPrompt(safeLens, safeMode);
      break;
    case 'oq-index':
      body = buildOQIndexPrompt(safeLens, safeMode);
      break;
    case 'home':
    default:
      body = buildHomePrompt(safeLens, safeMode);
  }

  const dynamicRetrieval = buildDynamicRetrieval(frameworkMentions, safeRoute);
  const modeDirective = buildModeDirective(safeMode);
  const sharedFooter = buildSharedFooter(safeLens);

  return [body, dynamicRetrieval, modeDirective, sharedFooter].filter(Boolean).join('\n\n');
}

// ─── Shared header / footer ───────────────────────────────────────────────────

function buildAppContext(weight) {
  // weight is just illustrative — actual content scales by route. This is the
  // app-tier constant content.
  if (weight === 'compressed') {
    return `APP: PrivateBox GRC OS — typed compliance ontology across 8 frameworks unified by schema v2.`;
  }
  return [
    `APP CONTEXT`,
    `PrivateBox is a South African on-prem AI vendor (privatebox.co.za) selling sovereign AI infrastructure to legal, medical, and financial customers. This GRC OS is PrivateBox's internal Governance, Risk & Compliance Operating System — a typed compliance ontology across 8 frameworks unified by schema v2 and an explicit cross-framework graph.`,
    ``,
    `Frameworks: ISO 27001 (ISMS, certifiable), ISO 27701 (PIMS, certifiable), ISO 42001 (AIMS, certifiable), EU AI Act (regulation), POPIA (SA regulation), King V (SA governance code, apply-and-explain), SOC 2 (attestation), NIST (voluntary — AI RMF + SSDF + SP 800-218A overlay).`,
    ``,
    `PrivateBox carries two business models: on-prem (customer hardware, single-tenant, production today) and AI Factory (partner DC ringfenced multi-tenant, aspirational — blocked on partner-DC selection). The current user lens propagates through ownership, scope, and applicability.`,
  ].join('\n');
}

function buildSharedFooter(lens) {
  return [
    `LENS: User's active lens is "${lens}". When ownership or applicability is lens-dependent, surface the lens-specific answer; never contradict the page UI. If lens is "ai-factory" and a control has owner_by_model.ai_factory.status: pending, surface the blocking open question.`,
    ``,
    `CITATION POLICY: Every claim cites the YAML id of its source (e.g., "per popia-cond-7…"). Render citation IDs in inline markdown links of the form [id](/<routeForId>). Never invent IDs. If you cannot ground an answer in the provided context, say so plainly and suggest which page the user should navigate to.`,
    ``,
    `REFUSAL CLAUSES`,
    `- Never claim PrivateBox is "certified", "compliant", or "audited" to any standard. Only state alignment per external_safe_claim / external_safe_phrasing fields — and emit those verbatim when used.`,
    `- Never paraphrase external_safe_claim / external_safe_phrasing. Emit verbatim with quotes, or do not emit.`,
    `- When asked "is this what the standard actually requires?", distinguish requirement (PrivateBox's paraphrase) from authoritative source. Flag relevant open questions about paywalled source PDFs.`,
    `- Never reproduce substantial passages from copyrighted standard text (ISO, NIST, AICPA, EU AI Act etc.). Paraphrase only.`,
    `- If lens is "on-prem", never apply AI Factory owner_by_model defaults. If lens is "ai-factory" and partner-DC OQ is pending, surface the blocker.`,
    `- Refuse to invent new external_safe_phrasing beyond what is in YAML. New procurement language requires a YAML update.`,
    ``,
    `STYLE`,
    `Be terse, structured, and grounded. Prefer tables / bullet lists for evidence and crosswalks. Lead with the answer; reasoning second. If the user is on a requirement page and asks something covered by structured fields (owner, evidence, audit_methods, cadence, failure_modes, external_safe_claim), use those fields directly rather than re-reasoning.`,
  ].join('\n');
}

function buildModeDirective(mode) {
  switch (mode) {
    case 'procurement':
      return [
        `OUTPUT MODE: procurement`,
        `Emit external_safe_claim / external_safe_phrasing verbatim with quotes and citation. Do NOT generate new procurement language. If the YAML field is missing or empty for what the user asked, say "PrivateBox does not yet have approved external phrasing for this — recommend updating the YAML before publishing." Surface relevant red-flag claim language when applicable (claims to avoid).`,
      ].join('\n');
    case 'audit':
      return [
        `OUTPUT MODE: audit prep`,
        `Lead with documented_evidence (bulleted artefact list). Follow with audit_methods (Insp/Int/Samp/Obs/Rep — explain what each means in this context). Include cadence and failure_modes. For SOC 2 reqs, distinguish type_i_evidence vs type_ii_evidence vs suggested_observation_period. For NIST SSDF, surface the recurring-evidence cadence.`,
      ].join('\n');
    case 'crosswalk':
      return [
        `OUTPUT MODE: crosswalk`,
        `Render as a table: current req | target framework | target ref(s) | crosswalk note. Use 1-hop edges only. If the user asks about a framework not yet in the graph, say so. Note any reverse edges that exist (this req is referenced BY other frameworks).`,
      ].join('\n');
    case 'explain':
    default:
      return [
        `OUTPUT MODE: explain`,
        `Conversational. Lead with the requirement's plain-English purpose, then PrivateBox's interpretation, then 1–2 key fields the user is likely to need next (owner, evidence, common failure modes, or how it links to neighbouring frameworks). End with an explicit "next-question" suggestion when natural.`,
      ].join('\n');
  }
}

// ─── Route-specific builders ──────────────────────────────────────────────────

function buildHomePrompt(lens, mode) {
  const fws = Object.entries(indices.frameworks);
  const directory = fws
    .map(([id, fw]) => {
      const reqCount = fw.requirements?.length || 0;
      const scnCount = fw.scenarios?.length || 0;
      const oqCount = fw.open_questions?.length || 0;
      const oneLine = (fw.pb_application?.why_chosen || '').split('.')[0] + '.';
      return `- ${id} | ${fw.full_name || id} | ${fw.type || '?'} | ${fw.audit_type || '?'} | reqs:${reqCount} scenarios:${scnCount} OQs:${oqCount}\n  ${truncate(oneLine, 220)}`;
    })
    .join('\n');

  const anchors = indices.anchorReqs
    .slice(0, 12)
    .map((r) => `- ${r.id} (${r._framework || ''}): ${r.title}`)
    .join('\n');

  const pendingOQs = Object.values(indices.oqById)
    .filter((oq) => oq.decision_status === 'pending')
    .slice(0, 15)
    .map((oq) => `- ${oq.id} (${oq._framework}): ${truncate(oq.question, 140)} | blocks ${(oq.blocks_requirements || []).length} reqs | owner: ${oq.decision_owner || 'unassigned'}`)
    .join('\n');

  return [
    buildAppContext(),
    ``,
    `ROUTE: home (no framework selected). The user is at the top of the OS — your job is to help them navigate to the right framework / requirement / scenario, not to answer specific compliance questions deeply.`,
    ``,
    `FRAMEWORK DIRECTORY`,
    directory,
    ``,
    `HIGHEST-LEVERAGE CONTROLS (top anchor requirements — 3+ incoming cross-framework references)`,
    anchors,
    ``,
    `PENDING OPEN QUESTIONS (15 most-recent, sorted by framework)`,
    pendingOQs,
  ].join('\n');
}

function buildFrameworkPrompt(route, lens, mode) {
  const fw = indices.frameworks[route.frameworkId];
  if (!fw) return `ROUTE ERROR: framework "${route.frameworkId}" not found in data.json.`;

  const lensScope = fw.pb_application?.scope_decisions?.[lens === 'ai-factory' ? 'ai_factory' : 'on_prem'];
  const topRisks = (fw.pb_application?.top_risks || []).slice(0, 8).map((r, i) => `${i + 1}. ${truncate(r, 240)}`).join('\n');

  const scenarios = (fw.scenarios || []).map((s) => `- ${s.id}: ${s.name}`).join('\n');
  const oqs = (fw.open_questions || [])
    .map((o) => `- ${o.id} (${o.decision_status}): ${truncate(o.question, 140)} | blocks ${(o.blocks_requirements || []).length} reqs`)
    .join('\n');
  const evidenceFamilies = (fw.evidence_families || []).slice(0, 18).map((e) => `- ${e.id}: ${e.name}`).join('\n');

  // Cross-cutting: anchor reqs scoped to this framework
  const fwAnchors = indices.anchorReqs
    .filter((r) => r._framework === route.frameworkId)
    .slice(0, 8)
    .map((r) => `- ${r.id}: ${r.title}`)
    .join('\n');

  // Disclosure framework / description criteria (King V / SOC 2)
  const extras = [];
  if (fw.disclosure_framework) {
    extras.push(`DISCLOSURE FRAMEWORK (King V): ${fw.disclosure_framework.reporting_model}. Concluding statement required: ${fw.disclosure_framework.concluding_statement_required}. Outcomes: ${(fw.disclosure_framework.required_outcomes || []).join(', ')}.`);
  }
  if (fw.description_criteria) {
    const dcs = fw.description_criteria.map((dc) => `${dc.id}: ${dc.title}${dc.mandatory ? ' (mandatory)' : ''}`).join('; ');
    extras.push(`DESCRIPTION CRITERIA (SOC 2): ${dcs}`);
  }
  if (fw.sub_frameworks) {
    const subs = fw.sub_frameworks.map((sf) => `${sf.id}: ${sf.name} (${sf.version})`).join('; ');
    extras.push(`SUB-FRAMEWORKS (NIST bundle): ${subs}`);
  }
  if (fw.companion_standards) {
    const comps = fw.companion_standards.map((c) => `${c.id}: ${c.name}`).join('; ');
    extras.push(`COMPANION STANDARDS: ${comps}`);
  }

  return [
    buildAppContext('compressed'),
    ``,
    `ROUTE: framework page — ${fw.full_name} (id: ${route.frameworkId}, type: ${fw.type}, audit_type: ${fw.audit_type}, certifiable: ${fw.certifiable})`,
    `Version: ${fw.version}. Issuer: ${fw.issuer}.`,
    ``,
    `WHY THIS FRAMEWORK FOR PB`,
    truncate(fw.pb_application?.why_chosen || '', 1800),
    ``,
    `SCOPE DECISION (${lens === 'ai-factory' ? 'AI Factory' : lens === 'on-prem' ? 'On-Prem' : 'On-Prem default'} lens)`,
    `Coverage: ${lensScope?.coverage || 'unknown'}`,
    truncate(lensScope?.rationale || '', 900),
    ``,
    `TOP RISKS (PrivateBox-specific)`,
    topRisks,
    ``,
    extras.length ? extras.join('\n') + '\n' : '',
    `SCENARIOS`,
    scenarios || '(none)',
    ``,
    `OPEN QUESTIONS`,
    oqs || '(none)',
    ``,
    `EVIDENCE FAMILIES`,
    evidenceFamilies || '(none)',
    ``,
    `FRAMEWORK ANCHOR REQUIREMENTS (most cross-referenced)`,
    fwAnchors || '(none — this is a foundational framework like ISO 27001 which is target-only)',
  ].filter(Boolean).join('\n');
}

function buildRequirementPrompt(route, lens, mode) {
  const req = indices.byId[route.reqId];
  if (!req) return `ROUTE ERROR: requirement "${route.reqId}" not found in data.json.`;
  const fw = indices.frameworks[req._framework];

  // Page tier — full req entry
  const pageContent = formatRequirementFull(req, lens);

  // Framework tier — compressed
  const fwCompressed = [
    `FRAMEWORK CONTEXT — ${fw.full_name} (${req._framework})`,
    `Type: ${fw.type} | Audit type: ${fw.audit_type} | Certifiable: ${fw.certifiable}`,
    `Why chosen (1-line): ${truncate((fw.pb_application?.why_chosen || '').split('.')[0] + '.', 360)}`,
    fw.pb_application?.scope_decisions?.[lens === 'ai-factory' ? 'ai_factory' : 'on_prem']
      ? `Scope (${lens} lens): ${fw.pb_application.scope_decisions[lens === 'ai-factory' ? 'ai_factory' : 'on_prem'].coverage} — ${truncate(fw.pb_application.scope_decisions[lens === 'ai-factory' ? 'ai_factory' : 'on_prem'].rationale, 400)}`
      : '',
    `Top 3 PB-specific risks: ${(fw.pb_application?.top_risks || []).slice(0, 3).map((r, i) => `(${i + 1}) ${truncate(r, 160)}`).join(' | ')}`,
  ].filter(Boolean).join('\n');

  // Page cross-cutting: triggered scenarios + blocking OQs (titles only)
  const triggers = (indices.scenarioTriggers[req.id] || []).map((scnId) => {
    const scn = indices.scenarioById[scnId];
    return scn ? `- ${scnId}: ${scn.name}` : `- ${scnId}`;
  }).join('\n');
  const blockers = (indices.oqBlockers[req.id] || []).map((oqId) => {
    const oq = indices.oqById[oqId];
    return oq ? `- ${oqId} (${oq.decision_status}): ${truncate(oq.question, 160)}` : `- ${oqId}`;
  }).join('\n');

  // 218A overlay back-reference: if this is an SSDF task, list overlays that target it
  const overlays = (indices.overlayTarget[req.id] || []).map((overlayId) => {
    const overlay = indices.byId[overlayId];
    return overlay ? `- ${overlayId}: ${overlay.title}` : `- ${overlayId}`;
  }).join('\n');

  return [
    buildAppContext('compressed'),
    ``,
    `ROUTE: requirement page — ${req.id} (${req.kind})`,
    ``,
    fwCompressed,
    ``,
    pageContent,
    ``,
    triggers ? `SCENARIOS THAT ACTIVATE THIS REQUIREMENT\n${triggers}` : '',
    blockers ? `OPEN QUESTIONS BLOCKING THIS REQUIREMENT\n${blockers}` : '',
    overlays ? `NIST 218A OVERLAYS TARGETING THIS REQUIREMENT\n${overlays}` : '',
  ].filter(Boolean).join('\n');
}

function buildScenarioPrompt(route, lens, mode) {
  const scn = indices.scenarioById[route.scenarioId];
  if (!scn) return `ROUTE ERROR: scenario "${route.scenarioId}" not found in data.json.`;
  const fw = indices.frameworks[scn._framework];

  const triggers = (scn.triggered_requirements || []).map((t) => {
    const req = indices.byId[t.requirement_id];
    const title = req ? req.title : '?';
    return `- ${t.requirement_id}: ${title}\n  Scenario-specific note: ${t.scenario_specific_note || '(none)'}`;
  }).join('\n');

  return [
    buildAppContext('compressed'),
    ``,
    `ROUTE: scenario page — ${scn.id} (framework: ${scn._framework})`,
    ``,
    `FRAMEWORK CONTEXT — ${fw.full_name}`,
    `Type: ${fw.type} | Why chosen (1-line): ${truncate((fw.pb_application?.why_chosen || '').split('.')[0] + '.', 360)}`,
    ``,
    `SCENARIO`,
    `Name: ${scn.name}`,
    `Framework-specific ID: ${scn.framework_specific_id || '(none)'}`,
    `Applies to business models: ${(scn.applies_to_business_models || []).join(', ')}`,
    `PB role: ${scn.pb_role || '(none)'}`,
    `Customer role: ${scn.customer_role || '(none)'}`,
    `Risk tier: ${scn.risk_tier || '(n/a)'}`,
    ``,
    `Description: ${scn.description || '(none)'}`,
    ``,
    `Notes: ${scn.notes || '(none)'}`,
    ``,
    `TRIGGERED REQUIREMENTS (the controls this scenario activates)`,
    triggers || '(none)',
  ].join('\n');
}

function buildOQPrompt(route, lens, mode) {
  const oq = indices.oqById[route.oqId];
  if (!oq) return `ROUTE ERROR: open question "${route.oqId}" not found in data.json.`;

  const blockedReqs = (oq.blocks_requirements || []).map((reqId) => {
    const req = indices.byId[reqId];
    return req ? `- ${reqId}: ${req.title}` : `- ${reqId}`;
  }).join('\n');

  const blockedScenarios = (oq.blocks_scenarios || []).map((scnId) => {
    const scn = indices.scenarioById[scnId];
    return scn ? `- ${scnId}: ${scn.name}` : `- ${scnId}`;
  }).join('\n');

  return [
    buildAppContext('compressed'),
    ``,
    `ROUTE: open question page — ${oq.id} (framework: ${oq._framework})`,
    ``,
    `OPEN QUESTION`,
    `Question: ${oq.question}`,
    `Decision owner: ${oq.decision_owner || 'unassigned'}`,
    `Decision status: ${oq.decision_status}`,
    `Created: ${oq.created || '(unknown)'}`,
    oq.resolved_value ? `Resolved value: ${oq.resolved_value} on ${oq.resolved_at}` : '',
    ``,
    `Candidate answers:`,
    (oq.candidate_answers || []).map((c, i) => `  ${i + 1}. ${c}`).join('\n') || '(none listed)',
    ``,
    `Notes: ${oq.notes || '(none)'}`,
    ``,
    blockedReqs ? `BLOCKS REQUIREMENTS\n${blockedReqs}` : '',
    blockedScenarios ? `BLOCKS SCENARIOS\n${blockedScenarios}` : '',
  ].filter(Boolean).join('\n');
}

function buildGraphPrompt(lens, mode) {
  const topAnchors = indices.anchorReqs.slice(0, 20).map((r) => {
    const incoming = (indices.reverseGraph[r.id] || []).length;
    return `- ${r.id} (${r._framework}): ${r.title} — ${incoming} incoming refs`;
  }).join('\n');

  const fwSummary = Object.entries(indices.frameworks).map(([fwId, fw]) => {
    const out = (fw.requirements || []).reduce((acc, r) => acc + (r.crosswalk?.length || 0), 0);
    return `- ${fwId}: ${(fw.requirements || []).length} reqs, ~${out} outgoing crosswalk groups`;
  }).join('\n');

  return [
    buildAppContext(),
    ``,
    `ROUTE: cross-framework graph view`,
    ``,
    `TOP ANCHOR REQUIREMENTS (most-referenced controls across the 8 frameworks)`,
    topAnchors,
    ``,
    `OUTGOING CROSSWALK SUMMARY PER FRAMEWORK`,
    fwSummary,
  ].join('\n');
}

function buildOQIndexPrompt(lens, mode) {
  const all = Object.values(indices.oqById);
  const pending = all.filter((o) => o.decision_status === 'pending');
  const resolved = all.filter((o) => o.decision_status === 'resolved');
  const deferred = all.filter((o) => o.decision_status === 'deferred');

  const pendingList = pending.map((o) => `- ${o.id} (${o._framework}): ${truncate(o.question, 160)} | blocks ${(o.blocks_requirements || []).length} reqs | owner: ${o.decision_owner || 'unassigned'}`).join('\n');

  return [
    buildAppContext(),
    ``,
    `ROUTE: open questions index`,
    ``,
    `STATUS SUMMARY: pending ${pending.length} | resolved ${resolved.length} | deferred ${deferred.length}`,
    ``,
    `PENDING OPEN QUESTIONS (all)`,
    pendingList,
  ].join('\n');
}

// ─── Page-tier requirement formatter (the deepest field-by-field render) ────

function formatRequirementFull(req, lens) {
  const lines = [`PAGE CONTENT — REQUIREMENT ${req.id}`];

  lines.push(`Kind: ${req.kind}${req.sub_framework ? ` (sub-framework: ${req.sub_framework})` : ''}`);
  lines.push(`Native ID: ${req.native_id}`);
  lines.push(`Group: ${req.group || '?'} / ${req.group_name || '?'}`);
  lines.push(`Title: ${req.title}`);
  lines.push('');

  if (req.requirement) {
    lines.push(`Requirement text (PrivateBox paraphrase of source standard):`);
    lines.push(`> ${req.requirement.trim()}`);
    lines.push('');
  }
  if (req.objective) {
    lines.push(`Objective:`);
    lines.push(`> ${req.objective.trim()}`);
    lines.push('');
  }

  if (req.pb_interpretation) {
    lines.push(`PrivateBox interpretation (operationalisation — DISTINCT from the standard's text):`);
    lines.push(req.pb_interpretation.trim());
    lines.push('');
  }

  if (req.auditor_intent) {
    lines.push(`Auditor intent: ${req.auditor_intent.trim()}`);
    lines.push('');
  }

  // Ownership — lens-aware
  lines.push(`Owner (base): ${req.owner || 'unspecified'}`);
  if (req.owner_by_model) {
    const onPrem = req.owner_by_model.on_prem;
    const aiFactory = req.owner_by_model.ai_factory;
    lines.push(`Owner by model:`);
    if (typeof onPrem === 'string') lines.push(`  on-prem: ${onPrem}`);
    else if (onPrem) lines.push(`  on-prem: ${JSON.stringify(onPrem)}`);
    if (typeof aiFactory === 'string') {
      lines.push(`  ai-factory: ${aiFactory}`);
    } else if (aiFactory) {
      lines.push(`  ai-factory: status=${aiFactory.status}${aiFactory.open_question ? ` (blocked by ${aiFactory.open_question})` : ''}`);
    }
  }
  lines.push(`Business models: ${(req.business_models || []).join(', ')}`);
  lines.push('');

  if (req.role_applicability) {
    const roles = Object.entries(req.role_applicability).filter(([, v]) => v === 'Y' || v === 'C').map(([r, v]) => `${r}${v === 'C' ? ' (conditional)' : ''}`);
    if (roles.length) lines.push(`Role applicability: ${roles.join(', ')}`);
  }
  if (req.tier) lines.push(`Risk tier: ${req.tier}`);
  if (req.applies) lines.push(`Applies: ${req.applies}${req.applies_rationale ? ` — ${req.applies_rationale}` : ''}`);
  lines.push(`Maturity target: ${req.maturity_target || '?'}`);
  lines.push('');

  if (req.documented_evidence && req.documented_evidence.length) {
    lines.push(`Documented evidence (artefacts that prove this):`);
    for (const e of req.documented_evidence) lines.push(`  - ${e}`);
    lines.push('');
  }
  if (req.operational_evidence) {
    lines.push(`Operational evidence: ${req.operational_evidence.trim()}`);
    lines.push('');
  }
  if (req.audit_methods && req.audit_methods.length) {
    const methods = req.audit_methods.map((m) => ({
      Insp: 'Inspection (look at artefact)',
      Int: 'Interview (ask the operator)',
      Samp: 'Sampling (random subset of records)',
      Obs: 'Observation (watch the process)',
      Rep: 'Re-performance (do it with auditor watching)',
    }[m] || m));
    lines.push(`Audit methods: ${methods.join(', ')}`);
  }
  if (req.cadence) lines.push(`Cadence: ${req.cadence}`);
  if (req.failure_modes) {
    lines.push('');
    lines.push(`Failure modes (where this typically goes wrong — honest content, quote when relevant):`);
    lines.push(req.failure_modes.trim());
  }
  lines.push('');

  // SOC 2-specific fields
  if (req.type_i_evidence) lines.push(`SOC 2 Type I evidence: ${req.type_i_evidence.trim()}`);
  if (req.type_ii_evidence) lines.push(`SOC 2 Type II evidence: ${req.type_ii_evidence.trim()}`);
  if (req.suggested_observation_period) lines.push(`SOC 2 suggested observation period: ${req.suggested_observation_period}`);

  // 218A overlay fields
  if (req.overlay_target_id) lines.push(`218A overlay targets: ${req.overlay_target_id}`);
  if (req.overlay_modifies) lines.push(`218A overlay modifies: ${req.overlay_modifies.trim()}`);

  // Companion refs (42001)
  if (req.companion_refs && req.companion_refs.length) {
    lines.push(`Companion refs: ${req.companion_refs.join(', ')}`);
    if (req.companion_note) lines.push(`Companion note: ${req.companion_note.trim()}`);
  }

  // External-safe phrasing (mode-critical)
  const safeText = req.external_safe_claim || req.external_safe_phrasing;
  if (safeText) {
    lines.push('');
    lines.push(`External-safe phrasing (pre-approved for procurement/customer-facing — emit verbatim only):`);
    lines.push(`"${safeText.trim()}"`);
  }

  // Crosswalks
  if (req.crosswalk && req.crosswalk.length) {
    lines.push('');
    lines.push(`Crosswalks to other frameworks:`);
    for (const cw of req.crosswalk) {
      const refs = (cw.refs || []).join(', ');
      lines.push(`  - ${cw.framework}: ${refs}`);
      if (cw.note) lines.push(`    note: ${cw.note}`);
    }
  }

  return lines.join('\n');
}

// ─── Dynamic retrieval (frameworks mentioned in user message) ────────────────

function buildDynamicRetrieval(frameworkMentions, route) {
  if (!frameworkMentions || frameworkMentions.length === 0) return '';

  const currentFw = route?.frameworkId;
  const others = frameworkMentions.filter((f) => f !== currentFw);
  if (others.length === 0) return '';

  const cards = others
    .filter((fwId) => indices.frameworks[fwId])
    .slice(0, 3)
    .map((fwId) => {
      const fw = indices.frameworks[fwId];
      return `- ${fwId}: ${fw.full_name} (${fw.type}, audit_type: ${fw.audit_type})\n  Why: ${truncate((fw.pb_application?.why_chosen || '').split('.')[0] + '.', 280)}`;
    })
    .join('\n');

  return cards
    ? [
        `DYNAMIC RETRIEVAL — user message mentioned other frameworks. One-line cards:`,
        cards,
        ``,
        `If user wants depth on a non-current framework, suggest navigating to its framework page. Do NOT dump that framework's full requirements into this turn.`,
      ].join('\n')
    : '';
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function truncate(text, maxChars) {
  if (!text) return '';
  const t = String(text).trim();
  if (t.length <= maxChars) return t;
  return t.slice(0, maxChars - 1).trimEnd() + '…';
}

// ─── Convenience: build a structured summary for testing / introspection ────

export function buildContextSummary({ route, lens, data }) {
  buildIndices(data);
  return {
    routeType: route?.type || 'home',
    lens,
    cachedDataRef: cachedDataRef === data,
    counts: {
      frameworks: Object.keys(indices.frameworks).length,
      requirements: Object.keys(indices.byId).length,
      scenarios: Object.keys(indices.scenarioById).length,
      openQuestions: Object.keys(indices.oqById).length,
      anchorReqs: indices.anchorReqs.length,
    },
  };
}
