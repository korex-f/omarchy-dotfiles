# Phase 2 entry points

The executable Bash wrappers share `lib/entry.sh` and a standard-library Python
3.11+ engine. `lib/policy.py` validates policy and payload safety;
`lib/deploy.py` handles exact Git sources, atomic copies and guarded rollback;
`lib/select.sh` implements Gum or numbered Bash selection.

Each install component uses the same preflight/confirmation/verification path.
Pass explicit profile/selection flags as documented in the root README.
`select-profile.sh` builds a dry-run plan; it never persists selections.
`doctor.sh` is read-only; `rollback.sh <run-id>` is an explicit recovery write.
Tests use `--fixture` with temporary marked fake homes and mocked external
package/tool operations. No live deployment was performed during development.
