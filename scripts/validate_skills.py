#!/usr/bin/env python3
"""Validate bundled Agent Skills resources and evaluation seed data (stdlib only)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
EVALS_FILE = ROOT / "evals" / "trigger-routing.json"
EXECUTION_CATALOG = ROOT / "evals" / "execution-catalog.json"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:[ \t]+(.*))?$")
CHECKBOX_RE = re.compile(r"^- \[([ xX])\] (\S.*)$")
CHECKLIST_HEADING = re.compile(r"^#{1,6}\s+(?:Step\s*\d+\s*(?:--|[—–-])\s*)?Anti-hallucination checklist\s*$", re.I)
PLACEHOLDER_START = re.compile(r"\$\{")

MIRRORED_REFERENCES = {
    Path("skills/quarkus-planning/references/extension-glossary.md"): Path("skills/quarkus-explore/references/extension-glossary.md"),
    Path("skills/quarkus-planning/references/entity-description.md"): Path("skills/quarkus-explore/references/entity-description.md"),
    Path("skills/quarkus-planning/references/rest-endpoints.md"): Path("skills/quarkus-explore/references/rest-endpoints.md"),
}
BANNER_PREFIX = "> Local copy of `"


def _plain_scalar(value: str) -> tuple[str | None, str | None]:
    value = value.strip()
    if not value:
        return "", None
    if value.startswith(('"', "'")):
        if value.startswith('"'):
            match = re.fullmatch(r'"([^"\\]*)"(?:[ \t]+#.*)?', value)
            if not match:
                return None, "malformed or unsupported double-quoted scalar"
            return match.group(1), None
        match = re.fullmatch(r"'((?:[^']|'')*)'(?:[ \t]+#.*)?", value)
        if not match:
            return None, "malformed single-quoted scalar"
        return match.group(1).replace("''", "'"), None
    value = re.split(r"[ \t]+#", value, maxsplit=1)[0].rstrip()
    if (value.startswith(("#", "[", "{", "!", "&", "*", "@", "`", "%"))
            or re.match(r"^(?:[?:-])[ \t]", value) or re.search(r":[ \t]", value)):
        return None, "unsupported YAML flow, tag, alias, or indicator scalar"
    if re.fullmatch(r"(?i)(?:~|null|true|false|[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?|[-+]?(?:\.inf|\.nan))", value):
        return None, "plain scalar is not a string; quote it explicitly"
    return value, None


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None, str | None]:
    """Parse flat strings and description blocks (>, >-, |, |-); this is not general YAML."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, None, "missing opening frontmatter delimiter"
    end = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
    if end is None:
        return {}, None, "missing closing frontmatter delimiter"
    fields: dict[str, str] = {}
    current_key: str | None = None
    current_value = ""
    block_marker: str | None = None
    block_lines: list[str] = []
    duplicate: str | None = None

    def finish() -> None:
        nonlocal current_key, current_value, block_marker, block_lines, duplicate
        if current_key is None:
            return
        if current_key in fields:
            duplicate = current_key
        elif block_marker is None:
            fields[current_key] = current_value
        else:
            nonblank = [len(line) - len(line.lstrip(" ")) for line in block_lines if line.strip()]
            indent = min(nonblank) if nonblank else 0
            content = [line[indent:] if line.strip() else "" for line in block_lines]
            rendered = "\n".join(content)
            if block_marker.startswith(">"):
                rendered = re.sub(r"(?<=\S)\n(?=\S)", " ", rendered)
            fields[current_key] = rendered.strip("\n")
        current_key, current_value, block_marker, block_lines = None, "", None, []

    for line in lines[1:end]:
        match = KEY_RE.match(line) if not line.startswith((" ", "\t")) else None
        if match:
            finish()
            current_key = match.group(1)
            value = (match.group(2) or "").strip()
            if value.startswith((">", "|")):
                if current_key != "description" or value not in (">", ">-", "|", "|-"):
                    return {}, None, f"unsupported or malformed block scalar: {value!r}"
                block_marker = value
            else:
                current_value, scalar_error = _plain_scalar(value)
                if scalar_error:
                    return {}, None, f"{scalar_error} for {current_key}: {value!r}"
                current_value = current_value or ""
        elif current_key is None:
            if line.strip():
                return {}, None, f"unrecognized frontmatter line: {line!r}"
        elif block_marker is not None:
            if line.strip() and (not line.startswith(" ") or line.startswith("\t")):
                return {}, None, f"block description content must be indented: {line!r}"
            block_lines.append(line)
        elif line.strip():
            return {}, None, f"unsupported multiline scalar or invalid frontmatter syntax: {line!r}"
    finish()
    if duplicate:
        return {}, None, f"duplicate frontmatter key: {duplicate}"
    return fields, "\n".join(lines[end + 1:]).strip(), None


