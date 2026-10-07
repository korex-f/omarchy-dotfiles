# Package categorization

The manifests are a proposed workstation baseline, not a command to install.
All listed packages were checked against the source package database except
`swappy`, which was present in the first manifest but is not installed; it has
been removed pending an explicit decision.

| Category | Packages / policy |
|---|---|
| Omarchy/system dependency | `omarchy*`, `hyprland`, `quickshell`, `uwsm`, portals, PipeWire/WirePlumber, NetworkManager, BlueZ, UPower, power profiles |
| Desktop | terminals, Nautilus, Udiskie, brightness/display and screenshot/clipboard tooling; Brave and Zen are default because current default bindings launch them |
| Keyboard workflow | `omasnap` from the Omarchy package repository, `strata-bin` from AUR, and Learnomarchy from a tested Git source checkout |
| Development | Git, GitHub CLI, uv, Docker stack, Neovim, Zed, mise, Node, Python/Ruff/Pyright, Terraform |
| CLI/productivity | Starship, Zoxide, FZF, Ripgrep, FD, Eza, Bat, JQ/YQ, tmux/lazygit/lazydocker |
| Optional | Foot/Alacritty alongside Kitty, DDC, Docker stack, Terraform, AUR browsers and utility applications; retain only after a user baseline decision |
| Hardware/host-specific | No package is currently isolated here; future GPU drivers, firmware, monitor/DDC, Bluetooth extras, printing, and device tools must move to host overlays |

The AUR entries are explicitly inventoried but should not all be treated as
core: Brave and Zen are default workflow dependencies for the selected
keybindings; font glyphs support the UI; the
remaining tools (`disktree`, `ruff-lsp`, `sidra`, `xdman-beta`, `zapfast`) need
an explicit keep/remove decision before a clean baseline is declared.

Both browser components are included by `--minimal` as well as normal default
component selection. Because they are AUR packages, a fresh install without an
existing reviewed AUR helper stops with an explicit prerequisite; unattended
AUR installation is not enabled. Strata and Omasnap are package identities in
the workflow component, avoiding duplicate source ownership. Learnomarchy is
installed as a detached tested source checkout under XDG data; its upstream
installer is not run. See `keybindings.md` for provenance and dependencies.
