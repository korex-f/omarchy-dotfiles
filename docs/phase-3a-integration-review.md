# Phase 3A: initial integration review (superseded)

This is the initial 2026-10-01 read-only review. The 2026-10-07 Phase 3A closure pass supersedes its plugin-policy and tool-installation blockers. Its live-state observations remain historical; no deployment, plugin edit, install, service change, commit, or push occurred.

## Current plugin and source status

The manifest contained 31 plugin records: 19 default, 4 optional, 8 excluded,
none host-specific or undecided. The current Omarchy plugin directory contained
29 checkouts at the reconciliation pass. AgentDeck is the exception: its ID
was present in the live `shell.json` plugin list, but no checkout/manifest was
found. It is explicitly excluded and the portable layout is independently
generated, not merged from live JSON.

The canonical commit fetch check succeeded for 18 of 19 defaults. Exact pinned
revisions were fetched for all defaults except Theme Picker:

| Plugin | Exact pin | Status |
|---|---|---|
| Reprieve | `38c6292e7f22e554935c36f6597b8a1bac5e146f` | Exact canonical fetch; also current `main` and `v1.5.2` |
| Spaces | `f8306d763c7b3c89d24172edb0e68fb6dacb68a9` | Exact canonical fetch; current `main` has advanced, pin retained unchanged |
| Tugboat | `73b2071eb14442613bf32abd77424a5a0c4263b9` | Exact canonical fetch and current advertised canonical `main`; local tracking ref had been stale |
| Theme Picker | `1ef6fdf335c64dd7707b9bf0cce5c452259048ab` | Canonical URL returns Repository not found; local object exists, no substitute chosen |
| Other 15 previously inventoried defaults | Manifest pins | Exact fetches succeeded |

Daily Islamic Reminder (`dki.quran-verse-of-the-day`) and Omapager
(`njpatel.omapager`) are explicitly `exclude`; neither checkout was touched.
Their historical cache/dirty-patch notes remain in `plugins.lock.toml` and
`plugin-normalization.md`. Notification Center is also excluded. Historical
issues for excluded Capture Shelf, Hijri Clock and Habit remain recorded but do
not block this default install.

At the initial review, the default-plugin gate remained blocked by Theme Picker.
It was subsequently excluded by explicit user decision on 2026-10-07. External account
requirements for GitHub, Tugboat, provider-usage plugins, mail, and other
optional integration capabilities remain machine-local setup, not repository
credentials.

## Notification ownership

Omarchy's first-party `omarchy.notifications` service is the sole owner of
notification ingestion, D-Bus ownership, history, unread state and popups.
There is no separate notification-center UI or bar count in the selected
baseline. Omapager and Notification Center are absent, and the proposed shell
does not put `omarchy.notifications` in `disabledPlugins[]`. This is the
first-party default behavior; no live service was toggled or D-Bus owner
changed.

## Proposed Shell v1 layout

See `proposed-shell-layout.json`. It retains the selected current/default
widgets; Spaces occupies the left workspace position and stock
`omarchy.workspaces` is omitted. Reprieve is one bar-layout entry, which enables
its service and widget through the current shell registry; it is not duplicated
in `plugins[]`. AgentDeck, Daily Islamic Reminder, Omapager, Notification
Center, and other optional/excluded/unselected entries are absent. Stock
notifications are left enabled by omission from `disabledPlugins[]`.

The current Spaces item has only an ID and no additional settings. Its optional
Claude Code activity integration may be enabled later as an explicit hook
action; no existing `~/.claude/settings.json`, credentials, sessions, history,
or agent runtime state is copied. Reprieve's recovery journal at
`$XDG_STATE_HOME/reprieve` is likewise runtime state.

## Hyprland bindings and host portability

The live entrypoint is Lua-based and loads Omarchy defaults before
`hypr.bindings`; the old quarantined `.conf` snapshot was not used as evidence.
The current personal and plugin bindings are summarized in `keybindings.md`.
`hyprctl -j binds` could not return a runtime list in this inspection session,
so runtime-only dynamic behavior could not be queried directly. Static review
covered the active user Lua module and installed Fathom and Reprieve code.

The portable baseline is now `home/.config/hypr/bindings.lua`, and only this
file is added to the deployment allowlist. It uses PATH/XDG-based references,
retains explicit overrides, and keeps Reprieve's supported fenced setup block
as the single owner of its five shortcuts. The baseline contains no
`/home/dki`, monitor layout, scaling, device environment or hardware-specific
binding. Host monitor/scaling/output configuration remains in `hosts/<id>/`.

Intentional collisions are documented: Fathom replaces both stock Alt-Tab
registrations; Reprieve replaces stock Super+W close; Brave replaces the
stock browser at Super+Shift+B; Strata replaces both Nautilus shortcuts; and
Omasnap replaces Print. No active Lua binding references AgentDeck, Daily
Islamic Reminder, Omapager or Notification Center. No ambiguous key collision
was found. The `hyprctl` live list remains an untestable-in-isolation item for
VM/session verification.

Zen and Brave are default components and are included even in the minimal
profile because their shortcuts are defaults. Both are AUR packages, so no
reviewed helper means preflight stops; unattended AUR builds remain prohibited.
At this initial review Strata, Omasnap and Learnomarchy were not installer
managed. The closure pass now assigns Strata to the `strata-bin` AUR package,
Omasnap to the Omarchy `omasnap` package and Learnomarchy to the source-tool
lock. See `keybindings.md` and `source-tools.lock.toml`.

## Current VM readiness gate

Phase 3B is **not ready**. A disposable VM/full install must wait until:

- Theme Picker has a canonical fetchable source/pin, or the user explicitly
  changes its policy/source.
- Strata, Omasnap and Learnomarchy are represented by a reviewed,
  reproducible installation mechanism; include Strata's runtime dependencies.
- The fresh-install AUR helper prerequisite is documented and tested (or
  browser packages are supplied through another reviewed source).
- This repository's static checks and installer suite pass; no secrets/runtime
  paths enter deployment.
- The VM uses a disposable snapshot and dedicated empty user. Test the pinned
  Omarchy/Quickshell/Hyprland compatibility contract, shell layout rendering,
  Hyprland Lua loading, notification ownership, plugin service startup,
  backups/rollback, idempotency, and every default shortcut dependency.

Exact Phase 3B sequence once unblocked:

1. Resolve the Theme Picker source/policy and the three external app install
   mechanisms without changing their recorded exact commits silently.
2. Re-fetch every selected default plugin pin and confirm manifest ID/type.
3. Run all static manifest, shell-layout, binding, secret/runtime and installer
   regression checks.
4. Start from a disposable VM snapshot at the declared compatibility versions;
   install the minimal profile, verify `doctor`, shortcuts, Quickshell widgets,
   notifications and host-neutral Hyprland startup.
5. Test a second install, explicit profile replay, backup recovery and rollback;
   capture results and re-run the safety scans.
6. Stop for approval before any deployment to the actual HOME or publication.
