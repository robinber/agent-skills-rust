# Changelog

## Unreleased

- Define deterministic policy precedence, exact approval semantics, stop
  conditions, and mandatory `COMPLETE` / `COMPLETE WITH GAPS` / `BLOCKED`
  reporting.
- Make the error reference the sole panic-contract source and add task-based
  reference routing.
- Reduce `SKILL.md` to the always-loaded core; add concurrency, semver,
  target/feature-matrix, and unavailable-tool guidance.
- Replace divergent multi-tool clones with one canonical checkout, a
  version-scoped Claude symlink, and Grok reuse of Claude skills.
- Add static validation, command-shape fixtures, behavioral evaluation cases,
  a Kira native-discovery matrix for Codex/Claude/Grok, and pull-request CI.

## 1.0.2 — 2026-08-03

Fixes from independent Claude Code review of the public v1.0.1 tree.

- Remove project jargon ("the slice"); require operator sign-off for new `unsafe`.
- Install: prefer real checkouts over symlinks; document silent Claude Code
  symlink discovery failures; require directory name `rust-strict`; Windows note.
- Correct pre-Cargo-1.74 lint fallback (crate attributes / CLI flags, not
  package `[lints]`).
- Align fallible-`new` / `try_new` guidance (convention-dependent throughout).
- README: published URL; drop hardcoded "currently" version line.
- Docs: `private_intra_doc_links` is warn-by-default under `-D warnings`.
- Quality floor wording: "different, explicitly scoped policy".
- Template: mention `CLAUDE.md` alongside `AGENTS.md`.

## 1.0.1 — 2026-08-03

Operability and portability fixes from independent Codex review.

- Install: Codex / Claude Code / Grok path matrix and GitHub URL.
- Verification: derive toolchain, package scope, and feature rows; no hardcoded
  `+nightly` / `--all-features` baseline.
- Fix malformed canonical `cargo clippy` template (feature/target before `--`).
- Supply chain: full `cargo deny check` (includes bans).
- MSRV vs toolchain separation; Rust 1.81 skill-syntax floor and fallbacks.
- Docs: scoped `cargo test --doc` when runnable examples change.
- Unsafe: Edition 2024 checklist; secret-safe Debug; async Send decision table.
- Drift: default strict profile overridable via `AGENTS.md`.
- Metadata: `--locked` only with a committed lockfile; dual rustfmt filenames;
  LICENSE copyright holder.

## 1.0.0 — 2026-08-03

Initial portable release.

- Base: most robust project-local skill (range-replay lineage).
- Portable rules from moe-sim and kira.
- References: workflow, lints, testing, docs, api-design, errors, unsafe,
  cli-systems, drift-control.
- Install docs + `AGENTS.md` snippet template for consuming projects.
