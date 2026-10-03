#!/usr/bin/env python3
"""Render source-backed Quarkus examples and run an isolated Maven fixture."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/template-rendered"
OUT = FIXTURE / "target/rendered"
CRUD = ROOT / "skills/quarkus-crud-rest-controller/examples"
MAPPER = ROOT / "skills/quarkus-mapper-creator/examples"


def heading_section(path: Path, heading: str, subheading: str | None = None) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    index = next((i for i, line in enumerate(lines) if line.strip() == heading), None)
    if index is None:
        raise ValueError(f"missing heading {heading!r} in {path}")
    level = len(heading.split()[0])
    end = next((i for i in range(index + 1, len(lines))
                if (match := re.match(r"^(#{1,6}) ", lines[i])) and len(match.group(1)) <= level), len(lines))
    section = lines[index + 1:end]
    if subheading:
        sub_index = next((i for i, line in enumerate(section) if line.strip() == subheading), None)
        if sub_index is None:
            raise ValueError(f"missing heading {subheading!r} in {path} under {heading!r}")
        sublevel = len(subheading.split()[0])
        sub_end = next((i for i in range(sub_index + 1, len(section))
                        if (match := re.match(r"^(#{1,6}) ", section[i])) and len(match.group(1)) <= sublevel), len(section))
        section = section[sub_index + 1:sub_end]
    return "\n".join(section)


def declared_placeholders(document: str) -> set[str]:
    return set(re.findall(r"\|\s*`?\$\{([A-Za-z][A-Za-z0-9]*)\}`?\s*\|", document)) | set(
        re.findall(r"\|\s*`\{(packageName|className|requestPath)\}`\s*\|", document)
    )


def render_fence(path: Path, heading: str, subheading: str | None = None,
                 fence_index: int = 0) -> str:
    document = path.read_text(encoding="utf-8")
    section = heading_section(path, heading, subheading)
    blocks = re.findall(r"```(?:java)?\s*\n(.*?)\n```", section, re.S)
    if fence_index >= len(blocks):
        raise ValueError(f"expected code fence {fence_index + 1} under {heading!r} in {path}")
    result = blocks[fence_index]
    used = set(re.findall(r"\$\{([A-Za-z][A-Za-z0-9]*)\}", result)) | set(
        re.findall(r"\{(packageName|className|requestPath)\}", result)
    )
    undeclared = used - declared_placeholders(document)
    if undeclared:
        raise ValueError(f"undeclared placeholders in {path} [{heading}]: {sorted(undeclared)}")
    return result


def substitute(source: str, values: dict[str, str]) -> str:
    result = source
    for key, value in values.items():
        result = result.replace("${" + key + "}", value).replace("{" + key + "}", value)
    unresolved = re.findall(r"\$\{[^}]+\}|\{(?:packageName|className|requestPath)\}", result)
    if unresolved:
        raise ValueError("unresolved template variables: " + ", ".join(sorted(set(unresolved))))
    return result


class Renderer:
    def __init__(self) -> None:
        self.sources: dict[str, str] = {}

    def fence(self, path: Path, heading: str, subheading: str | None = None,
              fence_index: int = 0) -> str:
        self.sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        return render_fence(path, heading, subheading, fence_index)

    def expanded(self, path: Path, heading: str, subheading: str | None,
                 values: dict[str, str], fence_index: int = 0) -> str:
        return substitute(self.fence(path, heading, subheading, fence_index), values)


def block_values(renderer: Renderer) -> tuple[dict[str, str], str]:
    fields = ["name", "note", "count", "active", "amount", "token", "state", "longValue", "ratio"]
    types = [
        ("String", "name"), ("String", "note"), ("int", "count"), ("Boolean", "active"),
        ("BigDecimal (JSON string representation)", "amount"),
        ("UUID (JSON string representation)", "token"),
        ("Enum (JSON string representation)", "state"), ("long", "longValue"), ("double", "ratio"),
    ]
    checks: list[str] = []
    writes: list[str] = []
    fragment = CRUD / "_fragments/patch-field/java.md"
    for kind, field in types:
        checks.append(substitute(renderer.fence(fragment, f"## {kind}", "### Type check"),
                                 {"fieldName": field, "enumTypeFqn": "example.Item.State"}))
        null_assignment = ('throw new jakarta.ws.rs.BadRequestException("Null is not allowed");'
                           if field in {"count", "active", "longValue", "ratio"}
                           else f"entity.{field} = null;")
        writes.append(substitute(renderer.fence(fragment, f"## {kind}", "### no-DTO write"), {
            "fieldName": field, "enumTypeFqn": "example.Item.State", "nullAssignment": null_assignment,
            "fieldWritePrefix": f"entity.{field} = ", "fieldWriteSuffix": ";",
        }))
    names = ", ".join(json.dumps(name) for name in fields)
    primitive = ', '.join(json.dumps(name) for name in ("count", "active", "longValue", "ratio"))
    common = {"mutableFieldNames": names, "primitiveFieldNames": primitive,
              "patchTypeChecks": "\n".join(checks), "validatorFieldName": "validator"}
    return common, "\n".join(writes)


def resource_skeleton(renderer: Renderer, classname: str, path: str) -> str:
    template = CRUD / "_skeletons/java.md"
    return substitute(renderer.fence(template, "## Code"), {
        "packageName": "example", "className": classname, "requestPath": path,
    })


def render_public_resource(renderer: Renderer, common: dict[str, str], writes: str) -> str:
    inject = renderer.expanded(CRUD / "_beans/injection/java.md",
        "### repository + Validator (no DTO, PATCH or PATCH_MANY selected)", None,
        {"RepoFqn": "example.ItemRepository", "repoFieldName": "repository", "ResourceName": "ItemResource"})
    helpers = renderer.expanded(CRUD / "_methods/patch/java.md", "## Shared helpers (insert once)", None, common)
    patch_path = CRUD / "_methods/patch/java.md"
    apply_fence = renderer.fence(patch_path, "### no DTO", None, 0)
    patch_fence = renderer.fence(patch_path, "### no DTO", None, 1)
    apply = substitute(apply_fence, {"EntityFqn": "Item", "patchAssignments": writes, **common})
    patch = substitute(patch_fence, {"EntityFqn": "example.Item", "IdType": "Long", "entityVar": "item", "repoFieldName": "repository"})
    many = renderer.expanded(CRUD / "_methods/patch-many/java.md", "### no DTO", None, {
        "IdType": "Long", "EntityFqn": "example.Item", "entityVarPlural": "items",
        "repoFieldName": "repository", "idAccessExpression": "entity.id",
    })
    listing = renderer.expanded(CRUD / "_methods/get-list/java.md", "### pagination, with fixed sort, no DTO", None, {
        "EntityFqn": "example.Item", "repoFieldName": "repository", "sortFieldName": "name",
    })
    create = renderer.expanded(CRUD / "_methods/create/java.md", "### defaults", None, {
        "EntityFqn": "example.Item", "entityVar": "item", "repoFieldName": "repository",
    })
    get_one = renderer.expanded(CRUD / "_methods/get-one/java.md", "### defaults", None, {
        "EntityFqn": "example.Item", "IdType": "Long", "repoFieldName": "repository",
    })
    body = "\n\n".join((inject, helpers, apply, listing, create, get_one, patch, many))
    return resource_skeleton(renderer, "ItemResource", "/items").replace("\n\n}", "\n" + body + "\n}")


def render_mapper(renderer: Renderer) -> None:
    template = MAPPER / "_fragments/partial-update-method/java.md"
    names = ["name", "note", "count", "active", "amount", "token", "state", "longValue", "ratio"]
    mapping_lines = "\n".join(
        f'@org.mapstruct.Mapping(target = "{name}", source = "{name}")' for name in names
    )
    method = renderer.expanded(template,
        "### Safe CRUD PATCH variant (only when called with the CRUD PATCH contract)", None, {
            "mutableUpdateMappings": mapping_lines, "entityClassFqn": "example.Item",
            "dtoClassFqn": "example.ItemDto", "methodName": "partialUpdate",
            "dtoParamName": "itemDto", "entityParamName": "item",
        })
    mapper = OUT / "src/main/java/example/ItemMapper.java"
    source = mapper.read_text(encoding="utf-8")
    if "// SAFE_PATCH_METHOD" not in source:
        raise ValueError("mapper fixture is missing safe method insertion marker")
    mapper.write_text(source.replace("// SAFE_PATCH_METHOD", method), encoding="utf-8")


def render_dto_resource(renderer: Renderer, common: dict[str, str]) -> str:
    beans = renderer.expanded(CRUD / "_beans/injection/java.md",
        "### repository + mapper + ObjectMapper + Validator (DTO mode, PATCH or PATCH_MANY selected)", None, {
            "RepoFqn": "example.ItemRepository", "repoFieldName": "repository", "MapperFqn": "example.ItemMapper",
            "mapperFieldName": "mapper", "ObjectMapperFqn": "com.fasterxml.jackson.databind.ObjectMapper",
            "ResourceName": "DtoItemResource",
        })
    helpers = renderer.expanded(CRUD / "_methods/patch/java.md", "## Shared helpers (insert once)", None, common)
    dto_helper = renderer.expanded(CRUD / "_methods/patch/java.md", "## Shared DTO helper (DTO mode only)", None, {
        "DtoFqn": "example.ItemDto"})
    patch = renderer.expanded(CRUD / "_methods/patch/java.md", "### with DTO + mapper", None, {
        "DtoFqn": "example.ItemDto", "EntityFqn": "example.Item", "IdType": "Long",
        "entityVar": "item", "repoFieldName": "repository", "mapperFieldName": "mapper",
        "toDtoMethodName": "toItemDto", "updateEntityMethodName": "partialUpdate",
    })
    many = renderer.expanded(CRUD / "_methods/patch-many/java.md", "### with DTO + mapper", None, {
        "DtoFqn": "example.ItemDto", "EntityFqn": "example.Item", "IdType": "Long",
        "entityVarPlural": "items", "repoFieldName": "repository", "mapperFieldName": "mapper",
        "toDtoMethodName": "toItemDto", "updateEntityMethodName": "partialUpdate", "idAccessExpression": "entity.id",
    })
    listing = renderer.expanded(CRUD / "_methods/get-list/java.md", "### no pagination, with DTO", None, {
        "EntityFqn": "example.Item", "DtoFqn": "example.ItemDto", "repoFieldName": "repository",
        "entityVarPlural": "items", "mapperFieldName": "mapper", "toDtoMethodName": "toItemDto",
    })
    create = renderer.expanded(CRUD / "_methods/create/java.md", "### with DTO", None, {
        "DtoFqn": "example.ItemDto", "EntityFqn": "example.Item", "dtoVar": "itemDto",
        "entityVar": "item", "repoFieldName": "repository", "mapperFieldName": "mapper",
        "toEntityMethodName": "toEntity", "toDtoMethodName": "toItemDto",
    })
    get_one = renderer.expanded(CRUD / "_methods/get-one/java.md", "### with DTO", None, {
        "DtoFqn": "example.ItemDto", "EntityFqn": "example.Item", "IdType": "Long",
        "repoFieldName": "repository", "entityVar": "item", "mapperFieldName": "mapper",
        "toDtoMethodName": "toItemDto",
    })
    body = "\n\n".join((beans, helpers, dto_helper, listing, create, get_one, patch, many))
    return resource_skeleton(renderer, "DtoItemResource", "/dto-items").replace("\n\n}", "\n" + body + "\n}")


def render_setter_resource(renderer: Renderer, common: dict[str, str]) -> str:
    entity = "example.SetterItem"
    repo = "example.SetterItemRepository"
    bean = renderer.expanded(CRUD / "_beans/injection/java.md",
        "### repository + Validator (no DTO, PATCH or PATCH_MANY selected)", None, {
            "RepoFqn": repo, "repoFieldName": "repository", "ResourceName": "SetterItemResource"})
    helpers = renderer.expanded(CRUD / "_methods/patch/java.md", "## Shared helpers (insert once)", None, {
        **common,
        "mutableFieldNames": '"name", "count"', "primitiveFieldNames": '"count"',
        "patchTypeChecks": "\n".join((
            substitute(renderer.fence(CRUD / "_fragments/patch-field/java.md", "## String", "### Type check"), {"fieldName": "name"}),
            substitute(renderer.fence(CRUD / "_fragments/patch-field/java.md", "## int", "### Type check"), {"fieldName": "count"}),
        )),
    })
    fragment = CRUD / "_fragments/patch-field/java.md"
    assignments = "\n".join((
        substitute(renderer.fence(fragment, "## String", "### no-DTO write"), {
            "fieldName": "name", "nullAssignment": "entity.setName(null);",
            "fieldWritePrefix": "entity.setName(", "fieldWriteSuffix": ");",
        }),
        substitute(renderer.fence(fragment, "## int", "### no-DTO write"), {
            "fieldName": "count", "nullAssignment": 'throw new jakarta.ws.rs.BadRequestException("Null is not allowed");',
            "fieldWritePrefix": "entity.setCount(", "fieldWriteSuffix": ");",
        }),
    ))
    # Convert shared type checks to the setter entity's actual allowlist.
    apply = renderer.fence(CRUD / "_methods/patch/java.md", "### no DTO", None, 0)
    apply = substitute(apply, {"EntityFqn": entity, "patchAssignments": assignments,
        "mutableFieldNames": '"name", "count"', "primitiveFieldNames": '"count"',
        "patchTypeChecks": "\n".join((
            substitute(renderer.fence(fragment, "## String", "### Type check"), {"fieldName": "name"}),
            substitute(renderer.fence(fragment, "## int", "### Type check"), {"fieldName": "count"}),
        )), "validatorFieldName": "validator"})
    repo_name = "repository"
    helper_apply = apply
    patch = substitute(renderer.fence(CRUD / "_methods/patch/java.md", "### no DTO", None, 1), {"EntityFqn": entity, "IdType": "Long", "entityVar": "item", "repoFieldName": repo_name})
    many = renderer.expanded(CRUD / "_methods/patch-many/java.md", "### no DTO", None, {
        "IdType": "Long", "EntityFqn": entity, "entityVarPlural": "items", "repoFieldName": repo_name,
        "idAccessExpression": "entity.id",
    })
    create = renderer.expanded(CRUD / "_methods/create/java.md", "### defaults", None, {
        "EntityFqn": entity, "entityVar": "item", "repoFieldName": repo_name,
    })
    get_one = renderer.expanded(CRUD / "_methods/get-one/java.md", "### defaults", None, {
        "EntityFqn": entity, "IdType": "Long", "repoFieldName": repo_name,
    })
    body = "\n\n".join((bean, helpers, helper_apply, create, get_one, patch, many))
    return resource_skeleton(renderer, "SetterItemResource", "/setter-items").replace("\n\n}", "\n" + body + "\n}")


def generate() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(FIXTURE / "src", OUT / "src")
    shutil.copy2(FIXTURE / "pom.xml", OUT / "pom.xml")
    renderer = Renderer()
    common, writes = block_values(renderer)
    resources = OUT / "src/main/java/example"
    resources.mkdir(parents=True, exist_ok=True)
    (resources / "ItemResource.java").write_text(render_public_resource(renderer, common, writes), encoding="utf-8")
    (resources / "DtoItemResource.java").write_text(render_dto_resource(renderer, common), encoding="utf-8")
    (resources / "SetterItemResource.java").write_text(render_setter_resource(renderer, common), encoding="utf-8")
    render_mapper(renderer)
    it_doc = ROOT / "skills/quarkus-test-writing/examples/integration-test.md"
    # The integration example has one unnamed Java fence.
    renderer.sources[str(it_doc.relative_to(ROOT))] = hashlib.sha256(it_doc.read_bytes()).hexdigest()
    it_match = re.search(r"```java\s*\n(.*?)\n```", it_doc.read_text(encoding="utf-8"), re.S)
    if not it_match:
        raise ValueError(f"missing integration test example fence in {it_doc}")
    it_code = substitute(it_match.group(1), {
        "testPackage": "example", "TargetClass": "ItemResource", "methodName": "packagedCrudRoute",
        "verifiedPath": "/items", "expectedStatus": "200", "verifiedJsonPath": "[0].name",
        "expectedValue": '"packaged"',
    })
    it_code = it_code.replace('        given()\n                .when().get("/items")',
        '        given().contentType("application/json").body("{\\"name\\":\\"packaged\\",\\"count\\":4}").post("/items").then().statusCode(200);\n'
        '        given()\n                .when().get("/items")')
    test_path = OUT / "src/test/java/example/ItemResourceIT.java"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(it_code, encoding="utf-8")
    (OUT / "render-inputs.json").write_text(json.dumps(
        [{"path": path, "sha256": digest} for path, digest in sorted(renderer.sources.items())], indent=2) + "\n", encoding="utf-8")


def report_counts(report: Path) -> tuple[int, int, int]:
    files = sorted(report.glob("TEST-*.xml")) if report.exists() else []
    if not files:
        raise RuntimeError(f"no fresh XML reports in {report}")
    tests = failures = skipped = 0
    for file in files:
        root = ET.parse(file).getroot()
        if root.tag != "testsuite":
            raise RuntimeError(f"unexpected report root {root.tag!r}: {file}")
        try:
            count = int(root.get("tests", "-1"))
            fail = int(root.get("failures", "-1"))
            error = int(root.get("errors", "-1"))
            skip = int(root.get("skipped", "0"))
        except ValueError as exc:
            raise RuntimeError(f"invalid report counts in {file}") from exc
        if count <= 0 or fail < 0 or error < 0 or skip < 0 or skip > count:
            raise RuntimeError(
                f"invalid report counts in {file}: tests={count}, failures={fail}, errors={error}, skipped={skip}"
            )
        fail += error
        if count == skip:
            raise RuntimeError(f"all report tests skipped in {file}: tests={count}, skipped={skip}")
        if fail:
            raise RuntimeError(f"test failures/errors in {file}: tests={count}, failures+errors={fail}, skipped={skip}")
        tests += count
        failures += fail
        skipped += skip
    if tests <= 0 or tests == skipped or failures:
        raise RuntimeError(f"invalid aggregate report counts in {report}: tests={tests}, failures={failures}, skipped={skipped}")
    return tests, failures, skipped


def main() -> int:
    generate()
    reports = [OUT / "target/surefire-reports", OUT / "target/failsafe-reports"]
    if any(path.exists() for path in reports):
        raise RuntimeError("report output was not fresh after isolated target recreation")
    mvn = shutil.which("mvn")
    if not mvn:
        raise RuntimeError("mvn is unavailable")
    version = subprocess.run([mvn, "-version"], cwd=OUT, text=True, capture_output=True, check=True).stdout.splitlines()[:3]
    cmd = [mvn, "-B", "-ntp", "clean", "verify", "-DskipITs=false"]
    result = subprocess.run(cmd, cwd=OUT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (OUT / "maven.log").write_text(result.stdout, encoding="utf-8")
    print("\n".join(version))
    print("COMMAND:", " ".join(cmd))
    print("LOG:", OUT / "maven.log")
    print(result.stdout[-16000:])
    if result.returncode:
        return result.returncode
    for name in ("surefire-reports", "failsafe-reports"):
        counts = report_counts(OUT / "target" / name)
        print(f"{name}: tests={counts[0]} failures+errors={counts[1]} skipped={counts[2]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FIXTURE ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