def checklist_error(body: str) -> str | None:
    lines = body.splitlines()
    headings = [i for i, line in enumerate(lines) if CHECKLIST_HEADING.match(line.strip())]
    if not headings:
        return "missing final Anti-hallucination checklist heading"
    start = headings[-1]
    if any(line.strip().startswith("#") for line in lines[start + 1:]):
        return "Anti-hallucination checklist is not the final section"
    content = [line for line in lines[start + 1:] if line.strip()]
    checks = [line.lstrip() for line in content if line.lstrip().startswith("- [")]
    if not checks:
        return "final Anti-hallucination checklist has no non-empty checkbox items"
    if not all(CHECKBOX_RE.match(line) for line in checks):
        return "checklist checkbox item is empty or malformed"
    last_check = max(i for i, line in enumerate(content) if line.lstrip().startswith("- ["))
    if any(not line[:1].isspace() for line in content[last_check + 1:]):
        return "final checklist section has content after its last checkbox"
    return None


def malformed_placeholders(text: str) -> list[int]:
    """Return line numbers with an opening template marker lacking a closing brace."""
    bad: list[int] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        pos = 0
        while True:
            pos = line.find("${", pos)
            if pos < 0:
                break
            if line.find("}", pos + 2) < 0:
                bad.append(line_no)
                break
            pos += 2
    return bad


def bundled_candidates(document: Path, skill_dir: Path, target: str) -> list[Path]:
    clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not clean or "{" in clean or "}" in clean:
        return []
    return [(document.parent / clean).resolve(), (skill_dir / clean).resolve()]


def is_portable_external(candidate: Path, skill_dir: Path) -> bool:
    parts = candidate.parts
    return candidate.name == "quarkus-facts.md" and "docs" in parts or (
        candidate.name == "SKILL.md" and candidate.parent.name.startswith("quarkus-")
        and candidate.parent.name != skill_dir.name
    )


def has_portability_policy(skill_dir: Path) -> bool:
    entry = skill_dir / "SKILL.md"
    if not entry.is_file():
        return False
    body = entry.read_text(encoding="utf-8").lower()
    return ("portable resources and sibling handoffs" in body
            and "if missing" in body
            and "apply equivalent local instructions" in body
            and "docs/quarkus-facts.md" in body)


def validate_resource_reference(document: Path, skill_dir: Path, target: str,
                                label: str, errors: list[str], strict_bundled: bool = True) -> None:
    candidates = bundled_candidates(document, skill_dir, target)
    if not candidates:
        return
    for candidate in candidates:
        try:
            candidate.relative_to(skill_dir.resolve())
        except ValueError:
            continue
        if candidate.exists():
            return
    normalized = target.replace("\\", "/")
    parts = Path(normalized).parts
    if parts and parts[0].startswith("quarkus-") and parts[0] != skill_dir.name:
        first_line = document.read_text(encoding="utf-8").splitlines()[:1]
        is_mirror_banner = bool(first_line and first_line[0].startswith(BANNER_PREFIX))
        if is_mirror_banner and has_portability_policy(skill_dir):
            return
        errors.append(f"{label}: sibling resource is not a bundled entrypoint or declared mirror: {target}")
        return
    is_bundle_path = any(part in parts for part in ("references", "examples"))
    is_sibling = Path(normalized).name == "SKILL.md" and "quarkus-" in normalized
    is_facts = "docs" in parts and Path(normalized).name == "quarkus-facts.md"
    if any(part in parts for part in ("src", "target", "build")) or "plans" in parts:
        return  # user-project paths mentioned as instructions are not bundled resources
    external = next((candidate for candidate in candidates if is_portable_external(candidate, skill_dir)), None)
    if (is_sibling or is_facts) and external and has_portability_policy(skill_dir):
        return
    if not strict_bundled and (is_sibling or is_facts) and external:
        if not has_portability_policy(skill_dir):
            errors.append(f"{label}: external resource has no standalone fallback policy: {target}")
        return
    local_markdown = Path(normalized).suffix.lower() == ".md"
    if is_bundle_path or local_markdown:
        errors.append(f"{label}: bundled Markdown resource does not exist inside this skill: {target}")


