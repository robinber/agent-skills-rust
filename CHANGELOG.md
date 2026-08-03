# Changelog

## Unreleased

Cross-review hardening (Codex technical axis, Grok operational axis):

- Bind `COMPLETE` to the decision-table minimum verification of every
  applicable task class; "never invent blocking conditions" applies only
  beyond that floor.
- Define the approved unsafe surface as the minimal set of FFI entrypoints,
  types, and operations the task names or necessarily implies.
- Split nested-rule resolution into cumulative, narrower-scope, and
  relaxation cases; a nested relaxation on the same scope and concern is a
  conflict, never a specificity override.
- Require baseline evidence (pre-change tree or CI history) before labeling a
  failure pre-existing; without it the classification is indeterminate.
- Treat panics reachable from untrusted input without prior fallible
  validation as boundary errors regardless of local invariant comments, and
  panics in private helpers reachable from public APIs as caller-visible.
- Correct the FFI layout rule (`repr` attributes do not make nested fields
  FFI-safe; require `improper_ctypes*` to pass), the Windows argv caveat for
  `cmd.exe`/batch files, continuous draining of piped child streams, the
  atomicity-versus-crash-durability split for file replacement, and the
  allocator-exhaustion scope of the typed-error rule.
- Map bare imperatives to normative levels, make the `todo!`/`unimplemented!`
  ban explicit, and close the review-output versus completion-schema ordering
  contradiction.
- Add five adversarial behavior evals and validator contract-phrase checks so
  the new enforcement semantics cannot silently rot.
- Align activation fixtures with additive routing (review, dependency, and
  arithmetic scenarios load their new references) and validate every eval's
  reference list against the decision table parsed from `SKILL.md`.

Initial normative-semantics rework:

- Add explicit HARD / DEFAULT / ADVISORY normative levels and forbid promoting
  defaults into hard gates.
- Make task classification additive across decision-table rows.
- Resolve same-level policy disagreements by applicability and specificity;
  block only on genuinely incompatible outcomes for the same scope.
- Define objectively when a gate is required and classify observed failures as
  introduced, affected pre-existing, unrelated pre-existing, or indeterminate.
- Add a mandatory final diff audit and a per-command verification schema with a
  baseline-failures section.
- Rework the panic contract semantically: recoverable boundary conditions never
  panic, policy-permitted internal invariant panics need no separate approval,
  and the implicit panic surface (indexing, arithmetic, borrows) is audited.
- Scope unsafe approval: a task naming an FFI/unsafe surface counts as approval
  for that exact surface; add an FFI ABI/ownership contract checklist.
- Correct the atomic-ordering rule (no default ordering; justify success and
  failure orderings separately) and clarify that async-aware lock guards may
  cross `.await`.
- Separate the Rust 1.81 suppression-syntax floor from the Cargo 1.74 manifest
  lint-table floor in `SKILL.md`.
- Preserve deliberate repository lint-group policy instead of declaring it
  unacceptable; forbid only newly enabling whole `nursery`/`restriction`.
- Make `thiserror` conditional on repository convention and unify the
  fallibility-naming rule with idiomatic constructor names.
- Extend the semver checklist (`#[non_exhaustive]`, `repr`, re-exported
  dependency types, macros) and defer to the Cargo SemVer chapter as
  authoritative.
- Add `references/review.md` (finding standard, review passes, output order),
  `references/correctness-safety.md` (arithmetic, conversions, untrusted
  input, resource bounds), and `references/dependencies-release.md`
  (dependency hygiene, publication verification).
- Extend `references/cli-systems.md` with filesystem and child-process I/O
  rules and `references/testing.md` with compile-fail, snapshot, benchmark,
  and fuzzing escalation rows.
- Turn size thresholds into analysis triggers, distinguish knowledge from
  syntactic duplication, and add an anti-overengineering policy.
- Accept standard source-checkout directory names while keeping the
  `rust-strict` install-directory contract in discovery validation.
- Allow a release version to be prepared before its matching Git tag exists;
  still reject tags newer than `VERSION`.
- Align the README pin example with the current release so `main` validation
  remains green after tagging.

## 1.1.0 — 2026-08-03

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
