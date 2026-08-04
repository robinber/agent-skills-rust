# Ownership and RAII

Use this reference when a change acquires or releases a resource, introduces a
guard or `Drop` implementation, or defines explicit close, finish, commit,
rollback, cancellation, or shutdown behavior.

## 1. Source-backed constraints

- [`Drop`](https://doc.rust-lang.org/core/ops/trait.Drop.html) is synchronous;
  Rust also drops owned fields automatically, so implement it only when the
  type directly owns additional cleanup behavior.
- Safe [`mem::forget`](https://doc.rust-lang.org/core/mem/fn.forget.html) may
  skip destruction, so soundness must never depend on a destructor running.
- [`AsyncDrop`](https://doc.rust-lang.org/std/future/trait.AsyncDrop.html) may
  be unavailable or unstable on the declared toolchain. Verify it instead of
  assuming async destruction exists.

## 2. Decide whether RAII fits

Prefer an RAII guard when cleanup is required on every ordinary control-flow
exit and is synchronous, bounded, and effectively infallible. Common examples
include releasing a lock, returning a permit or capacity reservation, restoring
temporary state, and closing an operating-system handle when close errors are
not part of the caller's success contract.

Do not force RAII onto lifecycle work whose outcome the caller must observe:

- fallible flush, finish, close, or protocol shutdown;
- asynchronous cleanup;
- business decisions such as commit, publish, or acknowledge;
- coordinated draining or shutdown that must wait for other work.

Use an explicit lifecycle method for those operations. A hybrid design may use
RAII as a best-effort fallback, for example explicit commit with rollback on
drop. Never make successful commit or durable persistence depend only on
destruction.

## 3. Define the guard contract

- Return a guard only after acquisition succeeds and its invariant is fully
  established. Keep partially acquired resources in local owners that clean up
  automatically if construction fails.
- Give the cleanup obligation one non-`Copy` owner. Moving the guard transfers
  the obligation; borrowing it does not.
- Keep lifecycle state private. Expose methods that preserve the invariant
  instead of flags callers can mutate independently.
- If explicit release and fallback destruction coexist, represent armed,
  finished, and released states so the resource is released exactly once.
  `Option::take` or a private state enum is often sufficient; do not add a
  typestate API unless callers benefit from the extra surface.
- `Drop` must not panic. It cannot return an error, and it should not block for
  unbounded work or perform ordinary business logic.
- Keep a safe abstraction sound when its destructor is skipped. `mem::forget`,
  reference cycles, process abort, and operating-system failure mean RAII is
  not a universal cleanup guarantee. Skipping destruction may leak a resource;
  it must not permit undefined behavior or invalidate other live values.

Review manual `ManuallyDrop`, raw ownership transfer, and custom deallocation
under `references/unsafe.md`; RAII does not make an unsafe ownership proof
automatic.

## 4. Combine explicit finalization with Drop

When finalization can fail, provide an explicit fallible finalizer such as
`finish`, `close`, or `shutdown` that returns `Result`. Prefer consuming `self`
when retry is meaningless and reuse after finalization would be invalid. Use a
mutable receiver or return ownership on failure when the caller may retry.

- Disarm fallback cleanup only after explicit finalization succeeds.
- Preserve the original resource or a valid fallback state when finalization
  fails; do not mark it complete before the fallible operation commits.
- Use `Drop` only for a synchronous, non-panicking fallback such as rollback,
  cancellation signalling, or best-effort release.
- Document which errors explicit finalization reports and what the destructor
  does when it was not called.

The synchronous `Drop` trait cannot await asynchronous cleanup. Do not assume
an async destructor is available: verify the declared toolchain and treat any
unstable `AsyncDrop` use as a toolchain-specific async design decision. Unless
the repository explicitly adopts and verifies that surface, expose an async
lifecycle method and give a supervisor responsibility for awaiting it. `Drop`
may perform a safe non-blocking signal or local release, but must not pretend
that asynchronous draining completed.

## 5. Verify lifecycle behavior

Test the contract at the ownership boundary:

- normal scope exit and early return through `?` release exactly once;
- moving a guard transfers cleanup without duplicating it;
- explicit success disarms fallback cleanup;
- explicit failure preserves the documented retry or fallback behavior;
- dropped transactions roll back while committed transactions do not;
- async cancellation and shutdown follow the documented ownership policy.

Use deterministic fakes or counters when they make acquisition and release
observable. Panic-unwind tests prove cleanup only for unwinding builds; they do
not prove cleanup under `panic = "abort"`, process termination, or
`mem::forget`.