def validate_links(skill_dir: Path, errors: list[str], strict_bundled: bool = True) -> None:
    skill_dir = skill_dir.resolve()
    for document in sorted(skill_dir.rglob("*.md")):
        rel = document.relative_to(skill_dir)
        content = document.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(content):
            raw = match.group(1).strip()
            raw = raw[1:raw.index(">")].strip() if raw.startswith("<") and ">" in raw else raw.split()[0]
            if not raw or raw.startswith(("#", "http://", "https://", "mailto:", "//")):
                continue
            validate_resource_reference(document, skill_dir, raw, str(rel), errors, strict_bundled)
        # Backticked authored resource paths are references too, but arbitrary user-project paths
        # (src/main/java/...) and Maven properties (e.g. ${mapstruct.version}) are not.
        non_link_content = LINK_RE.sub("", content)
        for token in re.findall(r"`([^`]+\.md)`", non_link_content):
            normalized = token.replace("\\", "/")
            if (not any(part in normalized.split("/") for part in ("references", "examples"))
                    and Path(normalized).name != "SKILL.md"
                    and not ("docs" in normalized.split("/") and Path(normalized).name == "quarkus-facts.md")):
                continue
            if "${" in token:
                continue
            validate_resource_reference(document, skill_dir, token, str(rel), errors, strict_bundled)


def _blocklist_tokens(facts_path: Path) -> list[str]:
    text = facts_path.read_text(encoding="utf-8")
    match = re.search(r"### Blocklist[^\n]*\n(.*?)(?=\n##? |\Z)", text, re.S)
    if not match:
        raise ValueError(f"Blocklist section missing in {facts_path}")
    return re.findall(r"`([^`]+)`", match.group(1))


def _blocklist_pattern(token: str) -> re.Pattern[str]:
    if token.startswith("@"):
        # Keep @BeanMapping distinct from the exact @Bean annotation.
        return re.compile(r"(?<![\w$])" + re.escape(token) + r"(?![A-Za-z0-9_$])")
    if re.fullmatch(r"[A-Za-z0-9_.-]+", token):
        return re.compile(r"(?<![A-Za-z0-9_$])" + re.escape(token) + r"(?![A-Za-z0-9_$])", re.I)
    return re.compile(re.escape(token), re.I)


def validate_example_blocklist(skill_dir: Path, errors: list[str], facts_path: Path) -> None:
    tokens = _blocklist_tokens(facts_path)
    patterns = [(token, _blocklist_pattern(token)) for token in tokens]
    for document in sorted((skill_dir / "examples").rglob("*.md")) if (skill_dir / "examples").exists() else []:
        for index, match in enumerate(re.finditer(r"```([^\n]*)\n(.*?)\n```", document.read_text(encoding="utf-8"), re.S), 1):
            code = match.group(2)
            for token, pattern in patterns:
                if pattern.search(code):
                    errors.append(f"{document.relative_to(skill_dir)}: blocked example token {token!r} in fence {index}")


def validate_placeholders(skill_dir: Path, errors: list[str]) -> None:
    for document in sorted(skill_dir.rglob("*.md")):
        for line in malformed_placeholders(document.read_text(encoding="utf-8")):
            errors.append(f"{document.relative_to(skill_dir)}:{line}: malformed ${{...}} placeholder (missing closing brace)")


