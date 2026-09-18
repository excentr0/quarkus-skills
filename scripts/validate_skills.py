#!/usr/bin/env python3
"""Validate the repository's Agent Skills files without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
EVALS_FILE = ROOT / "evals" / "trigger-routing.json"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:[ \t]*(.*))?$")


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None, str | None]:
    """Return frontmatter fields, body, and a parsing error."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, None, "missing opening frontmatter delimiter"

    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}, None, "missing closing frontmatter delimiter"

    fields: dict[str, str] = {}
    current_key: str | None = None
    current_value: list[str] = []
    folded: set[str] = set()

    def finish() -> None:
        nonlocal current_key, current_value
        if current_key is None:
            return
        if current_key in folded:
            fields[current_key] = " ".join(part.strip() for part in current_value if part.strip()).strip()
        else:
            fields[current_key] = _unquote(" ".join(current_value).strip())
        current_key = None
        current_value = []

    for line in lines[1:end]:
        match = KEY_RE.match(line) if not line.startswith((" ", "\t")) else None
        if match:
            finish()
            current_key = match.group(1)
            value = (match.group(2) or "").strip()
            if value.startswith((">", "|")):
                folded.add(current_key)
                current_value = []
            else:
                current_value = [value]
            continue
        if current_key is None:
            if line.strip():
                return {}, None, f"unrecognized frontmatter line: {line!r}"
            continue
        current_value.append(line)
    finish()
    return fields, "\n".join(lines[end + 1 :]).strip(), None


def validate_skill(path: Path, errors: list[str], warnings: list[str]) -> str | None:
    fields, body, parse_error = parse_frontmatter(path.read_text(encoding="utf-8"))
    relative = path.relative_to(ROOT)
    if parse_error:
        errors.append(f"{relative}: {parse_error}")
        return None

    name = fields.get("name", "").strip()
    description = fields.get("description", "").strip()
    if not name:
        errors.append(f"{relative}: frontmatter is missing name")
    elif len(name) > 64:
        errors.append(f"{relative}: name is {len(name)} characters (limit 64)")
    elif not NAME_RE.fullmatch(name):
        errors.append(f"{relative}: invalid skill name {name!r}")
    elif name != path.parent.name:
        errors.append(f"{relative}: name {name!r} does not match directory {path.parent.name!r}")

    if not description:
        errors.append(f"{relative}: frontmatter is missing description")
    elif len(description) > 1024:
        errors.append(f"{relative}: description is {len(description)} characters (limit 1024)")

    if not body:
        errors.append(f"{relative}: body is empty")
    else:
        body_lines = len(body.splitlines())
        approx_tokens = len(re.findall(r"\w+|[^\w\s]", body, flags=re.UNICODE))
        if body_lines > 500:
            warnings.append(f"{relative}: body is {body_lines} lines (recommended maximum 500)")
        if approx_tokens > 5000:
            warnings.append(
                f"{relative}: body is approximately {approx_tokens} tokens "
                "(recommended maximum 5000)"
            )

    for match in LINK_RE.finditer(path.read_text(encoding="utf-8")):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and ">" in raw_target:
            raw_target = raw_target[1 : raw_target.index(">")]
        else:
            raw_target = raw_target.split()[0]
        if not raw_target or raw_target.startswith(("#", "http://", "https://", "mailto:", "//")):
            continue
        target = unquote(raw_target.split("#", 1)[0].split("?", 1)[0])
        if not target:
            continue
        candidate = (path.parent / target).resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{relative}: local link escapes repository: {raw_target}")
            continue
        if not candidate.exists():
            errors.append(f"{relative}: local link does not exist: {raw_target}")

    return name or None


def validate_eval_seeds(known_skills: set[str], errors: list[str]) -> None:
    relative = EVALS_FILE.relative_to(ROOT)
    if not EVALS_FILE.exists():
        errors.append(f"{relative}: file does not exist")
        return
    try:
        data = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{relative}: invalid JSON: {exc}")
        return
    if not isinstance(data, list) or not data:
        errors.append(f"{relative}: expected a non-empty JSON array")
        return

    near_miss_skills = {
        "quarkus-explore",
        "quarkus-kafka-configuration",
        "quarkus-rabbitmq-configuration",
    }
    seen_near_misses: set[str] = set()
    for index, case in enumerate(data):
        label = f"{relative}[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label}: expected an object")
            continue
        for key in ("skill", "prompt", "should_trigger"):
            if key not in case:
                errors.append(f"{label}: missing {key}")
        skill = case.get("skill")
        prompt = case.get("prompt")
        should_trigger = case.get("should_trigger")
        if not isinstance(skill, str) or skill not in known_skills:
            errors.append(f"{label}: skill must name a known skill")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{label}: prompt must be a non-empty string")
        if type(should_trigger) is not bool:
            errors.append(f"{label}: should_trigger must be boolean")
        if isinstance(skill, str) and skill in near_miss_skills and should_trigger is False:
            seen_near_misses.add(skill)

    for skill in sorted(near_miss_skills - seen_near_misses):
        errors.append(f"{relative}: missing near-miss case for {skill}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    skill_paths = sorted(
        path
        for path in SKILLS_ROOT.glob("*/SKILL.md")
        if not path.parent.name.endswith("-workspace")
    )
    if not skill_paths:
        errors.append("skills: no SKILL.md files found")

    known_skills: set[str] = set()
    for path in skill_paths:
        name = validate_skill(path, errors, warnings)
        if name:
            if name in known_skills:
                errors.append(f"duplicate skill name: {name}")
            known_skills.add(name)

    validate_eval_seeds(known_skills, errors)

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_paths)} skills and {EVALS_FILE.relative_to(ROOT)}.")
    if warnings:
        print(f"Validation passed with {len(warnings)} warning(s); size recommendations are non-fatal.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
