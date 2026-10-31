# Errors and panics

Contents: 1. Error design · 2. Never swallow failures · 3. Panic contract ·
4. Panic surface audit

## 1. Error design

- Return `Result` for every recoverable failure and propagate with `?`.
- Libraries return concrete, matchable error types, usually one enum per module
  or operation family; they never erase errors early into `Box<dyn Error>` or
  `anyhow::Error`. Follow the repository's convention. Use `thiserror` when it
  is already present or clearly worth adding; a small type can implement
  `Display`, `Error`, and `From` by hand.
- Binaries may use `anyhow::Result` or `Box<dyn Error + Send + Sync>` at the
  top level, attaching context with `.context(...)` that says what was being
  attempted.
- Put context where the failure happens. Use `#[from]` only when the source
  type alone identifies the failure. For I/O, parsing, and other generic causes,
  store the operation and its inputs (path, key, offset) in the variant and
  keep the cause in a `#[source]` field; a bare `Io(#[from] io::Error)` prints
  "No such file or directory" with no path.
- Report each cause once: return the inner error from `source()` or include its
  message in `Display`, never both, so reporters that walk the chain do not
  repeat it.
- Write `Display` messages as concise lowercase phrases without trailing
  punctuation.
- Prefer typed variants over string-only `bail!` when callers or an exit-code
  map must distinguish failures.
- Document `# Errors` on public fallible functions.
- Never include secrets in `Display` or `Debug` output.
- Mark public error enums `#[non_exhaustive]` when new failure modes are
  expected and the crate is published or reused.
- Map errors to actionable messages and stable exit codes at the CLI boundary
  (see `references/cli-systems.md`).

```rust
use std::path::PathBuf;

#[derive(Debug, thiserror::Error)]
#[non_exhaustive]
pub enum ConfigError {
    #[error("failed to read config file {}", .path.display())]
    Read {
        path: PathBuf,
        #[source]
        source: std::io::Error,
    },
    #[error("invalid value for `{key}`")]
    InvalidValue { key: String },
}
```

## 2. Never swallow failures

Removing a panic must not hide the failure. Never replace `unwrap` with
`let _ =`, `.ok()`, `unwrap_or_default()`, `filter_map(Result::ok)`, or
`map_err(|_| ...)` on an operation whose failure matters. Propagate it, handle
it explicitly, or log it at the boundary that owns the decision. Discarding an
error is acceptable only when failure is genuinely irrelevant, and then the
code says why (for example a best-effort cleanup in `Drop`). Clippy's
`let_underscore_must_use`, `unused_result_ok`, and `map_err_ignore` catch many
cases.

## 3. Panic contract

Outside tests, add `unwrap`, `expect`, `panic!`, or another panicking path only
under this contract. Never ship `todo!` or `unimplemented!` on reachable paths.

- Never panic on untrusted input, parsing, I/O, configuration, foreseeable
  capacity limits, or environmental failure; return typed errors (for example
  `try_reserve` for foreseeable allocation limits). Infallible std allocation
  aborts on exhaustion, so do not promise typed errors for it unless the
  repository adopts fallible allocation.
- A panic reachable from external input without a prior fallible constructor
  or validation step that made the invalid state unrepresentable is a boundary
  error, whatever a comment claims. Panics in private helpers reachable from
  public APIs are caller-visible.
- An internal invariant panic needs no approval when all of these hold:
  1. repository lint and panic policy permits it, through a scoped
     `#[expect(clippy::expect_used, reason = "...")]` when the lint is denied;
  2. the violated condition is a programmer bug, and recovery would be
     meaningless or would conceal corruption;
  3. the invariant is established locally and the message says why it holds
     (`expect("parser validated the header length")`);
  4. any caller-visible panic is documented under `# Panics`;
  5. the exception is mechanically scoped and does not weaken the
     repository-wide lint floor.
- Ask for approval only when repository policy forbids the panic or the change
  broadens a caller-visible panic contract. If a condition fails, return a
  typed error or redesign the state; do not wrap a genuine bug in a `Result`
  callers cannot meaningfully handle.
- A poisoned lock means another thread panicked mid-update. Treat
  `.lock().expect("<state> mutex poisoned")` as an invariant panic. Recover
  with `PoisonError::into_inner` only when the critical section cannot leave
  the protected state half-updated.
- An invariant panic is a bug path, never control flow.
- Tests may panic, unwrap, and expect when the lint configuration allows it
  (see `references/lints.md`).

## 4. Panic surface audit

The absence of `panic!` does not prove an API is panic-free. Audit:

- indexing and slicing whose bounds are not already established;
- division, remainder, and shifts with unchecked operands;
- arithmetic that can overflow in the deployed profile;
- `RefCell` borrows and unwrapped poisoned locks;
- conversions, formatting callbacks, and APIs that panic on invalid values.

Document `# Panics` for realistic caller-visible paths, not every theoretical
internal one. Arithmetic and conversion policy is in
`references/correctness-safety.md`.
