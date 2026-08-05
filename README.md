# rust-strict

Portable Agent Skill for **release-quality Rust work**: Cargo/workspace
discipline, impact-scoped verification, lint ratchet, API and error contracts,
ownership/RAII lifecycles, `unsafe` boundaries, and no-net-new-debt defaults.

This skill is **project-agnostic**. Repository policy (`AGENTS.md`,
`Cargo.toml`, toolchain files, CI) is the effective contract; the skill teaches
agents how to discover and enforce it without inventing policy from memory.

**Version:** see [`VERSION`](VERSION).  
**Published at:** https://github.com/robinber/agent-skills-rust

## What this is

| Path | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | Skill entrypoint (load first) |
| [`references/`](references/) | Deep guidance, loaded on demand |
| [`agents/openai.yaml`](agents/openai.yaml) | Optional Codex / ChatGPT skill UI metadata |
| [`templates/AGENTS.snippet.md`](templates/AGENTS.snippet.md) | What to keep **in each project** |
| [`scripts/validate_skill.py`](scripts/validate_skill.py) | Static metadata, links, command, release, and fixture validation |
| [`evals/`](evals/) | Activation, behavior, command, and discovery evaluation cases |

## Design split

| Lives in this skill | Lives in each project's `AGENTS.md` |
|---|---|
| How to anchor, verify, lint-ratchet | Exact MSRV, aliases, `just check` |
| Default drift profile (800 / 1000 LOC, ≤ 6 params) | Overrides + current pressure-zone files |
| Typed errors, thin `main`, supply-chain rules | Concrete error enums and exit-code maps |
| Generic unsafe / arithmetic / API rules | Domain invariants and critical surfaces |
| Ownership, RAII, and finalization defaults | Concrete resource lifecycle and cleanup policy |
| "Respect repository policy" | What the repo actually chose (e.g. pedantic) |

Do **not** fork this skill to hardcode module maps or product-specific
duplication lists. Put those in the consuming repository.

## Install paths (one source of truth)

Keep one canonical checkout. The install directory must be named `rust-strict`
to match the skill frontmatter.

| Tool | Project-local discovery path | Recommended source |
|---|---|---|
| **Codex** | `.agents/skills/rust-strict/` | Canonical checkout or submodule |
| **Claude Code** | `.claude/skills/rust-strict/` | Symlink to the canonical checkout |
| **Grok in a mixed Claude/Grok repo** | Reads `.claude/skills/rust-strict/` directly | Reuse the Claude path; do not create a third clone |

Current [Claude Code skill documentation](https://code.claude.com/docs/en/slash-commands)
uses `.claude/skills`, and the official changelog records fixes for symlinked
skill directories in Claude Code 2.0.62. Use 2.0.62 or newer for the symlink
layout. [Grok documents zero-configuration Claude Code skill
compatibility](https://docs.x.ai/build/features/skills-plugins-marketplaces), so
`.grok/skills/rust-strict` is unnecessary in a mixed environment.

### Recommended — one tool (submodule)

```bash
# Codex primary
mkdir -p .agents/skills
git submodule add https://github.com/robinber/agent-skills-rust.git .agents/skills/rust-strict
git submodule update --init --recursive

# Claude Code primary (use this path instead if Claude is your main agent)
# mkdir -p .claude/skills
# git submodule add https://github.com/robinber/agent-skills-rust.git .claude/skills/rust-strict
```

### Multi-tool — canonical checkout plus symlink

```bash
mkdir -p .agents/skills .claude/skills

# Canonical submodule for Codex
git submodule add https://github.com/robinber/agent-skills-rust.git .agents/skills/rust-strict

# Claude Code 2.0.62+ follows this project-local directory symlink.
# Grok reuses the same Claude skill path.
ln -sfn ../../.agents/skills/rust-strict .claude/skills/rust-strict
```

### Legacy, Windows, and immutable-copy fallbacks

- **Claude Code older than 2.0.62:** upgrade when possible. Otherwise vendor one
  immutable copy under `.claude/skills/rust-strict` and record that it must be
  updated from the canonical version.
- **Windows without symlink capability:** enable Developer Mode or create the
  link with suitable privileges. If that is unavailable, use the same immutable
  vendored-copy fallback and pin the identical release.
- **Teams deliberately vendoring skills:** generate the copy from the canonical
  checkout during an explicit update, validate both trees, and review the
  version change. Do not maintain independent live clones.

Always perform a post-install discovery check:

- Codex: confirm `rust-strict` appears in the skill selector/listing.
- Claude Code: run `/skills` and confirm `rust-strict` appears.
- Grok: run `/skills` and confirm the Claude-path copy is discovered.

### Pin a tag

```bash
cd .agents/skills/rust-strict
git fetch --tags
git checkout v1.3.0
cd -
git add .agents/skills/rust-strict
git commit -m "Pin rust-strict skill to v1.3.0"
```

### Wire agent project files

Add a load-order entry and the project delta. Start from
[`templates/AGENTS.snippet.md`](templates/AGENTS.snippet.md). Use `AGENTS.md`
and/or `CLAUDE.md` depending on which file your tools load.

## Activation

Agents should load this skill for repository-backed modification, review,
debugging, documentation, or verification of Rust packages and Cargo
workspaces. It should not trigger for general syntax explanations, beginner
learning questions without a repository, translation/summarization, casual
language-agnostic brainstorming, or non-Rust edits in a mixed repository.

Frontmatter in `SKILL.md` provides the `name` and `description` used by skill
discovery. Discovery only works if the skill is installed under a path the tool
scans (see the matrix above) and the directory is named `rust-strict`.

## Skill toolchain floor

Full skill syntax (`#[expect]`, lint `reason = "..."`, common workspace lint
patterns) assumes **Rust 1.81+**. On older MSRV, keep the same intent with
fallback syntax and note the gap. MSRV is declared by package
`rust-version` / inherited workspace package metadata — not by
`rust-toolchain.toml` alone.

## Provenance

Unified from three project-local forks (`range-replay` as the robust base,
plus portable rules from `moe-sim` and `kira`). Project-specific content was
stripped so one skill can serve every Rust repository.

Reviews: independent Codex passes (v1.0.0 → v1.0.1) and Claude Code review
(v1.0.2 install + portability fixes).

## Validate changes

The validator requires Python 3 and PyYAML. It checks metadata, local Markdown
links, reference routing, command fixtures, evaluation schemas, placeholders,
line limits, and release-version consistency.

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_skill.py
```

CI runs the same validator on every pull request. Declarative activation,
behavior, command, and native-discovery cases live in [`evals/`](evals/). The
Kira discovery matrix remains a credentialed local forward-test: it verifies
Codex through `.agents/skills`, Claude through `.claude/skills`, and Grok through
the Claude path with `.agents` and `.grok` intentionally absent.

## Versioning

- **Semver** on tags: `vMAJOR.MINOR.PATCH`.
- `VERSION` file matches the latest release.
- Breaking changes to correctness/safety invariants or intentional removal of
  a previously guaranteed behavior → major bump.
- Default drift profile numbers may be refined in minor versions when framed as
  defaults (not silent correctness regressions).
- Clarifications and operability fixes → patch.

## License

MIT — see [`LICENSE`](LICENSE).
