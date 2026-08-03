# Correctness and input safety

Use this reference when a change handles arithmetic on sizes, offsets, counts,
or capacities; numeric conversions; untrusted or externally supplied input; or
resource limits.

## 1. Arithmetic and conversions

- Treat sizes, offsets, counts, capacities, lengths, timestamps, and externally
  supplied numeric values as boundary-sensitive.
- Use checked arithmetic when overflow means invalid input, corruption, or an
  impossible allocation. Use saturating or wrapping arithmetic only when that
  semantic is intentional and documented.
- Avoid narrowing `as` conversions at trust boundaries; `as` silently truncates
  and never fails. Prefer `TryFrom` and propagate a typed error.
- Validate divisors, shift amounts, ranges, and index relationships before use.
- Keep unit conversions explicit through names, newtypes, or checked helpers;
  do not mix units behind a shared primitive type.
- Test zero, maximum, just-over-maximum, and mixed-width cases for
  boundary-sensitive arithmetic.

## 2. Untrusted input and resource bounds

Any value derived from an untrusted or external source that controls
allocation, iteration, recursion, concurrency, file access, retries, or
blocking duration must have an explicit bound or a repository-documented trust
assumption.

- Validate declared or length-prefixed sizes against the actual data and a sane
  limit before allocating.
- Bound recursion and nesting depth when parsing recursive structures.
- Bound decompression and archive expansion by output size and entry count;
  reject entries that escape the extraction root through path traversal,
  absolute paths, or symlinks.
- Bound queues, retries, and spawned work; see `references/concurrency.md` for
  backpressure policy.
- Apply timeouts to network and IPC operations that can otherwise block
  forever.
- Treat deserialization of untrusted data as parsing: enforce limits and depth
  and return typed errors, never panics. See the panic contract in
  `references/errors.md`.

## 3. Data invariants

- Validate at the boundary: construct valid values with fallible constructors,
  then let interior code rely on the established invariant.
- Encode invariants in types where practical (non-empty, bounded, validated
  newtypes) instead of re-checking the same condition everywhere.
- When an invariant spans multiple fields, keep mutation behind methods that
  re-establish it; do not expose fields that can break it.
