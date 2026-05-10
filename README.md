# PrivateBox GRC OS

Internal governance, risk, and compliance operating system for PrivateBox.
Unifies nine compliance frameworks under a single schema with explicit cross-framework crosswalks. Two-business-model lens (on-prem / AI Factory) propagates through every view.

## Status

3 of 9 frameworks complete (ISO 27001, ISO 27701, EU AI Act). Schema v2 locked. Read-only OS prototype with 6 navigable views and lens toggle. Validator, crosswalk pipeline, and OS data builder all tested.

## Quick start

```bash
make validate    # Schema check on all framework YAMLs
make data        # Rebuild os/src/data.json
make dev         # Serve OS at localhost:5173
```

See [MIGRATION.md](MIGRATION.md) for full setup.

## Working with Claude

Run `claude` in the repo root. `CLAUDE.md` orients context. The `compliance-framework-author` skill at `.claude/skills/` codifies the methodology for new framework authoring.

## Layout

- `frameworks/<id>/` — one folder per framework, self-contained (yaml + build script + source material)
- `build/` — schema validator, crosswalk pipeline, data builder
- `os/` — vite-served React app (the rendering surface)
- `docs/` — schema spec, structural survey, crosswalk reports
- `.claude/skills/` — methodology codified as skills

## Pending

ISO 42001, NIST bundle, SOC 2, POPIA, King V, COBIT 2019.

After framework expansion: Controls library, Risks register, AI Systems registry, Vendors register, Evidence vault, SOPs library, Trust Pack composer.
