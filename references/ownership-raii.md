# Ownership and RAII

Use this reference for resource acquisition or release, guards, `Drop`, or
explicit close, finish, commit, rollback, cancellation, and shutdown behavior.

Contents: 1. Constraints · 2. Decide whether RAII fits · 3. Guard contract ·
4. Explicit finalization with `Drop` · 5. Verification

## 1. Constraints

- [`Drop`](https://doc.rust-lang.org/core/ops/trait.Drop.html) is synchronous;
  implement it only when automatic field destruction is insufficient.
- Safe [`mem::forget`](https://doc.rust-lang.org/core/mem/fn.forget.html) may
  skip destruction, so soundness must never depend on a destructor running.
- [`AsyncDrop`](https://doc.rust-lang.org/std/future/trait.AsyncDrop.html) may be
  unavailable or unstable; verify the declared toolchain before using it.

## 2. Decide whether RAII fits

Prefer an RAII guard when cleanup is required on every ordinary control-flow
exit and is synchronous, bounded, and effectively infallible. Common examples
include releasing a lock, returning a permit or reservation, restoring temporary
state, and closing a handle when close errors are not part of success.

Do not force RAII onto lifecycle work whose outcome the caller must observe:

- fallible flush, finish, close, or protocol shutdown;
- asynchronous cleanup;
- business decisions such as commit, publish, or acknowledge;
- coordinated draining or shutdown that must wait for other work.

Use an explicit lifecycle method for those operations. A hybrid may use RAII as
a best-effort fallback, such as explicit commit with rollback on drop. Never
make successful commit or durable persistence depend only on destruction.

## 3. Define the guard contract

- Return a guard only after acquisition succeeds and its invariant is fully
  established. Keep partially acquired resources in local owners that clean up
  automatically if construction fails.
- Give the cleanup obligation one non-`Copy` owner. Moving the guard transfers
  the obligation; borrowing it does not.
- Mark guard types `#[must_use = "..."]` with a message naming what the guard
  releases. `let _ = acquire()` drops the guard on the spot, while
  `let _guard = acquire()` keeps it alive until the end of the scope. Bind every
  guard to a named variable and call `drop(guard)` when release must happen
  earlier.
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

For one-off cleanup local to a scope, use `core::mem::DropGuard` when the MSRV
is 1.100 or newer, instead of a hand-written guard type or `scopeguard::guard`.
It owns a value, derefs to it, and passes it to the closure when dropped:

```rust
use std::{fs, io, mem::DropGuard, path::Path};

fn replace_file(path: &Path, bytes: &[u8]) -> io::Result<()> {
    let tmp = DropGuard::new(path.with_extension("tmp"), |tmp| {
        // Best-effort cleanup; the error that got us here is the one to report.
        let _ = fs::remove_file(tmp);
    });
    fs::write(&*tmp, bytes)?; // an early return removes the temporary file
    fs::rename(&*tmp, path)?;
    DropGuard::dismiss(tmp); // success: the closure never runs
    Ok(())
}
```

- The closure is the destructor, so the contract above applies to it: it is
  synchronous, bounded, and must not panic. It runs on every exit that drops
  the guard, including unwinding, and never under `panic = "abort"` or
  `mem::forget`.
- Bind the guard to a named variable. `DropGuard::new` is `#[must_use]`, but
  `let _ = DropGuard::new(..)` satisfies that and runs the cleanup immediately.
- Cancel with `DropGuard::dismiss(guard)`, an associated function that returns
  the value and drops the closure without running it. Never cancel with
  `mem::forget`, which leaks the value and everything the closure captured.
- Hand the cleanup its state as the guarded value rather than capturing it;
  use `DropGuard::new((), |()| ..)` when there is none.
- Write a named `#[must_use]` guard type instead when the guard is returned to
  callers, stored in a field, or carries lifecycle state: the closure type
  cannot be named, and a public guard deserves its own documentation.
- Below MSRV 1.100, keep the existing pattern (a private guard type, or
  `scopeguard` where it is already a dependency). On any MSRV, `DropGuard` has
  no on-unwind-only or on-success-only mode.

Review `ManuallyDrop`, raw ownership transfer, and custom deallocation under
`references/unsafe.md`; RAII does not make an unsafe ownership proof automatic.

## 4. Combine explicit finalization with Drop

Provide an explicit fallible finalizer such as `finish`, `close`, or `shutdown`.
Consume `self` when retry is meaningless; otherwise preserve or return ownership.

- Drive lifecycle state from the operation's actual ownership and effect, not
  from `Ok` or `Err` alone. A finalizer may consume or release the resource and
  still report an error.
- Keep fallback cleanup armed when failure definitely preserves ownership and
  retry is valid. When failure consumes the resource, disarm cleanup and enter
  a terminal failed state. When the effect is unknown, enter a terminal failed
  or indeterminate state and prohibit blind retry or fallback cleanup.
- Move a resource out of its armed slot before an operation that consumes it on
  every result. Record success only after the operation commits, while keeping
  terminal failure distinct from successful completion.
- Use `Drop` only for a synchronous, non-panicking fallback such as rollback,
  cancellation signalling, or best-effort release.
- Document which errors explicit finalization reports and what the destructor
  does when it was not called.

```rust
#[must_use = "dropping a Transaction rolls it back"]
pub struct Transaction<'c> {
    conn: &'c mut Connection,
    finished: bool,
}

impl Transaction<'_> {
    pub fn commit(mut self) -> Result<(), DbError> {
        self.finished = true;
        self.conn.execute("COMMIT")
    }
}

impl Drop for Transaction<'_> {
    fn drop(&mut self) {
        if !self.finished {
            let _ = self.conn.execute("ROLLBACK");
        }
    }
}
```

`commit` marks the transaction finished before trying, so a failed commit,
whose effect is unknown, never triggers a blind rollback; only a transaction
that was never committed rolls back on drop.

The synchronous `Drop` trait cannot await asynchronous cleanup. Treat unstable
`AsyncDrop` as a toolchain-specific design decision. Otherwise expose an async
lifecycle method owned by a supervisor; `Drop` may signal or release locally but
must not pretend asynchronous draining completed.

## 5. Verify lifecycle behavior

Test the contract at the ownership boundary:

- normal scope exit and early return through `?` release exactly once;
- moving a guard transfers cleanup without duplicating it;
- explicit success disarms fallback cleanup;
- finalizer errors cover retained, consumed, and indeterminate outcomes without
  duplicate cleanup;
- dropped transactions roll back while committed transactions do not;
- async cancellation and shutdown follow the documented ownership policy.

Use deterministic fakes or counters. Panic-unwind tests prove cleanup only for
unwinding builds, not `panic = "abort"`, process termination, or `mem::forget`.
