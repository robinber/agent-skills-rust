#!/usr/bin/env python3
"""Validate rust-strict metadata, structure, fixtures, and release consistency."""

from __future__ import annotations

import re
import shlex
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
REQUIRED_REFERENCES = {
    "references/workflow.md",
    "references/review.md",
    "references/testing.md",
    "references/lints.md",
    "references/docs.md",
    "references/api-design.md",
    "references/errors.md",
    "references/ownership-raii.md",
    "references/correctness-safety.md",
    "references/unsafe.md",
    "references/concurrency.md",
    "references/cli-systems.md",
    "references/dependencies-release.md",
    "references/drift-control.md",
}
REQUIRED_ACTIVATION_IDS = {
    "review-rust-pr",
    "add-cargo-feature",
    "change-public-trait",
    "review-unsafe-ffi",
    "update-msrv",
    "modify-deny-policy",
    "fix-overflow",
    "add-raii-guard",
    "review-doctest",
    "explain-ownership",
    "translate-error",
    "summarize-blog",
    "brainstorm-architecture",
    "frontend-only-mixed-repo",
}
REQUIRED_BEHAVIOR_IDS = {
    "repo-policy-conflict",
    "required-test-unavailable",
    "weaken-lint-floor",
    "new-unsafe-required",
    "ci-docs-conflict",
    "mutually-exclusive-features",
    "pinned-toolchain-newer-msrv",
    "target-specific-package",
    "narrow-test-limited-coverage",
    "public-api-semver-risk",
    "invariant-panic-input-error",
    "async-cancellation-safety",
    "complementary-gates-cumulative",
    "unrelated-preexisting-failure",
    "task-scoped-unsafe-approval",
    "invariant-panic-programmer-bug",
    "path-scoped-relaxation-conflict",
    "preexisting-without-baseline",
    "minimum-verification-floor",
    "task-unsafe-surface-stretch",
    "invariant-panic-after-weak-parse",
    "raii-infallible-guard",
    "raii-fallible-finalization",
    "raii-explicit-commit",
    "raii-async-shutdown",
    "raii-consuming-error-terminal",
}
REQUIRED_COMMAND_IDS = {
    "fmt-check",
    "clippy-scoped",
    "rustdoc-scoped",
    "cargo-deny",
    "cargo-metadata",
    "msrv-check",
    "target-check",
    "test-target",
    "test-filter",
    "test-libtest-options",
    "test-doctest",
    "miri-test",
    "semver-check",
}

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


def load_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(read(path))
    except yaml.YAMLError as exc:
        fail(f"{relative(path)}: invalid YAML: {exc}")
        return None


