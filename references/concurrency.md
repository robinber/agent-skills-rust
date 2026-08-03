# Concurrency and async

Use this reference when touching async runtimes, threads, locks, channels,
atomics, spawned tasks, blocking pools, or concurrent public contracts.

## 1. Ownership and supervision

- Give every spawned task or thread an owner responsible for completion,
  cancellation, error propagation, and cleanup.
- Do not detach work silently when its failure or lifetime affects the caller.
- Define shutdown order: stop intake, signal cancellation, drain or discard by
  policy, await owned work, then release resources.
- Preserve the first meaningful failure while still cleaning up remaining work.

## 2. Locks and shared state

- Never hold a synchronous mutex or read/write guard across `.await`.
- Keep critical sections short and free of blocking I/O, callbacks, and
  re-entrant calls.
- Define and document lock ordering when more than one lock can be acquired.
- Prefer ownership transfer or message passing over shared mutable state when it
  makes the invariant simpler.
- Treat poisoning, abandoned owners, and partial updates as designed states, not
  impossible accidents.

## 3. Cancellation and partial commits

- Identify every await point after state mutation or resource acquisition.
- Make cancellation before commit harmless; after commit, make the result
  observable and idempotent or compensate explicitly.
- Do not rely on destructors to perform async cleanup.
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

## 5. Blocking work

- Do not run blocking filesystem, CPU-heavy, foreign, or synchronization work on
  an async executor thread unless the runtime explicitly permits it.
- Use `spawn_blocking` or a dedicated bounded pool when appropriate, and include
  that pool in shutdown and capacity accounting.
- Remember that cancelling the async waiter may not cancel already-running
  blocking work; design ownership accordingly.

## 6. Atomics and auto-traits

- Justify every non-default atomic ordering against the synchronization relation
  it establishes. Do not use `Relaxed` merely for speed.
- Prefer locks or channels when the atomic state machine is harder to prove than
  the performance benefit warrants.
- Review `Send` and `Sync` as public contracts, including captured values,
  futures, trait objects, and FFI handles.
- Treat `unsafe impl Send` or `unsafe impl Sync` as new unsafe requiring the
  core approval rule and a local proof in `references/unsafe.md`.

## 7. Verification

- Use deterministic barriers, channels, notifications, controlled clocks, or
  model checkers instead of sleeps where practical.
- Exercise cancellation at each meaningful await/commit boundary.
- Test queue saturation, shutdown with work in flight, producer/consumer failure,
  timeout, and retry exhaustion when those states are supported.
- Consider Loom or an equivalent model checker for compact synchronization state
  machines; keep the model bounded and separate from ordinary runtime tests.
- Treat ThreadSanitizer or stress tests as additional evidence, not deterministic
  proof.
- Report unexercised schedulers, targets, runtimes, or timing-dependent surfaces
  through the completion contract.
