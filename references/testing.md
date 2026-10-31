# Testing

Use this reference for unit, integration, doctest, fixture, property, and
test-command selection. Report package, target, feature, platform, and filter
scope exactly.

Contents: 1. `cargo test` shapes · 2. Test boundary · 3. Fixtures and oracles ·
4. Property and adversarial tests · 5. Determinism and gaps

## 1. Canonical `cargo test` shapes

Keep Cargo package, target, and feature options before the positional test
filter. Put libtest options after `--`.

```bash
cargo test -p <package> <target-selection> <feature-selection>
```

```bash
cargo test -p <package> <target-selection> <feature-selection> <test-filter>
```

```bash
cargo test -p <package> <target-selection> <feature-selection> <test-filter> -- <libtest-options>
```

```bash
cargo test -p <package> --doc <feature-selection>
```

Replace `<target-selection>` with options such as `--lib`, `--bin <name>`,
`--test <name>`, or omit it. Replace `<feature-selection>` with
`--all-features`, `--no-default-features`, `--features <features>`, or omit it.
Do not place feature options after `<test-filter>`.

## 2. Select the test boundary

- Use unit tests for isolated module behavior and internal invariants.
- Use integration tests for public APIs, package boundaries, and CLI/process
  behavior.
- Use doctests for public examples and visible invariants. Neither `cargo doc`
  nor `cargo test --all-targets` executes them; run `cargo test --doc`.
- Prefer direct function/module tests over process setup unless argument parsing,
  streams, exit codes, environment, or process wiring is the behavior under
  test.
- Add a regression that fails for the original bug when fixing a defect.
- When a test conflicts with the specification, stop and report it. Never edit,
  special-case, delete, or `#[ignore]` a test, or weaken an assertion, to get a
  green run. Every ignore carries `#[ignore = "reason"]` and is reported.
- Confirm the test you claim actually ran. A filter that matches nothing prints
  `0 passed` and still exits 0 (use `-- --exact` for one test); `[[test]]`
  targets whose `required-features` are disabled are skipped silently; and
  `#[cfg(feature = ...)]` tests compile out.
- Do not describe a filtered invocation as package- or workspace-wide proof.

Widen when shared code, public behavior, target wiring, feature gates, build
scripts, or cross-package behavior can invalidate the narrow result. Follow the
platform and feature matrix in `references/workflow.md`.

## 3. Fixtures and oracles

- Prefer small hand-calculated examples for parsing, plans, budgets, arithmetic,
  checksums, validation, and deterministic rendering.
- Name fixtures after the contract and include invalid, boundary, and adversarial
  cases.
- Keep large or machine-specific data outside source control unless the
  repository deliberately versions it.
- Assert externally meaningful behavior, not a second copy of the
  implementation.

## 4. Property and adversarial tests

Use property testing when pure transformations have a large input space and a
few examples cannot cover the invariant. Keep generators realistic and combine
properties with fixed regressions for known edge cases.

| Surface | Useful escalation |
|---|---|
| Parsing, round trips, coalescing, arithmetic | Table-driven tests, then property tests (`proptest`) |
| Parsers of untrusted input or binary formats | Property tests, then targeted fuzzing (`cargo fuzz`) when risk warrants |
| Proc macros, type-state APIs, complex bounds | Compile-pass and compile-fail tests (for example `trybuild`) with reviewed diagnostics |
| Stable textual output or serialized formats | Snapshot tests (`insta`): observe the mismatch first, accept intended changes with `cargo insta accept` (not the interactive `review`), review the diff, never hand-edit snapshots, delete leftover `.snap.new` files |
| Performance claims | Before/after benchmark (`criterion`, `divan`) in a relevant profile; do not claim unmeasured speedups |
| Unsafe memory behavior | Focused safe-API tests and Miri when compatible |
| Concurrency/cancellation | Deterministic coordination, model testing (`loom`) where practical; see `references/concurrency.md` |
| Weak assertions suspected | Mutation testing of the changed lines (`cargo mutants -p <package> --in-diff <diff-file>`) as an occasional audit |
| New tests may miss the change | `cargo llvm-cov -p <package> --show-missing-lines`; report the lines reached, not a percentage |
| Flaky or slow suite | `cargo nextest` isolation, explicit timeouts, removal of shared global state, `--stress-count <n>` before claiming a fix; nextest does not run doctests |
| MSRV-sensitive behavior | Declared-MSRV test/check row or repository MSRV CI job |

Do not add heavy infrastructure without risk-based justification.

## 5. Determinism and gaps

- Avoid timing sleeps when channels, notifications, barriers, clocks, or atomic
  coordination can establish the condition.
- Keep tests independent of execution order and shared mutable global state.
- Never call `env::set_var` or `env::remove_var` in tests: libtest runs tests on
  parallel threads, which makes this undefined behavior on Unix (the functions
  are `unsafe` in edition 2024). Inject configuration, or set the environment
  on a child `Command`.
- Test timer logic with a paused clock (`#[tokio::test(start_paused = true)]`,
  which needs Tokio's `test-util` feature).
  `#[tokio::test]` is single-threaded by default; use
  `flavor = "multi_thread"` when the test needs cross-thread behavior.
- Integration tests cannot see `#[cfg(test)]` items; expose shared fakes
  through a `test-util` feature (see `references/api-design.md`).
- Bound retries, generated cases, queues, and timeouts.
- When an external service, privileged device, target, or machine-specific
  harness cannot run, use the unavailable-tool procedure in
  `references/workflow.md`.
- Generated code, thin entrypoints, and trivial glue may rely on coverage of the
  code they delegate to only when that coverage is explicit.
