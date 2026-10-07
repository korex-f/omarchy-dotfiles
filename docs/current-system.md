# Current system inventory

Audited 2026-09-27. This records the source workstation only; it does not
declare an installation procedure.

| Component | Observed version / state |
|---|---|
| Omarchy | `4.0.4-1` |
| Hyprland | `0.56.2-2` |
| Quickshell | `0.3.1-1` |
| Kitty | `0.48.2-1` |
| Neovim | `0.12.5-1` |
| Zed | `1.18.1-1` |
| uv | `0.12.10-1` |
| Docker | `29.7.2-1` |
| lazydocker | `0.25.2-1` |
| Codex CLI | `0.156.1`, mise-managed |
| Claude Code | `2.1.281`, mise-managed |
| Brave | `brave-bin 1:1.95.104-1` |
| Zen | `zen-browser-bin 1.22.3b-1` |

The Omarchy package is at `/usr/share/omarchy`; `~/.local/share/omarchy` is a
symlink to it. It is package-owned. One `omarchy-shell` Quickshell process
hosts the desktop shell. `~/.config/omarchy/shell.json` uses the built-in
`omarchy.bar` (no explicit `bar.id`) with user widgets and a top opaque layout.

Portable copies retained in `home/` were scanned for credential-like strings,
absolute `/home/dki` paths, runtime socket paths, and host identifiers before
copying. The only intentional runtime references retained are standard
Omarchy/XDG references needed for theming and Kitty's per-process socket.

`~/.config/hypr/monitors.conf` was intentionally not copied. The portable main
configuration still includes it, so a future host overlay must supply it.

`packages.pacman.txt` is a curated subset of explicitly installed native
packages. `packages.aur.txt` contains the eight observed explicit foreign
packages. Neither records transitive dependencies; package managers resolve
those at installation time.

Compatibility metadata is recorded in `manifests/compatibility.toml`; it is a
tested-version declaration, not an upgrade or migration mechanism.
