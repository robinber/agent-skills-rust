# CLI and systems boundaries

Contents: 1. Process shape · 2. Logging · 3. Secrets · 4. Filesystem and child
processes

## 1. Process shape

- Keep `main` as glue: parse arguments, build configuration, call library code,
  and translate the result into an exit code. Put parsing, validation, domain
  logic, and rendering behind functions that can be unit tested. A tiny one-off
  binary may keep logic in `main`.
- Keep runtime plumbing separate from presentation; domain logic should not
  know how output is rendered.
- Write results to stdout and diagnostics to stderr. Map failures to stable,
  documented exit codes when the tool is scripted, returning
  `std::process::ExitCode` from `main` rather than calling `exit` deep in the
  code.
- Treat the failure path as a feature: clear message, correct stream, correct
  exit code.
- Handle `BrokenPipe` on stdout gracefully; a closed pager is not a crash.
- Define signal and shutdown behavior for long-running processes: which cleanup
  runs and which exit code results.
- Cover argument handling, streams, and exit codes with integration tests;
  test pure logic directly.

## 2. Logging

- Libraries emit events but never install a global subscriber or logger (no
  `tracing_subscriber::fmt().init()`, `set_global_default`, or
  `env_logger::init()` in library or test-helper code); a second
  initialization panics, and the library overrides the application's choice.
- Log with structured fields (`info!(path = %path.display(), "loaded")`)
  rather than preformatted strings. Record untrusted values with `?` so control
  characters are escaped.
- Never hold a `Span::enter()` guard across `.await`; attach spans with
  `.instrument(span)` or `#[instrument]`.
- `#[instrument]` records every argument, using `Debug` for non-primitive
  values. Use `skip_all` with explicit `fields(...)`, or `skip(secret)`, and do
  not add `ret` to functions returning secrets.
- Do not force a full `tracing` stack into a tiny CLI; it pays off once the
  tool is multi-step or long-running.

## 3. Secrets

- Never put secrets on process argv. Prefer stdin, inherited descriptors, or a
  platform secret store.
- Environment variables and config files are acceptable only as a documented
  project mechanism with permissions, lifetime, and redaction rules. Never log
  or `Debug`-print their contents.

## 4. Filesystem and child processes

- Handle partial reads and writes with `read_exact`, `write_all`, or a loop.
  `flush` hands data to the OS; use `sync_all` or `sync_data` when the contract
  requires data on disk.
- Separate replacement atomicity from crash durability: create the temporary
  file exclusively in the target directory with restrictive permissions, sync
  it, replace with a platform-supported atomic rename (`fs::rename` semantics
  vary by platform), and sync the parent directory when the new entry must
  survive a crash.
- Clean up temporary files and partial state on error paths.
- Accept external paths as `OsStr` or `Path`; never assume UTF-8.
- Build child-process argv directly; never route interpolated input through a
  shell. On Windows, `cmd.exe` and batch files parse arguments non-standardly
  and can execute argument content; validate or allowlist arguments to them, or
  invoke a native executable.
- Drain every piped child stream (stdout, stderr, piped stdin) concurrently and
  continuously; bound retained output by truncating, streaming, or spilling
  while still draining, never by pausing reads. Always `wait` on children and
  define kill and timeout behavior so no child outlives its owner.
