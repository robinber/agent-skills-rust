# Testing

Use this reference for unit, integration, doctest, fixture, property, and
test-command selection. Report package, target, feature, platform, and filter
scope exactly.

## 1. Canonical `cargo test` shapes

Keep Cargo package, target, and feature options before the positional test
filter. Put libtest options after `--`.

<!-- command-fixture: test-target -->
```bash
cargo test -p <package> <target-selection> <feature-selection>
```

<!-- command-fixture: test-filter -->
```bash
cargo test -p <package> <target-selection> <feature-selection> <test-filter>
```

<!-- command-fixture: test-libtest-options -->
```bash
cargo test -p <package> <target-selection> <feature-selection> <test-filter> -- <libtest-options>
```

<!-- command-fixture: test-doctest -->
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
- Use doctests for public examples and visible invariants. `cargo doc` does not
  execute them.
- Prefer direct function/module tests over process setup unless argument parsing,
  streams, exit codes, environment, or process wiring is the behavior under
  test.
- Add a regression that fails for the original bug when fixing a defect.
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
| Parsing, round trips, coalescing, arithmetic | Table-driven tests, then property tests |
| Unsafe memory behavior | Focused safe-API tests and Miri when compatible |
| Concurrency/cancellation | Deterministic coordination, model testing where practical; see `references/concurrency.md` |
| Weak assertions suspected | Mutation testing as an occasional audit |
| Flaky or slow suite | Nextest isolation, explicit timeouts, and removal of shared global state |
| MSRV-sensitive behavior | Declared-MSRV test/check row or repository MSRV CI job |

Do not add heavy infrastructure without risk-based justification.

## 5. Determinism and gaps

- Avoid timing sleeps when channels, notifications, barriers, clocks, or atomic
  coordination can establish the condition.
- Keep tests independent of execution order and shared mutable global state.
- Bound retries, generated cases, queues, and timeouts.
- When an external service, privileged device, target, or machine-specific
  harness cannot run, use the unavailable-tool procedure in
  `references/workflow.md`.
- Generated code, thin entrypoints, and trivial glue may rely on coverage of the
  code they delegate to only when that coverage is explicit.
