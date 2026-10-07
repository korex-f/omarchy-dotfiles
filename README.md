# Portable Omarchy environment

Workstation policy, pinned dependencies and a conservative installer for an
already installed Arch/Omarchy workstation. This is not an OS installer, a
third-party source archive, or a credentials/profile/runtime-state backup.

The installer is tested in disposable fake homes only. No deployment to the
audited workstation has occurred. Selected default plugin revisions have been
remotely verified; Theme Picker is excluded by explicit decision because its
recorded source is unavailable. Phase 3B still needs to prove shell layout,
notification ownership and the Hyprland include contract in a disposable
environment. Inventory snapshots are quarantined rather than deployed. See
[Phase 2 report](docs/phase-2.md) and [plugin decisions](docs/plugin-decisions.md).

## Fresh installation

Install Omarchy through its own supported installation process first. Bring
the entire system up to date through Omarchy before installing packages here;
this installer never runs `pacman -Sy`, a partial upgrade or a hidden whole-system
upgrade. Prerequisites: Bash, Python 3.11+ (standard-library TOML parser), Git,
pacman and a regular user. Native package application uses sudo; selected AUR
packages require an existing yay or paru and interactive PKGBUILD review.
Do not run this repository as root. Gum is optional and never auto-installed.

Once the source/desktop gates are resolved and a canonical dotfiles repository
has been established:

```bash
git clone <repo>
cd omarchy-dotfiles
./install.sh --dry-run
./install.sh
./scripts/doctor.sh
```

Read the plan before typing `install`. A failed preflight exits 2 without
deployment or package/tool installation. Dry runs do not clone, back up,
persist selections, install tools/packages or export profiles.
Network source validation occurs during application staging, before package
or configuration changes; a dry run cannot prove remote object availability.

## Flow and modes

Environment check → explicit machine profile → package components → optional
plugins → theme sources → configuration plan → confirmation → installation →
verification. Default plugins are selected automatically, not inferred from
the audited `enabled` field. Optional checkboxes are generated from the manifest.
Host plugins require explicit profile membership. Excluded plugins are never
installed; undecided entries block plugin application. No existing plugin or
package is deleted merely because it is absent from a new selection.

```bash
./install.sh --dry-run --minimal
./install.sh --minimal
./install.sh --profile custom
./install.sh --profile my-laptop --non-interactive
./install.sh --profile custom --all
./install.sh --replay --non-interactive
./install.sh --reproduce --dry-run
./install.sh --reproduce
./install.sh --ui bash
```

`--minimal` chooses system/Kitty/CLI/browser/workflow components and no
optional plugins/themes; it still includes all default plugins.
`--all` selects optional package components and optional plugins, never
excluded/undecided plugins or unrelated host plugins. Themes are a separate
explicit choice. `--all` cannot override saved profiles silently.
`--non-interactive` requires explicit decisions or a complete saved profile;
native installs use `sudo -n` and pacman's `--noconfirm`. Missing privilege
authorization fails, rather than asking for a password. Missing AUR packages
block non-interactive mode because PKGBUILD review is required. Provision
reviewed AUR packages interactively first. No credentials are prompted for or
stored. Compatibility mismatch requires explicit `--allow-incompatible` after
review; acceptance does not certify a new version.

Focused component application is explicit and does not mark skipped scopes
as installed:

```bash
./install.sh --minimal --only config --dry-run
./scripts/install-config.sh --minimal --conflicts backup
./scripts/install-packages.sh --profile custom
./scripts/install-plugins.sh --minimal
./scripts/install-themes.sh --minimal --themes sunset
./scripts/install-tools.sh --minimal --components development
```

`--reproduce` applies the explicit `workstation` profile non-interactively,
using each selected source's `tested_revision`. It cannot accept component,
plugin, theme or step overrides. Package names still resolve through current
Arch/AUR repositories; binary package versions are not frozen. Ordinary
interactive installs remain the normal path for current packages.

`--only` accepts comma-separated `packages,config,plugins,themes,tools`.
Package component IDs and membership live in `manifests/components.toml`;
all package inventory entries are covered exactly once. Extra
terminals, Docker, Terraform, browsers, DDC, glyphs and experimental AUR tools
are optional UI choices rather than unconditional installs. `--components`,
`--optional-plugins` and `--themes` accept comma-separated IDs or `none`.
Provider/account prerequisites remain separate setup tasks. In particular,
Docker service activation/access and printer setup are not automated.

## Profiles and reinstallation

Profiles are chosen by a human-supplied stable ID, never by hostname. See
[host-profile contract](docs/host-profiles.md). Export a completed portable
selection with `--save-profile my-workstation`; existing profile directories
are never overwritten. Review the exported TOML before committing it later.
Saving an overlay under a new ID is deliberately not automatic.

The applied local selection is
`~/.config/omarchy-dotfiles/selections.toml` (ignored by Git). It records selected
components, optional IDs, theme sources, host requirements, exact plugin pins,
scope and a manifest/payload digest. It is written only after verification.
Failed application keeps a journal but does not mark a selection complete.
Replay detects manifest/payload or pin drift and refuses silent changes.

