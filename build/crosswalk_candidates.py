"""
Crosswalk candidate generator.

Loads ISO 27001, ISO 27701, EU AI Act YAMLs. For each requirement, extracts a keyword
signature. Then for each cross-framework pair, computes a similarity score based on:
  (a) Keyword Jaccard similarity (title + first sentence)
  (b) Native ID match (e.g., 27001 A.5.7 vs 27701 A.3 5.7 share "5.7")
  (c) Structural rules (clauses 4-10 are 1:1 between 27001 and 27701 by Annex SL HLS)

Outputs a markdown report sorted by confidence, ready for human review.
This is a CANDIDATE generator — no crosswalks are written without confirmation.
"""

import yaml
import re
from pathlib import Path
from collections import defaultdict


FRAMEWORKS = ["iso-27001", "iso-27701", "eu-ai-act"]
# YAML paths supplied via CLI; this stays for backward compat but isn't used
YAML_DIR = None


# Stopwords specific to compliance/privacy/security domain — these are too common
# to discriminate (every requirement mentions "documented" or "appropriate")
STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "at", "by",
    "with", "from", "as", "is", "are", "be", "must", "shall", "should", "may",
    "documented", "documentation", "document", "appropriate", "necessary",
    "required", "include", "including", "ensure", "implement", "establish",
    "maintain", "review", "system", "process", "procedure", "controls", "control",
    "data", "information", "organization", "organisation", "this", "these",
    "that", "those", "such", "any", "all", "each", "where", "when", "which",
    "who", "what", "how", "iso", "iec", "27001", "27701", "art", "article",
    "clause", "annex", "iv", "v", "i", "ii", "iii",
}


def load_framework(yaml_path):
    """Load a framework YAML; returns (id, data)."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    return data["id"], data


def keyword_set(text):
    """Extract a set of meaningful keywords from a text fragment."""
    if not text:
        return set()
    # Lowercase, split on non-word, filter
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) >= 3}


def requirement_signature(req):
    """Build a keyword signature for a requirement."""
    title = req.get("title", "")
    requirement_text = req.get("requirement", "") or ""
    objective = req.get("objective", "") or ""
    pb_interp = req.get("pb_interpretation", "") or ""
    # Combine, with title weighted by repetition (3x) and pb_interp deweighted (truncated)
    combined = (title + " ") * 3 + " ".join([requirement_text, objective, pb_interp[:200]])
    return keyword_set(combined)


def native_id_tokens(req):
    """Extract numeric ID tokens (e.g., '5.7', '8.13') for structural matching."""
    nid = req.get("native_id", "")
    return set(re.findall(r"\d+\.\d+(?:\.\d+)?|\d+", str(nid)))


def jaccard(a, b):
    """Jaccard similarity between two sets."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def score_pair(req_a, req_b):
    """Score a candidate crosswalk pair. Returns (score, components_dict)."""
    sig_a = requirement_signature(req_a)
    sig_b = requirement_signature(req_b)

    keyword_score = jaccard(sig_a, sig_b)

    # Native ID match — high signal for 27001 ↔ 27701 A.3 (same numbering)
    ids_a = native_id_tokens(req_a)
    ids_b = native_id_tokens(req_b)
    id_match = bool(ids_a & ids_b)

    # Structural rule: 27001 clauses 4-10 ↔ 27701 clauses 4-10 (Annex SL HLS shared)
    structural = False
    if (req_a["kind"] == "clause" and req_b["kind"] == "clause"
            and req_a.get("native_id") == req_b.get("native_id")):
        structural = True

    # Final score: weighted combination
    score = keyword_score
    if id_match and (req_a["kind"] in ("control_org", "control_shared")
                     or req_b["kind"] in ("control_org", "control_shared")):
        score += 0.4  # 27001 Annex A ↔ 27701 A.3 numbering correspondence
    if structural:
        score += 0.5

    return score, {
        "keyword_score": round(keyword_score, 3),
        "id_match": id_match,
        "structural": structural,
        "shared_keywords": sorted(sig_a & sig_b)[:10],
    }