def validate_skill(path: Path, errors: list[str], warnings: list[str], facts_path: Path | None = None,
                   strict_bundled: bool = True) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: cannot read: {exc}")
        return None
    fields, body, parse_error = parse_frontmatter(text)
    if parse_error:
        errors.append(f"{path}: {parse_error}")
        return None
    name = fields.get("name", "").strip()
    description = fields.get("description", "").strip()
    if not name:
        errors.append(f"{path}: frontmatter is missing name")
    elif len(name) > 64:
        errors.append(f"{path}: name exceeds 64 characters")
    elif not NAME_RE.fullmatch(name):
        errors.append(f"{path}: invalid skill name {name!r}")
    elif name != path.parent.name:
        errors.append(f"{path}: name {name!r} does not match directory {path.parent.name!r}")
    if not description:
        errors.append(f"{path}: frontmatter is missing description")
    elif len(description) > 1024:
        errors.append(f"{path}: description exceeds 1024 characters")
    if not body:
        errors.append(f"{path}: body is empty")
    else:
        lines = len(body.splitlines())
        tokens = len(re.findall(r"\w+|[^\w\s]", body, flags=re.UNICODE))
        if lines > 500:
            warnings.append(f"{path}: body is {lines} lines (recommended maximum 500)")
        if tokens > 5000:
            warnings.append(f"{path}: body is approximately {tokens} tokens (recommended maximum 5000)")
        error = checklist_error(body)
        if error:
            errors.append(f"{path}: {error}")
    validate_placeholders(path.parent, errors)
    validate_links(path.parent, errors, strict_bundled)
    if facts_path:
        validate_example_blocklist(path.parent, errors, facts_path)
    return name or None


def validate_selected_fixture_placeholders(root: Path, errors: list[str]) -> int:
    """Read-only validation for fences rendered by the fixture; does not generate target files."""
    path = root / "scripts/run_template_fixture.py"
    spec = importlib.util.spec_from_file_location("template_fixture_renderer", path)
    if spec is None or spec.loader is None:
        errors.append(f"{path}: cannot load read-only fence renderer")
        return 0
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    crud = root / "skills/quarkus-crud-rest-controller/examples"
    mapper = root / "skills/quarkus-mapper-creator/examples"
    selected = [
        (crud / "_skeletons/java.md", "## Code", None, 0),
        (crud / "_beans/injection/java.md", "### repository + Validator (no DTO, PATCH or PATCH_MANY selected)", None, 0),
        (crud / "_beans/injection/java.md", "### repository + mapper + ObjectMapper + Validator (DTO mode, PATCH or PATCH_MANY selected)", None, 0),
        (crud / "_methods/patch/java.md", "## Shared helpers (insert once)", None, 0),
        (crud / "_methods/patch/java.md", "## Shared DTO helper (DTO mode only)", None, 0),
    ]
    selected.extend([
        (crud / "_methods/patch/java.md", "### no DTO", None, 0),
        (crud / "_methods/patch/java.md", "### no DTO", None, 1),
        (crud / "_methods/patch/java.md", "### with DTO + mapper", None, 0),
        (crud / "_methods/patch-many/java.md", "### no DTO", None, 0),
        (crud / "_methods/patch-many/java.md", "### with DTO + mapper", None, 0),
        (mapper / "_fragments/partial-update-method/java.md", "### Safe CRUD PATCH variant (only when called with the CRUD PATCH contract)", None, 0),
    ])
    scalar_types = ["String", "Boolean", "int", "long", "double", "BigDecimal (JSON string representation)", "UUID (JSON string representation)", "Enum (JSON string representation)"]
    fragment = crud / "_fragments/patch-field/java.md"
    for kind in scalar_types:
        selected.extend([(fragment, f"## {kind}", "### Type check", 0), (fragment, f"## {kind}", "### no-DTO write", 0)])
    selected.extend([
        (crud / "_methods/create/java.md", "### with DTO", None, 0),
        (crud / "_methods/get-one/java.md", "### with DTO", None, 0),
        (crud / "_methods/get-list/java.md", "### no pagination, with DTO", None, 0),
    ])
    checked = 0
    for source, heading, subheading, index in selected:
        try:
            module.render_fence(source, heading, subheading, index)
            checked += 1
        except (OSError, ValueError) as exc:
            errors.append(f"selected template {source.relative_to(root)} [{heading}]: {exc}")
    return checked