def mapping(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        fail(f"{context}: expected a YAML mapping")
        return {}
    return value


def sequence(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        fail(f"{context}: expected a YAML sequence")
        return []
    return value


def validate_frontmatter() -> None:
    skill_path = ROOT / "SKILL.md"
    content = read(skill_path)
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", content, re.DOTALL)
    if match is None:
        fail("SKILL.md: missing or malformed YAML frontmatter")
        return

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        fail(f"SKILL.md: invalid YAML frontmatter: {exc}")
        return

    frontmatter = mapping(data, "SKILL.md frontmatter")
    extra = set(frontmatter) - {"name", "description"}
    if extra:
        fail(f"SKILL.md: unsupported frontmatter keys: {sorted(extra)}")

    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if name != EXPECTED_NAME:
        fail(f"SKILL.md: name must equal {EXPECTED_NAME!r}, got {name!r}")
    if not isinstance(description, str) or not description.strip():
        fail("SKILL.md: description must be a non-empty string")
    elif len(description) > 1024:
        fail(f"SKILL.md: description is {len(description)} characters; maximum is 1024")

    line_count = len(content.splitlines())
    if line_count > MAX_SKILL_LINES:
        fail(f"SKILL.md: {line_count} lines exceeds limit {MAX_SKILL_LINES}")


def validate_openai_metadata() -> None:
    path = ROOT / "agents/openai.yaml"
    data = mapping(load_yaml(path), relative(path))
    interface = mapping(data.get("interface"), "agents/openai.yaml interface")
    short = interface.get("short_description")
    prompt = interface.get("default_prompt")
    if not isinstance(short, str):
        fail("agents/openai.yaml: short_description must be a string")
    elif not 25 <= len(short) <= 64:
        fail(
            "agents/openai.yaml: short_description must contain 25-64 "
            f"characters, got {len(short)}"
        )
    if not isinstance(prompt, str) or "$rust-strict" not in prompt:
        fail("agents/openai.yaml: default_prompt must contain $rust-strict")


def validate_required_files() -> None:
    for item in sorted(REQUIRED_REFERENCES):
        if not (ROOT / item).is_file():
            fail(f"missing required reference: {item}")
    for item in (
        "README.md",
        "CHANGELOG.md",
        "VERSION",
        "agents/openai.yaml",
        "requirements-dev.txt",
        "templates/AGENTS.snippet.md",
        "evals/activation.yaml",
        "evals/discovery.yaml",
        "evals/policy-conflicts.yaml",
        "evals/verification-scoping.yaml",
        "evals/unsafe-and-api.yaml",
        "evals/ownership-raii.yaml",
        "evals/command-templates.yaml",
        ".github/workflows/validate-skill.yml",
    ):
        if not (ROOT / item).is_file():
            fail(f"missing required file: {item}")


def validate_yaml_files() -> None:
    for pattern in ("*.yaml", "*.yml"):
        for path in sorted(ROOT.rglob(pattern)):
            if ".git" not in path.parts:
                load_yaml(path)


def validate_local_links_and_references() -> None:
    link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    code_path_pattern = re.compile(
        r"`((?:references|scripts|evals|agents|templates)/[^`\s]+)`"
    )

    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        content = read(path)
        for raw_target in link_pattern.findall(content):
            target = raw_target.strip()
            if target.startswith("<") and ">" in target:
                target = target[1 : target.index(">")]
            else:
                target = target.split(maxsplit=1)[0]
            if re.match(r"^(?:https?|mailto):", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", maxsplit=1)[0])
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                fail(f"{relative(path)}: broken local Markdown link: {raw_target}")

        for raw_target in code_path_pattern.findall(content):
            target = raw_target.rstrip(".,;:")
            if not (ROOT / target).exists():
                fail(f"{relative(path)}: referenced local path does not exist: {target}")


def validate_placeholders() -> None:
    marker = re.compile(r"<YOUR_GITHUB_URL>|\b(?:TODO|FIXME|TBD)\b(?![!(])")
    suffixes = {".md", ".yaml", ".yml", ".txt"}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in suffixes or ".git" in path.parts:
            continue
        match = marker.search(read(path))
        if match:
            fail(f"{relative(path)}: unresolved placeholder {match.group(0)!r}")


def version_tuple(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def validate_release_consistency() -> None:
    version = read(ROOT / "VERSION").strip()
    if re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        fail(f"VERSION: expected semantic version, got {version!r}")
        return

    changelog = read(ROOT / "CHANGELOG.md")
    released = re.findall(r"^##\s+(\d+\.\d+\.\d+)\b", changelog, re.MULTILINE)
    if not released or released[0] != version:
        fail(f"CHANGELOG.md: latest released version must equal VERSION {version}")

    readme = read(ROOT / "README.md")
    example_versions = set(
        re.findall(r"(?:git checkout|--branch)\s+v(\d+\.\d+\.\d+)\b", readme)
    )
    if not example_versions:
        fail("README.md: no release-tag example found")
    elif example_versions != {version}:
        fail(
            "README.md: release-tag examples must all match VERSION "
            f"{version}, got {sorted(example_versions)}"
        )

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
        latest_tag = max(tags, key=version_tuple)
        if version_tuple(latest_tag) > version_tuple(version):
            fail(
                f"git tags: latest release tag v{latest_tag} is newer than "
                f"VERSION {version}"
            )


def normalize_command(block: str) -> str:
    lines = [
        line.strip()
        for line in block.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    command = " ".join(lines).replace("\\ ", " ")
    return re.sub(r"\s+", " ", command).strip()


def validate_command_shape(fixture_id: str, command: str) -> None:
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        fail(f"command fixture {fixture_id}: cannot tokenize command: {exc}")
        return

    if "<test-filter>" in tokens:
        filter_index = tokens.index("<test-filter>")
        for selection in ("<target-selection>", "<feature-selection>"):
            if selection in tokens and tokens.index(selection) > filter_index:
                fail(
                    f"command fixture {fixture_id}: {selection} must precede "
                    "<test-filter>"
                )
        if "--" in tokens and tokens.index("--") < filter_index:
            fail(f"command fixture {fixture_id}: <test-filter> must precede --")

    if fixture_id == "clippy-scoped":
        if "--" not in tokens:
            fail("command fixture clippy-scoped: missing -- before lint flags")
        else:
            separator = tokens.index("--")
            for selection in ("<target-selection>", "<feature-selection>"):
                if selection not in tokens or tokens.index(selection) > separator:
                    fail(
                        "command fixture clippy-scoped: package/target/feature "
                        "selection must precede --"
                    )


def validate_command_fixtures() -> None:
    path = ROOT / "evals/command-templates.yaml"
    data = mapping(load_yaml(path), relative(path))
    fixture_items = sequence(data.get("fixtures"), f"{relative(path)} fixtures")
    fixtures: dict[str, tuple[str, set[str]]] = {}

    for index, item in enumerate(fixture_items):
        fixture = mapping(item, f"{relative(path)} fixture {index}")
        fixture_id = fixture.get("id")
        command = fixture.get("command")
        sources = fixture.get("sources")
        if not isinstance(fixture_id, str) or not isinstance(command, str):
            fail(f"{relative(path)} fixture {index}: id and command must be strings")
            continue
        source_items = sequence(sources, f"command fixture {fixture_id} sources")
        source_set = {source for source in source_items if isinstance(source, str)}
        if len(source_set) != len(source_items):
            fail(f"command fixture {fixture_id}: every source must be a unique string")
        if fixture_id in fixtures:
            fail(f"duplicate command fixture id: {fixture_id}")
        fixtures[fixture_id] = (normalize_command(command), source_set)
        validate_command_shape(fixture_id, command)

    if set(fixtures) != REQUIRED_COMMAND_IDS:
        fail(
            "command fixture ids differ from required set; missing="
            f"{sorted(REQUIRED_COMMAND_IDS - set(fixtures))}, extra="
            f"{sorted(set(fixtures) - REQUIRED_COMMAND_IDS)}"
        )

    marker_pattern = re.compile(
        r"<!--\s*command-fixture:\s*([a-z0-9-]+)\s*-->\s*"
        r"```bash\s*\n(.*?)\n```",
        re.DOTALL,
    )
    occurrences: dict[str, list[tuple[str, str]]] = {}
    for source in sorted({source for _, sources in fixtures.values() for source in sources}):
        source_path = ROOT / source
        if not source_path.is_file():
            fail(f"command fixture source does not exist: {source}")
            continue
        for fixture_id, block in marker_pattern.findall(read(source_path)):
            occurrences.setdefault(fixture_id, []).append((source, normalize_command(block)))

    for fixture_id, (expected, sources) in fixtures.items():
        actual = occurrences.get(fixture_id, [])
        actual_sources = {source for source, _ in actual}
        if actual_sources != sources:
            fail(
                f"command fixture {fixture_id}: documented sources "
                f"{sorted(actual_sources)} do not match fixture sources {sorted(sources)}"
            )
        for source, command in actual:
            if command != expected:
                fail(
                    f"command fixture {fixture_id} in {source}: documented command "
                    f"{command!r} != expected {expected!r}"
                )

    undocumented = set(occurrences) - set(fixtures)
    if undocumented:
        fail(f"documented command markers lack fixtures: {sorted(undocumented)}")


def load_decision_table() -> dict[str, set[str]]:
    """Map each task class to the unconditional references its table row mandates.

    Only the clause before the first semicolon in the references cell is
    unconditional; later clauses add conditional references.
    """
    table: dict[str, set[str]] = {}
    in_table = False
    for line in read(ROOT / "SKILL.md").splitlines():
        if line.startswith("## Task decision table"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0].startswith("---") or cells[0] == "Task class":
            continue
        first_clause = cells[1].split(";", maxsplit=1)[0]
        refs = set(re.findall(r"`([a-z0-9-]+\.md)`", first_clause))
        if refs:
            key = cells[0].replace("`", "").lower()
            table[key] = {f"references/{ref}" for ref in refs}
    if not table:
        fail("SKILL.md: task decision table not found or empty")
    return table


def validate_reference_list(value: object, context: str) -> None:
    refs = sequence(value, context)
    for ref in refs:
        if not isinstance(ref, str) or not (ROOT / ref).is_file():
            fail(f"{context}: invalid reference {ref!r}")


def validate_task_classes(value: object, context: str) -> list[str]:
    items = sequence(value, context)
    task_classes: list[str] = []
    for item in items:
        if not isinstance(item, str) or not item.strip():
            fail(f"{context}: every task class must be a non-empty string")
            continue
        task_classes.append(item)

    normalized = [task_class.lower() for task_class in task_classes]
    if len(set(normalized)) != len(normalized):
        fail(f"{context}: task classes must be unique")
    if not task_classes:
        fail(f"{context}: expected at least one task class")
    return task_classes


def validate_mandatory_references(
    task_classes: list[str],
    references: object,
    decision_table: dict[str, set[str]],
    context: str,
) -> None:
    mandatory: set[str] = set()
    for task_class in task_classes:
        task_references = decision_table.get(task_class.lower())
        if task_references is None:
            fail(f"{context}: task class {task_class!r} has no decision-table row")
            continue
        mandatory.update(task_references)

    listed = {ref for ref in sequence(references, context) if isinstance(ref, str)}
    missing = mandatory - listed
    if missing:
        fail(
            f"{context}: missing mandatory references for task classes "
            f"{task_classes!r}: "
            f"{sorted(missing)}"
        )


def validate_activation_evals() -> None:
    path = ROOT / "evals/activation.yaml"
    data = mapping(load_yaml(path), relative(path))
    if data.get("schema_version") != 2:
        fail(f"{relative(path)}: expected schema_version 2")
    scenarios = sequence(data.get("scenarios"), f"{relative(path)} scenarios")
    decision_table = load_decision_table()
    seen: set[str] = set()
    for index, item in enumerate(scenarios):
        scenario = mapping(item, f"activation scenario {index}")
        scenario_id = scenario.get("id")
        should_trigger = scenario.get("should_trigger")
        expected = mapping(scenario.get("expected"), f"activation scenario {scenario_id} expected")
        if not isinstance(scenario_id, str):
            fail(f"activation scenario {index}: id must be a string")
            continue
        if scenario_id in seen:
            fail(f"duplicate activation scenario id: {scenario_id}")
        seen.add(scenario_id)
        if not isinstance(scenario.get("prompt"), str):
            fail(f"activation scenario {scenario_id}: prompt must be a string")
        if not isinstance(should_trigger, bool):
            fail(f"activation scenario {scenario_id}: should_trigger must be boolean")
        elif should_trigger:
            task_classes = validate_task_classes(
                expected.get("task_classes"),
                f"activation scenario {scenario_id} task_classes",
            )
            validate_reference_list(
                expected.get("references"), f"activation scenario {scenario_id} references"
            )
            validate_mandatory_references(
                task_classes,
                expected.get("references"),
                decision_table,
                f"activation scenario {scenario_id}",
            )
        elif not isinstance(expected.get("reason"), str):
            fail(f"activation scenario {scenario_id}: non-trigger case needs reason")

    if seen != REQUIRED_ACTIVATION_IDS:
        fail(
            "activation scenario ids differ from required set; missing="
            f"{sorted(REQUIRED_ACTIVATION_IDS - seen)}, extra="
            f"{sorted(seen - REQUIRED_ACTIVATION_IDS)}"
        )


def validate_behavior_evals() -> None:
    allowed_decisions = {
        "continue",
        "continue_and_report",
        "request_explicit_approval",
        "blocked",
    }
    allowed_states = {"COMPLETE", "COMPLETE WITH GAPS", "BLOCKED"}
    decision_table = load_decision_table()
    seen: set[str] = set()
    for filename in (
        "policy-conflicts.yaml",
        "verification-scoping.yaml",
        "unsafe-and-api.yaml",
        "ownership-raii.yaml",
    ):
        path = ROOT / "evals" / filename
        data = mapping(load_yaml(path), relative(path))
        if data.get("schema_version") != 2:
            fail(f"{relative(path)}: expected schema_version 2")
        scenarios = sequence(data.get("scenarios"), f"{relative(path)} scenarios")
        for index, item in enumerate(scenarios):
            scenario = mapping(item, f"{filename} scenario {index}")
            scenario_id = scenario.get("id")
            expected = mapping(scenario.get("expected"), f"scenario {scenario_id} expected")
            if not isinstance(scenario_id, str):
                fail(f"{filename} scenario {index}: id must be a string")
                continue
            if scenario_id in seen:
                fail(f"duplicate behavior scenario id: {scenario_id}")
            seen.add(scenario_id)
            if not isinstance(scenario.get("prompt"), str):
                fail(f"behavior scenario {scenario_id}: prompt must be a string")
            task_classes = validate_task_classes(
                expected.get("task_classes"),
                f"behavior scenario {scenario_id} task_classes",
            )
            validate_reference_list(
                expected.get("references"), f"behavior scenario {scenario_id} references"
            )
            validate_mandatory_references(
                task_classes,
                expected.get("references"),
                decision_table,
                f"behavior scenario {scenario_id}",
            )
            if expected.get("decision") not in allowed_decisions:
                fail(f"behavior scenario {scenario_id}: invalid decision")
            if expected.get("completion_state") not in allowed_states:
                fail(f"behavior scenario {scenario_id}: invalid completion_state")
            for key in ("verification", "forbidden_claims"):
                values = sequence(expected.get(key), f"behavior scenario {scenario_id} {key}")
                if not values or not all(isinstance(value, str) for value in values):
                    fail(f"behavior scenario {scenario_id}: {key} needs text entries")

    if seen != REQUIRED_BEHAVIOR_IDS:
        fail(
            "behavior scenario ids differ from required set; missing="
            f"{sorted(REQUIRED_BEHAVIOR_IDS - seen)}, extra="
            f"{sorted(seen - REQUIRED_BEHAVIOR_IDS)}"
        )


def validate_discovery_evals() -> None:
    path = ROOT / "evals/discovery.yaml"
    data = mapping(load_yaml(path), relative(path))
    if data.get("suite") != "native-discovery" or data.get("harness") != "kira":
        fail("evals/discovery.yaml: expected native-discovery suite with Kira harness")

    setup = mapping(data.get("setup"), "discovery setup")
    if setup.get("install_directory") != EXPECTED_NAME:
        fail("evals/discovery.yaml: install directory must match the skill name")

    markers = mapping(data.get("expected_markers"), "discovery expected_markers")
    if markers.get("name") != EXPECTED_NAME:
        fail("evals/discovery.yaml: expected marker name must be rust-strict")
    states = sequence(markers.get("completion_states"), "discovery completion_states")
    if states != ["COMPLETE", "COMPLETE WITH GAPS", "BLOCKED"]:
        fail("evals/discovery.yaml: completion-state markers are incomplete or unordered")

    cases = sequence(data.get("cases"), "evals/discovery.yaml cases")
    by_agent: dict[str, dict[str, object]] = {}
    for index, item in enumerate(cases):
        case = mapping(item, f"discovery case {index}")
        agent = case.get("agent")
        if not isinstance(agent, str):
            fail(f"discovery case {index}: agent must be a string")
            continue
        if agent in by_agent:
            fail(f"evals/discovery.yaml: duplicate agent case {agent}")
        by_agent[agent] = case
        for key in ("id", "native_invocation", "required_adapter", "forbidden_fallback"):
            if not isinstance(case.get(key), str):
                fail(f"discovery case {agent}: {key} must be a string")

    if set(by_agent) != {"codex", "claude", "grok"}:
        fail("evals/discovery.yaml: cases must cover codex, claude, and grok exactly")
    if by_agent.get("codex", {}).get("required_adapter") != ".agents/skills/rust-strict":
        fail("evals/discovery.yaml: Codex must use the .agents adapter")
    if by_agent.get("claude", {}).get("required_adapter") != ".claude/skills/rust-strict":
        fail("evals/discovery.yaml: Claude must use the .claude adapter")
    grok = by_agent.get("grok", {})
    if grok.get("required_adapter") != ".claude/skills/rust-strict":
        fail("evals/discovery.yaml: Grok must reuse the Claude adapter")
    precondition = grok.get("precondition")
    if not isinstance(precondition, str) or ".agents/skills/rust-strict" not in precondition:
        fail("evals/discovery.yaml: Grok case must exclude the .agents adapter")


def validate_policy_ownership() -> None:
    markdown = {
        relative(path): read(path)
        for path in sorted(ROOT.rglob("*.md"))
        if ".git" not in path.parts
    }
    panic_headers = [path for path, content in markdown.items() if "### Panic contract" in content]
    if panic_headers != ["references/errors.md"]:
        fail(f"panic contract must exist only in references/errors.md, got {panic_headers}")

    def normalized(text: str) -> str:
        return re.sub(r"\s+", " ", text)

    errors_reference = normalized(markdown.get("references/errors.md", ""))
    required_panic_terms = (
        "repository lint and panic policy permits it",
        "programmer bug",
        "public panic surface is documented with `# Panics`",
        "mechanically scoped",
        "broadens a caller-visible panic contract",
        "never control flow",
        "prior fallible constructor",
        "private helpers reachable from public APIs",
    )
    for term in required_panic_terms:
        if term not in errors_reference:
            fail(f"references/errors.md: panic contract missing {term!r}")

    contract_phrases = {
        "SKILL.md": (
            "## Normative language",
            "Classification is additive",
            "completion floor",
            "## Baseline failures",
            "incompatible outcomes",
        ),
        "references/workflow.md": (
            "A gate is **required** only when",
            "unrelated pre-existing",
            "indeterminate",
            "baseline evidence",
            "## 8. Final diff audit",
            "completion floor",
        ),
        "references/unsafe.md": (
            "### Approval scope",
            "minimal set of FFI entrypoints",
            "never waives the safety-proof",
        ),
        "references/ownership-raii.md": (
            "`Drop` must not panic",
            "explicit fallible finalizer",
            "The synchronous `Drop` trait cannot await asynchronous cleanup",
            "`mem::forget`",
            "released exactly once",
            "actual ownership and effect",
            "terminal failed or indeterminate state",
        ),
    }
    for path_key, phrases in contract_phrases.items():
        content = markdown.get(path_key, "")
        flat = normalized(content)
        for phrase in phrases:
            if phrase not in content and phrase not in flat:
                fail(f"{path_key}: missing required contract phrase {phrase!r}")

    skill = markdown.get("SKILL.md", "")
    for heading in (
        "## Error handling rules",
        "## Unsafe and safety contracts",
        "## Documentation rules",
        "## Lint policy",
        "## Async rules",
    ):
        if heading in skill:
            fail(f"SKILL.md: detailed policy must stay in references, found {heading}")
    for required in (
        "## Policy precedence",
        "## Stop and escalation matrix",
        "## Task decision table",
        "## Verification selection algorithm",
        "## Completion contract",
        "STATE: COMPLETE | COMPLETE WITH GAPS | BLOCKED",
    ):
        if required not in skill:
            fail(f"SKILL.md: missing core contract {required!r}")

    readme = markdown.get("README.md", "")
    if "git clone" in readme:
        fail("README.md: independent clone instructions violate one-source installation")
    if "ln -sfn ../../.agents/skills/rust-strict .claude/skills/rust-strict" not in readme:
        fail("README.md: canonical Claude symlink command is missing")


def main() -> int:
    validate_frontmatter()
    validate_openai_metadata()
    validate_required_files()
    validate_yaml_files()
    validate_local_links_and_references()
    validate_placeholders()
    validate_release_consistency()
    validate_command_fixtures()
    validate_activation_evals()
    validate_behavior_evals()
    validate_discovery_evals()
    validate_policy_ownership()

    if errors:
        print(f"rust-strict validation FAILED ({len(errors)} issue(s)):")
        for issue in errors:
            print(f"- {issue}")
        return 1

    skill_lines = len(read(ROOT / "SKILL.md").splitlines())
    print(
        "rust-strict validation PASSED: "
        f"SKILL.md={skill_lines}/{MAX_SKILL_LINES} lines, "
        f"activation={len(REQUIRED_ACTIVATION_IDS)}, "
        f"behavior={len(REQUIRED_BEHAVIOR_IDS)}, "
        "discovery=3, "
        f"commands={len(REQUIRED_COMMAND_IDS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
