# rust-strict

Portable Agent Skill for **release-quality Rust work**: Cargo/workspace
discipline, impact-scoped verification, lint ratchet, API and error contracts,
`unsafe` boundaries, and no-net-new-debt defaults.

This skill is **project-agnostic**. Repository policy (`AGENTS.md`,
`Cargo.toml`, toolchain files, CI) is the effective contract; the skill teaches
agents how to discover and enforce it without inventing policy from memory.

**Version:** see [`VERSION`](VERSION) (currently `1.0.1`).  
**Intended GitHub name:** `agent-skills-rust`.

## What this is

| Path | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | Skill entrypoint (load first) |
| [`references/`](references/) | Deep guidance, loaded on demand |
| [`agents/openai.yaml`](agents/openai.yaml) | Optional Codex / ChatGPT skill UI metadata |
| [`templates/AGENTS.snippet.md`](templates/AGENTS.snippet.md) | What to keep **in each project** |

## Design split

| Lives in this skill | Lives in each project's `AGENTS.md` |
|---|---|
| How to anchor, verify, lint-ratchet | Exact MSRV, aliases, `just check` |
| Default drift profile (800 / 1000 LOC, ≤ 6 params) | Overrides + current pressure-zone files |
| Typed errors, thin `main`, supply-chain rules | Concrete error enums and exit-code maps |
| Generic unsafe / arithmetic / API rules | Domain invariants and critical surfaces |
| "Respect repository policy" | What the repo actually chose (e.g. pedantic) |

Do **not** fork this skill to hardcode module maps or product-specific
duplication lists. Put those in the consuming repository.

## Install paths (tool matrix)

Agent tools load project skills from **different directories**. Install (or
symlink) the skill where each tool actually looks:

| Tool | Project-local skill directory | Notes |
|---|---|---|
| **Codex** | `.agents/skills/rust-strict/` | Codex walks `.agents/skills` from cwd up to repo root |
| **Claude Code** | `.claude/skills/rust-strict/` | Claude documents `.claude/skills` for project skills |
| **Grok** | `.grok/skills/rust-strict/` and/or `.claude/skills/` | Prefer `.grok/skills`; `.claude/skills` often works for compatibility |

The **content** is portable (`SKILL.md` + `references/`). The **path** is
tool-specific. For multi-tool repos, one submodule plus relative symlinks is
enough:

```bash
# Example: canonical checkout for Codex, symlinks for others
mkdir -p .agents/skills .claude/skills .grok/skills
git submodule add https://github.com/robinber/agent-skills-rust.git .agents/skills/rust-strict
ln -sfn ../../.agents/skills/rust-strict .claude/skills/rust-strict
ln -sfn ../../.agents/skills/rust-strict .grok/skills/rust-strict
```

Point `AGENTS.md` at the path your primary agent uses (see
[`templates/AGENTS.snippet.md`](templates/AGENTS.snippet.md)).

### Option A — git submodule (recommended)

```bash
# from the consuming project root — pick the path for your primary tool
mkdir -p .agents/skills
git submodule add https://github.com/robinber/agent-skills-rust.git .agents/skills/rust-strict
git submodule update --init --recursive
```

Pin a tag when you want a frozen skill version:

```bash
cd .agents/skills/rust-strict
git fetch --tags
git checkout v1.0.1
cd -
git add .agents/skills/rust-strict
git commit -m "Pin rust-strict skill to v1.0.1"
```

### Option B — copy / vendor

```bash
mkdir -p .agents/skills
git clone --depth 1 --branch v1.0.1 https://github.com/robinber/agent-skills-rust.git .agents/skills/rust-strict
rm -rf .agents/skills/rust-strict/.git
```

Prefer submodule or a release archive over a permanent vendored fork so
improvements stay shared.

### Wire `AGENTS.md`

Add a load-order entry and the project delta. Start from
[`templates/AGENTS.snippet.md`](templates/AGENTS.snippet.md).

## Activation

Agents should load this skill when the task involves Rust code, Cargo
manifests/workspaces, clippy/rustfmt/rustdoc/tests, API design, error handling,
`unsafe`, technical-debt drift, or release-quality verification.

Frontmatter in `SKILL.md` provides the `name` and `description` used by skill
discovery. Discovery only works if the skill is installed under a path the tool
scans (see the matrix above).

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

v1.0.1 incorporates an independent Codex review (portability of install paths,
verification baseline, deny checks, MSRV floors, doctests, secrets, Edition
2024 unsafe).

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
