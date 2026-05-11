# ISO 42001 — Pending Crosswalks (resolved log)

Originally a backlog of crosswalks waiting for target frameworks to exist. Per §11 of `source/privatebox-iso-ai-governance-architecture.md` (PB Architecture Pack), 42001 was authored before NIST AI RMF, POPIA, and King V landed; this file captured the intended mappings.

**Status as of 2026-05-11: all originally-pending sections are RESOLVED.**

| Originally pending → | Status | Wired in commit |
|---|---|---|
| NIST AI RMF | ✅ Resolved | `nist` framework authored; ~34 crosswalks added to `iso-42001.yaml` per the NIST commit |
| POPIA | ✅ Resolved | `popia` framework authored; ~24 crosswalks added to `iso-42001.yaml` per the POPIA commit |
| King V | ✅ Resolved | `king-v` framework authored; reverse-graph edges auto-derived (King V is the overlay framework; outgoing crosswalks live in `king-v.yaml`) |

File retained for historical traceability. Future framework-pending mappings (if any) should follow the same pattern: capture here when the target framework hasn't been authored yet, mark as resolved when it lands.

To inspect current outgoing crosswalks from 42001:

```sh
python3 -c "
import yaml
d = yaml.safe_load(open('frameworks/iso-42001/iso-42001.yaml'))
for r in d['requirements']:
    for x in r.get('crosswalk', []):
        print(f\"{r['id']} → {x['framework']}: {','.join(x['refs'])}\")
" | sort | uniq -c
```
