---
name: os-development
description: Use this skill when extending or modifying the GRC OS React app (os/src/App.jsx). Triggers include adding a new view, changing the lens system, adding a new entity type (Controls, Risks, AI Systems, Vendors, Evidence vault, SOPs), modifying the navigation, restyling components, or fixing a UI bug. Also use when adding new framework-specific overview content (FRAMEWORK_OVERVIEW). Do NOT use for editing framework YAMLs (that's the compliance-framework-author skill) or for adding new build-pipeline scripts.
---

# Extending the GRC OS

This skill captures the React OS architecture so a fresh Claude session can extend it without reverse-engineering. Read in full before substantive UI work.

## File layout

The OS is one React app served by Vite:

```
os/
├── package.json                       # react, lucide-react, vite, tailwind
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.jsx                       # vite entry; wraps App in StrictMode
    ├── index.css                      # @tailwind directives only
    ├── data.json                      # built artifact — DO NOT hand-edit
    └── App.jsx                        # ALL UI lives here, ~1700 lines
```

`App.jsx` is intentionally one file. Single-file is faster to scan, faster to grep, faster to load into Claude's context. It's well-organised by section banners (`// ===` blocks). When it grows past ~3000 lines, consider splitting — but resist until then.

## Constraints

- **No arbitrary Tailwind values.** `bg-[#abc]` and `w-[300px]` will not work; the production Tailwind build only generates classes named in `tailwind.config.js`'s scanned files. Use core utilities (`bg-stone-50`, `w-full`, `max-w-3xl`). The migration kit's `make all` runs a regex check that catches arbitrary values.
- **No external CSS files** beyond `index.css`. Style with utility classes; if a custom style is unavoidable, use inline `style={{ }}` (the existing app does this once for `fontFamily`).
- **No new heavy dependencies** without justification. Current deps: React, lucide-react. No charting library, no animation library, no router (we use a custom view state machine — see Navigation below).
- **No client-side persistence.** The OS is currently read-only. When write paths land, they'll need a backend; don't reach for localStorage to fake it.

## Data shape

`data.json` (built by `build/build_os_data.py`) has this top-level structure:

```typescript
{
  frameworks: {
    "iso-27001": {
      _id, id, full_name, version, issuer, type, audit_type, certifiable,
      pb_application: { why_chosen, scope_decisions: { on_prem, ai_factory }, top_risks },
      requirements: [{ id, native_id, kind, title, owner, owner_by_model?, requirement?, objective?, business_models, crosswalk?, ... }],
      requirements_index: { [req.id]: req },     // for fast lookup
      scenarios: [{ id, name, applies_to_business_models, ... }],
      open_questions: [{ id, question, decision_status, blocks_requirements, blocks_scenarios }],
      evidence_families: [{ id, name, examples, why_auditor_cares, cadence, typical_owner }],
      effective_dates: [{ milestone, date, obligations, status, notes }],
      roles: [string],
      tiers: [string],
      shared_responsibility_model: [...],
    },
    "iso-27701": { ... },
    "eu-ai-act": { ... },
  },
  forward_graph: { [reqId]: [{ target_id, target_framework, source_framework, note }] },
  reverse_graph: { [reqId]: [{ source_id, source_framework, target_framework, note }] },
  anchor_stats: { [reqId]: number },        // incoming-link count per requirement
  scenario_clusters: { [scnId]: { id, framework, ..., cluster: { direct: [], via_crosswalks: [] } } },
  all_open_questions: { [oqId]: { id, question, ..., _frameworks: [fwId] } },
}
```

When adding entity types (Controls, Risks, AI Systems, etc.), extend the top-level object. Don't fold them into `frameworks{}` — they're cross-cutting.

## Helpers (top of App.jsx)

These lookup functions assume `data.json` shape. Use them, don't re-implement:

- `getRequirement(reqId)` — finds across all frameworks
- `getReverseLinks(reqId)` — returns inbound crosswalk entries
- `getOpenQuestion(oqId)`
- `getScenarioCluster(scnId)` — returns scenario + its activation cluster
- `tierClass(tier)` — color class for risk tiers
- `ownerClass(owner)` — color class for owner enum

Add new helpers at the top, near the existing ones. Keep them pure functions of `DATA`.

## Lens system

The two-business-model lens (`on-prem` / `ai-factory` / `both`) propagates through everything via React Context.

**Architecture:**

```jsx
const LensContext = createContext('both');
const LensSetterContext = createContext(() => {});
const useLens = () => useContext(LensContext);

function App() {
  const [lens, setLens] = useState('both');
  return (
    <LensContext.Provider value={lens}>
      <LensSetterContext.Provider value={setLens}>
        ...
      </LensSetterContext.Provider>
    </LensContext.Provider>
  );
}
```

**Helper functions for lens-aware rendering:**

- `getOwnerForLens(req, lens)` — returns `{ owner, pending, open_question, divergent, on_prem, ai_factory }`. Handles three cases: no `owner_by_model` (return base owner), single-model lens (return that model's owner), `both` lens (return base + flag divergence). When AI Factory owner is `{status: 'pending', open_question: 'oq-...'}`, returns `pending: true` with the OQ id.
- `scenarioAppliesToLens(scn, lens)` — checks `applies_to_business_models`. Returns true for `both` lens regardless.
- `oqAppliesToLens(oqId, lens)` — heuristic on id pattern (AI-factory-specific OQs hidden in on-prem lens).

**Adding a lens-aware component:**

```jsx
function MyComponent({ req }) {
  const lens = useLens();                      // hook at top of component
  const ownerInfo = getOwnerForLens(req, lens);
  // render using ownerInfo.owner, ownerInfo.pending, etc.
}
```

**Hook discipline:** `useLens()` must be at the top of the component, never inside an IIFE or conditional. If you need lens inside a `.map()` or `.filter()`, capture it in a const at the top and reference the const in the callback.

**Lens-aware filtering pattern:**

```jsx
function MyView() {
  const lens = useLens();
  const filtered = items.filter(item => /* lens-specific predicate */);
  const hidden = items.length - filtered.length;
  return (
    <>
      {hidden > 0 && (
        <span>{hidden} hidden by {LENS_LABELS[lens]} lens</span>
      )}
      {filtered.map(...)}
    </>
  );
}
```

## Navigation (no router)

State machine in `App`:

```jsx
const [view, setView] = useState({ type: 'home' });
const [history, setHistory] = useState([]);
```

`view.type` is one of: `'home'`, `'framework'`, `'requirement'`, `'scenario'`, `'openq'`, `'graph'`. Other fields on `view` carry the entity id (e.g., `{ type: 'framework', id: 'iso-27001' }`).

`navigate(newView)` pushes the current view onto `history` and switches. `back()` pops.

**Adding a new view type:**

1. Define the component: `function MyNewView({ ...props, navigate }) { ... }`
2. In `App`, add a render branch: `{view.type === 'mynew' && <MyNewView id={view.id} navigate={navigate} />}`
3. Add a sidebar entry in `Sidebar`: `{ id: 'mynew', label: 'My new', icon: <Icon size={16} />, onClick: () => navigate({ type: 'mynew' }) }`
4. Anywhere you want to link in: `<button onClick={() => navigate({ type: 'mynew', id: someId })}>...</button>`

No router, no URL state. This is deliberate — the OS is a single-page tool, not a public web app. Browser back-button doesn't work; the in-app back arrow in the header does.

## Component conventions

**Styling vocabulary** (consistent across all views):
- Background: `bg-stone-50` (page), `bg-white` (cards), `bg-amber-50` (highlights/active), `bg-stone-100` (subtle hover)
- Borders: `border-stone-200` (subtle), `border-stone-300` (visible), `border-amber-700` (accent)
- Text: `text-stone-950` (headings), `text-stone-900` (body), `text-stone-700` (secondary), `text-stone-500` (meta), `text-stone-400` (least)
- Accent: `text-amber-800` / `text-amber-900` for emphasis; `text-amber-700` for hover
- Owner colors: see `ownerClass()` helper
- Tier colors: see `tierClass()` helper

**Typography:**
- `font-serif` for headings (h1, h2, JourneyStep titles)
- `font-mono` for ids, numbers, owner codes, framework metadata
- Default sans for body
- Always pair `tabular-nums` with monospace numbers when they need to align

**Section header components:**
- `SectionHeader` — small, for subsections inside a view
- `JourneyStep` — large, numbered, for the 4-section spine in FrameworkDetail. Use this when you want the user to feel "this is step N of a journey."

**Field labels:** `<FieldLabel>...</FieldLabel>` for the small uppercase label above values.

**Pills:** `<Pill color="amber|emerald|stone|red|sky|violet">label</Pill>` for tags / chips / badges.

**Stats:** `<Stat label="..." value={n} sub="optional subtitle" />` for metric strips.

## Adding framework-specific overview content

The `FRAMEWORK_OVERVIEW` map at the top of App.jsx provides Section 1 content for the user-journey spine in FrameworkDetail. When a new framework lands:

```jsx
const FRAMEWORK_OVERVIEW = {
  // ... existing
  'iso-42001': {
    plain_english: "ISO/IEC 42001 is the international standard for an Artificial Intelligence Management System...",
    key_concepts: [
      { label: 'AIMS', description: '...' },
      { label: 'AI lifecycle', description: '...' },
      { label: 'Annex A controls', description: '...' },
      { label: 'Annex B impacts', description: '...' },
    ],
  },
};
```

Each framework gets exactly four key concepts. Pick the four words an auditor or buyer would expect a PB founder to know cold. The plain-English paragraph is non-PB-specific (no "for PrivateBox" framing) — that's Section 2's job.

When this map outgrows comfortable inline authoring (4+ frameworks), move it to YAML (`framework.plain_english`, `framework.key_concepts`) and read from `DATA.frameworks[fwId]`.

## Adding a new entity type (Controls, Risks, etc.)

The road from "concept" to "rendered view" for a new entity type:

1. **Schema first.** Define the entity's shape in `docs/schema-v2.md`. Add a validator rule.
2. **Source.** Decide where the entity lives. If it's framework-bound (e.g., framework-specific risks), add it inside the framework YAML. If cross-cutting (e.g., PB Controls library satisfying multiple frameworks), create `entities/controls.yaml` (new top-level dir) or similar.
3. **Build pipeline.** Update `build/build_os_data.py` to load + index the entity. Add it to the top-level `data.json` shape. Update reverse_graph computation if entities reference requirements.
4. **Helpers.** Add lookup functions at top of App.jsx: `getControl(controlId)`, etc.
5. **List view.** Render the entity's index page (sidebar entry + view component).
6. **Detail view.** Render single-entity page with crosswalks back to requirements.
7. **Cross-references.** Update RequirementDetail to link to entities (e.g., "Controls satisfying this requirement: [list]").

Don't try to do all seven in one pass. List view first; detail view next; cross-references last.

## Common pitfalls

**Hooks called inside callbacks/IIFEs.** React rule: hooks at top of component only. If you wrote `{condition && (() => { const lens = useLens(); ... })()}`, lift the hook out: `const lens = useLens();` at the top, then `{condition && (...)}`.

**Forgetting to rebuild data.json after YAML edit.** Vite hot-reloads JSX changes but YAML changes need `make data` to flow into `os/src/data.json`. Restart-vite if hot-reload doesn't pick up the new JSON (rare).

**Owner color helper missing a value.** `ownerClass()` has a fixed enum. New owner codes (e.g., a `PARTNER` for AI Factory partner DC) need an addition to the helper.

**Tier color helper missing a value.** Same — `tierClass()` covers EU AI Act tiers; new framework tiers need additions.

**Lens not propagating into a new view.** Confirm the view component calls `useLens()` at the top; confirm it's rendered inside `LensContext.Provider` (every `view.type === ...` branch is, since they're all children of App).

**Babel parse fails after edit.** Run `cd os && node -e "require('@babel/parser').parse(require('fs').readFileSync('src/App.jsx','utf8'),{sourceType:'module',plugins:['jsx']})"` to find the line. Most common: unbalanced JSX brackets, mistyped curly close in a template literal.

## Reference

- `os/src/App.jsx` — the full app
- `os/src/data.json` — current built data (look here to understand the shape)
- Original wireframes (in transcripts of prior sessions; not in the repo) — Dashboard, Framework Detail, Control Detail, Reports, AI Systems Registry. Ask user before assuming a wireframe pattern.
