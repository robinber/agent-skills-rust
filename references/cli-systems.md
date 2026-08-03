# cli-systems

## 1. Source-backed guidance

- Keep `main.rs` thin: parse arguments, build config, call orchestration code,
  and translate the result into an exit code.
- Move testable logic into library modules so the core behavior can be exercised
  without spawning the full process.
- Separate orchestration/runtime concerns from UI and formatting concerns;
  domain logic should not need to know how output is presented.
- Send user-facing errors to `stderr`, reserve `stdout` for successful machine-
  or user-facing output, and map failures to meaningful exit codes.
- Favor integration tests for CLI tools when they verify argument handling,
  process wiring, and user-visible behavior end to end.

## 2. Skill policy

- Treat `main` as glue, not as the home for real business logic.
- Put parsing, validation, domain logic, and rendering behind functions that can
  be unit tested directly.
- Keep the boundary between runtime plumbing and presentation crisp so each
  piece has one job.
- Design the failure path as a product feature: clear message, correct stream,
  correct exit code.
- Prefer stable, documented exit codes when the CLI is scripted or automated.
- Do not force a full `tracing` stack into a tiny CLI; structured logging becomes
  valuable when the tool grows multi-step or long-running behavior.
- Never put secrets on process argv. Prefer stdin, inherited descriptors, or a
  platform secret store when practical. Env vars and config files are acceptable
  only as a documented project mechanism with permissions, lifetime, and
  redaction rules (do not log or `Debug`-dump their contents).

## 3. Filesystem and child-process I/O

- Handle partial reads and writes: use `read_exact`/`write_all` or loop until
  complete. Treat `flush` as distinct from durability; use `sync_all` or
  `sync_data` when the contract requires data on disk.
- Replace files atomically (write a temporary file in the same directory, then
  rename) when readers may observe the path mid-write; set restrictive
  permissions before writing sensitive content.
- Clean up temporary files and partial state on error paths.
- Accept externally supplied paths as `OsStr`/`Path`; do not assume UTF-8.
- Handle `BrokenPipe` on stdout gracefully when output may be piped; a closed
  pager is not a crash.
- Build child-process argv directly; never route interpolated input through a
  shell.
- Consume child `stdout`/`stderr` concurrently or with bounded buffers to avoid
  pipe deadlock; always `wait` on children and define kill/timeout behavior so
  no child outlives its owner unintentionally.
- Define signal and shutdown behavior for long-running processes: which cleanup
  runs and which exit code results.

## 4. Allowed exceptions

- A tiny one-off binary may keep logic in `main` if there is no realistic reuse
  or testability benefit.
- Some process-heavy or device-specific system tools may need more orchestration
  in `main`, but the testable core should still be extracted where possible.
- Unit tests are still useful for pure logic; integration tests should cover the
  command line and process boundary when behavior depends on them.
