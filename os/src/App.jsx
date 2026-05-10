import React, { useState, useMemo, useCallback, createContext, useContext } from 'react';
import {
  ChevronRight,
  ChevronLeft,
  Home,
  Layers,
  HelpCircle,
  Network,
  Search,
  X,
  ExternalLink,
  AlertCircle,
  CheckCircle2,
  Clock,
  ArrowRight,
  Bookmark,
} from 'lucide-react';

import DATA from './data.json';

// =============================================================================
// Data
// =============================================================================



// =============================================================================
// Helpers
// =============================================================================

function getRequirement(reqId) {
  for (const fw of Object.values(DATA.frameworks)) {
    if (fw.requirements_index[reqId]) {
      return { ...fw.requirements_index[reqId], _framework: fw._id };
    }
  }
  return null;
}

function getReverseLinks(reqId) {
  return DATA.reverse_graph[reqId] || [];
}

function getForwardLinks(reqId) {
  return DATA.forward_graph[reqId] || [];
}

function getOpenQuestion(oqId) {
  return DATA.all_open_questions[oqId] || null;
}

function getScenarioCluster(scnId) {
  return DATA.scenario_clusters[scnId] || null;
}

function getFrameworkLabel(fwId) {
  const labels = {
    'iso-27001': 'ISO 27001',
    'iso-27701': 'ISO 27701',
    'iso-42001': 'ISO 42001',
    'eu-ai-act': 'EU AI Act',
  };
  return labels[fwId] || fwId;
}

function frameworkAccent(fwId) {
  // Subtle differentiation — dot color when listing cross-framework refs
  return {
    'iso-27001': 'bg-stone-700',
    'iso-27701': 'bg-emerald-700',
    'iso-42001': 'bg-indigo-700',
    'eu-ai-act': 'bg-amber-700',
  }[fwId] || 'bg-stone-400';
}

function frameworkLabelClass(fwId) {
  return {
    'iso-27001': 'text-stone-700',
    'iso-27701': 'text-emerald-800',
    'iso-42001': 'text-indigo-800',
    'eu-ai-act': 'text-amber-800',
  }[fwId] || 'text-stone-600';
}

function tierClass(tier) {
  return {
    'prohibited': 'bg-red-100 text-red-900 border-red-300',
    'high-risk': 'bg-amber-100 text-amber-900 border-amber-300',
    'gpai': 'bg-violet-100 text-violet-900 border-violet-300',
    'limited': 'bg-sky-100 text-sky-900 border-sky-300',
    'minimal': 'bg-stone-100 text-stone-700 border-stone-300',
  }[tier] || 'bg-stone-100 text-stone-700 border-stone-300';
}

function ownerClass(owner) {
  if (!owner) return 'text-stone-500';
  if (owner === 'PB') return 'text-stone-900 font-medium';
  if (owner.startsWith('PB/')) return 'text-amber-800';
  if (owner === 'SH') return 'text-amber-700';
  if (owner.endsWith('/CL')) return 'text-sky-800';
  if (owner === 'CL') return 'text-sky-800';
  return 'text-stone-700';
}

// =============================================================================
// Business-model lens
// =============================================================================
// The two-business-model framing (on-prem / ai-factory / both) propagates
// through everything: owner shown on requirements, scenarios filtered by
// applicability, open questions filtered by which model they block.

const LensContext = createContext('both');
const LensSetterContext = createContext(() => {});
const useLens = () => useContext(LensContext);

const LENS_LABELS = {
  'on-prem': 'On-prem',
  'ai-factory': 'AI Factory',
  'both': 'Both',
};

// =============================================================================
// Framework overview content (Section 1 of the user-journey spine)
// =============================================================================
// Plain-English description and key concepts for each framework. Authored
// inline rather than in YAML so the writing can stay close to how a reader
// actually encounters the framework. When a 4th framework is added this
// should move into the YAML source as `plain_english` and `key_concepts`.

const FRAMEWORK_OVERVIEW = {
  'iso-27001': {
    plain_english: "ISO/IEC 27001 is the international standard for an Information Security Management System. It defines a risk-based, organisation-wide approach to managing information security. Two parts: mandatory clauses 4–10 describe the management system itself; Annex A is a catalogue of 93 controls from which an organisation selects what applies to its risks. Organisations can be independently certified by an accredited body via a Stage 1 documentation audit and a Stage 2 implementation audit, with annual surveillance audits thereafter.",
    key_concepts: [
      { label: 'ISMS', description: 'Information Security Management System — the whole thing the standard describes. Policies, processes, controls, and how they\'re managed together.' },
      { label: 'SoA', description: 'Statement of Applicability — declares which Annex A controls are in scope, and why excluded ones are excluded. Auditors read it first.' },
      { label: 'RTP', description: 'Risk Treatment Plan — the linkage from identified risks to chosen controls. Auditors trace risks → SoA → controls.' },
      { label: 'Stage 1 / 2', description: 'Two-stage external audit. Stage 1 reviews documentation; Stage 2 verifies what\'s documented is actually being done. Surveillance annually thereafter.' },
    ],
  },
  'iso-27701': {
    plain_english: "ISO/IEC 27701 is the international standard for a Privacy Information Management System. It extends ISO 27001 — you can't certify to 27701 without an underlying 27001 ISMS. It splits controls based on whether you're a data controller (determining why and how data is processed) or a processor (acting on a controller's instructions). Many organisations operate in both roles; 27701 supports that dual posture explicitly.",
    key_concepts: [
      { label: 'PIMS', description: 'Privacy Information Management System — the 27701 layer that sits on top of an ISMS.' },
      { label: 'Controller / Processor', description: 'The two GDPR-style roles. Different obligations apply depending on which role you\'re in for a given data flow.' },
      { label: 'A.1 / A.2 / A.3', description: '27701\'s three control sets: A.1 controllers-only, A.2 processors-only, A.3 shared. PB carries both roles, so all three apply.' },
      { label: 'HLS inheritance', description: 'High-Level Structure shared with 27001 — clauses 4–10 mirror it. A solid ISMS makes much of 27701 fall out for free.' },
    ],
  },
  'eu-ai-act': {
    plain_english: "The EU Artificial Intelligence Act is the first comprehensive AI regulation. It classifies AI systems by risk tier — prohibited, high-risk, limited risk, minimal risk — and scales obligations to the tier. General-Purpose AI models (GPAI) have a separate obligation set under Articles 51–55. Roles matter: providers, deployers, importers, distributors, authorised representatives, and product manufacturers each have distinct duties. The Act applies extraterritorially: if AI outputs are used in the EU, the Act applies regardless of where the provider sits.",
    key_concepts: [
      { label: 'Risk tiers', description: 'Prohibited, High-risk, Limited, Minimal — plus GPAI as a separate category. Determines what obligations apply.' },
      { label: 'Roles', description: 'Provider builds it. Deployer uses it. Importer brings it in. Article 25 can flip a deployer into a provider — material role-flip exposure.' },
      { label: 'Annex III', description: 'The list of high-risk use cases (employment screening, creditworthiness, education access, etc). Triggers full Chapter III obligations.' },
      { label: 'Phased dates', description: 'Feb 2025: prohibited practices + AI literacy. Aug 2025: GPAI. Aug 2026: most provisions. Aug 2027: legacy GPAI grace ends.' },
    ],
  },
  'iso-42001': {
    plain_english: "ISO/IEC 42001 is the international standard for an AI Management System (AIMS). It uses the same Annex SL high-level structure as ISO 27001 and 27701 — clauses 4–10 describe the management system itself — and adds AI-specific controls in Annex A across nine objectives (A.2–A.10) covering policy, governance, impact assessment, lifecycle, data, transparency, use, and supplier relationships. Two companion guidance standards deepen it: ISO/IEC 42005:2025 defines the AI System Impact Assessment methodology referenced from Clause 6.1.4 and A.5; ISO/IEC 42006:2025 sets the auditor competence and audit-time rules certification bodies must meet. Organisations are independently certified via Stage 1 documentation review + Stage 2 implementation audit, with annual surveillance.",
    key_concepts: [
      { label: 'AIMS', description: 'AI Management System — the whole governance frame. Sits alongside an ISMS (27001) and PIMS (27701) under a single integrated management system, which is how PrivateBox runs it.' },
      { label: 'AISIA', description: 'AI System Impact Assessment — required by Clause 6.1.4 and Annex A.5; depth defined by ISO/IEC 42005:2025. Foreseeable-misuse coverage is the most-commonly-missed element.' },
      { label: 'Annex A controls', description: '38–39 controls across A.2–A.10 (numbering varies in secondary sources; published ISO PDF is canonical). SoA must address every one — applicability, owner, evidence, justification for exclusions.' },
      { label: 'Designed-in-alignment', description: 'PrivateBox\'s pre-certification posture: "designed in alignment with ISO/IEC 42001:2023" — never claim certified until an accredited body issues a certificate against a defined scope.' },
    ],
  },
};

// Resolve owner for the active lens. owner_by_model can be:
//   on_prem: 'SH' | 'PB' | etc.  (string)
//   ai_factory: 'SH' | { status: 'pending', open_question: 'oq-...' }
// Returns: { owner, pending, open_question, divergent }
function getOwnerForLens(req, lens) {
  const obm = req.owner_by_model;
  const baseOwner = req.owner || '—';

  if (!obm) {
    return { owner: baseOwner, pending: false, divergent: false };
  }

  const onPrem = obm.on_prem;
  const aiFactory = obm.ai_factory;
  const aiPending = aiFactory && typeof aiFactory === 'object' && aiFactory.status === 'pending';

  if (lens === 'on-prem') {
    return { owner: onPrem || baseOwner, pending: false, divergent: false };
  }
  if (lens === 'ai-factory') {
    if (aiPending) {
      return { owner: '—', pending: true, open_question: aiFactory.open_question, divergent: false };
    }
    return { owner: aiFactory || baseOwner, pending: false, divergent: false };
  }
  // both: show base owner with divergent flag
  return { owner: baseOwner, pending: false, divergent: true, on_prem: onPrem, ai_factory: aiFactory };
}

