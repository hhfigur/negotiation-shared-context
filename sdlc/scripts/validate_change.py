#!/usr/bin/env python3
"""Validate a Negotiation AI SDLC change directory and lifecycle prerequisites.

Zero-dependency by design (Python standard library only). This intentionally does not implement
a general YAML parser. See `parse_simple_frontmatter` and `structural_check_traceability` for the
exact, documented scope and limits of what is checked.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

CHANGE_ID_RE = re.compile(r"^[0-9]{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_STATUSES = {
    "draft",
    "in_review",
    "accepted",
    "rejected",
    "superseded",
    "blocked",
    "completed",
    "released",
    "measured",
}

ARTIFACTS = {
    "intent.md": {
        "artifact": "intent",
        "headings": [
            "# Intent:",
            "## Problem or opportunity",
            "## Desired outcome",
            "## Scope",
            "## Outcome measures",
            "## Decision record",
        ],
    },
    "spec.md": {
        "artifact": "specification",
        "headings": [
            "# Specification:",
            "## Functional requirements",
            "## Non-functional requirements",
            "## Acceptance criteria",
            "## Decision record",
        ],
    },
    "plan.md": {
        "artifact": "implementation_plan",
        "headings": [
            "# Implementation Plan:",
            "## Current-state findings",
            "## Repository workstreams",
            "## Test and evidence plan",
            "## Risks",
            "## Decision record",
        ],
    },
    "debug-evidence.md": {
        "artifact": "debug_evidence",
        "headings": [
            "# Debug Evidence:",
            "## Reproduction protocol",
            "## Competing hypotheses",
            "## Root-cause conclusion",
            "## Regression-test strategy",
            "## Diagnosis gate",
        ],
    },
    "verification.md": {
        "artifact": "verification",
        "headings": [
            "# Verification:",
            "## Scope and independence",
            "## Acceptance-criteria verification",
            "## Quality checks",
            "## Verification conclusion",
        ],
    },
    "review.md": {
        "artifact": "review",
        "headings": [
            "# Independent Review:",
            "## Review scope",
            "## Findings",
            "## Traceability review",
            "## Gate recommendation",
        ],
    },
    "release.md": {
        "artifact": "release",
        "headings": [
            "# Release Record:",
            "## Release scope",
            "## Entry evidence",
            "## Rollback",
            "## Release decision",
        ],
    },
    "outcome.md": {
        "artifact": "outcome",
        "headings": [
            "# Outcome Review:",
            "## Original intent and release",
            "## Outcome measures",
            "## Interpretation",
            "## Outcome decision",
        ],
    },
    "incident.md": {
        "artifact": "incident",
        "headings": [
            "# Incident:",
            "## Impact",
            "## Detection",
            "## Timeline",
            "## Follow-up actions",
            "## Incident closure",
        ],
    },
}

# Top-level keys traceability.yaml is expected to declare. Checked structurally (see
# structural_check_traceability), not by full YAML parsing.
TRACEABILITY_TOP_LEVEL_KEYS = (
    "schema_version",
    "change_id",
    "title",
    "status",
    "artifacts",
    "repositories",
    "requirements",
    "evidence",
    "risks",
    "findings",
    "releases",
    "outcomes",
)
TRACEABILITY_ARTIFACT_KEYS = (
    "intent",
    "specification",
    "plan",
    "debug_evidence",
    "verification",
    "review",
    "release",
    "outcome",
    "incident",
)


class FrontmatterError(ValueError):
    pass


def parse_simple_scalar(text: str) -> Any:
    """Parse one YAML-ish scalar or flow-sequence value.

    Supports: empty/null, booleans, single- or double-quoted strings, unquoted bare strings,
    integers, floats, and a single level of flow-sequence syntax (`[]`, `[a, b]`, `["a", "b"]`).
    Does not support: nested flow sequences/mappings, block sequences, multiline strings, anchors,
    tags, or any other YAML 1.1/1.2 construct. Callers must not feed this anything more complex.
    """
    text = text.strip()
    if text == "" or text in ("null", "~", "Null", "NULL"):
        return None
    if text in ("true", "True", "TRUE"):
        return True
    if text in ("false", "False", "FALSE"):
        return False
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        return text[1:-1]
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        if "[" in inner or "]" in inner or "{" in inner or "}" in inner:
            raise FrontmatterError(f"nested flow collections are not supported: {text!r}")
        return [parse_simple_scalar(item) for item in inner.split(",")]
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


def parse_simple_frontmatter(text: str) -> dict[str, Any]:
    """Parse a flat `key: value` YAML frontmatter block using the standard library only.

    Documented scope: this handles exactly the shape used by this project's canonical templates —
    top-level, unindented `key: value` pairs where each value is a scalar or a single-level flow
    sequence (see `parse_simple_scalar`). It deliberately refuses (raises `FrontmatterError`,
    naming the offending line) anything requiring real YAML semantics: indented/nested content,
    block scalars (`|`, `>`), multi-document markers, or duplicate keys. If a template ever needs
    genuine nested frontmatter, this parser must be replaced, not silently worked around.
    """
    data: dict[str, Any] = {}
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue
        if line[0] in " \t":
            raise FrontmatterError(
                f"line {lineno}: indented/nested frontmatter is not supported by this "
                f"zero-dependency parser: {line!r}"
            )
        if ":" not in line:
            raise FrontmatterError(f"line {lineno}: expected 'key: value', got: {line!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise FrontmatterError(f"line {lineno}: unsupported key syntax: {key!r}")
        if key in data:
            raise FrontmatterError(f"line {lineno}: duplicate key: {key!r}")
        stripped_value = value.strip()
        if stripped_value in ("|", ">", "|-", ">-", "|+", ">+"):
            raise FrontmatterError(
                f"line {lineno}: block scalar syntax ({stripped_value!r}) is not supported by "
                f"this zero-dependency parser"
            )
        data[key] = parse_simple_scalar(value)
    return data


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("missing opening YAML frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise FrontmatterError("missing closing YAML frontmatter delimiter") from exc
    frontmatter_text = "\n".join(lines[1:end])
    data = parse_simple_frontmatter(frontmatter_text)
    body = "\n".join(lines[end + 1 :])
    return data, body


def normalized(value: Any) -> str:
    return str(value or "").strip().lower()


def is_set(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and not text.startswith("<") and "{{" not in text


def structural_check_traceability(path: Path, change_id: str, errors: list[str]) -> dict[str, Any]:
    """Zero-dependency structural check of traceability.yaml.

    This does NOT perform full YAML semantic parsing. traceability.yaml contains nested mappings
    and lists of mappings (requirements, evidence, findings, releases) that cannot be safely
    parsed without a YAML library. This function only checks: the presence of expected top-level
    keys (as unindented `key:` lines), the presence of expected `artifacts:` sub-keys (as
    consistently-indented `  key:` lines), and the top-level `change_id` scalar value. It cannot
    detect malformed nesting, duplicate keys inside a nested block, type errors within a nested
    block, or a semantically invalid but textually-present key. Returns a minimal dict with
    whatever top-level scalars this function was able to safely extract, for the checks below
    that need them (currently: `change_id`).
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    result: dict[str, Any] = {}

    change_id_value = None
    for line in lines:
        if line.startswith("change_id:"):
            try:
                change_id_value = parse_simple_scalar(line.partition(":")[2])
            except FrontmatterError:
                change_id_value = line.partition(":")[2].strip()
            break
    result["change_id"] = change_id_value
    if change_id_value is None:
        errors.append("traceability.yaml: no top-level 'change_id:' key found")
    elif str(change_id_value) != change_id:
        errors.append(
            f"traceability.yaml: change_id must be {change_id!r}, got {change_id_value!r}"
        )

    for key in TRACEABILITY_TOP_LEVEL_KEYS:
        if not any(line.startswith(f"{key}:") for line in lines):
            errors.append(f"traceability.yaml: missing top-level key: {key}")

    if any(line.startswith("artifacts:") for line in lines):
        missing = [
            key
            for key in TRACEABILITY_ARTIFACT_KEYS
            if not re.search(rf"^\s+{re.escape(key)}:", text, re.MULTILINE)
        ]
        if missing:
            errors.append(
                "traceability.yaml: missing artifact keys under 'artifacts:': "
                + ", ".join(sorted(missing))
            )

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate one SDLC change directory.")
    parser.add_argument("change_dir", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat unresolved placeholders in accepted or completed artifacts as errors.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    change_dir = args.change_dir.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not change_dir.is_dir():
        print(f"ERROR: not a directory: {change_dir}", file=sys.stderr)
        return 2

    change_id = change_dir.name
    if not CHANGE_ID_RE.fullmatch(change_id):
        errors.append(f"directory name is not a valid change ID: {change_id}")

    for required in ("intent.md", "traceability.yaml"):
        if not (change_dir / required).is_file():
            errors.append(f"missing required file: {required}")

    parsed: dict[str, dict[str, Any]] = {}
    bodies: dict[str, str] = {}

    for filename, rules in ARTIFACTS.items():
        path = change_dir / filename
        if not path.exists():
            continue
        try:
            frontmatter, body = parse_frontmatter(path)
        except (OSError, UnicodeError, FrontmatterError) as exc:
            errors.append(f"{filename}: invalid frontmatter: {exc}")
            continue

        parsed[filename] = frontmatter
        bodies[filename] = body

        if frontmatter.get("artifact") != rules["artifact"]:
            errors.append(
                f"{filename}: artifact must be {rules['artifact']!r}, got {frontmatter.get('artifact')!r}"
            )
        if str(frontmatter.get("change_id", "")) != change_id:
            errors.append(
                f"{filename}: change_id must be {change_id!r}, got {frontmatter.get('change_id')!r}"
            )
        status = normalized(frontmatter.get("status"))
        if status not in VALID_STATUSES:
            errors.append(f"{filename}: invalid or missing status: {status!r}")
        for heading in rules["headings"]:
            if heading not in body:
                errors.append(f"{filename}: missing required heading prefix: {heading}")

        if status in {"accepted", "completed", "released", "measured"}:
            if args.strict and ("<" in body or "{{" in body):
                errors.append(f"{filename}: unresolved placeholders remain in a final-state artifact")

        if status == "accepted" and filename in {"intent.md", "spec.md", "plan.md"}:
            if not is_set(frontmatter.get("accepted_by")):
                errors.append(f"{filename}: accepted status requires accepted_by")
            if not is_set(frontmatter.get("accepted_at")):
                errors.append(f"{filename}: accepted status requires accepted_at")

    trace_path = change_dir / "traceability.yaml"
    trace: dict[str, Any] = {}
    if trace_path.is_file():
        try:
            trace = structural_check_traceability(trace_path, change_id, errors)
        except (OSError, UnicodeError) as exc:
            errors.append(f"traceability.yaml: could not read file: {exc}")

    intent_status = normalized(parsed.get("intent.md", {}).get("status"))
    spec_status = normalized(parsed.get("spec.md", {}).get("status"))
    plan_status = normalized(parsed.get("plan.md", {}).get("status"))

    if spec_status == "accepted" and intent_status != "accepted":
        errors.append("spec.md is accepted but intent.md is not accepted")
    if plan_status == "accepted" and spec_status != "accepted":
        errors.append("plan.md is accepted but spec.md is not accepted")

    debug = parsed.get("debug-evidence.md")
    if debug:
        fix_authorized = debug.get("fix_authorized") is True
        diagnosis_mode = normalized(debug.get("diagnosis_mode")) or "full"
        if diagnosis_mode not in {"full", "deterministic_fast_path"}:
            errors.append(
                f"debug-evidence.md: invalid diagnosis_mode: {debug.get('diagnosis_mode')!r}"
            )
        if fix_authorized:
            root_status = normalized(debug.get("root_cause_status"))
            if root_status not in {"confirmed", "accepted_uncertainty"}:
                errors.append(
                    "debug-evidence.md: fix_authorized requires root_cause_status confirmed or accepted_uncertainty"
                )
            if "## Regression-test strategy" not in bodies.get("debug-evidence.md", ""):
                errors.append("debug-evidence.md: authorized fix lacks regression-test strategy")
            if diagnosis_mode == "deterministic_fast_path" and (
                "## Diagnosis mode" not in bodies.get("debug-evidence.md", "")
            ):
                errors.append(
                    "debug-evidence.md: diagnosis_mode is deterministic_fast_path but no "
                    "'## Diagnosis mode' section is present"
                )

    verification = parsed.get("verification.md")
    if verification:
        result = normalized(verification.get("result"))
        if result in {"pass", "pass_with_limitations"} and plan_status != "accepted":
            errors.append("verification passed but plan.md is not accepted")

    release = parsed.get("release.md")
    if release:
        decision = normalized(release.get("release_decision"))
        if decision in {"approve", "approved"}:
            verification_result = normalized((verification or {}).get("result"))
            review_recommendation = normalized(
                parsed.get("review.md", {}).get("gate_recommendation")
            )
            if verification_result not in {"pass", "pass_with_limitations"}:
                errors.append("approved release requires passing verification")
            if review_recommendation not in {"approve", "conditional_approval"}:
                errors.append("approved release requires an approving review recommendation")

    for filename in ARTIFACTS:
        if filename not in parsed and (change_dir / filename).exists():
            warnings.append(f"{filename}: exists but could not be fully validated")

    if errors:
        print(f"Validation FAILED for {change_dir}")
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        return 1

    print(f"Validation PASSED for {change_dir}")
    print(f"Artifacts validated: {len(parsed)} markdown artifact(s) plus traceability.yaml")
    print(
        "NOTE: traceability.yaml was checked structurally (top-level and artifacts.* key "
        "presence), not by full YAML semantic parsing — see structural_check_traceability's "
        "docstring for exact scope and limits."
    )
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
