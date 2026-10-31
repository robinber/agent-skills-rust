#!/usr/bin/env python3
"""Validate rust-strict metadata, links, reference routing, and release consistency."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:
    print(
        "ERROR: PyYAML is required. Install development dependencies with "
        "`python3 -m pip install -r requirements-dev.txt`.",
        file=sys.stderr,
    )
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parents[1]
MAX_SKILL_LINES = 350
EXPECTED_NAME = "rust-strict"

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"{relative(path)}: cannot read file: {exc}")
        return ""


def markdown_files() -> list[Path]:
    return [path for path in sorted(ROOT.rglob("*.md")) if ".git" not in path.parts]


def validate_frontmatter() -> None:
    content = read(ROOT / "SKILL.md")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", content, re.DOTALL)
    if match is None:
        fail("SKILL.md: missing or malformed YAML frontmatter")
        return

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        fail(f"SKILL.md: invalid YAML frontmatter: {exc}")
        return

    if not isinstance(data, dict):
        fail("SKILL.md: frontmatter must be a mapping")
        return
    extra = set(data) - {"name", "description"}
    if extra:
        fail(f"SKILL.md: unsupported frontmatter keys: {sorted(extra)}")
    if data.get("name") != EXPECTED_NAME:
        fail(f"SKILL.md: name must equal {EXPECTED_NAME!r}, got {data.get('name')!r}")
    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        fail("SKILL.md: description must be a non-empty string")
    elif len(description) > 1024:
        fail(f"SKILL.md: description is {len(description)} characters; maximum is 1024")

    line_count = len(content.splitlines())
    if line_count > MAX_SKILL_LINES:
        fail(f"SKILL.md: {line_count} lines exceeds limit {MAX_SKILL_LINES}")


def validate_openai_metadata() -> None:
    path = ROOT / "agents/openai.yaml"
    try:
        data = yaml.safe_load(read(path))
    except yaml.YAMLError as exc:
        fail(f"{relative(path)}: invalid YAML: {exc}")
        return
    interface = data.get("interface") if isinstance(data, dict) else None
    if not isinstance(interface, dict):
        fail("agents/openai.yaml: missing interface mapping")
        return
    short = interface.get("short_description")
    if not isinstance(short, str) or not 25 <= len(short) <= 64:
        fail("agents/openai.yaml: short_description must contain 25-64 characters")
    prompt = interface.get("default_prompt")
    if not isinstance(prompt, str) or f"${EXPECTED_NAME}" not in prompt:
        fail(f"agents/openai.yaml: default_prompt must contain ${EXPECTED_NAME}")


def validate_local_links() -> None:
    link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    code_path_pattern = re.compile(r"`((?:references|scripts|agents|templates)/[^`\s]+)`")

    for path in markdown_files():
        content = read(path)
        for raw_target in link_pattern.findall(content):
            target = raw_target.strip().split(maxsplit=1)[0]
            if re.match(r"^(?:https?|mailto):", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", maxsplit=1)[0])
            if target and not (path.parent / target).resolve().exists():
                fail(f"{relative(path)}: broken local Markdown link: {raw_target}")

        for raw_target in code_path_pattern.findall(content):
            target = raw_target.rstrip(".,;:")
            if not (ROOT / target).exists():
                fail(f"{relative(path)}: referenced local path does not exist: {target}")


def validate_reference_routing() -> None:
    skill = read(ROOT / "SKILL.md")
    routed = set(re.findall(r"`(references/[a-z0-9-]+\.md)`", skill))
    present = {relative(path) for path in (ROOT / "references").glob("*.md")}
    for orphan in sorted(present - routed):
        fail(f"SKILL.md: reference {orphan} is never routed")
    for missing in sorted(routed - present):
        fail(f"SKILL.md: routed reference {missing} does not exist")


def validate_placeholders() -> None:
    marker = re.compile(r"<YOUR_GITHUB_URL>|\b(?:TODO|FIXME|TBD)\b(?![!(])")
    for path in markdown_files():
        match = marker.search(read(path))
        if match:
            fail(f"{relative(path)}: unresolved placeholder {match.group(0)!r}")


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def validate_release_consistency() -> None:
    version = read(ROOT / "VERSION").strip()
    if re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        fail(f"VERSION: expected semantic version, got {version!r}")
        return

    released = re.findall(r"^##\s+(\d+\.\d+\.\d+)\b", read(ROOT / "CHANGELOG.md"), re.MULTILINE)
    if not released or released[0] != version:
        fail(f"CHANGELOG.md: latest released version must equal VERSION {version}")

    examples = set(re.findall(r"git checkout\s+v(\d+\.\d+\.\d+)\b", read(ROOT / "README.md")))
    if examples and examples != {version}:
        fail(f"README.md: tag examples {sorted(examples)} must match VERSION {version}")

    try:
        result = subprocess.run(
            ["git", "tag", "--list", "v*"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return
    tags = [
        match.group(1)
        for line in result.stdout.splitlines()
        if (match := re.fullmatch(r"v(\d+\.\d+\.\d+)", line)) is not None
    ]
    if tags:
        latest = max(tags, key=version_tuple)
        if version_tuple(latest) > version_tuple(version):
            fail(f"git tags: latest release tag v{latest} is newer than VERSION {version}")


def main() -> int:
    validate_frontmatter()
    validate_openai_metadata()
    validate_local_links()
    validate_reference_routing()
    validate_placeholders()
    validate_release_consistency()

    if errors:
        print(f"rust-strict validation FAILED ({len(errors)} issue(s)):")
        for issue in errors:
            print(f"- {issue}")
        return 1

    skill_lines = len(read(ROOT / "SKILL.md").splitlines())
    references = len(list((ROOT / "references").glob("*.md")))
    print(
        "rust-strict validation PASSED: "
        f"SKILL.md={skill_lines}/{MAX_SKILL_LINES} lines, references={references}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
