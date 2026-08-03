# AGENTS.md snippet for projects using rust-strict

Copy and adapt the sections below into the consuming repository's `AGENTS.md`.
Do **not** paste the full skill body here — only the project contract.

Adjust the skill path for your primary agent tool (see the README install
matrix): `.agents/skills/` (Codex), `.claude/skills/` (Claude Code),
`.grok/skills/` (Grok).

---

## Load order

1. This file — repository-wide agent rules and product constraints.
2. [`README.md`](README.md) — product scope and non-goals (if present).
3. [`.agents/skills/rust-strict/SKILL.md`](.agents/skills/rust-strict/SKILL.md)
   — required before changing, reviewing, debugging, or claiming verification
   for Rust or Cargo work. (Change this path if the skill is installed under
   `.claude/skills` or `.grok/skills`.)
4. Rust policy files: `Cargo.toml`, `rust-toolchain.toml`, `.cargo/config.toml`,
   `.rustfmt.toml` or `rustfmt.toml`, `clippy.toml`, and `deny.toml` when they
   exist.
5. Subsystem documentation next to the code being changed.

When these documents appear to disagree, stop and surface the conflict. Do not
silently choose the interpretation that permits more work.

## Package facts

Fill in for this repository:

- Layout: single package at repo root / Cargo workspace members: …
- Edition: from package / workspace package metadata in `Cargo.toml`
- MSRV (`rust-version`): from package / inherited workspace package metadata
- Default toolchain: `rust-toolchain.toml` (if present)
- Nightly: only when required (document which commands, e.g. rustfmt options)
- Feature matrix: default features / CI feature rows (do not assume
  `--all-features` unless true here)
- Lint floor: do not weaken … (point at `Cargo.toml` `[lints]` /
  `[workspace.lints]`)
- Convenience gates: cargo aliases / `just check` / CI workflow paths
- Drift profile: use rust-strict defaults, or override thresholds here

## Domain contract (project-specific)

Keep product rules here, not in the shared skill:

- Module map or crate boundaries that agents must respect
- Error types and CLI exit-code map
- Secrets / redaction / credential transport rules
- Critical surfaces that need tests when touched
- Known pressure-zone files (current large modules)
- Domain duplication hotspots (search before adding a third copy)
- Explicit deviations from rust-strict (temporary or permanent), with reason

## Working rules (optional short deltas)

- Make the smallest change that satisfies the request.
- Enforced in non-test code (if true here): `unsafe`, `unwrap`, `expect`,
  `todo!`, `unimplemented!`, `dbg!`, …
- Prefer typed errors over panics in non-test code.
