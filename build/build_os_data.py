"""
Pre-process all framework YAMLs into a single combined JSON for the OS.

Usage:
  python build/build_os_data.py <fw1.yaml> <fw2.yaml> ... <output.json>

Computes:
  - frameworks: per-framework metadata + requirements + scenarios + open_questions + evidence_families
  - reverse_graph: req_id -> list of {source_id, source_framework, target_framework, note}
  - anchor_stats: per-requirement incoming-link count (for the graph view)
  - scenario_clusters: scn_id -> list of all requirements activated (direct + 1-hop crosswalk)
"""

import json
import sys
import yaml
from pathlib import Path
from collections import defaultdict


def load_framework(yaml_path):
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    return data["id"], data


def main():
    if len(sys.argv) < 3:
        print("Usage: python build/build_os_data.py <fw1.yaml> [<fw2.yaml> ...] <output.json>")
        sys.exit(1)
    yaml_paths = sys.argv[1:-1]
    out_path = Path(sys.argv[-1])
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load all frameworks
    frameworks = {}
    for yp in yaml_paths:
        fw_id, fw_data = load_framework(yp)
        frameworks[fw_id] = fw_data
        n = len(fw_data["requirements"])
        print(f"Loaded {fw_id}: {n} requirements")

    # Build forward + reverse graphs
    forward_graph = defaultdict(list)
    reverse_graph = defaultdict(list)
    for fw_id, fw_data in frameworks.items():
        for req in fw_data["requirements"]:
            for entry in req.get("crosswalk") or []:
                target_fw = entry.get("framework")
                note = entry.get("note", "")
                for ref in entry.get("refs", []):
                    forward_graph[req["id"]].append({
                        "target_id": ref,
                        "target_framework": target_fw,
                        "note": note,
                    })
                    reverse_graph[ref].append({
                        "source_id": req["id"],
                        "source_framework": fw_id,
                        "note": note,
                    })

    # Build all-requirements lookup for scenario expansion
    all_reqs = {}
    for fw_id, fw_data in frameworks.items():
        for req in fw_data["requirements"]:
            all_reqs[req["id"]] = {**req, "_framework": fw_id}

    # Anchor stats: incoming-link count per requirement
    anchor_stats = {req_id: len(refs) for req_id, refs in reverse_graph.items() if refs}

    # Scenario clusters: for each scenario, expand to direct triggers + 1-hop crosswalks
    scenario_clusters = {}
    for fw_id, fw_data in frameworks.items():
        for scn in fw_data.get("scenarios", []):
            cluster = {"direct": [], "via_crosswalks": []}
            seen = set()
            for trigger in scn.get("triggered_requirements", []):
                tid = trigger.get("requirement_id")
                if tid:
                    cluster["direct"].append({
                        "requirement_id": tid,
                        "framework": all_reqs.get(tid, {}).get("_framework", "?"),
                        "note": trigger.get("scenario_specific_note", ""),
                    })
                    seen.add(tid)
            # 1-hop crosswalk expansion (forward only; reverse is OS-side per schema decision)
            for tid in [t["requirement_id"] for t in scn.get("triggered_requirements", []) if t.get("requirement_id")]:
                for fw_entry in forward_graph.get(tid, []):
                    nb = fw_entry["target_id"]
                    if nb not in seen and nb in all_reqs:
                        cluster["via_crosswalks"].append({
                            "requirement_id": nb,
                            "framework": all_reqs[nb]["_framework"],
                            "via": tid,
                            "note": fw_entry["note"],
                        })
                        seen.add(nb)
            scenario_clusters[scn["id"]] = {
                **{k: v for k, v in scn.items() if k != "triggered_requirements"},
                "framework": fw_id,
                "cluster": cluster,
            }

    # Trim per-framework scenarios to remove the redundant data now in scenario_clusters
    # (keep top-level metadata only; cluster lookups come from scenario_clusters)
    frameworks_compact = {}
    for fw_id, fw_data in frameworks.items():
        compact = dict(fw_data)
        compact["_id"] = fw_id
        # Index requirements by id for O(1) lookup in JS
        compact["requirements_index"] = {r["id"]: r for r in fw_data["requirements"]}
        frameworks_compact[fw_id] = compact

    # Open questions cross-framework lookup
    all_open_questions = {}
    for fw_id, fw_data in frameworks.items():
        for oq in fw_data.get("open_questions", []):
            # Same OQ id may appear in multiple frameworks (carry-overs); merge blocks
            oq_id = oq["id"]
            if oq_id in all_open_questions:
                existing = all_open_questions[oq_id]
                existing["blocks_requirements"] = list(set(
                    (existing.get("blocks_requirements") or []) + (oq.get("blocks_requirements") or [])
                ))
                existing["blocks_scenarios"] = list(set(
                    (existing.get("blocks_scenarios") or []) + (oq.get("blocks_scenarios") or [])
                ))
                existing["_frameworks"] = list(set(existing.get("_frameworks", []) + [fw_id]))
            else:
                all_open_questions[oq_id] = {**oq, "_frameworks": [fw_id]}

    # Final output
    output = {
        "frameworks": frameworks_compact,
        "reverse_graph": dict(reverse_graph),
        "forward_graph": dict(forward_graph),
        "anchor_stats": anchor_stats,
        "scenario_clusters": scenario_clusters,
        "all_open_questions": all_open_questions,
    }

    out_path = out_path  # already set from CLI args
    with open(out_path, "w") as f:
        json.dump(output, f, separators=(",", ":"))  # compact

    size_kb = out_path.stat().st_size / 1024
    print(f"\nWrote {out_path}: {size_kb:.1f} KB")
    print(f"  frameworks: {len(output['frameworks'])}")
    print(f"  forward edges: {sum(len(v) for v in output['forward_graph'].values())}")
    print(f"  reverse edges: {sum(len(v) for v in output['reverse_graph'].values())}")
    print(f"  scenario clusters: {len(output['scenario_clusters'])}")
    print(f"  open questions: {len(output['all_open_questions'])}")
    print(f"  anchor reqs (3+ incoming): {sum(1 for c in output['anchor_stats'].values() if c >= 3)}")


if __name__ == "__main__":
    main()