function scenarioAppliesToLens(scn, lens) {
  if (lens === 'both') return true;
  const models = scn.applies_to_business_models || ['on-prem', 'ai-factory'];
  return models.includes(lens);
}

// Open questions don't carry a business_models field directly, but their id
// pattern reveals which model they block. AI Factory-specific questions
// don't gate on-prem readiness.
function oqAppliesToLens(oqId, lens) {
  if (lens !== 'on-prem') return true;
  const aiFactorySpecific = oqId.includes('ai-factory') || oqId.includes('partner-dc');
  return !aiFactorySpecific;
}

function LensToggle() {
  const lens = useLens();
  const setLens = useContext(LensSetterContext);
  const options = [
    { id: 'on-prem', label: 'On-prem' },
    { id: 'ai-factory', label: 'AI Factory' },
    { id: 'both', label: 'Both' },
  ];
  return (
    <div className="flex items-center gap-1 border border-stone-300 bg-white p-0.5">
      <span className="font-mono text-xs uppercase tracking-wider text-stone-500 px-2">model:</span>
      {options.map(o => (
        <button
          key={o.id}
          onClick={() => setLens(o.id)}
          className={`font-mono text-xs uppercase tracking-wider px-3 py-1 transition-colors ${
            lens === o.id
              ? 'bg-stone-900 text-stone-50'
              : 'text-stone-600 hover:bg-stone-100'
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Layout / shared
// =============================================================================

function Pill({ children, color = 'stone', className = '' }) {
  const colorClasses = {
    stone: 'bg-stone-100 text-stone-700 border-stone-300',
    amber: 'bg-amber-50 text-amber-900 border-amber-300',
    emerald: 'bg-emerald-50 text-emerald-900 border-emerald-300',
    red: 'bg-red-50 text-red-900 border-red-300',
    sky: 'bg-sky-50 text-sky-900 border-sky-300',
    violet: 'bg-violet-50 text-violet-900 border-violet-300',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-mono uppercase tracking-wide border ${colorClasses[color]} ${className}`}>
      {children}
    </span>
  );
}

function FrameworkDot({ fwId }) {
  return <span className={`inline-block w-1.5 h-1.5 rounded-full ${frameworkAccent(fwId)}`} />;
}

function ReqLink({ reqId, navigate, children, withDot = true }) {
  const req = getRequirement(reqId);
  if (!req) return <span className="text-stone-400">{reqId}</span>;
  return (
    <button
      onClick={() => navigate({ type: 'requirement', id: reqId })}
      className="inline-flex items-center gap-1.5 text-left hover:text-amber-800 transition-colors group"
    >
      {withDot && <FrameworkDot fwId={req._framework} />}
      <span className="font-mono text-xs text-stone-500 group-hover:text-amber-700">{reqId}</span>
      {children && <span className="text-stone-700 group-hover:text-amber-800">{children}</span>}
    </button>
  );
}

function SectionHeader({ children, count }) {
  return (
    <div className="border-b border-stone-300 mb-4 pb-1.5 flex items-baseline gap-3">
      <h3 className="font-serif text-lg text-stone-950 tracking-tight">{children}</h3>
      {count !== undefined && (
        <span className="font-mono text-xs text-stone-500">{count}</span>
      )}
    </div>
  );
}

function JourneyStep({ number, title, caption }) {
  return (
    <div className="mt-12 mb-6">
      <div className="flex items-baseline gap-4 border-b border-stone-300 pb-2">
        <span className="font-mono text-xs uppercase tracking-widest text-amber-800">
          Step {number}
        </span>
        <h2 className="font-serif text-2xl text-stone-950 tracking-tight">{title}</h2>
      </div>
      {caption && (
        <p className="text-sm text-stone-600 mt-2 leading-relaxed">{caption}</p>
      )}
    </div>
  );
}

function FieldLabel({ children }) {
  return (
    <div className="font-mono text-xs uppercase tracking-wider text-stone-500 mb-1">
      {children}
    </div>
  );
}

function Field({ label, children, className = '' }) {
  if (!children && children !== 0) return null;
  return (
    <div className={`mb-5 ${className}`}>
      <FieldLabel>{label}</FieldLabel>
      <div className="text-stone-800 leading-relaxed">{children}</div>
    </div>
  );
}

// =============================================================================
// Header
// =============================================================================

function Header({ view, navigate, back, canBack }) {
  return (
    <header className="border-b border-stone-300 bg-stone-50 sticky top-0 z-10">
      <div className="px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate({ type: 'home' })}
            className="font-serif text-lg text-stone-950 tracking-tight hover:text-amber-800 transition-colors"
          >
            PrivateBox <span className="text-stone-500">/</span> GRC OS
          </button>
          <span className="font-mono text-xs text-stone-400">v0.1 prototype</span>
        </div>
        <div className="flex items-center gap-3">
          <LensToggle />
          {canBack && (
            <button
              onClick={back}
              className="font-mono text-xs text-stone-600 hover:text-amber-800 transition-colors flex items-center gap-1"
            >
              <ChevronLeft size={14} /> back
            </button>
          )}
        </div>
      </div>
      <Breadcrumb view={view} navigate={navigate} />
    </header>
  );
}

function Breadcrumb({ view, navigate }) {
  const crumbs = [];
  if (view.type === 'framework') {
    crumbs.push({ label: getFrameworkLabel(view.id), id: view.id });
  } else if (view.type === 'requirement') {
    const req = getRequirement(view.id);
    if (req) {
      crumbs.push({
        label: getFrameworkLabel(req._framework),
        onClick: () => navigate({ type: 'framework', id: req._framework }),
      });
      crumbs.push({ label: view.id, mono: true });
    }
  } else if (view.type === 'scenario') {
    const scn = getScenarioCluster(view.id);
    if (scn) {
      crumbs.push({
        label: getFrameworkLabel(scn.framework),
        onClick: () => navigate({ type: 'framework', id: scn.framework }),
      });
      crumbs.push({ label: 'Scenarios' });
      crumbs.push({ label: scn.framework_specific_id || view.id, mono: true });
    }
  } else if (view.type === 'openq') {
    crumbs.push({ label: 'Open Questions' });
    if (view.id) crumbs.push({ label: view.id, mono: true });
  } else if (view.type === 'graph') {
    crumbs.push({ label: 'Cross-Framework Graph' });
  }

  if (crumbs.length === 0) return <div className="h-6 px-6 border-t border-stone-200" />;
  return (
    <div className="px-6 py-1.5 border-t border-stone-200 flex items-center gap-2 text-xs">
      <button
        onClick={() => navigate({ type: 'home' })}
        className="text-stone-500 hover:text-amber-800"
      >
        Home
      </button>
      {crumbs.map((c, i) => (
        <React.Fragment key={i}>
          <ChevronRight size={12} className="text-stone-400" />
          {c.onClick ? (
            <button onClick={c.onClick} className="text-stone-600 hover:text-amber-800">
              {c.label}
            </button>
          ) : (
            <span className={c.mono ? 'font-mono text-stone-700' : 'text-stone-700'}>
              {c.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

// =============================================================================
// Sidebar
// =============================================================================

function Sidebar({ navigate, currentView }) {
  const isActive = (type, id) => {
    if (currentView.type !== type) return false;
    return id === undefined || currentView.id === id;
  };
  const item = (label, onClick, active, icon, count) => (
    <button
      onClick={onClick}
      className={`w-full text-left px-3 py-1.5 flex items-center gap-2 text-sm transition-colors border-l-2 ${
        active
          ? 'bg-amber-50 border-amber-700 text-amber-900'
          : 'border-transparent text-stone-700 hover:bg-stone-100 hover:border-stone-300'
      }`}
    >
      {icon && <span className="text-stone-500">{icon}</span>}
      <span className="flex-1">{label}</span>
      {count !== undefined && (
        <span className="font-mono text-xs text-stone-400">{count}</span>
      )}
    </button>
  );

  return (
    <aside
      className="w-64 border-r border-stone-200 bg-stone-50 sticky overflow-y-auto py-4"
      style={{ top: '73px', height: 'calc(100vh - 73px)' }}
    >
      <div className="mb-6">
        {item('Home', () => navigate({ type: 'home' }), isActive('home'), <Home size={14} />)}
      </div>

      <div className="mb-6">
        <div className="px-3 py-1 font-mono text-xs uppercase tracking-wider text-stone-500">
          Frameworks
        </div>
        {Object.values(DATA.frameworks).map(fw => (
          <button
            key={fw._id}
            onClick={() => navigate({ type: 'framework', id: fw._id })}
            className={`w-full text-left px-3 py-1.5 flex items-center gap-2 text-sm transition-colors border-l-2 ${
              isActive('framework', fw._id)
                ? 'bg-amber-50 border-amber-700 text-amber-900'
                : 'border-transparent text-stone-700 hover:bg-stone-100 hover:border-stone-300'
            }`}
          >
            <FrameworkDot fwId={fw._id} />
            <span className="flex-1 truncate">{getFrameworkLabel(fw._id)}</span>
            <span className="font-mono text-xs text-stone-400">
              {fw.requirements.length}
            </span>
          </button>
        ))}
      </div>

      <div className="mb-6">
        <div className="px-3 py-1 font-mono text-xs uppercase tracking-wider text-stone-500">
          Cross-cutting
        </div>
        {item(
          'Open Questions',
          () => navigate({ type: 'openq' }),
          isActive('openq'),
          <HelpCircle size={14} />,
          Object.keys(DATA.all_open_questions).length
        )}
        {item(
          'Cross-Framework Graph',
          () => navigate({ type: 'graph' }),
          isActive('graph'),
          <Network size={14} />,
          Object.values(DATA.anchor_stats).filter(c => c >= 2).length
        )}
      </div>
    </aside>
  );
}

// =============================================================================
// Home
// =============================================================================

function HomePage({ navigate }) {
  const lens = useLens();
  const totalReqs = Object.values(DATA.frameworks).reduce(
    (sum, fw) => sum + fw.requirements.length, 0
  );
  const totalScenarios = Object.values(DATA.frameworks).reduce(
    (sum, fw) => sum + (fw.scenarios || []).filter(s => scenarioAppliesToLens(s, lens)).length, 0
  );
  const allOQs = Object.values(DATA.all_open_questions);
  const visibleOQs = allOQs.filter(oq => oqAppliesToLens(oq.id, lens));
  const totalOQs = visibleOQs.length;
  const hiddenOQs = allOQs.length - visibleOQs.length;
  const totalCrosswalks = Object.values(DATA.forward_graph).reduce(
    (sum, refs) => sum + refs.length, 0
  );
  const anchors = Object.entries(DATA.anchor_stats)
    .filter(([_, c]) => c >= 3)
    .sort(([, a], [, b]) => b - a);

  return (
    <div className="max-w-4xl">
      <div className="mb-12">
        <h1 className="font-serif text-4xl text-stone-950 tracking-tight mb-2">
          Compliance alignment record
        </h1>
        <p className="text-stone-600 leading-relaxed max-w-2xl">
          Three frameworks, unified by an explicit cross-framework graph.
          Schema v2. End-to-end loop test on real data — find what breaks before scaling to nine.
        </p>
        {lens !== 'both' && (
          <div className="mt-3 inline-flex items-center gap-2 text-xs font-mono text-stone-600">
            <span className="text-stone-400 uppercase tracking-wider">viewing:</span>
            <span className="text-amber-800 uppercase tracking-wider">{LENS_LABELS[lens]} lens</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 gap-px bg-stone-200 border border-stone-200 mb-12">
        <Stat label="Frameworks" value={Object.keys(DATA.frameworks).length} />
        <Stat label="Requirements" value={totalReqs} />
        <Stat
          label="Scenarios"
          value={totalScenarios}
          sub={lens !== 'both' && totalScenarios !== 25 ? `${25 - totalScenarios} hidden` : null}
        />
        <Stat
          label="Open Questions"
          value={totalOQs}
          sub={hiddenOQs > 0 ? `${hiddenOQs} hidden` : null}
        />
      </div>

      <div className="mb-12">
        <SectionHeader>Frameworks</SectionHeader>
        <div className="space-y-3">
          {Object.values(DATA.frameworks).map(fw => (
            <FrameworkCard
              key={fw._id}
              fw={fw}
              onClick={() => navigate({ type: 'framework', id: fw._id })}
            />
          ))}
        </div>
      </div>

      <div className="mb-12">
        <SectionHeader count={anchors.length}>Cross-framework anchors</SectionHeader>
        <p className="text-sm text-stone-600 mb-4 max-w-2xl leading-relaxed">
          Requirements with three or more incoming cross-framework references.
          One control well-implemented here discharges multiple framework obligations.
        </p>
        <div className="space-y-2">
          {anchors.map(([reqId, count]) => {
            const req = getRequirement(reqId);
            if (!req) return null;
            const sources = getReverseLinks(reqId);
            const fws = [...new Set(sources.map(s => s.source_framework))];
            return (
              <button
                key={reqId}
                onClick={() => navigate({ type: 'requirement', id: reqId })}
                className="w-full text-left flex items-center gap-4 p-3 border border-stone-200 hover:border-amber-700 hover:bg-amber-50 transition-colors group"
              >
                <div className="font-serif text-3xl text-amber-800 tabular-nums w-10 text-right">{count}</div>
                <div className="flex-1 min-w-0">
                  <div className="font-mono text-xs text-stone-500 mb-0.5">{reqId}</div>
                  <div className="text-stone-900 truncate">{req.title}</div>
                </div>
                <div className="flex items-center gap-1 text-xs text-stone-500">
                  {fws.map(f => (
                    <React.Fragment key={f}>
                      <FrameworkDot fwId={f} />
                      <span className={frameworkLabelClass(f)}>{getFrameworkLabel(f)}</span>
                    </React.Fragment>
                  ))}
                </div>
                <ArrowRight size={16} className="text-stone-400 group-hover:text-amber-700" />
              </button>
            );
          })}
        </div>
      </div>

      <div className="mb-12">
        <SectionHeader count={totalCrosswalks}>Graph density</SectionHeader>
        <div className="grid grid-cols-3 gap-px bg-stone-200 border border-stone-200">
          <Stat label="Forward edges" value={totalCrosswalks} />
          <Stat
            label="Reqs with crosswalks"
            value={Object.keys(DATA.forward_graph).length}
            sub={`${Math.round(100 * Object.keys(DATA.forward_graph).length / totalReqs)}%`}
          />
          <Stat
            label="Anchor reqs (2+ in)"
            value={Object.values(DATA.anchor_stats).filter(c => c >= 2).length}
          />
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, sub }) {
  return (
    <div className="bg-stone-50 px-4 py-3">
      <div className="font-mono text-xs uppercase tracking-wider text-stone-500 mb-1">{label}</div>
      <div className="font-serif text-2xl text-stone-950 tabular-nums">
        {value}
        {sub && <span className="text-stone-500 text-base ml-2">{sub}</span>}
      </div>
    </div>
  );
}

function FrameworkCard({ fw, onClick }) {
  const lens = useLens();
  const xwCount = fw.requirements.filter(r => r.crosswalk && r.crosswalk.length > 0).length;
  const visibleScenarios = (fw.scenarios || []).filter(s => scenarioAppliesToLens(s, lens));
  const visibleOQs = (fw.open_questions || []).filter(oq => oqAppliesToLens(oq.id, lens));
  return (
    <button
      onClick={onClick}
      className="w-full text-left p-4 border border-stone-200 hover:border-amber-700 hover:bg-amber-50 transition-colors group"
    >
      <div className="flex items-start gap-3 mb-3">
        <FrameworkDot fwId={fw._id} />
        <div className="flex-1">
          <div className="font-serif text-lg text-stone-950 tracking-tight">{fw.full_name}</div>
          <div className="text-xs text-stone-500 mt-0.5">
            <span className="font-mono">{fw.id}</span>
            <span className="mx-2">·</span>
            <span>v{fw.version}</span>
            <span className="mx-2">·</span>
            <span className="capitalize">{fw.type.replace(/_/g, ' ')}</span>
            <span className="mx-2">·</span>
            <span className="capitalize">{fw.audit_type.replace(/_/g, ' ')}</span>
          </div>
        </div>
        <ArrowRight size={16} className="text-stone-400 group-hover:text-amber-700 mt-1.5" />
      </div>
      <div className="flex items-center gap-6 text-xs text-stone-600 ml-5">
        <span><span className="font-mono tabular-nums">{fw.requirements.length}</span> requirements</span>
        {visibleScenarios.length > 0 && (
          <span><span className="font-mono tabular-nums">{visibleScenarios.length}</span> scenarios</span>
        )}
        <span><span className="font-mono tabular-nums">{visibleOQs.length}</span> open questions</span>
        <span><span className="font-mono tabular-nums">{xwCount}</span> with crosswalks</span>
      </div>
    </button>
  );
}

// =============================================================================
// Framework detail
// =============================================================================

function FrameworkDetail({ fwId, navigate }) {
  const fw = DATA.frameworks[fwId];
  const lens = useLens();
  const [filter, setFilter] = useState({ kind: null, group: null, owner: null, search: '' });

  if (!fw) return <div>Framework not found</div>;

  const reqs = useMemo(() => {
    return fw.requirements.filter(r => {
      if (filter.kind && r.kind !== filter.kind) return false;
      if (filter.group && r.group !== filter.group) return false;
      if (filter.owner) {
        // Owner filter respects lens — match against lens-resolved owner
        const o = getOwnerForLens(r, lens);
        if (o.pending || o.owner !== filter.owner) return false;
      }
      if (filter.search) {
        const s = filter.search.toLowerCase();
        if (!(r.id.toLowerCase().includes(s) ||
              r.title.toLowerCase().includes(s) ||
              (r.requirement || '').toLowerCase().includes(s) ||
              (r.objective || '').toLowerCase().includes(s))) return false;
      }
      return true;
    });
  }, [fw, filter, lens]);

  // Group reqs by group
  const grouped = useMemo(() => {
    const g = {};
    reqs.forEach(r => {
      const key = `${r.group || ''} ${r.group_name || ''}`.trim() || 'Other';
      if (!g[key]) g[key] = [];
      g[key].push(r);
    });
    return g;
  }, [reqs]);

  const kinds = [...new Set(fw.requirements.map(r => r.kind))];
  const groups = [...new Set(fw.requirements.map(r => `${r.group || ''} ${r.group_name || ''}`.trim() || 'Other'))];
  const owners = [...new Set(fw.requirements.map(r => r.owner).filter(Boolean))];

  return (
    <div className="max-w-5xl">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <FrameworkDot fwId={fw._id} />
          <span className="font-mono text-xs text-stone-500 uppercase tracking-wider">
            {fw.type.replace(/_/g, ' ')} · {fw.audit_type.replace(/_/g, ' ')}
          </span>
        </div>
        <h1 className="font-serif text-3xl text-stone-950 tracking-tight mb-2">{fw.full_name}</h1>
        <div className="text-sm text-stone-600">
          <span className="font-mono">{fw.id}</span>
          <span className="mx-2">·</span>
          <span>v{fw.version}</span>
          <span className="mx-2">·</span>
          <span>{fw.issuer}</span>
          {fw.certifiable && (<><span className="mx-2">·</span><span>certifiable</span></>)}
        </div>
      </div>

      {/* Quick-jump nav */}
      <nav className="mb-8 flex items-center gap-1 text-xs">
        <span className="font-mono text-stone-400 uppercase tracking-widest mr-2">jump to:</span>
        {[
          { n: 1, label: 'What it is' },
          { n: 2, label: 'Applied to PB' },
          { n: 3, label: 'Requirements' },
          { n: 4, label: 'Artifacts' },
        ].map(s => (
          <a
            key={s.n}
            href={`#step-${s.n}`}
            className="font-mono px-2 py-1 text-stone-600 hover:text-amber-800 hover:bg-amber-50 transition-colors"
          >
            {s.n} · {s.label}
          </a>
        ))}
      </nav>

      {/* SECTION 1 — What this framework is */}
      <div id="step-1">
        <JourneyStep
          number={1}
          title="What this framework is"
          caption="Plain-English overview, before any PrivateBox-specific lens."
        />
        {FRAMEWORK_OVERVIEW[fw._id] ? (
          <>
            <p className="text-stone-800 leading-relaxed mb-6">
              {FRAMEWORK_OVERVIEW[fw._id].plain_english}
            </p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
              {FRAMEWORK_OVERVIEW[fw._id].key_concepts.map(c => (
                <div key={c.label} className="p-3 border border-stone-200 bg-white">
                  <div className="font-mono text-xs uppercase tracking-wider text-amber-800 mb-1">
                    {c.label}
                  </div>
                  <div className="text-xs text-stone-700 leading-relaxed">
                    {c.description}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p className="text-sm italic text-stone-500">Plain-English overview pending.</p>
        )}

        {/* Issuer / type / audit type / phase dates summary */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-stone-200 border border-stone-200 mb-6">
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Issuer</FieldLabel>
            <div className="text-sm text-stone-800">{fw.issuer}</div>
          </div>
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Type</FieldLabel>
            <div className="text-sm text-stone-800 capitalize">{fw.type.replace(/_/g, ' ')}</div>
          </div>
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Audit type</FieldLabel>
            <div className="text-sm text-stone-800 capitalize">{fw.audit_type.replace(/_/g, ' ')}</div>
          </div>
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Certifiable</FieldLabel>
            <div className="text-sm text-stone-800">{fw.certifiable ? 'Yes' : 'No'}</div>
          </div>
        </div>

        {/* Effective dates timeline (if present — EU AI Act has 4 milestones) */}
        {fw.effective_dates && fw.effective_dates.length > 0 && (
          <div className="mb-6 p-4 border-l-4 border-amber-700 bg-amber-50">
            <FieldLabel>Phased effective dates</FieldLabel>
            <div className="mt-2 space-y-2">
              {fw.effective_dates.map((d, i) => (
                <div key={i} className="flex items-baseline gap-3 text-sm">
                  <span className="font-mono text-xs text-amber-900 w-24 shrink-0 tabular-nums">{d.date}</span>
                  <div className="flex-1">
                    <div className="text-stone-900">{d.milestone}</div>
                    {d.notes && <div className="text-xs text-stone-600 mt-0.5 leading-relaxed">{d.notes}</div>}
                  </div>
                  {d.status && (
                    <span className={`font-mono text-xs uppercase tracking-wider shrink-0 ${
                      d.status === 'in_force' ? 'text-emerald-700' : 'text-stone-500'
                    }`}>
                      {d.status.replace(/_/g, ' ')}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* SECTION 2 — Applied to PrivateBox */}
      <div id="step-2">
        <JourneyStep
          number={2}
          title="Applied to PrivateBox"
          caption="Why this framework matters for PB, scope per business model, and the top risks under it."
        />

        {fw.pb_application?.why_chosen && (
          <div className="mb-6 p-5 bg-amber-50 border-l-4 border-amber-700">
            <FieldLabel>Why this framework</FieldLabel>
            <p className="text-stone-800 leading-relaxed mt-1">{fw.pb_application.why_chosen}</p>
          </div>
        )}

        {/* Scope decisions per business model */}
        {fw.pb_application?.scope_decisions && (
          <div className="mb-6">
            <FieldLabel>Scope by business model</FieldLabel>
            <div className="mt-2 grid grid-cols-1 lg:grid-cols-2 gap-3">
              {Object.entries(fw.pb_application.scope_decisions).map(([modelKey, sd]) => {
                const modelLabel = modelKey === 'on_prem' ? 'On-prem' : modelKey === 'ai_factory' ? 'AI Factory' : modelKey;
                const lensKey = modelKey === 'on_prem' ? 'on-prem' : 'ai-factory';
                const isActive = lens === lensKey;
                const coverage = sd.coverage || sd.applicability || '—';
                const coverageColor = coverage === 'full' ? 'emerald' : coverage === 'partial' ? 'amber' : 'stone';
                return (
                  <div
                    key={modelKey}
                    className={`p-4 border ${isActive ? 'border-amber-700 bg-amber-50' : 'border-stone-200 bg-white'}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs uppercase tracking-wider text-stone-700">
                        {modelLabel}
                        {isActive && <span className="ml-2 text-amber-800">· active lens</span>}
                      </span>
                      <Pill color={coverageColor}>{coverage}</Pill>
                    </div>
                    <p className="text-sm text-stone-700 leading-relaxed">{sd.rationale || sd.notes || '—'}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Top risks */}
        {fw.pb_application?.top_risks && fw.pb_application.top_risks.length > 0 && (
          <div className="mb-6">
            <FieldLabel>Top risks under this framework</FieldLabel>
            <ul className="mt-2 space-y-1.5">
              {fw.pb_application.top_risks.map((r, i) => (
                <li key={i} className="text-sm text-stone-800 leading-relaxed flex items-start gap-2">
                  <span className="text-amber-700 font-mono mt-0.5 shrink-0">▸</span>
                  <span>{typeof r === 'string' ? r : (r.description || r.risk || JSON.stringify(r))}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Roles (EU AI Act, ISO 27701) */}
        {fw.roles && fw.roles.length > 0 && (
          <div className="mb-6">
            <FieldLabel>Roles defined</FieldLabel>
            <div className="mt-2 flex flex-wrap gap-2">
              {fw.roles.map((role, i) => (
                <Pill key={i} color="violet">
                  {typeof role === 'string' ? role : (role.id || role.name || role.label)}
                </Pill>
              ))}
            </div>
          </div>
        )}

        {/* Tiers (EU AI Act) */}
        {fw.tiers && fw.tiers.length > 0 && (
          <div className="mb-6">
            <FieldLabel>Risk tiers</FieldLabel>
            <div className="mt-2 flex flex-wrap gap-2">
              {fw.tiers.map((t, i) => {
                const tid = typeof t === 'string' ? t : (t.id || t.name);
                return <Pill key={i} className={tierClass(tid)}>{tid}</Pill>;
              })}
            </div>
          </div>
        )}
      </div>

      {/* SECTION 3 — Granular requirements */}
      <div id="step-3">
        <JourneyStep
          number={3}
          title="Granular requirements"
          caption={`All ${fw.requirements.length} requirements with PrivateBox interpretation, owner, evidence, and crosswalks. Click any row for full detail.`}
        />
      </div>

      {fw.scenarios && fw.scenarios.length > 0 && (() => {
        const visibleScenarios = fw.scenarios.filter(s => scenarioAppliesToLens(s, lens));
        if (visibleScenarios.length === 0) return null;
        const filteredOut = fw.scenarios.length - visibleScenarios.length;
        return (
          <div className="mb-8">
            <SectionHeader count={visibleScenarios.length}>
              Scenarios
              {filteredOut > 0 && (
                <span className="ml-2 font-mono text-xs text-stone-400 normal-case tracking-normal">
                  ({filteredOut} hidden by {LENS_LABELS[lens]} lens)
                </span>
              )}
            </SectionHeader>
            <div className="grid grid-cols-2 gap-2">
              {visibleScenarios.map(scn => (
                <button
                  key={scn.id}
                  onClick={() => navigate({ type: 'scenario', id: scn.id })}
                  className="text-left p-3 border border-stone-200 hover:border-amber-700 hover:bg-amber-50 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs text-stone-500">
                      {scn.framework_specific_id || scn.id}
                    </span>
                    {scn.risk_tier && (
                      <span className={`text-xs px-1.5 py-0.5 border ${tierClass(scn.risk_tier)}`}>
                        {scn.risk_tier}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-stone-900 leading-snug">{scn.name}</div>
                </button>
              ))}
            </div>
          </div>
        );
      })()}

      <SectionHeader count={reqs.length}>
        {reqs.length === fw.requirements.length ? 'Requirements' : `Filtered requirements`}
      </SectionHeader>

      <div className="mb-4 space-y-2">
        <div className="flex items-center gap-2 text-xs">
          <Search size={14} className="text-stone-400" />
          <input
            type="text"
            placeholder="Search by ID, title, or text…"
            value={filter.search}
            onChange={e => setFilter({ ...filter, search: e.target.value })}
            className="flex-1 px-2 py-1 border border-stone-300 bg-white text-sm focus:outline-none focus:border-amber-700"
          />
          {(filter.search || filter.kind || filter.group || filter.owner) && (
            <button
              onClick={() => setFilter({ kind: null, group: null, owner: null, search: '' })}
              className="text-stone-500 hover:text-stone-900 flex items-center gap-1"
            >
              <X size={14} /> clear
            </button>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <FilterDropdown label="kind" options={kinds} value={filter.kind} onChange={v => setFilter({ ...filter, kind: v })} />
          {groups.length > 1 && (
            <FilterDropdown label="group" options={groups} value={filter.group} onChange={v => setFilter({ ...filter, group: v })} />
          )}
          <FilterDropdown label="owner" options={owners} value={filter.owner} onChange={v => setFilter({ ...filter, owner: v })} />
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(grouped).map(([groupKey, items]) => (
          <div key={groupKey}>
            <div className="font-mono text-xs uppercase tracking-wider text-stone-500 mb-2 pb-1 border-b border-stone-200">
              {groupKey} <span className="text-stone-400">({items.length})</span>
            </div>
            <div className="divide-y divide-stone-100">
              {items.map(req => (
                <RequirementRow key={req.id} req={req} navigate={navigate} />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* SECTION 4 — Artifacts & supporting data */}
      <div id="step-4">
        <JourneyStep
          number={4}
          title="Artifacts & supporting data"
          caption="What the framework's metadata block carries beyond the requirements list."
        />
        {(() => {
          const visibleScenarios = (fw.scenarios || []).filter(s => scenarioAppliesToLens(s, lens));
          const visibleOQs = (fw.open_questions || []).filter(oq => oqAppliesToLens(oq.id, lens));
          const xwReqsCount = fw.requirements.filter(r => r.crosswalk && r.crosswalk.length > 0).length;
          const xwTargets = fw.requirements.reduce(
            (s, r) => s + (r.crosswalk || []).reduce((s2, e) => s2 + (e.refs || []).length, 0), 0
          );
          // Incoming references — count reqs in this framework that appear as targets in the reverse graph
          const incomingCount = fw.requirements.filter(r =>
            (DATA.reverse_graph[r.id] || []).length > 0
          ).length;
          const incomingTotal = fw.requirements.reduce(
            (s, r) => s + ((DATA.reverse_graph[r.id] || []).length), 0
          );
          return (
            <>
              <div className="grid grid-cols-2 lg:grid-cols-5 gap-px bg-stone-200 border border-stone-200 mb-6">
                <Stat label="Requirements" value={fw.requirements.length} />
                <Stat
                  label="Scenarios"
                  value={visibleScenarios.length}
                  sub={lens !== 'both' && visibleScenarios.length !== (fw.scenarios || []).length
                    ? `${(fw.scenarios || []).length - visibleScenarios.length} hidden`
                    : null}
                />
                <Stat
                  label="Open questions"
                  value={visibleOQs.length}
                  sub={lens !== 'both' && visibleOQs.length !== (fw.open_questions || []).length
                    ? `${(fw.open_questions || []).length - visibleOQs.length} hidden`
                    : null}
                />
                <Stat
                  label="Evidence families"
                  value={(fw.evidence_families || []).length}
                />
                <Stat
                  label="Crosswalks"
                  value={xwTargets}
                  sub={xwReqsCount > 0 ? `from ${xwReqsCount} reqs` : null}
                />
              </div>

              {/* Evidence families list */}
              {fw.evidence_families && fw.evidence_families.length > 0 && (
                <div className="mb-6">
                  <FieldLabel>Evidence families ({fw.evidence_families.length})</FieldLabel>
                  <div className="mt-2 grid grid-cols-1 lg:grid-cols-2 gap-2">
                    {fw.evidence_families.map((ef, i) => (
                      <div key={i} className="p-3 border border-stone-200 bg-white">
                        <div className="flex items-baseline justify-between mb-1">
                          <div className="font-mono text-xs text-stone-500">
                            {ef.id || `family-${i + 1}`}
                          </div>
                          {ef.typical_owner && (
                            <span className={`font-mono text-xs ${ownerClass(ef.typical_owner)}`}>
                              {ef.typical_owner}
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-stone-900 mb-1">{ef.name || ef.title || ef.label}</div>
                        {ef.why_auditor_cares && (
                          <div className="text-xs text-stone-600 leading-relaxed mb-1.5 italic">
                            {ef.why_auditor_cares}
                          </div>
                        )}
                        {ef.examples && Array.isArray(ef.examples) && ef.examples.length > 0 && (
                          <div className="text-xs text-stone-500 mb-1">
                            <span className="font-mono uppercase tracking-wider text-stone-400">examples · </span>
                            {ef.examples.slice(0, 3).join(', ')}
                            {ef.examples.length > 3 && <span className="text-stone-400"> +{ef.examples.length - 3} more</span>}
                          </div>
                        )}
                        {ef.cadence && (
                          <div className="text-xs text-stone-500">
                            <span className="font-mono uppercase tracking-wider text-stone-400">cadence · </span>
                            {ef.cadence}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Incoming references summary — this framework as a target */}
              {incomingCount > 0 && (
                <div className="mb-6 p-4 border border-stone-200 bg-stone-50">
                  <FieldLabel>This framework as a target</FieldLabel>
                  <p className="text-sm text-stone-700 mt-1 leading-relaxed">
                    <span className="font-mono text-stone-900 tabular-nums">{incomingCount}</span> requirements
                    in this framework are referenced by other frameworks
                    (<span className="font-mono text-stone-900 tabular-nums">{incomingTotal}</span> incoming references total).
                    Strong control implementation here discharges multiple framework obligations at once.
                  </p>
                </div>
              )}

              {/* Placeholder for not-yet-built entities */}
              <div className="mb-6 p-4 border border-dashed border-stone-300 bg-stone-50">
                <FieldLabel>Coming next</FieldLabel>
                <p className="text-sm text-stone-600 mt-1 leading-relaxed">
                  PB Controls library, SOPs, and Evidence vault as first-class entities are not yet built.
                  When they land, this section will surface counts of controls implementing this framework, SOPs executing those controls, and concrete evidence items linked to each requirement — the original "37 controls / 22 SOPs / 61 evidence" pattern from the dashboard wireframe.
                </p>
              </div>
            </>
          );
        })()}
      </div>
    </div>
  );
}

function FilterDropdown({ label, options, value, onChange }) {
  return (
    <div className="flex items-center gap-1">
      <span className="font-mono text-stone-500 uppercase tracking-wider">{label}:</span>
      <select
        value={value || ''}
        onChange={e => onChange(e.target.value || null)}
        className="bg-transparent border border-stone-300 px-1.5 py-0.5 text-xs focus:outline-none focus:border-amber-700"
      >
        <option value="">all</option>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function RequirementRow({ req, navigate }) {
  const lens = useLens();
  const xwCount = (req.crosswalk || []).reduce((s, e) => s + (e.refs || []).length, 0);
  const inCount = getReverseLinks(req.id).length;
  const ownerInfo = getOwnerForLens(req, lens);

  return (
    <button
      onClick={() => navigate({ type: 'requirement', id: req.id })}
      className="w-full text-left py-2.5 px-2 hover:bg-stone-100 transition-colors group flex items-start gap-4"
    >
      <div className="font-mono text-xs text-stone-500 group-hover:text-amber-700 w-32 shrink-0 pt-0.5">
        {req.native_id}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-stone-900 group-hover:text-amber-900 leading-snug">
          {req.title}
        </div>
        {req.tier && (
          <div className="mt-1">
            <span className={`text-xs px-1.5 py-0.5 border ${tierClass(req.tier)}`}>
              {req.tier}
            </span>
          </div>
        )}
      </div>
      <div className="flex items-center gap-3 shrink-0 text-xs text-stone-500">
        {ownerInfo.pending ? (
          <span className="font-mono text-amber-700" title={`Pending — ${ownerInfo.open_question}`}>
            pending
          </span>
        ) : ownerInfo.owner && ownerInfo.owner !== '—' ? (
          <span className={`font-mono ${ownerClass(ownerInfo.owner)}`}>
            {ownerInfo.owner}
            {ownerInfo.divergent && req.owner_by_model && <span className="text-amber-700 ml-0.5">*</span>}
          </span>
        ) : null}
        {xwCount > 0 && (
          <span className="font-mono" title="forward crosswalks">→ {xwCount}</span>
        )}
        {inCount > 0 && (
          <span className="font-mono text-amber-700" title="incoming references">{inCount} ←</span>
        )}
      </div>
    </button>
  );
}

// =============================================================================
// Requirement detail
// =============================================================================

function RequirementDetail({ reqId, navigate }) {
  const req = getRequirement(reqId);
  const lens = useLens();
  if (!req) return <div>Requirement not found: {reqId}</div>;

  const reverseLinks = getReverseLinks(reqId);
  const triggeredBy = (req.triggered_by_scenarios || []);
  const ownerInfo = getOwnerForLens(req, lens);

  // Find open questions blocking this requirement
  const blockingOQs = Object.values(DATA.all_open_questions).filter(oq =>
    (oq.blocks_requirements || []).includes(reqId)
  );

  return (
    <div className="max-w-3xl">
      {/* Header */}
      <div className="mb-8 pb-6 border-b border-stone-300">
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <FrameworkDot fwId={req._framework} />
          <span className={`font-mono text-xs uppercase tracking-wider ${frameworkLabelClass(req._framework)}`}>
            {getFrameworkLabel(req._framework)}
          </span>
          <span className="text-stone-300">·</span>
          <span className="font-mono text-xs uppercase tracking-wider text-stone-500">
            {req.kind.replace(/_/g, ' ')}
          </span>
          {req.tier && (
            <>
              <span className="text-stone-300">·</span>
              <span className={`text-xs px-1.5 py-0.5 border ${tierClass(req.tier)}`}>
                {req.tier}
              </span>
            </>
          )}
          {req.source_authority && req.source_authority !== 'binding' && (
            <Pill color="violet">{req.source_authority}</Pill>
          )}
        </div>
        <div className="flex items-baseline gap-3 mb-1">
          <span className="font-mono text-sm text-stone-500">{req.native_id}</span>
          <h1 className="font-serif text-2xl text-stone-950 tracking-tight">{req.title}</h1>
        </div>
        <div className="font-mono text-xs text-stone-400 mt-2">{reqId}</div>
        {(req.group || req.group_name) && (
          <div className="text-sm text-stone-600 mt-2">
            {req.group} {req.group_name && `· ${req.group_name}`}
          </div>
        )}
      </div>

      {/* Quick facts */}
      <div className="grid grid-cols-3 gap-px bg-stone-200 border border-stone-200 mb-8">
        {(req.owner || req.owner_by_model) && (
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>
              Owner
              {lens !== 'both' && (
                <span className="ml-1.5 normal-case tracking-normal text-stone-400">
                  · {LENS_LABELS[lens]}
                </span>
              )}
            </FieldLabel>
            {ownerInfo.pending ? (
              <button
                onClick={() => navigate({ type: 'openq', id: ownerInfo.open_question })}
                className="font-mono text-sm text-amber-700 underline hover:text-amber-900"
              >
                pending
              </button>
            ) : (
              <div className={`font-mono text-sm ${ownerClass(ownerInfo.owner)}`}>
                {ownerInfo.owner}
                {ownerInfo.divergent && <span className="text-amber-700 ml-1" title="varies by business model">*</span>}
              </div>
            )}
          </div>
        )}
        {req.applies && (
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Applies</FieldLabel>
            <div className="font-mono text-sm text-stone-800">{req.applies}</div>
          </div>
        )}
        {req.maturity_target && (
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Maturity target</FieldLabel>
            <div className="font-mono text-sm text-stone-800">{req.maturity_target}</div>
          </div>
        )}
      </div>

      {/* Effective dates */}
      {(req.effective_from || req.effective_until) && (
        <div className="mb-6 p-3 border-l-4 border-amber-700 bg-amber-50">
          <FieldLabel>Effective</FieldLabel>
          <div className="text-sm text-stone-800 mt-1">
            {req.effective_from && <span>from <span className="font-mono">{req.effective_from}</span></span>}
            {req.effective_until && <span> until <span className="font-mono">{req.effective_until}</span></span>}
          </div>
        </div>
      )}

      {/* Owner_by_model — flagging divergence (only when 'both' lens; otherwise primary card shows lens-specific owner) */}
      {req.owner_by_model && lens === 'both' && (
        <div className="mb-6 p-3 border border-amber-300 bg-amber-50">
          <div className="flex items-start gap-2">
            <AlertCircle size={16} className="text-amber-700 mt-0.5 shrink-0" />
            <div className="flex-1">
              <FieldLabel>Ownership diverges by business model</FieldLabel>
              <div className="text-sm text-stone-800 mt-1 space-y-1">
                <div><span className="font-mono text-xs">on_prem:</span> {req.owner_by_model.on_prem}</div>
                <div className="flex items-start gap-2">
                  <span className="font-mono text-xs">ai_factory:</span>
                  <span className="text-amber-800">
                    pending — blocked by{' '}
                    <button
                      onClick={() => navigate({ type: 'openq', id: req.owner_by_model.ai_factory.open_question })}
                      className="underline hover:text-amber-700"
                    >
                      {req.owner_by_model.ai_factory.open_question}
                    </button>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Core text */}
      <Field label="Requirement">
        {req.requirement && <p className="leading-relaxed">{req.requirement}</p>}
        {req.objective && !req.requirement && <p className="leading-relaxed">{req.objective}</p>}
      </Field>
      {req.objective && req.requirement && (
        <Field label="Objective"><p className="leading-relaxed">{req.objective}</p></Field>
      )}
      {req.auditor_intent && (
        <Field label="Auditor intent"><p className="leading-relaxed text-stone-700">{req.auditor_intent}</p></Field>
      )}

      {/* PB interpretation - the key field, highlighted */}
      {req.pb_interpretation && (
        <div className="mb-6 p-4 bg-stone-100 border-l-4 border-stone-700">
          <FieldLabel>PrivateBox interpretation</FieldLabel>
          <p className="leading-relaxed text-stone-900 mt-1">{req.pb_interpretation}</p>
        </div>
      )}

      {req.applies_rationale && (
        <Field label="Applies rationale">
          <p className="leading-relaxed text-stone-700">{req.applies_rationale}</p>
        </Field>
      )}

      {/* Role applicability */}
      {req.role_applicability && (
        <Field label="Role applicability">
          <div className="space-y-1">
            {Object.entries(req.role_applicability).filter(([k]) => !k.endsWith('_note')).map(([role, val]) => (
              <div key={role} className="flex items-baseline gap-3 text-sm">
                <span className="font-mono text-xs text-stone-500 w-24 capitalize">{role}</span>
                <span className="font-mono text-xs text-stone-800">{val}</span>
                {req.role_applicability[`${role}_note`] && (
                  <span className="text-stone-600 italic">— {req.role_applicability[`${role}_note`]}</span>
                )}
              </div>
            ))}
          </div>
        </Field>
      )}

      {/* Triggered by scenarios */}
      {triggeredBy.length > 0 && (
        <Field label={`Triggered by scenarios (${triggeredBy.length})`}>
          <div className="space-y-1">
            {triggeredBy.map(scnId => {
              const scn = getScenarioCluster(scnId);
              if (!scn) return <div key={scnId} className="text-stone-400">{scnId}</div>;
              return (
                <button
                  key={scnId}
                  onClick={() => navigate({ type: 'scenario', id: scnId })}
                  className="w-full text-left flex items-center gap-2 py-1 px-2 hover:bg-stone-100 transition-colors group"
                >
                  <Bookmark size={12} className="text-stone-400 group-hover:text-amber-700" />
                  <span className="font-mono text-xs text-stone-500">{scn.framework_specific_id || scnId}</span>
                  <span className="text-sm text-stone-800 group-hover:text-amber-900">{scn.name}</span>
                  {scn.risk_tier && (
                    <span className={`ml-auto text-xs px-1.5 py-0 border ${tierClass(scn.risk_tier)}`}>
                      {scn.risk_tier}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </Field>
      )}

      {/* Evidence */}
      {(req.documented_evidence || req.evidence || req.operational_evidence) && (
        <Field label="Evidence">
          {req.documented_evidence && (
            <div className="mb-2">
              <div className="text-xs font-mono text-stone-500 mb-1">Documented:</div>
              <ul className="list-none space-y-0.5">
                {req.documented_evidence.map((e, i) => (
                  <li key={i} className="text-sm text-stone-700 pl-3 border-l border-stone-200">{e}</li>
                ))}
              </ul>
            </div>
          )}
          {req.operational_evidence && (
            <div className="mb-2">
              <div className="text-xs font-mono text-stone-500 mb-1">Operational:</div>
              <p className="text-sm text-stone-700 leading-relaxed">{req.operational_evidence}</p>
            </div>
          )}
          {req.evidence && !req.documented_evidence && (
            <p className="text-sm text-stone-700 leading-relaxed">{req.evidence}</p>
          )}
          {req.audit_methods && (
            <div className="text-xs text-stone-600 mt-2">
              <span className="font-mono uppercase">methods:</span> {req.audit_methods.join(', ')}
              {req.cadence && <span className="ml-3"><span className="font-mono uppercase">cadence:</span> {req.cadence}</span>}
            </div>
          )}
        </Field>
      )}

      {req.implementation && <Field label="Implementation"><p className="text-sm leading-relaxed text-stone-700">{req.implementation}</p></Field>}

      {req.pitfall && (
        <div className="mb-6 p-3 border-l-4 border-red-700 bg-red-50">
          <FieldLabel>Pitfall</FieldLabel>
          <p className="text-sm text-stone-800 leading-relaxed mt-1">{req.pitfall}</p>
        </div>
      )}
      {req.failure_modes && (
        <div className="mb-6 p-3 border-l-4 border-red-700 bg-red-50">
          <FieldLabel>Failure modes</FieldLabel>
          <p className="text-sm text-stone-800 leading-relaxed mt-1">{req.failure_modes}</p>
        </div>
      )}

      {req.good_vs_audit_ready && (
        <Field label="Good vs audit-ready">
          <div className="space-y-2 text-sm">
            <div><span className="font-mono text-xs text-stone-500 uppercase">good:</span> <span className="text-stone-700">{req.good_vs_audit_ready.good}</span></div>
            <div><span className="font-mono text-xs text-amber-700 uppercase">audit-ready:</span> <span className="text-stone-800">{req.good_vs_audit_ready.audit_ready}</span></div>
          </div>
        </Field>
      )}

      {req.remediation && <Field label="Remediation"><p className="text-sm leading-relaxed text-stone-700">{req.remediation}</p></Field>}

      {(req.external_safe_claim || req.external_safe_phrasing) && (
        <div className="mb-6 p-4 bg-emerald-50 border-l-4 border-emerald-700">
          <FieldLabel>External-safe phrasing</FieldLabel>
          <p className="text-stone-800 leading-relaxed italic mt-1">
            "{req.external_safe_claim || req.external_safe_phrasing}"
          </p>
        </div>
      )}

      {req.scope_note && <Field label="Scope note"><p className="text-sm leading-relaxed text-stone-700 italic">{req.scope_note}</p></Field>}

      {/* Crosswalks (forward) — grouped by framework, with per-target notes */}
      {req.crosswalk && req.crosswalk.length > 0 && (
        <div className="mb-8">
          <SectionHeader count={req.crosswalk.reduce((s, e) => s + e.refs.length, 0)}>
            Crosswalks (forward)
          </SectionHeader>
          {(() => {
            // Group by target framework
            const byFw = {};
            for (const entry of req.crosswalk) {
              if (!byFw[entry.framework]) byFw[entry.framework] = [];
              byFw[entry.framework].push(entry);
            }
            return Object.entries(byFw).map(([fw, entries]) => (
              <div key={fw} className="mb-5">
                <div className="flex items-center gap-2 mb-2">
                  <FrameworkDot fwId={fw} />
                  <span className={`font-mono text-xs uppercase tracking-wider ${frameworkLabelClass(fw)}`}>
                    {getFrameworkLabel(fw)}
                  </span>
                  <span className="font-mono text-xs text-stone-400">
                    {entries.reduce((s, e) => s + e.refs.length, 0)}
                  </span>
                </div>
                <div className="ml-3 space-y-2">
                  {entries.map((entry, j) => (
                    <div key={j} className="border-l-2 border-stone-200 pl-3 py-1">
                      <div className="space-y-0.5">
                        {entry.refs.map(ref => {
                          const target = getRequirement(ref);
                          return (
                            <ReqLink key={ref} reqId={ref} navigate={navigate} withDot={false}>
                              {target ? `— ${target.title}` : ''}
                            </ReqLink>
                          );
                        })}
                      </div>
                      {entry.note && (
                        <div className="text-xs text-stone-600 italic leading-relaxed mt-1">
                          {entry.note}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ));
          })()}
        </div>
      )}

      {/* Reverse references */}
      {reverseLinks.length > 0 && (
        <div className="mb-8">
          <SectionHeader count={reverseLinks.length}>Referenced by</SectionHeader>
          <p className="text-xs text-stone-500 mb-2">
            Other frameworks point to this requirement — reverse graph resolved at load.
          </p>
          <div className="space-y-1">
            {reverseLinks.map((link, i) => {
              const src = getRequirement(link.source_id);
              return (
                <div key={i} className="flex items-baseline gap-3 py-1.5 border-l-2 border-stone-200 pl-3 hover:border-amber-700 transition-colors">
                  <ReqLink reqId={link.source_id} navigate={navigate}>
                    {src ? `— ${src.title}` : ''}
                  </ReqLink>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Open questions */}
      {blockingOQs.length > 0 && (
        <div className="mb-8">
          <SectionHeader count={blockingOQs.length}>Blocked by open questions</SectionHeader>
          <div className="space-y-2">
            {blockingOQs.map(oq => (
              <button
                key={oq.id}
                onClick={() => navigate({ type: 'openq', id: oq.id })}
                className="w-full text-left p-3 border border-amber-300 bg-amber-50 hover:bg-amber-100 transition-colors group"
              >
                <div className="flex items-start gap-2">
                  <HelpCircle size={14} className="text-amber-700 mt-0.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-mono text-xs text-amber-700">{oq.id}</div>
                    <div className="text-sm text-stone-900 mt-0.5">{oq.question}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Source provenance */}
      {(req.source_refs || req.source_authority) && (
        <div className="mt-8 pt-4 border-t border-stone-200 text-xs text-stone-500">
          {req.source_authority && <span className="font-mono uppercase mr-2">authority: {req.source_authority}</span>}
          {req.source_refs && req.source_refs.length > 0 && (
            <span className="font-mono">{req.source_refs.join(' · ')}</span>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Scenario detail
// =============================================================================

function ScenarioDetail({ scnId, navigate }) {
  const scn = getScenarioCluster(scnId);
  const lens = useLens();
  if (!scn) return <div>Scenario not found: {scnId}</div>;

  const directReqs = scn.cluster.direct;
  const xwReqs = scn.cluster.via_crosswalks;
  const totalReqs = directReqs.length + xwReqs.length;

  // Group cross-walked by target framework
  const xwByFramework = {};
  xwReqs.forEach(r => {
    if (!xwByFramework[r.framework]) xwByFramework[r.framework] = [];
    xwByFramework[r.framework].push(r);
  });

  return (
    <div className="max-w-3xl">
      {/* Header */}
      <div className="mb-8 pb-6 border-b border-stone-300">
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <FrameworkDot fwId={scn.framework} />
          <span className={`font-mono text-xs uppercase tracking-wider ${frameworkLabelClass(scn.framework)}`}>
            {getFrameworkLabel(scn.framework)}
          </span>
          <span className="text-stone-300">·</span>
          <span className="font-mono text-xs uppercase tracking-wider text-stone-500">scenario</span>
          {scn.risk_tier && (
            <>
              <span className="text-stone-300">·</span>
              <span className={`text-xs px-1.5 py-0.5 border ${tierClass(scn.risk_tier)}`}>
                {scn.risk_tier}
              </span>
            </>
          )}
        </div>
        <div className="flex items-baseline gap-3 mb-1">
          <span className="font-mono text-sm text-stone-500">{scn.framework_specific_id}</span>
          <h1 className="font-serif text-2xl text-stone-950 tracking-tight">{scn.name}</h1>
        </div>
        <div className="font-mono text-xs text-stone-400 mt-2">{scn.id}</div>
      </div>

      {/* Roles */}
      <div className="grid grid-cols-2 gap-px bg-stone-200 border border-stone-200 mb-8">
        {scn.pb_role && (
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>PrivateBox role</FieldLabel>
            <div className="font-mono text-sm text-stone-900 capitalize">{scn.pb_role}</div>
          </div>
        )}
        {scn.customer_role && (
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Customer role</FieldLabel>
            <div className="font-mono text-sm text-stone-900 capitalize">{scn.customer_role}</div>
          </div>
        )}
      </div>

      {/* Description */}
      {scn.description && <Field label="Description"><p className="leading-relaxed">{scn.description}</p></Field>}

      {scn.applies_to_business_models && (
        <div className="mb-6 flex items-center gap-2">
          <FieldLabel>Business models:</FieldLabel>
          {scn.applies_to_business_models.map(bm => (
            <Pill key={bm} color={lens === bm ? 'amber' : 'stone'}>{bm}</Pill>
          ))}
          {lens !== 'both' && !scn.applies_to_business_models.includes(lens) && (
            <span className="font-mono text-xs text-amber-700">
              · doesn't apply to {LENS_LABELS[lens]}
            </span>
          )}
        </div>
      )}

      {scn.legal_basis && <Field label="Legal basis"><p className="text-sm leading-relaxed text-stone-700">{scn.legal_basis}</p></Field>}
      {scn.why_role_allocation && <Field label="Why this role allocation"><p className="text-sm leading-relaxed text-stone-700">{scn.why_role_allocation}</p></Field>}
      {scn.on_prem_note && <Field label="On-prem note"><p className="text-sm leading-relaxed text-stone-700">{scn.on_prem_note}</p></Field>}
      {scn.shared_responsibility && <Field label="Shared responsibility"><p className="text-sm leading-relaxed text-stone-700">{scn.shared_responsibility}</p></Field>}
      {scn.contractual_implication && <Field label="Contractual implication"><p className="text-sm leading-relaxed text-stone-700">{scn.contractual_implication}</p></Field>}

      {scn.common_misclassification && (
        <div className="mb-6 p-3 border-l-4 border-red-700 bg-red-50">
          <FieldLabel>Common misclassification</FieldLabel>
          <p className="text-sm text-stone-800 leading-relaxed mt-1">{scn.common_misclassification}</p>
        </div>
      )}
      {scn.risk_if_misclassified && (
        <div className="mb-6 p-3 border-l-4 border-red-700 bg-red-50">
          <FieldLabel>Risk if misclassified</FieldLabel>
          <p className="text-sm text-stone-800 leading-relaxed mt-1">{scn.risk_if_misclassified}</p>
        </div>
      )}

      {(scn.sales_safe_wording || scn.sales_safe_explanation) && (
        <div className="mb-6 p-4 bg-emerald-50 border-l-4 border-emerald-700">
          <FieldLabel>Sales-safe phrasing</FieldLabel>
          <p className="text-stone-800 leading-relaxed italic mt-1">"{scn.sales_safe_wording || scn.sales_safe_explanation}"</p>
        </div>
      )}

      {/* THE KEY VIEW: cluster expansion */}
      <div className="mb-8">
        <SectionHeader count={totalReqs}>Activated requirements (cluster)</SectionHeader>
        <p className="text-sm text-stone-600 mb-4 leading-relaxed">
          Direct triggers within {getFrameworkLabel(scn.framework)}, plus 1-hop crosswalk expansion to other frameworks.
          Doing this scenario well requires attention to all {totalReqs} requirements — not just the {directReqs.length} regulatory triggers.
        </p>

        {/* Direct triggers */}
        <div className="mb-6">
          <div className="font-mono text-xs uppercase tracking-wider text-stone-700 mb-2">
            Direct ({directReqs.length}) <span className="text-stone-500">— from this framework</span>
          </div>
          <div className="space-y-1">
            {directReqs.map(t => {
              const r = getRequirement(t.requirement_id);
              return (
                <div key={t.requirement_id} className="border-l-2 border-stone-700 pl-3 py-1.5">
                  <ReqLink reqId={t.requirement_id} navigate={navigate}>
                    {r ? `— ${r.title}` : ''}
                  </ReqLink>
                  {t.note && (
                    <div className="text-xs text-stone-600 italic mt-0.5 ml-6 leading-relaxed">{t.note}</div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Cross-framework expansion */}
        {Object.keys(xwByFramework).length > 0 && (
          <div className="mb-2">
            <div className="font-mono text-xs uppercase tracking-wider text-amber-800 mb-2">
              Via crosswalks ({xwReqs.length})
              <span className="text-stone-500"> — cross-framework activation</span>
            </div>
            {Object.entries(xwByFramework).map(([fw, items]) => (
              <div key={fw} className="mb-3">
                <div className="flex items-center gap-2 mb-1">
                  <FrameworkDot fwId={fw} />
                  <span className={`font-mono text-xs uppercase tracking-wider ${frameworkLabelClass(fw)}`}>
                    {getFrameworkLabel(fw)} ({items.length})
                  </span>
                </div>
                <div className="ml-3 space-y-1">
                  {items.map(t => {
                    const r = getRequirement(t.requirement_id);
                    return (
                      <div key={t.requirement_id} className="border-l-2 border-amber-300 pl-3 py-1">
                        <ReqLink reqId={t.requirement_id} navigate={navigate} withDot={false}>
                          {r ? `— ${r.title}` : ''}
                        </ReqLink>
                        <div className="text-xs text-stone-500 italic mt-0.5">
                          via{' '}
                          <button
                            onClick={() => navigate({ type: 'requirement', id: t.via })}
                            className="font-mono text-stone-600 hover:text-amber-700"
                          >
                            {t.via}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Open Questions
// =============================================================================

function OpenQuestionsView({ navigate, focusId }) {
  const [filter, setFilter] = useState('pending');
  const lens = useLens();
  const allOQs = Object.values(DATA.all_open_questions);
  // Lens filter first (hide AI Factory-specific OQs in on-prem lens), then status filter
  const lensFiltered = allOQs.filter(oq => oqAppliesToLens(oq.id, lens));
  const filtered = filter === 'all' ? lensFiltered : lensFiltered.filter(oq => oq.decision_status === filter);

  if (focusId) {
    const oq = getOpenQuestion(focusId);
    if (oq) return <OpenQuestionDetail oq={oq} navigate={navigate} />;
  }

  const counts = {
    pending: lensFiltered.filter(oq => oq.decision_status === 'pending').length,
    resolved: lensFiltered.filter(oq => oq.decision_status === 'resolved').length,
    deferred: lensFiltered.filter(oq => oq.decision_status === 'deferred').length,
    all: lensFiltered.length,
  };
  const hiddenByLens = allOQs.length - lensFiltered.length;

  return (
    <div className="max-w-3xl">
      <div className="mb-8">
        <h1 className="font-serif text-3xl text-stone-950 tracking-tight mb-2">
          Open Questions
        </h1>
        <p className="text-stone-600 leading-relaxed max-w-2xl">
          Unresolved governance and business decisions that block requirement resolution.
          Each question lists the requirements and scenarios it blocks.
        </p>
        {hiddenByLens > 0 && (
          <div className="mt-3 text-xs font-mono text-stone-500">
            <span className="text-amber-700">{hiddenByLens}</span> questions hidden by {LENS_LABELS[lens]} lens
            <span className="text-stone-400"> · these block AI Factory readiness only</span>
          </div>
        )}
      </div>

      <div className="flex gap-1 mb-6 border-b border-stone-300">
        {['pending', 'resolved', 'deferred', 'all'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 text-sm border-b-2 transition-colors ${
              filter === f
                ? 'border-amber-700 text-amber-900 font-medium'
                : 'border-transparent text-stone-500 hover:text-stone-900'
            }`}
          >
            <span className="capitalize">{f}</span>
            {counts[f] !== undefined && <span className="ml-1.5 font-mono text-xs">{counts[f]}</span>}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map(oq => (
          <button
            key={oq.id}
            onClick={() => navigate({ type: 'openq', id: oq.id })}
            className="w-full text-left p-4 border border-stone-200 hover:border-amber-700 hover:bg-amber-50 transition-colors group"
          >
            <div className="flex items-start gap-3">
              <HelpCircle size={16} className="text-amber-700 mt-0.5 shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-mono text-xs text-stone-500 mb-1">{oq.id}</div>
                <div className="text-stone-900 group-hover:text-amber-900 leading-snug">{oq.question}</div>
                <div className="flex items-center gap-3 mt-2 text-xs text-stone-500">
                  <span>{(oq.blocks_requirements || []).length} requirements blocked</span>
                  {(oq.blocks_scenarios || []).length > 0 && (
                    <span>· {(oq.blocks_scenarios || []).length} scenarios blocked</span>
                  )}
                  {oq.decision_owner && <span>· owner: {oq.decision_owner}</span>}
                </div>
              </div>
              <ArrowRight size={16} className="text-stone-400 group-hover:text-amber-700" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function OpenQuestionDetail({ oq, navigate }) {
  return (
    <div className="max-w-3xl">
      <div className="mb-8 pb-6 border-b border-stone-300">
        <div className="flex items-center gap-2 mb-3">
          <Pill color="amber">{oq.decision_status}</Pill>
          {(oq._frameworks || []).map(fw => (
            <span key={fw} className="flex items-center gap-1.5">
              <FrameworkDot fwId={fw} />
              <span className={`font-mono text-xs ${frameworkLabelClass(fw)}`}>{getFrameworkLabel(fw)}</span>
            </span>
          ))}
        </div>
        <h1 className="font-serif text-2xl text-stone-950 tracking-tight mb-2">{oq.question}</h1>
        <div className="font-mono text-xs text-stone-400 mt-2">{oq.id}</div>
      </div>

      {oq.candidate_answers && oq.candidate_answers.length > 0 && (
        <Field label="Candidate answers">
          <ul className="space-y-1.5">
            {oq.candidate_answers.map((a, i) => (
              <li key={i} className="text-stone-800 pl-3 border-l border-stone-300">{a}</li>
            ))}
          </ul>
        </Field>
      )}

      {oq.notes && (
        <div className="mb-6 p-4 bg-stone-100 border-l-4 border-stone-700">
          <FieldLabel>Notes</FieldLabel>
          <p className="leading-relaxed text-stone-800 mt-1">{oq.notes}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-px bg-stone-200 border border-stone-200 mb-8">
        {oq.decision_owner && (
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Decision owner</FieldLabel>
            <div className="text-sm text-stone-800">{oq.decision_owner}</div>
          </div>
        )}
        {oq.created && (
          <div className="bg-stone-50 px-4 py-2.5">
            <FieldLabel>Created</FieldLabel>
            <div className="font-mono text-sm text-stone-800">{oq.created}</div>
          </div>
        )}
      </div>

      {oq.blocks_requirements && oq.blocks_requirements.length > 0 && (
        <div className="mb-8">
          <SectionHeader count={oq.blocks_requirements.length}>Blocks requirements</SectionHeader>
          <div className="space-y-1">
            {oq.blocks_requirements.map(rid => {
              const r = getRequirement(rid);
              return (
                <div key={rid} className="py-1 border-l-2 border-amber-300 pl-3">
                  <ReqLink reqId={rid} navigate={navigate}>
                    {r ? `— ${r.title}` : ''}
                  </ReqLink>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {oq.blocks_scenarios && oq.blocks_scenarios.length > 0 && (
        <div className="mb-8">
          <SectionHeader count={oq.blocks_scenarios.length}>Blocks scenarios</SectionHeader>
          <div className="space-y-1">
            {oq.blocks_scenarios.map(sid => {
              const s = getScenarioCluster(sid);
              return (
                <button
                  key={sid}
                  onClick={() => navigate({ type: 'scenario', id: sid })}
                  className="w-full text-left flex items-baseline gap-2 py-1 px-2 hover:bg-stone-100 transition-colors"
                >
                  <Bookmark size={12} className="text-stone-400" />
                  <span className="font-mono text-xs text-stone-500">{s ? s.framework_specific_id : sid}</span>
                  {s && <span className="text-sm text-stone-800">{s.name}</span>}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Graph view
// =============================================================================

function GraphView({ navigate }) {
  const allReqs = useMemo(() => {
    const reqs = [];
    Object.values(DATA.frameworks).forEach(fw => {
      Object.values(fw.requirements_index).forEach(r => {
        reqs.push({ ...r, _framework: fw._id });
      });
    });
    return reqs;
  }, []);

  const ranked = useMemo(() => {
    return Object.entries(DATA.anchor_stats)
      .filter(([_, c]) => c >= 1)
      .sort(([, a], [, b]) => b - a)
      .map(([reqId, count]) => {
        const req = getRequirement(reqId);
        return req ? { reqId, count, req } : null;
      })
      .filter(Boolean);
  }, []);

  const distribution = useMemo(() => {
    const dist = {};
    Object.values(DATA.anchor_stats).forEach(c => {
      dist[c] = (dist[c] || 0) + 1;
    });
    return dist;
  }, []);

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h1 className="font-serif text-3xl text-stone-950 tracking-tight mb-2">
          Cross-framework graph
        </h1>
        <p className="text-stone-600 leading-relaxed max-w-2xl">
          Requirements ranked by incoming-link count.
          Cross-framework anchor requirements are leverage points — investing in one
          discharges multiple framework obligations in parallel.
        </p>
      </div>

      <div className="mb-8 grid grid-cols-4 gap-px bg-stone-200 border border-stone-200">
        <Stat label="Forward edges" value={Object.values(DATA.forward_graph).reduce((s, v) => s + v.length, 0)} />
        <Stat label="Anchor reqs" value={Object.values(DATA.anchor_stats).filter(c => c >= 2).length} sub="2+ in" />
        <Stat label="Hub reqs" value={Object.values(DATA.anchor_stats).filter(c => c >= 3).length} sub="3+ in" />
        <Stat label="Most-linked" value={Math.max(...Object.values(DATA.anchor_stats))} sub="incoming" />
      </div>

      <div className="mb-8">
        <SectionHeader>Incoming-link distribution</SectionHeader>
        <div className="grid grid-cols-1 gap-1">
          {Object.entries(distribution).sort(([a], [b]) => Number(b) - Number(a)).map(([k, v]) => (
            <div key={k} className="flex items-center gap-3 text-sm">
              <span className="font-mono text-xs text-stone-500 w-24">{k} incoming</span>
              <div className="flex-1 h-5 bg-stone-100 relative">
                <div
                  className="h-full bg-amber-700"
                  style={{ width: `${Math.min(100, (v / 50) * 100)}%` }}
                />
              </div>
              <span className="font-mono text-xs text-stone-700 tabular-nums w-10 text-right">{v}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <SectionHeader count={ranked.length}>All anchored requirements</SectionHeader>
        <div className="space-y-2">
          {ranked.map(({ reqId, count, req }) => {
            const sources = getReverseLinks(reqId);
            const fws = [...new Set(sources.map(s => s.source_framework))];
            return (
              <button
                key={reqId}
                onClick={() => navigate({ type: 'requirement', id: reqId })}
                className="w-full text-left flex items-center gap-4 p-3 border border-stone-200 hover:border-amber-700 hover:bg-amber-50 transition-colors group"
              >
                <div className={`font-serif text-3xl tabular-nums w-10 text-right ${count >= 3 ? 'text-amber-800' : 'text-stone-700'}`}>
                  {count}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <FrameworkDot fwId={req._framework} />
                    <span className="font-mono text-xs text-stone-500">{reqId}</span>
                  </div>
                  <div className="text-stone-900 truncate">{req.title}</div>
                </div>
                <div className="flex items-center gap-2 text-xs text-stone-500 shrink-0">
                  {fws.map(f => <FrameworkDot key={f} fwId={f} />)}
                  <span className="font-mono">{fws.length} fw</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// App shell
// =============================================================================

export default function App() {
  const [view, setView] = useState({ type: 'home' });
  const [history, setHistory] = useState([]);
  const [lens, setLens] = useState('both');

  const navigate = useCallback((newView) => {
    setHistory(h => [...h, view]);
    setView(newView);
    window.scrollTo(0, 0);
  }, [view]);

  const back = useCallback(() => {
    setHistory(h => {
      if (h.length === 0) return h;
      setView(h[h.length - 1]);
      return h.slice(0, -1);
    });
    window.scrollTo(0, 0);
  }, []);

  return (
    <LensContext.Provider value={lens}>
      <LensSetterContext.Provider value={setLens}>
        <div className="min-h-screen bg-stone-50 text-stone-900" style={{ fontFamily: 'ui-sans-serif, system-ui, sans-serif' }}>
          <Header view={view} navigate={navigate} back={back} canBack={history.length > 0} />
          <div className="flex">
            <Sidebar navigate={navigate} currentView={view} />
            <main className="flex-1 px-8 py-10 max-w-none overflow-x-hidden">
              {view.type === 'home' && <HomePage navigate={navigate} />}
              {view.type === 'framework' && <FrameworkDetail fwId={view.id} navigate={navigate} />}
              {view.type === 'requirement' && <RequirementDetail reqId={view.id} navigate={navigate} />}
              {view.type === 'scenario' && <ScenarioDetail scnId={view.id} navigate={navigate} />}
              {view.type === 'openq' && <OpenQuestionsView navigate={navigate} focusId={view.id} />}
              {view.type === 'graph' && <GraphView navigate={navigate} />}
            </main>
          </div>
        </div>
      </LensSetterContext.Provider>
    </LensContext.Provider>
  );
}
