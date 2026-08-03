# Changelog

## 1.0.1 — 2026-08-03

Operability and portability fixes from independent Codex review, plus
pre-publish fixes from the Codex re-review:

- Fix malformed canonical `cargo clippy` template (feature/target before `--`).
- Replace install URL placeholders with `https://github.com/robinber/agent-skills-rust`.
- Anchor on both `.rustfmt.toml` and `rustfmt.toml`.
- Copyright holder in `LICENSE`.
- Soften fallible-`new` / `try_new` guidance as convention-dependent.

- Install: document Codex / Claude Code / Grok skill path matrix; symlink recipe.
- Verification: derive toolchain, package scope, and feature rows from the repo;
  stop hardcoding `+nightly` and `--all-features` as the universal baseline.
- Supply chain: use `cargo deny check` so configured bans are not skipped.
- MSRV: separate `rust-version` from `rust-toolchain.toml`; document skill floor
  (Rust 1.81+ for full syntax) and pre-1.81 fallbacks; add MSRV check guidance.
- Docs: require scoped `cargo test --doc` when runnable examples change.
- Unsafe: Edition 2024 checklist (`unsafe_op_in_unsafe_fn`, `unsafe extern`,
  `#[unsafe(...)]`, `unsafe impl` proofs).
- API/async: replace blanket `Send` preference with an executor decision table.
- Secrets: secret-safe `Debug`/`Display`, no secrets on argv, qualified env/file
  transport.
- Drift: reframe 800/1000 LOC and six-parameter rules as default strict profile
  (overridable via `AGENTS.md`), not uncontradictable universal law.
- Metadata: `--locked` only when a committed lockfile exists.
- Fix changelog wording (“portable rules”, not “greffs”).

## 1.0.0 — 2026-08-03

Initial portable release.

- Base: most robust project-local skill (range-replay lineage).
- Portable rules from moe-sim and kira.
- References: workflow, lints, testing, docs, api-design, errors, unsafe,
  cli-systems, drift-control.
- Install docs + `AGENTS.md` snippet template for consuming projects.
