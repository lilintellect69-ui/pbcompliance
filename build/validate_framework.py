"""
Framework YAML validator — checks any framework YAML against schema v2.

Usage:
  python scripts/validate_framework.py <path-to-yaml>
  python scripts/validate_framework.py /mnt/user-data/outputs/iso-27001.yaml

Exits non-zero on validation failure. Prints all errors and warnings.

Validation levels:
- ERROR: blocks loading. Schema-violating, must fix.
- WARNING: doesn't block, but worth investigating. Things like crosswalk
  targets that don't resolve, count drift, etc.
"""

import sys
import yaml
from pathlib import Path
from collections import Counter

# =============================================================================
# Enums (must match framework-schema-v2.md)
# =============================================================================

VALID_TYPES = {
    "management_system_standard",
    "attestation",
    "regulation",
    "voluntary_framework",
    "governance_code",
}

VALID_AUDIT_TYPES = {
    "certification",
    "attestation",
    "conformity_assessment",
    "regulatory_inspection",
    "self_attestation",
    "disclosure",
}

VALID_KINDS = {
    "clause",
    "control_org", "control_proc", "control_ctrl", "control_shared",
    "control_aims",
    "condition", "section",
    "criterion",
    "principle", "practice",
    "article",
    "function_outcome", "task", "overlay",
}

KIND_TO_PREFIX = {
    "clause": "cl",
    "control_org": "a",
    "control_ctrl": "a1",
    "control_proc": "a2",
    "control_shared": "a3",
    "control_aims": "a",
    "condition": "cond",
    "section": "s",
    "criterion": ("cc", "a", "c", "pi", "p"),  # SOC 2 has multiple prefixes
    "principle": "p",
    "practice": "rp",
    "article": "art",
    "function_outcome": ("gov", "map", "measure", "manage"),
    "task": ("po", "ps", "pw", "rv"),
    "overlay": "218a",
}

VALID_APPLIES = {"Y", "C", "N", "tier_dependent", "role_dependent", "scenario_dependent"}

VALID_OWNERS = {"PB", "PB/SH", "SH", "SH/CL", "CL"}

VALID_MATURITY = {"SA", "AR", "Cert", "SA/AR"}

VALID_SOURCE_AUTHORITY = {"binding", "guidance", "code", "draft", "market"}

# Required top-level fields
REQUIRED_TOP_LEVEL = {
    "schema_version", "id", "version", "full_name", "type", "issuer",
    "audit_type", "certifiable", "pb_interpretation_version",
    "pb_application", "requirements",
}

# Required per-requirement fields. Note: `requirement` (natural-language clause
# text) is used by clause-style kinds; `objective` (short purpose statement) is
# used by control-style kinds. At least one must be present.
REQUIRED_REQUIREMENT_FIELDS = {
    "id", "kind", "native_id", "title",
    "pb_interpretation", "owner", "business_models",
}

# Kinds that conventionally use `requirement` for natural-language text
CLAUSE_STYLE_KINDS = {
    "clause", "condition", "section", "article", "principle", "criterion",
    "function_outcome", "task", "overlay",
}

# Kinds that conventionally use `objective` for short purpose statement
CONTROL_STYLE_KINDS = {
    "control_org", "control_proc", "control_ctrl", "control_shared", "control_aims",
    "practice",
}


# =============================================================================
# Validation
# =============================================================================

