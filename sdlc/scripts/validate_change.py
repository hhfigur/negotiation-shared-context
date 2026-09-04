#!/usr/bin/env python3
"""Validate a Negotiation AI SDLC change directory and lifecycle prerequisites."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print(
        "ERROR: PyYAML is required for validation. Install it in an isolated environment; this script will not install dependencies automatically.",
        file=sys.stderr,
    )
    raise SystemExit(2)

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate one SDLC change directory.")
    parser.add_argument("change_dir", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat unresolved placeholders in accepted or completed artifacts as errors.",
    )
    return parser.parse_args()


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening YAML frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing YAML frontmatter delimiter") from exc
    frontmatter_text = "\n".join(lines[1:end])
    data = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    body = "\n".join(lines[end + 1 :])
    return data, body


def normalized(value: Any) -> str:
    return str(value or "").strip().lower()


def is_set(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and not text.startswith("<") and "{{" not in text


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
        except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
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
            loaded = yaml.safe_load(trace_path.read_text(encoding="utf-8")) or {}
            if not isinstance(loaded, dict):
                raise ValueError("root must be a mapping")
            trace = loaded
            if str(trace.get("change_id", "")) != change_id:
                errors.append(
                    f"traceability.yaml: change_id must be {change_id!r}, got {trace.get('change_id')!r}"
                )
        except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"traceability.yaml: invalid YAML: {exc}")

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
        if fix_authorized:
            root_status = normalized(debug.get("root_cause_status"))
            if root_status not in {"confirmed", "accepted_uncertainty"}:
                errors.append(
                    "debug-evidence.md: fix_authorized requires root_cause_status confirmed or accepted_uncertainty"
                )
            if "## Regression-test strategy" not in bodies.get("debug-evidence.md", ""):
                errors.append("debug-evidence.md: authorized fix lacks regression-test strategy")

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

    artifact_map = trace.get("artifacts") if isinstance(trace, dict) else None
    if isinstance(artifact_map, dict):
        expected_keys = {
            "intent",
            "specification",
            "plan",
            "debug_evidence",
            "verification",
            "review",
            "release",
            "outcome",
            "incident",
        }
        missing_keys = expected_keys.difference(artifact_map)
        if missing_keys:
            errors.append(
                "traceability.yaml: missing artifact keys: " + ", ".join(sorted(missing_keys))
            )
    elif trace_path.is_file():
        errors.append("traceability.yaml: artifacts must be a mapping")

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
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