def _strip_provenance_banner(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if lines and lines[0].startswith(BANNER_PREFIX):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "".join(lines)


def validate_mirrored_references(root: Path, errors: list[str]) -> None:
    for copy_rel, origin_rel in MIRRORED_REFERENCES.items():
        copy_path, origin_path = root / copy_rel, root / origin_rel
        if not copy_path.is_file() or not origin_path.is_file():
            errors.append(f"{copy_rel}: mirrored copy or origin missing")
            continue
        if _strip_provenance_banner(copy_path.read_text(encoding="utf-8")) != origin_path.read_text(encoding="utf-8"):
            errors.append(f"{copy_rel}: diverged from {origin_rel}")


def validate_eval_seeds(known_skills: set[str], errors: list[str], evals_file: Path = EVALS_FILE) -> dict[str, int]:
    try:
        data = json.loads(evals_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{evals_file}: invalid JSON: {exc}")
        return {}
    if not isinstance(data, list) or not data:
        errors.append(f"{evals_file}: expected a non-empty JSON array")
        return {}
    seen_ids: set[str] = set()
    language_positives: dict[str, set[str]] = {"en": set(), "ru": set()}
    near_miss_skills = {"quarkus-explore", "quarkus-kafka-configuration", "quarkus-rabbitmq-configuration"}
    negatives: set[str] = set()
    compositions = 0
    for i, case in enumerate(data):
        label = f"{evals_file.name}[{i}]"
        if not isinstance(case, dict):
            errors.append(f"{label}: expected object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{label}: id must be non-empty string")
        elif case_id in seen_ids:
            errors.append(f"{label}: duplicate id {case_id!r}")
        else:
            seen_ids.add(case_id)
        skill, prompt, trigger = case.get("skill"), case.get("prompt"), case.get("should_trigger")
        lang = case.get("language")
        if not isinstance(skill, str) or skill not in known_skills:
            errors.append(f"{label}: skill must name a known skill")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{label}: prompt must be non-empty")
        if type(trigger) is not bool:
            errors.append(f"{label}: should_trigger must be boolean")
        if lang not in ("en", "ru"):
            errors.append(f"{label}: language must be en or ru")
        expected, allowed = case.get("expected_reads"), case.get("allowed_companions")
        if not isinstance(expected, list) or not all(isinstance(x, str) and x in known_skills for x in expected):
            errors.append(f"{label}: expected_reads must be a list of known skill names")
            expected = []
        if not isinstance(allowed, list) or not all(isinstance(x, str) and x in known_skills for x in allowed):
            errors.append(f"{label}: allowed_companions must be a list of known skill names")
            allowed = []
        if isinstance(skill, str) and type(trigger) is bool:
            if trigger and isinstance(lang, str):
                language_positives.setdefault(lang, set()).add(skill)
            if not trigger and skill in near_miss_skills:
                negatives.add(skill)
        if isinstance(expected, list) and len(expected) > 1:
            compositions += 1
        for field in ("expected_handoffs",):
            value = case.get(field)
            if value is not None and (not isinstance(value, list) or not all(isinstance(x, str) and x in known_skills for x in value)):
                errors.append(f"{label}: {field} must be a list of known skill names when supplied")
        if "expected_stop_decision" in case and type(case["expected_stop_decision"]) is not bool:
            errors.append(f"{label}: expected_stop_decision must be boolean")
        if trigger is True and isinstance(skill, str) and skill not in expected:
            errors.append(f"{label}: positive seed expected_reads must include primary skill {skill}")
        if trigger is False and expected:
            errors.append(f"{label}: negative seed expected_reads must be empty")
        if trigger is False and isinstance(skill, str) and skill in allowed:
            errors.append(f"{label}: negative probe primary skill must not be an allowed companion")
    for language, positives in language_positives.items():
        missing = known_skills - positives
        if missing:
            errors.append(f"{evals_file.name}: missing {language} positive seeds for {', '.join(sorted(missing))}")
    for skill in sorted(near_miss_skills - negatives):
        errors.append(f"{evals_file.name}: missing broker near-miss for {skill}")
    if compositions < 1:
        errors.append(f"{evals_file.name}: missing multi-skill composition seed")
    return {"count": len(data), "skills": len(known_skills), "composition": compositions}


def validate_execution_catalog(path: Path, errors: list[str]) -> int:
    """Validate check definitions, not historical or fresh execution results."""
    try:
        cases = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return 0
    if not isinstance(cases, list) or not 5 <= len(cases) <= 10:
        errors.append(f"{path}: expected 5-10 execution check definitions")
        return 0
    ids: set[str] = set()
    for i, case in enumerate(cases):
        label = f"{path.name}[{i}]"
        if not isinstance(case, dict):
            errors.append(f"{label}: expected object")
            continue
        case_id, kind = case.get("id"), case.get("kind")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            errors.append(f"{label}: id missing or duplicate")
        else:
            ids.add(case_id)
        if "status" in case or "result" in case:
            errors.append(f"{label}: catalog defines checks, not execution results; remove status/result")
        if kind not in ("automated", "manual"):
            errors.append(f"{label}: kind must be automated or manual")
        detail_key = "command" if kind == "automated" else "scenario"
        if not isinstance(case.get(detail_key), str) or not case[detail_key].strip():
            errors.append(f"{label}: non-empty {detail_key} required for {kind!r} definition")
        if not isinstance(case.get("assertions"), list) or not case["assertions"] or not all(
                isinstance(item, str) and item for item in case["assertions"]):
            errors.append(f"{label}: non-empty assertions list required")
    return len(cases)


def discover_skill_paths(skills_root: Path) -> list[Path]:
    return sorted(path for path in skills_root.glob("*/SKILL.md")
                  if not path.parent.name.endswith("-workspace"))


def validate_standalone_copy(skill_dir: Path, errors: list[str], facts_path: Path) -> None:
    entry = skill_dir / "SKILL.md"
    if not entry.is_file():
        errors.append(f"{skill_dir}: isolated bundle has no SKILL.md")
        return
    local_errors: list[str] = []
    validate_skill(entry, local_errors, [], facts_path, strict_bundled=False)
    if not has_portability_policy(skill_dir):
        local_errors.append("SKILL.md: missing standalone external-facts/sibling fallback policy")
    errors.extend(f"standalone {skill_dir.name}: {error}" for error in local_errors)


def validate_standalone_packages(skill_paths: list[Path], facts_path: Path) -> int:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="quarkus-skills-standalone-") as temporary:
        base = Path(temporary)
        for skill_path in skill_paths:
            target = base / skill_path.parent.name
            shutil.copytree(skill_path.parent, target)
            validate_standalone_copy(target, errors, facts_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return len(errors)
    print(f"Standalone packaging smoke passed for {len(skill_paths)} isolated skills (temporary copies removed).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--standalone", action="store_true", help="copy and validate each skill independently")
    args = parser.parse_args(argv)
    errors: list[str] = []
    warnings: list[str] = []
    skill_paths = discover_skill_paths(SKILLS_ROOT)
    if not skill_paths:
        errors.append("skills: no SKILL.md files found")
    known: set[str] = set()
    for skill_path in skill_paths:
        name = validate_skill(skill_path, errors, warnings, ROOT / "docs/quarkus-facts.md")
        if name:
            if name in known:
                errors.append(f"duplicate skill name: {name}")
            known.add(name)
    validate_mirrored_references(ROOT, errors)
    seed_summary = validate_eval_seeds(known, errors)
    catalog_count = validate_execution_catalog(EXECUTION_CATALOG, errors)
    selected_count = validate_selected_fixture_placeholders(ROOT, errors)
    if args.standalone:
        standalone_errors = validate_standalone_packages(skill_paths, ROOT / "docs/quarkus-facts.md")
        if standalone_errors:
            errors.append(f"standalone smoke: {standalone_errors} error(s)")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validated {len(skill_paths)} skills; {seed_summary.get('count', 0)} routing seed cases validated (not measured); "
          f"{seed_summary.get('skills', 0)} skills have EN/RU positive seeds; {seed_summary.get('composition', 0)} compositions; "
          f"{selected_count} selected fixture fences checked for declared placeholders; {catalog_count} execution check definitions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
