# Phase 1 copy ledger

## Copied from the home configuration after content review

- `~/.bashrc`, `~/.bash_profile`
- `~/.config/starship.toml`, `~/.config/mise/config.toml`
- `~/.config/kitty/kitty.conf`
- `~/.config/zed/settings.json`
- `~/.config/hypr/hyprland.conf`, `input.conf`, `looknfeel.conf`,
  `autostart.conf`, `envs.conf`, `hypridle.conf`, `hyprsunset.conf`, `xdph.conf`
- `~/.config/omarchy/shell.json`
- `~/.config/nvim/**` regular configuration files, including `lazy-lock.json`
  and `.neoconf.json`

The copied content contains no discovered literal secret, token, password,
credential helper, absolute home path, hostname, or machine ID. Standard
Omarchy generated-state references were retained only as references, not copied
state. The Zed and shell JSON copies are compacted representations with the
same data as their audited source files.

## Deliberately excluded

| Source area | Reason |
|---|---|
| `~/.config/hypr/monitors.conf` | Physical display layout and scale; host-only |
| `~/.config/hypr/hyprlock.conf` | References a stale/nonportable local current-theme path; reconsider with theme deployment design |
| `~/.config/omarchy/plugins/**` | Third-party or owned software source; represented in the lock manifest only |
| `~/.config/omarchy/themes/**`, backgrounds | Upstream theme provenance/revisions are in the lock manifest; generated active theme is excluded |
| `~/.config/omarchy/extensions/**`, hooks, themed templates | Not copied in this phase; require separate executable-code and secret/path review |
| `~/.config/nvim/lua/plugins/theme.lua` | Symlink to generated active Omarchy theme state; omitted to avoid a symlink and generated-state dependency |
| `~/.config/zed/themes/**` | Safe initial scan completed, but source ownership/provenance should be established first |
| `~/.gitconfig` | Its GitHub credential helper embeds a machine-specific mise path; no portable replacement chosen |
| `~/.config/BraveSoftware/**`, `~/.config/zen/**` | Browser profiles, cookies, logins, history, session and extension state |
| `~/.ssh`, `~/.gnupg`, `~/.aws`, `~/.pki` | Private keys and credentials |
| `~/.docker`, `~/.local/share/uv/credentials` | Tokens and credentials |
| `~/.codex`, `~/.claude` | Authentication, histories, sessions, IDs, logs and caches |
| `~/.local/state/omarchy/**` | Clipboard, agent usage, caches, generated active-theme state and runtime locks |
| `*.bak*`, locks, SQLite WAL/SHM, caches | Backup/runtime data rather than declarative policy |
