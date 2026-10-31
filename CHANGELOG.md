# Changelog

## 2.0.0 — 2026-10-31

Core and structure:

- Rewrite `SKILL.md` as a lean core (296 → 186 lines): Rust quality defaults up
  front, one routing table, a short precedence and approval section, and a
  four-line report (State, Changed, Verified, Not covered) replacing the
  multi-section completion schema and the stop matrix.
- Let the repository contract grant standing, scoped approvals, and treat
  `CONTRIBUTING.md` and AI-contribution policies as part of that contract.
- Add `references/idioms.md`: modern std replacements for legacy crates gated
  by MSRV, ownership in signatures, exhaustive matching, porting from
  object-oriented languages, and performance defaults.
- Add `references/project-setup.md`: workspace layout, MSRV and toolchain
  choices, a verified starter lint table and `clippy.toml`,
  `style_edition = "2024"`, lockfile and `deny.toml` policy, a CI baseline
  with `CARGO_BUILD_WARNINGS=deny`, and docs.rs `doc_cfg` setup.
- Consolidate duplicated rules, remove the contradictory third-copy
  duplication rule, add contents blocks to long references, and use "user"
  consistently.
- Remove the `evals/` suites, command-fixture markers, and phrase pinning; the
  validator now checks only frontmatter, links, reference routing,
  placeholders, and release consistency.

Rules agents commonly miss:

- Tests: never edit, ignore, or weaken a test to get green; confirm a filtered
  test actually ran; observe snapshot mismatches before accepting them;
  stress-run flaky fixes; no `env::set_var` in tests.
- Errors: never swallow a failure to avoid a panic, put context in error
  variants instead of bare `#[from]`, report each cause once, and treat
  poisoned locks as invariant panics.
- Dependencies: never write crate names, versions, features, or APIs from
  memory; read `cargo info` for deprecated or tombstone releases; check
  RustSec even when unconfigured; never run a bare `cargo update`; resolve
  within the MSRV; use `cargo package --workspace` and crates.io trusted
  publishing; know cargo-deny's transitive `unsound` default and
  `[bans.std-replacements]`.
- API and ownership: additive features, one public path per item,
  `impl RangeBounds` for range parameters, compile-time `Send` assertions,
  `#[must_use]` guards and the `let _ =` pitfall.
- Concurrency and observability: lock guards in `match` scrutinees, no runtime
  inside a runtime, `select!` cancellation and futurelock, concurrent-map
  references as lock guards, `Span::enter()` across `.await`, secrets in
  `#[instrument]`, and escaping control characters in terminal and log output.
- Correctness and unsafe: `floor_char_boundary`, `strict_*` arithmetic,
  `cast_signed`/`cast_unsigned`, float comparison and casts, provenance APIs,
  unsafe soundness as a module property, `extern "C"` panics abort since 1.81,
  Miri many-seeds and strict provenance, and stable sanitizer targets.
- Modern idioms verified on Rust 1.99.1, including `if let` guards, trait
  upcasting, `get_disjoint_mut`, `extract_if`, `try_update` instead of the
  deprecated `fetch_update`, and `let Ok(v)` for infallible results.

Short compiled examples cover an error enum with context, a commit/rollback
guard, and a `SAFETY` comment.

## 1.4.0 — 2026-08-16

- Make divergence, not copy count, the duplication trigger: two copies of a rule
  that must agree are already a defect once nothing forces them to agree, and a
  second copy needs either one owner or a test that pins both and fails if they
  drift.
- Treat copies that have already diverged as a finding in their own right:
  establish the correct behavior, state why, and pin it with a regression test
  that fails against the rejected one, rather than preserving both behind a flag.
- Add a verification-selection step for checks no scoped command can reach —
  recorded identity or hash sets, generated files, cross-crate surface scans, and
  documentation mirroring a computed value — with an explicit gap report when the
  repository does not enumerate them.
- Add a `drift-control` behavior eval suite and two verification-scoping cases
  covering the new rules, including the already-diverged and
  similar-code-different-reasons boundaries.

## 1.3.0 — 2026-08-04

- Add a routed ownership and RAII reference covering when scope-bound cleanup
  fits, exactly-once guard ownership, skipped destructors, and the limits of
  `Drop`.
- Require explicit fallible finalization for observable errors, explicit async
  shutdown, and explicit business commits, with RAII limited to safe fallback
  cleanup.
- Add activation and adversarial behavior evals for infallible guards,
  fallible finalization, commit/rollback, and async shutdown, plus validator
  contract checks that keep the lifecycle rules discoverable.
- Model fallible finalization by retained, consumed, or indeterminate effects
  instead of assuming every `Err` preserves ownership.
- Move evals to a plural task-class schema and validate the union of mandatory
  references so additive classification is mechanically enforced.

## 1.2.0 — 2026-08-03

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