def main():
    import sys
    if len(sys.argv) < 3:
        print("# Usage: python build/crosswalk_candidates.py <fw1.yaml> <fw2.yaml> [<fw3.yaml> ...]")
        sys.exit(1)
    yaml_paths = sys.argv[1:]

    # Load all framework YAMLs
    frameworks = {}
    for yp in yaml_paths:
        fw_id, fw_data = load_framework(yp)
        frameworks[fw_id] = fw_data
        n = len(fw_data["requirements"])
        sys.stderr.write(f"# Loaded {fw_id}: {n} requirements\n")

    # Score all cross-framework pairs
    candidates = defaultdict(list)  # (fw_a, req_a_id) -> list of (fw_b, req_b_id, score, components)

    # Authorship rule: more-specific/newer references the more-general/older.
    # ISO 27001 is target-only — never carries outgoing crosswalks.
    # Build directed pairs: source frameworks reference target frameworks.
    fw_ids = list(frameworks.keys())
    pairs = []
    for fw_a in fw_ids:
        for fw_b in fw_ids:
            if fw_a == fw_b:
                continue
            # ISO 27001 is target-only
            if fw_a == "iso-27001":
                continue
            pairs.append((fw_a, fw_b))

    for fw_a, fw_b in pairs:
        reqs_a = frameworks[fw_a]["requirements"]
        reqs_b = frameworks[fw_b]["requirements"]
        for ra in reqs_a:
            scored = []
            for rb in reqs_b:
                score, comp = score_pair(ra, rb)
                if score >= 0.15:  # threshold to control noise
                    scored.append((rb["id"], rb["title"], score, comp))
            scored.sort(key=lambda x: -x[2])
            if scored:
                candidates[(fw_a, ra["id"], ra["title"])] = scored[:5]  # top 5 per req

    # Output a structured markdown report
    out = []
    out.append("# Crosswalk candidate report\n")
    out.append("Generated by candidate-only analysis. Each candidate pair shows score components.\n")
    out.append("Threshold: 0.15. Top 5 candidates per source requirement shown.\n\n")
    out.append("Score components:\n")
    out.append("- keyword_score: Jaccard similarity on title + requirement/objective + pb_interpretation prefix.\n")
    out.append("- id_match: native_id numeric tokens overlap (e.g., '5.7' shared).\n")
    out.append("- structural: clause 4.x-10.x match across management-system standards.\n\n")
    out.append("---\n\n")

    by_fw = defaultdict(list)
    for (fw_a, ra_id, ra_title), scored in candidates.items():
        by_fw[fw_a].append((ra_id, ra_title, scored))

    for fw_a in ["iso-27701", "eu-ai-act"]:  # author crosswalks from these into older frameworks
        out.append(f"## Source framework: {fw_a}\n\n")
        items = sorted(by_fw[fw_a], key=lambda x: x[0])
        for ra_id, ra_title, scored in items:
            out.append(f"### {ra_id} — {ra_title}\n")
            for rb_id, rb_title, score, comp in scored:
                out.append(f"- **{rb_id}** — {rb_title}\n")
                out.append(f"  - score: {score:.3f}, kw: {comp['keyword_score']}, id_match: {comp['id_match']}, struct: {comp['structural']}\n")
                if comp['shared_keywords']:
                    out.append(f"  - shared: {', '.join(comp['shared_keywords'])}\n")
            out.append("\n")
        out.append("\n")

    # Print report to stdout — Makefile redirects to docs/crosswalk-candidates-report.md
    sys.stdout.write("".join(out))
    sys.stderr.write(f"# Total source requirements with candidates: {len(candidates)}\n")
    sys.stderr.write(f"# Total candidate pairs: {sum(len(v) for v in candidates.values())}\n")


if __name__ == "__main__":
    main()