class Validator:
    def __init__(self, data, source_path):
        self.data = data
        self.source = str(source_path)
        self.errors = []
        self.warnings = []

    def err(self, msg, location=""):
        loc = f" [{location}]" if location else ""
        self.errors.append(f"{msg}{loc}")

    def warn(self, msg, location=""):
        loc = f" [{location}]" if location else ""
        self.warnings.append(f"{msg}{loc}")

    def validate(self):
        self._validate_top_level()
        if self.errors:
            return  # don't continue if top-level is broken
        self._validate_enums()
        self._validate_requirements()
        self._validate_open_questions()
        self._validate_scenarios()
        self._validate_cross_references()
        self._validate_counts()
        return len(self.errors) == 0

    # ---- top-level ----

    def _validate_top_level(self):
        for field in REQUIRED_TOP_LEVEL:
            if field not in self.data:
                self.err(f"missing required top-level field: {field}")

        if self.data.get("schema_version") != "2.0":
            self.err(
                f"schema_version must be '2.0', got: {self.data.get('schema_version')!r}"
            )

    def _validate_enums(self):
        if self.data.get("type") not in VALID_TYPES:
            self.err(
                f"invalid type: {self.data.get('type')!r}. "
                f"Must be one of {sorted(VALID_TYPES)}"
            )

        if self.data.get("audit_type") not in VALID_AUDIT_TYPES:
            self.err(
                f"invalid audit_type: {self.data.get('audit_type')!r}. "
                f"Must be one of {sorted(VALID_AUDIT_TYPES)}"
            )

        if not isinstance(self.data.get("certifiable"), bool):
            self.err(f"certifiable must be a bool, got: {type(self.data.get('certifiable')).__name__}")

    # ---- requirements ----

    def _validate_requirements(self):
        requirements = self.data.get("requirements", [])
        if not isinstance(requirements, list):
            self.err("requirements must be a list")
            return

        if not requirements:
            self.err("requirements list is empty")
            return

        seen_ids = set()
        framework_id = self.data.get("id", "")

        for i, req in enumerate(requirements):
            loc = f"requirements[{i}]"

            if not isinstance(req, dict):
                self.err(f"requirement must be a dict", loc)
                continue

            # Required fields
            for field in REQUIRED_REQUIREMENT_FIELDS:
                if field not in req:
                    self.err(f"missing required field: {field}", f"{loc} ({req.get('id', '?')})")

            # At least one of requirement/objective must be present
            if "requirement" not in req and "objective" not in req:
                self.err(
                    "must have either 'requirement' (clause-style) or 'objective' (control-style)",
                    f"{loc} ({req.get('id', '?')})",
                )

            # Soft check: clause-style kinds should have `requirement`; control-style should have `objective`
            kind = req.get("kind")
            if kind in CLAUSE_STYLE_KINDS and "requirement" not in req:
                self.warn(
                    f"kind={kind!r} typically uses 'requirement' field, only 'objective' present",
                    f"{loc} ({req.get('id', '?')})",
                )
            if kind in CONTROL_STYLE_KINDS and "objective" not in req:
                self.warn(
                    f"kind={kind!r} typically uses 'objective' field, only 'requirement' present",
                    f"{loc} ({req.get('id', '?')})",
                )

            # ID format
            req_id = req.get("id", "")
            if req_id in seen_ids:
                self.err(f"duplicate requirement id: {req_id}", loc)
            seen_ids.add(req_id)

            if framework_id and not req_id.startswith(f"{framework_id}-"):
                self.warn(
                    f"requirement id {req_id!r} doesn't start with framework id "
                    f"{framework_id!r}- (legacy ID? new files should use prefixed form)",
                    loc,
                )

            # Kind
            kind = req.get("kind")
            if kind not in VALID_KINDS:
                self.err(
                    f"invalid kind: {kind!r}. Must be one of {sorted(VALID_KINDS)}",
                    f"{loc} ({req_id})",
                )

            # Owner
            owner = req.get("owner")
            if owner not in VALID_OWNERS:
                self.err(
                    f"invalid owner: {owner!r}. Must be one of {sorted(VALID_OWNERS)}",
                    f"{loc} ({req_id})",
                )

            # owner_by_model shape
            if "owner_by_model" in req:
                obm = req["owner_by_model"]
                if not isinstance(obm, dict):
                    self.err(f"owner_by_model must be a dict", f"{loc} ({req_id})")
                else:
                    if "on_prem" not in obm:
                        self.err(f"owner_by_model missing on_prem key", f"{loc} ({req_id})")
                    if "ai_factory" not in obm:
                        self.err(f"owner_by_model missing ai_factory key", f"{loc} ({req_id})")

            # applies
            if "applies" in req:
                applies = req["applies"]
                if applies not in VALID_APPLIES:
                    self.err(
                        f"invalid applies: {applies!r}. Must be one of {sorted(VALID_APPLIES)}",
                        f"{loc} ({req_id})",
                    )

            # maturity
            if "maturity_target" in req:
                mt = req["maturity_target"]
                if mt not in VALID_MATURITY:
                    self.err(
                        f"invalid maturity_target: {mt!r}. Must be one of {sorted(VALID_MATURITY)}",
                        f"{loc} ({req_id})",
                    )

            # source_authority
            if "source_authority" in req:
                sa = req["source_authority"]
                if sa not in VALID_SOURCE_AUTHORITY:
                    self.err(
                        f"invalid source_authority: {sa!r}. Must be one of {sorted(VALID_SOURCE_AUTHORITY)}",
                        f"{loc} ({req_id})",
                    )

            # tier must match framework's tiers[]
            framework_tiers = set(self.data.get("tiers", []))
            if "tier" in req and req["tier"] != "n/a":
                if framework_tiers and req["tier"] not in framework_tiers:
                    self.err(
                        f"tier {req['tier']!r} not in framework's tiers list {sorted(framework_tiers)}",
                        f"{loc} ({req_id})",
                    )

            # role_applicability roles must match framework's roles[]
            framework_roles = set(self.data.get("roles", []))
            if "role_applicability" in req:
                ra = req["role_applicability"]
                if isinstance(ra, dict):
                    for role_key in ra.keys():
                        if role_key.endswith("_note"):
                            continue
                        if framework_roles and role_key not in framework_roles:
                            self.err(
                                f"role {role_key!r} in role_applicability not in framework's roles {sorted(framework_roles)}",
                                f"{loc} ({req_id})",
                            )

            # business_models
            if "business_models" in req:
                bm = req["business_models"]
                if not isinstance(bm, list) or not bm:
                    self.err(f"business_models must be a non-empty list", f"{loc} ({req_id})")

    # ---- open questions ----

    def _validate_open_questions(self):
        oqs = self.data.get("open_questions", [])
        if not isinstance(oqs, list):
            self.err("open_questions must be a list")
            return

        seen_ids = set()
        for i, oq in enumerate(oqs):
            loc = f"open_questions[{i}]"

            if not isinstance(oq, dict):
                self.err("open question must be a dict", loc)
                continue

            for field in ("id", "question", "decision_status"):
                if field not in oq:
                    self.err(f"missing required field: {field}", f"{loc} ({oq.get('id', '?')})")

            oq_id = oq.get("id", "")
            if oq_id in seen_ids:
                self.err(f"duplicate open_question id: {oq_id}", loc)
            seen_ids.add(oq_id)

            if oq_id and not oq_id.startswith("oq-"):
                self.warn(f"open_question id should start with 'oq-': {oq_id}", loc)

            status = oq.get("decision_status")
            if status not in {"pending", "resolved", "deferred"}:
                self.err(f"invalid decision_status: {status!r}", f"{loc} ({oq_id})")

            if status == "resolved":
                if not oq.get("resolved_value"):
                    self.warn(f"resolved open_question has no resolved_value", f"{loc} ({oq_id})")

    # ---- scenarios ----

    def _validate_scenarios(self):
        scenarios = self.data.get("scenarios", [])
        if not isinstance(scenarios, list):
            self.err("scenarios must be a list")
            return

        seen_ids = set()
        for i, scn in enumerate(scenarios):
            loc = f"scenarios[{i}]"

            if not isinstance(scn, dict):
                self.err("scenario must be a dict", loc)
                continue

            for field in ("id", "name"):
                if field not in scn:
                    self.err(f"missing required field: {field}", f"{loc} ({scn.get('id', '?')})")

            scn_id = scn.get("id", "")
            if scn_id in seen_ids:
                self.err(f"duplicate scenario id: {scn_id}", loc)
            seen_ids.add(scn_id)

    # ---- cross-references ----

    def _validate_cross_references(self):
        # Build sets of valid IDs
        req_ids = {r["id"] for r in self.data.get("requirements", []) if "id" in r}
        oq_ids = {q["id"] for q in self.data.get("open_questions", []) if "id" in q}
        scn_ids = {s["id"] for s in self.data.get("scenarios", []) if "id" in s}

        # Open questions referencing requirements
        for oq in self.data.get("open_questions", []):
            for ref in oq.get("blocks_requirements", []):
                if ref not in req_ids:
                    self.warn(
                        f"open_question {oq.get('id', '?')} references unknown requirement: {ref}",
                    )
            for ref in oq.get("blocks_scenarios", []):
                if ref not in scn_ids:
                    self.warn(
                        f"open_question {oq.get('id', '?')} references unknown scenario: {ref}",
                    )

        # Requirements referencing open questions and scenarios
        for req in self.data.get("requirements", []):
            obm = req.get("owner_by_model", {})
            af = obm.get("ai_factory", {}) if isinstance(obm, dict) else {}
            if isinstance(af, dict) and "open_question" in af:
                oq_ref = af["open_question"]
                if oq_ref not in oq_ids:
                    self.err(
                        f"requirement {req.get('id', '?')} owner_by_model.ai_factory.open_question "
                        f"references unknown: {oq_ref}",
                    )

            for ref in req.get("triggered_by_scenarios", []):
                if ref not in scn_ids:
                    self.warn(
                        f"requirement {req.get('id', '?')} triggered_by_scenarios "
                        f"references unknown: {ref}",
                    )

        # Scenarios referencing requirements
        for scn in self.data.get("scenarios", []):
            for tr in scn.get("triggered_requirements", []):
                if isinstance(tr, dict):
                    ref = tr.get("requirement_id")
                    if ref and ref not in req_ids:
                        self.warn(
                            f"scenario {scn.get('id', '?')} triggered_requirements "
                            f"references unknown requirement: {ref}",
                        )

    # ---- counts ----

    def _validate_counts(self):
        # ISO 27001 canonical counts
        framework_id = self.data.get("id")
        requirements = self.data.get("requirements", [])
        kinds = Counter(r.get("kind") for r in requirements)

        if framework_id == "iso-27001":
            if kinds.get("clause", 0) != 30:
                self.warn(
                    f"ISO 27001 should have 30 clauses, got {kinds.get('clause', 0)}"
                )
            if kinds.get("control_org", 0) != 93:
                self.warn(
                    f"ISO 27001 should have 93 Annex A controls, got {kinds.get('control_org', 0)}"
                )
        # Future: add canonical counts for other frameworks as they land


# =============================================================================
# Main
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_framework.py <path-to-yaml>")
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    print(f"Validating: {path}")
    print()

    with open(path) as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"YAML PARSE ERROR: {e}")
            sys.exit(1)

    if not isinstance(data, dict):
        print(f"ERROR: top-level YAML must be a mapping/dict, got {type(data).__name__}")
        sys.exit(1)

    v = Validator(data, path)
    v.validate()

    if v.errors:
        print(f"ERRORS ({len(v.errors)}):")
        for e in v.errors:
            print(f"  ✗ {e}")
        print()

    if v.warnings:
        print(f"WARNINGS ({len(v.warnings)}):")
        for w in v.warnings:
            print(f"  ⚠ {w}")
        print()

    if not v.errors and not v.warnings:
        print(f"  ✓ Schema v2 valid: {len(data.get('requirements', []))} requirements, "
              f"{len(data.get('open_questions', []))} open questions, "
              f"{len(data.get('scenarios', []))} scenarios")
        print()

    if v.errors:
        print(f"FAILED: {len(v.errors)} error(s), {len(v.warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"PASSED: {len(v.warnings)} warning(s)")
        sys.exit(0)


if __name__ == "__main__":
    main()
