# rust-strict

Portable Agent Skill for **release-quality Rust work**: Cargo/workspace
discipline, impact-scoped verification, lint ratchet, API and error contracts,
`unsafe` boundaries, and no-net-new-debt gates.

This skill is **project-agnostic**. Repository policy (`AGENTS.md`,
`Cargo.toml`, toolchain files, CI) is the effective contract; the skill teaches
agents how to discover and enforce it without inventing policy from memory.

**Version:** see [`VERSION`](VERSION) (currently `1.0.0`).

## What this is

| Path | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | Skill entrypoint (load first) |
| [`references/`](references/) | Deep guidance, loaded on demand |
| [`agents/openai.yaml`](agents/openai.yaml) | Optional agent UI metadata |
| [`templates/AGENTS.snippet.md`](templates/AGENTS.snippet.md) | What to keep **in each project** |

## Design split

| Lives in this skill | Lives in each project's `AGENTS.md` |
|---|---|
| How to anchor, verify, lint-ratchet | Exact MSRV, aliases, `just check` |
| Numeric drift gates (800 / 1000 LOC, ≤ 6 params) | Current pressure-zone files |
| Typed errors, thin `main`, supply-chain rules | Concrete error enums and exit-code maps |
| Generic unsafe / arithmetic / API rules | Domain invariants and critical surfaces |
| "Respect repository policy" | What the repo actually chose (e.g. pedantic) |

Do **not** fork this skill to hardcode module maps or product-specific
duplication lists. Put those in the consuming repository.

## Install in a Rust project

### Option A — git submodule (recommended)

```bash
# from the consuming project root
mkdir -p .agents/skills
git submodule add <YOUR_GITHUB_URL> .agents/skills/rust-strict
git submodule update --init --recursive
```

Pin a tag when you want a frozen skill version:

```bash
cd .agents/skills/rust-strict
git fetch --tags
git checkout v1.0.0
cd -
git add .agents/skills/rust-strict
git commit -m "Pin rust-strict skill to v1.0.0"
```

### Option B — copy / vendor

```bash
mkdir -p .agents/skills
git clone --depth 1 --branch v1.0.0 <YOUR_GITHUB_URL> .agents/skills/rust-strict
rm -rf .agents/skills/rust-strict/.git
```

Prefer submodule or a release archive over a permanent vendored fork so
improvements stay shared.

### Wire `AGENTS.md`

Add a load-order entry and the project delta. Start from
[`templates/AGENTS.snippet.md`](templates/AGENTS.snippet.md).

Minimal example:

```markdown
## Load order

1. This file.
2. `.agents/skills/rust-strict/SKILL.md` before any Rust change, review, or
   verification claim.
3. Code next to the module you edit.
```

## Activation

Agents should load this skill when the task involves Rust code, Cargo
manifests/workspaces, clippy/rustfmt/rustdoc/tests, API design, error handling,
`unsafe`, technical-debt drift, or release-quality verification.

Frontmatter in `SKILL.md` provides the `name` and `description` used by skill
discovery in Claude Code, Codex, Grok, and similar tools that honor
`.agents/skills/`.

## Provenance

Unified from three project-local forks (`range-replay` as the robust base,
plus portable ideas from `moe-sim` and `kira`). Project-specific content was
stripped so one skill can serve every Rust repository.

## Versioning

- **Semver** on tags: `vMAJOR.MINOR.PATCH`.
- `VERSION` file matches the latest release.
- Breaking changes to hard gates or verification baseline → major bump.
- New references or clarified guidance → minor/patch as appropriate.

## License

MIT — see [`LICENSE`](LICENSE).