To add a machine, create `hosts/<human-chosen-id>/profile.toml` from a reviewed
selection. Put monitor layout/scaling/GPU environment files under that profile's
`home/.config/hypr/`, never generic `home/`. Declare exact overlay `files`.
Hyprland overlays are currently gated until the Lua/conf include contract is
reviewed. Add host-only package files and explicitly declare host-policy plugin
IDs. Reviewed user units may be copied through the profile's home overlay;
services are not started/enabled by the installer.

## Configuration, backups and recovery

Deployment is an allowlisted regular-file copy, not a symlink manager.
`manifests/deployment.toml` currently permits selected Git, Starship, Neovim,
Kitty, Zed and mise policy. Documentation/license/ignore files are not deployed.
Shell and Hyprland audit snapshots are held for integration review. Monitor
files, Git identity/credential helpers, browser data and generated theme state
are not generic payloads. Git behavior uses the XDG config path; an existing
`~/.gitconfig` is not overwritten. Configure identity/signing locally and check
precedence with `git config --show-origin --list` (do not publish its output).

Identical files and exact clean checkouts are no-ops; a no-op run creates no
empty backup journal. Different existing files
block by default. After reviewing the plan, `--conflicts backup` authorizes
backed-up replacement. Symlinked destinations, dirty repositories and existing
checkouts at a different pin/remote are rejected even with that flag.

Backups and the write-ahead journal live under
`~/.local/state/omarchy-dotfiles/backups/<run-id>/`, separate from Omarchy's
runtime state. The installer prints the journal path, including on partial
failure. Journals contain paths/hashes, not credentials; sensitive originals
are refused rather than copied into backups. Installer and rollback share an
exclusive lock.

```bash
./scripts/rollback.sh <run-id> --dry-run
./scripts/rollback.sh <run-id>
```

Rollback preflights all targets and refuses files/checkouts changed since
installation. It restores reviewed originals and removes only unchanged
installer-created files. New pinned checkouts are moved into the backup run's
`retired/` directory for recovery, not deleted. Backup runs/empty directories
remain. Packages and mise tools are NOT uninstalled or downgraded by rollback;
partial external installs must be reviewed separately. Exported profiles also
remain in the repository. This is guarded file/source rollback, not a complete
system transaction or protection against power loss during external installs.

## Pins, plugins and themes

Plugin `tested_revision` is the known-good commit; `tracking_ref` describes the
branch/tag for future candidate discovery and `update_policy` controls that
future check. Neither normal interactive installation nor `--reproduce`
promotes upstream HEAD. See [the future update workflow](docs/update-workflow.md).
Update an owned plugin in its independent repository, test and publish its
reviewed commit, then update its canonical URL/recovery point here. Third-party plugins
are never vendored. Set `install_policy` to `default`, `optional`, `host` or
`exclude`; use `selection_status = "undecided"` with no policy while a decision
is pending. IDs and friendly metadata drive the selector dynamically. Exclusion
prevents new installation; removing an existing installation is never implicit.

Source installation uses the detached tested commit, checks canonical origin,
manifest ID/schema/entry points, refuses symlinks and sensitive/runtime source,
and never substitutes HEAD. Plugin code is trusted executable software despite
being pinned; review upstream before adding it. Sources are installed without
automatic enable/disable, layout edits, notifications-owner changes or reloads.
An already running Omarchy shell can hot-reload source placement; use a
disposable test session before approved deployment.

Theme choices install pinned source checkouts under the user theme directory.
They do not set the active theme, bypass Omarchy's theme sanitization/regeneration,
or copy generated active-theme artifacts. Missing provenance/dirty-source pins
block chosen themes. Audited `active_theme` is not implicit activation consent.

Mise reads exact approved versions from `home/.config/mise/config.toml` and
installs only missing pins using explicit `tool@version` arguments. No `latest`,
prune or global `mise use` is invoked. Upgrades require testing a proposed pin,
editing it deliberately, reviewing compatibility and re-saving affected profiles.
Pacman/AUR manifests intentionally do not promise exact package binary versions;
artifact/signature/snapshot locking remains a separate reproducibility decision.

## Doctor, tests and secrets

`./scripts/doctor.sh` is read-only: checks manifests, installed desktop versions,
commands, applied scope, file hashes, source pins/cleanliness/identity, mise pins,
broken links in managed configuration, shell schema/inventory references and
notification ownership when a shell configuration exists. Exit 2 means gaps
remain. Runtime D-Bus ownership, graphical rendering, plugin account setup,
Hyprland parsing and shell API behavior require a real session; doctor does not
claim these work from version numbers alone.

Run isolated tests (no live deployment):

```bash
python3 -B -m unittest discover -s tests -v
```

Fixtures use temporary directories below `/tmp`, synthetic local Git source
objects and mocked package/mise backends; they do not use the real HOME or
install packages. `--fixture` requires an explicit test marker and cannot point
at a normal home. Never use it to simulate a successful real installation.

[Secrets policy](docs/secrets-policy.md) applies to repository contents,
deployment, backup and rollback. Automated path/content checks are defense in
depth, not an exhaustive security scanner. No SSH/GPG/AWS keys, browser profiles,
agent auth/history/sessions, Docker/uv credentials, machine IDs, caches, Omarchy
runtime state or generated active-theme state belong in this repository.
