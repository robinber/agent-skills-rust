# errors

## 1. Source-backed guidance

- The Rust Book treats `Result<T, E>` as the default for recoverable errors and
  `panic!` as the tool for unrecoverable failures or bugs.
- Prefer typed, composable library errors when the caller may want to match,
  enrich, or recover from them.
- Use `?` as the normal propagation path in library and application code.
- Document error behavior on public functions, including panic conditions when
  they exist.
- At binary boundaries, `anyhow::Result` or `Box<dyn Error + Send + Sync>` is
  acceptable when the goal is to report a user-facing failure and exit cleanly.

## 2. Skill policy

- Library code should usually return a concrete error enum or another composable
  error type (`thiserror` is the default preference), not erase errors too early.
- Default: do not introduce `panic!`, `unwrap`, `expect`, `todo!`, or
  `unimplemented!` in non-test production code. Use typed errors and `?`.
- Prefer `build` / `try_new` / `TryFrom` for fallible construction when that
  clarifies the API; a fallible `new() -> Result<…>` is fine when it matches the
  crate convention (std sometimes uses fallible `new`).
- Make fallibility obvious in the API name and docs.
- Prefer `?` over manual propagation unless you need to attach context or
  translate the error.
- Keep validation at the boundary: construct valid values with fallible
  constructors, then let the rest of the code assume invariants hold.
- Preserve `source` / `#[from]` relationships so diagnostics keep the underlying
  cause.
- Map errors to actionable messages and stable exit codes at the CLI boundary.
- Prefer typed variants over string-only `bail!` when callers or exit-code maps
  need to distinguish failures.
- Do not include secrets in error `Display`/`Debug` output.

### Panic contract

- Prefer making illegal states unrepresentable over runtime panics.
- Allow a narrowly scoped internal invariant panic only when **all** of these
  conditions hold:
  1. repository policy permits it;
  2. the operator explicitly approves this exact exception and scope under the
     approval rules in `SKILL.md`;
  3. the condition is a programmer bug, never user input, parsing, I/O,
     configuration, resource exhaustion, or policy rejection;
  4. a public panic surface is documented with `# Panics`;
  5. the exception is mechanically scoped and does not weaken the
     repository-wide lint floor.
- If any condition is false, return a typed error or redesign the state instead.
- Keep an approved invariant panic as a bug path, never control flow.
- Prefer enabling `clippy::panic` (and related unwrap/expect lints) so the ban
  is mechanical, not review-only.
- Test-only panics/unwraps require Clippy test knobs or scoped expects; see
  `references/lints.md`.

## 3. Allowed exceptions

- Tests may use `panic!`, `unwrap`, or `expect` when failure should stop
  immediately **and** repository policy and package lint knobs allow it.
- A CLI or TUI `main` may use `anyhow` or `Box<dyn Error>` to collapse diverse
  failures into one exit path.
- A fallible `new() -> Result<…>` is acceptable when it matches crate or std
  convention. Prefer `try_new` / `build` / `TryFrom` when the crate distinguishes
  fallible construction from an infallible `new`.
