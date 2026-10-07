# Secrets and sensitive-state policy

This repository must never contain private keys, credentials, tokens, browser
profiles, machine identifiers, histories, or generated user state.

Explicitly excluded paths include `~/.ssh`, `~/.gnupg`, `~/.aws`, `~/.pki`,
`~/.docker`, `~/.local/share/uv/credentials`, `~/.codex`, `~/.claude`,
`~/.config/BraveSoftware`, `~/.config/zen`, and `~/.local/state/omarchy`.

The following are also excluded: plugin caches; Clipboard history/images;
Codex/Claude sessions, logs and auth files; browser cookies, passwords and
profiles; SQLite databases and WAL/SHM sidecars; backups; locks; and generated
active Omarchy theme state.

Do not store GitHub, mail, cloud, Docker, uv, SSH, GPG, or AI-agent credentials
in plugin settings or manifests. Future deployment must acquire secrets from a
separate approved provider. A path, token name, account name, hostname, or
device ID is not a substitute for a secret-management design.

Phase 2 deployment is an explicit allowlist. Sensitive/runtime paths, source
symlinks, machine-home paths and recognized private-key/token patterns are
rejected. Existing files are screened before backups, and backups are screened
again before rollback; recognized secrets are not copied or restored. Git
remotes must be credential-free canonical HTTPS URLs (temporary local remotes
are permitted only in marked `/tmp` test fixtures).

The installer records only selection IDs, revisions, scope and digests under
`~/.config/omarchy-dotfiles/`; file backups/journals are local recovery material
under `~/.local/state/omarchy-dotfiles/`. Both are ignored by Git and are distinct
from `~/.local/state/omarchy/`, which is never a payload. Exported profiles
contain no account details or identity. Account setup remains manual.

Pattern checks are defense in depth, not a proof that arbitrary upstream code
or every credential format is safe. Review source and every profile export
before publication. Negative tests contain synthetic invalid paths and a
dummy credential-bearing URL; these are test inputs, not real account secrets.
