# Host-profile contract

Portable policy lives in `home/`. A deployment chooses a machine profile
explicitly; it must not infer or permanently embed the current hostname.

Proposed selection contract:

```text
hosts/<profile-id>/
  profile.toml
  home/.config/hypr/monitors.conf
  home/.config/hypr/envs.conf        # only host-specific variables
  packages.{pacman,aur}.txt          # additive host-only packages
  home/.config/systemd/user/         # reviewed host-only units, if any
```

`profile.toml` should declare a human-chosen stable `profile_id`, role,
hardware capabilities, and compatibility target. A future bootstrap command
must require an explicit profile argument or an explicit local selector outside
version control; it must never key deployment solely on hostname.

- Monitor output names, modes, positions, scale, GDK scale, GPU workarounds,
  and vendor/device environment variables belong to the profile.
- Baseline Omarchy/Hyprland policy remains under `home/`.
- Host package lists are additive and categorized as hardware/host-specific.
- User services are absent from the current profile. Future units must be
  explicit, reviewed, and host-scoped rather than copied from runtime state.

## Prepared workstation profile

`hosts/workstation/profile.toml` selects the current portable default package
components and source/plugin steps without embedding machine identity or
hardware state. Its README separates portable defaults from pending monitor
and scaling configuration. Display layout/scaling remain pending until the
Omarchy Lua include contract is proved; no monitor/device identifiers are
captured.

## Implemented profile format

Handwritten profiles require explicit selection arrays for unattended use.
For example (not an actual selected machine):

```toml
schema_version = 1
profile_id = "my-laptop"
components = ["system", "kitty", "cli", "development", "nvim"]
optional_plugins = []
themes = ["sunset"]
steps = ["packages", "config", "plugins", "themes", "tools"]
host_plugins = []
files = []
```

`files` is an exact list of relative destinations whose sources live under
that profile's `home/`. Only reviewed Hyprland and user-systemd paths belong
to the overlay contract. No traversal, symlink source/destination, secret or
runtime payload is accepted. Native/AUR host package files are additive.
Units can be copied, but activation and service permissions remain explicit
operator tasks; no service is automatically enabled or started.

Hyprland file deployment is intentionally gated in Phase 2: the inventory's
`.conf` include graph conflicts with current packaged Lua guidance. Before
allowing monitor layouts, scaling and GPU environment overrides, review the
actual fresh-install include graph and wire an explicit profile include in
the correct syntax. Until then existing monitor files remain untouched and
declared Hyprland overlays block preflight rather than being silently ignored.

`minimal` and `custom` are built-in selector choices, not hostnames. Minimal
selects the system/Kitty/CLI components plus all default plugins. Custom adds
manifest-driven optional components, plugins and themes interactively.
`--save-profile <new-id>` exports a successful non-hardware selection into
`hosts/<new-id>/profile.toml`; overlay cloning is not automatic. Saved profiles
also carry manifest/payload and host-overlay/package digests, immutable plugin
revisions and compatibility-risk acceptance metadata. Replay refuses digest
or pin drift. Machine identity, credentials and runtime data are absent.
