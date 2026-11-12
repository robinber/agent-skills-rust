# Concurrency and async

Use this reference when touching async runtimes, threads, locks, channels,
atomics, spawned tasks, blocking pools, UI or real-time callbacks, or
concurrent public contracts.

Contents: 1. Ownership and supervision · 2. Locks and shared state ·
3. Cancellation and partial commits · 4. Capacity and backpressure ·
5. Runtimes and blocking work · 6. Deadline threads and callbacks ·
7. Atomics and auto traits · 8. Verification

## 1. Ownership and supervision

- Give every spawned task or thread an owner responsible for completion,
  cancellation, error propagation, and cleanup. Use a structured owner such as
  `std::thread::scope`, Tokio's `JoinSet`, or `tokio_util`'s `TaskTracker`
  with a `CancellationToken`, rather than dropping a `JoinHandle`.
- Do not detach work silently when its failure or lifetime affects the caller:
  a panic or error in a spawned task surfaces only through its handle.
- Define shutdown order: stop intake, signal cancellation, drain or discard by
  policy, await owned work, then release resources.
- Preserve the first meaningful failure while still cleaning up remaining work.

## 2. Locks and shared state

- Never hold a synchronous (blocking) mutex or read/write guard across
  `.await`. Async-aware lock guards may cross `.await` when the protected
  operation requires it; keep the guarded section minimal and do not await
  unrelated work while holding the guard.
- In async code, prefer a synchronous mutex when its guard never crosses an
  `.await`; it is cheaper than an async mutex. Reach for an async mutex only
  when the lock must be held across an await, and consider an owning task fed
  by a channel instead.
- Keep critical sections short and free of blocking I/O, callbacks, and
  re-entrant calls.
- Treat references into concurrent maps (`DashMap` `Ref`, `RefMut`, `Entry`) as
  lock guards: never hold one across `.await` or while calling the same map.
- Define and document lock ordering when more than one lock can be acquired.
- Prefer ownership transfer or message passing over shared mutable state when it
  makes the invariant simpler.
- Bind a lock guard to a named variable before matching on the protected data.
  A guard created in a `match`, `if let`, or `while let` scrutinee lives
  through the body, so locking again inside it deadlocks; edition 2024 only
  releases an `if let` guard before the `else` block. Clippy's nursery lint
  `significant_drop_in_scrutinee` flags this once enabled.
- Design for abandoned owners and partial updates. Handle poisoning per the
  panic contract in `references/errors.md`.

## 3. Cancellation and partial commits

- Identify every await point after state mutation or resource acquisition.
- Make cancellation before commit harmless; after commit, make the result
  observable and idempotent or compensate explicitly.
- Do not rely on destructors to perform async cleanup.
- In `select!` loops, use only cancellation-safe branches. A cancelled
  non-cancellation-safe future (a partial `read_exact`, a half-written frame)
  loses data silently. A losing `Sender::send` branch drops its message, so
  `reserve()` a slot first; a cancelled `Mutex::lock` or `Semaphore::acquire`
  loses its queue position.
- When a future must survive across `select!` iterations, spawn it and select
  on its `JoinHandle`. Polling it by reference (`&mut fut`) risks futurelock:
  while it holds or waits for a lock, permit, or channel slot, a branch handler
  that awaits other work needing the same resource stalls both forever. Drain
  `FuturesUnordered` without awaiting unrelated futures inside the loop, or use
  `JoinSet`.
- Specify whether cancellation loses queued work, returns it, retries it, or
  completes it during draining.
- Give timeout ownership to one layer. Avoid nested independent timeouts that
  obscure which operation was cancelled.

## 4. Capacity and backpressure

- Prefer bounded queues, semaphores, and concurrency limits derived from an
  explicit resource budget.
- Define behavior at capacity: wait, reject, shed, coalesce, or spill by policy.
- Avoid unbounded task spawning, buffering, retry queues, and fan-out.
- Keep retry policy bounded and cancellation-aware; prevent retry storms.

## 5. Runtimes and blocking work

- Never call `block_on` or build a runtime on an async executor thread; it
  panics or deadlocks. To reach async code from a synchronous callback inside a
  runtime, move to a blocking thread first (`spawn_blocking`, then
  `Handle::block_on`). Libraries expose `async fn` and leave the runtime to the
  application: no `#[tokio::main]` and no hidden runtime in library code.
- Do not run blocking filesystem, CPU-heavy, foreign, or synchronization work on
  an async executor thread unless the runtime explicitly permits it.
- Use `spawn_blocking` or a dedicated bounded pool when appropriate, and include
  that pool in shutdown and capacity accounting.
- Remember that cancelling the async waiter may not cancel already-running
  blocking work; design ownership accordingly.

## 6. Deadline threads and callbacks

A UI run loop, an OS event or input callback, and a real-time audio callback
must return within a deadline. Name these threads and treat them more strictly
than an executor thread:

- No blocking file I/O, IPC, network call, or unbounded computation on them. A
  real-time callback also takes no lock, allocates nothing, and logs nothing.
  Hand the work to another thread through a bounded channel or ring buffer.
- Derive buffer capacities from rate times duration once the rate is known,
  never from a fixed element count that silently shrinks at a higher rate.
- Give every waiting state an exit that the state machine owns: a timeout or a
  failure edge, not only the success event.
- Decide what happens when a callback fires while its state is already in use
  (a nested run loop, a re-entrant `RefCell` borrow): queue, coalesce, or drop,
  with a bound. Never re-dispatch without one.

## 7. Atomics and auto traits

- Justify every atomic ordering, including `SeqCst`, by naming the
  synchronization relationship it establishes; atomics have no default
  ordering. `Relaxed` is right for a counter or flag that synchronizes no other
  memory; do not choose it for speed when the value guards other data.
- For compare-exchange operations, justify the success and failure orderings
  separately.
- Prefer locks or channels when the atomic state machine is harder to prove than
  the performance benefit warrants.
- Review `Send` and `Sync` as public contracts, including captured values,
  futures, trait objects, and FFI handles.
- `unsafe impl Send` or `unsafe impl Sync` follows `references/unsafe.md`.

## 8. Verification

- Use deterministic barriers, channels, notifications, controlled clocks, or
  model checkers instead of sleeps where practical.
- Exercise cancellation at each meaningful await/commit boundary.
- Test queue saturation, shutdown with work in flight, producer/consumer failure,
  timeout, and retry exhaustion when those states are supported.
- Consider Loom or an equivalent model checker for compact synchronization state
  machines; keep the model bounded and separate from ordinary runtime tests.
- Before claiming a flaky test or race is fixed, rerun it many times
  (`cargo nextest run -p <package> --stress-count <n> <filter>`).
- Treat ThreadSanitizer or stress tests as additional evidence, not deterministic
  proof.
- Report unexercised schedulers, targets, runtimes, or timing-dependent surfaces
  under **Not covered** in the report.
