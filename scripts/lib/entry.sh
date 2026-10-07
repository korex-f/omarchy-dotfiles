#!/usr/bin/env bash
# Shared entry; does not source user shell configuration.
set -euo pipefail
run_engine() {
  command -v python3 >/dev/null || { echo 'Python 3.11+ is required (TOML parser); no packages installed.' >&2; return 2; }
  python3 -B -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Python 3.11+ required")'
  exec python3 -B "$repo_dir/scripts/lib/engine.py" "$@"
}
