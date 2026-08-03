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
  error type, not erase errors too early. Follow the repository's existing error
  convention first; use `thiserror` when it is already present or its
  introduction has a clear maintenance benefit. A small error type may implement
  `Display`, `Error`, and `From` manually without adding a dependency.
- Default: do not introduce `panic!`, `unwrap`, `expect`, `todo!`, or
  `unimplemented!` in non-test production code. Use typed errors and `?`.
- Prefer `build` / `try_new` / `TryFrom` for fallible construction when that
  clarifies the API; a fallible `new() -> Result<…>` is fine when it matches the
  crate convention (std sometimes uses fallible `new`).
- Make fallibility visible in the signature and docs. An established idiomatic
  name (`open`, `connect`, `parse`, `bind`, a conventional fallible `new`) does
  not need a `try_` prefix; the `Result` in the signature is the contract.
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
- Never introduce panic paths reachable from untrusted input, parsing, I/O,
  configuration, capacity or resource exhaustion, or ordinary environmental
  failure. Those are recoverable boundary conditions and must return typed
  errors.
- Allow a narrowly scoped internal invariant panic without separate approval
  only when **all** of these conditions hold:
  1. repository lint and panic policy permits it;
  2. the violated condition is a programmer bug, and recovery would be
     meaningless or would conceal corruption;
  3. the invariant is established and explained locally, and the panic message
     names the violated invariant;
  4. any caller-visible public panic surface is documented with `# Panics`;
  5. the exception is mechanically scoped and does not weaken the
     repository-wide lint floor.
- Request explicit approval only when repository policy forbids the panic or
  the change broadens a caller-visible panic contract.
- If any condition is false, return a typed error or redesign the state
  instead. Do not wrap a genuine programmer bug in an artificial `Result` that
  callers cannot meaningfully handle.
- Keep an invariant panic as a bug path, never control flow.
- Prefer enabling `clippy::panic` (and related unwrap/expect lints) so the ban
  is mechanical, not review-only.
- Test-only panics/unwraps require Clippy test knobs or scoped expects; see
  `references/lints.md`.

### Panic surface audit

Audit implicit panic paths, not only the explicit macros:

- indexing and slicing whose bounds are not already established;
- division, remainder, and shifts with unchecked operands;
- arithmetic that can overflow in the deployed profile;
- `RefCell` borrows and blindly unwrapped poisoned locks;
- conversions, formatting callbacks, and APIs that panic on invalid values.

The absence of `panic!` does not prove an API is panic-free. Document `# Panics`
for realistic caller-visible panic paths, not every theoretical internal
possibility. See `references/correctness-safety.md` for arithmetic and
conversion policy.

## 3. Allowed exceptions

- Tests may use `panic!`, `unwrap`, or `expect` when failure should stop
  immediately **and** repository policy and package lint knobs allow it.
- A CLI or TUI `main` may use `anyhow` or `Box<dyn Error>` to collapse diverse
  failures into one exit path.
- A fallible `new() -> Result<…>` is acceptable when it matches crate or std
  convention. Prefer `try_new` / `build` / `TryFrom` when the crate distinguishes
  fallible construction from an infallible `new`.
