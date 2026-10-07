# Current Hyprland keybinding baseline

This matrix was reconstructed from the active Omarchy Lua architecture on
2026-10-01: `~/.config/hypr/hyprland.lua` loads Omarchy defaults, then requires
`hypr.bindings`; the user's `bindings.lua` is loaded after the default binding
modules. The runtime query `hyprctl -j binds` was unavailable in this inspection
session, so dynamically generated bindings are checked against their installed
Lua sources rather than claimed as a live socket dump. No quarantined legacy
`.conf` snapshot was used.

The portable module is `home/.config/hypr/bindings.lua`. It is the only Hyprland
payload in the deployment allowlist. Monitor layout/scaling and other host
settings remain outside it.

## User and plugin bindings

| Keys | Action | Command / implementation | Source | Dependency | Portable? | Transformation | Conflict / status |
|---|---|---|---|---|---|---|---|
| `SUPER+B` | Launch Zen | `zen-browser` via Omarchy launch wrapper | user override / application shortcut | Zen Browser | Yes | PATH command; Zen component is default | None |
| `SUPER+SHIFT+B` | Launch Brave | `brave` via Omarchy launch wrapper | user override / application shortcut | Brave | Yes | PATH command; Brave component is default | Intentionally replaces Omarchy browser binding |
| `SUPER+A` | Open Claude web app | Omarchy web-app helper, `https://claude.ai` | user override / web-app shortcut | Browser, network; interactive account login only | Yes | URL is portable; no login data stored | None; no credentials copied |
| `SUPER+ALT+O` | Open Omaconv | `omarchy-shell shell toggle slcode777.omaconv` | user override / plugin integration | Default Omaconv plugin; user Claude session for its own feature | Yes | Stable plugin ID and PATH command | None; sessions remain runtime state |
| `SUPER+SHIFT+R` | Toggle Omastorm radar | `omarchy shell shell toggle com.omastorm.radar '{}'` | user override / plugin integration | Default Omastorm plugin; Omarchy command wrapper | Yes | Stable plugin ID and PATH command | None; wrapper syntax validated by installed CLI |
| `PRINT` | Screenshot/annotation | `omasnap` | user override / application shortcut | Omasnap | Yes, if installed | PATH command replaces machine path | Intentionally replaces Omarchy screenshot |
| `F12` | Screenshot/annotation | `omasnap` | user override / application shortcut | Omasnap | Yes, if installed | PATH command | No stock binding found |
| `ALT+SHIFT+4` | Screenshot/annotation | `omasnap` | user override / application shortcut | Omasnap | Yes, if installed | PATH command | No stock binding found |
| `SUPER+SHIFT+F` | Open Strata | `strata` via Omarchy launch wrapper | user override / application shortcut | Strata | Yes, if installed | PATH command replaces absolute `/home/dki/.local/bin/strata` | Intentionally replaces Omarchy Nautilus binding |
| `SUPER+ALT+SHIFT+F` | Open Strata in terminal cwd | `uwsm-app -- strata "$(omarchy-cmd-terminal-cwd)"` | user override / application shortcut | Strata, UWSM, Omarchy cwd helper | Yes, if installed | PATH-resolved Strata, stable Omarchy command | Intentionally replaces Nautilus-cwd binding |
| `SUPER+ALT+L` | Learnomarchy keybinding trainer | `$HOME/.local/share/omarchy-dotfiles/tools/learnomarchy/learnomarchy` (default XDG data path) | user override / application shortcut | Learnomarchy; Omarchy 4, `hyprctl`, `jq`, `xdg-terminal-exec`, `pw-play`, `grim`, `wl-copy` | Yes | Portable home-relative tested source checkout replaces absolute machine path | None |
| `ALT+TAB` | Fathom dive to next window | Fathom Lua chord handler | plugin integration | Default Fathom plugin | Yes | Guarded `dofile` uses XDG config root | Intentional takeover of duplicated stock cycle/reveal binding |
| `ALT+SHIFT+TAB` | Fathom rise to previous window | Fathom Lua chord handler | plugin integration | Default Fathom plugin | Yes | Guarded `dofile` uses XDG config root | Intentional takeover of duplicated stock cycle/reveal binding |
| `SUPER+W` | Park window | Reprieve CLI `park` | plugin integration | Default Reprieve plugin, Hyprland >= 0.56, `hyprctl`, `pactl`, `busctl`, Python 3 | Yes | Reprieve's single marked setup block; config root from XDG | Intentional replacement of stock close binding |
| `SUPER+ALT+W` | Permanently close parked/current window | Reprieve CLI `close` | plugin integration | Reprieve | Yes | Same marked block | No collision found |
| `SUPER+Z` | Restore parked window | Reprieve IPC action `tech.greyforge.reprieve:undo` | plugin integration | Reprieve service | Yes | Stable plugin IPC ID | No collision; differs from stock `SUPER+CTRL+Z` |
| `SUPER+Y` | Redo park | Reprieve IPC action `tech.greyforge.reprieve:redo` | plugin integration | Reprieve service | Yes | Stable plugin IPC ID | No collision; differs from stock `SUPER+SHIFT+Y` web app |
| `SUPER+SHIFT+Z` | Open Reprieve timeline | Reprieve IPC action `tech.greyforge.reprieve:timeline` | plugin integration | Reprieve service | Yes | Stable plugin IPC ID | No collision found |

No active user binding was hardware- or host-specific. Omarchy's own generic
media/lid/touchpad bindings remain Omarchy-owned. Its `code:20`/`code:21`
window-resize shortcuts are physical keycode defaults and may vary by keyboard
layout; they are not copied into this user module. Monitor/display shortcuts
remain stock Omarchy behavior; output names and scaling stay in host profiles.

## Inherited Omarchy defaults (not copied)

These bindings remain provided by the tested Omarchy package because the active
entrypoint does not set `omarchy_default_bindings = false`. They are listed to
make the effective workflow review complete; the portable module deliberately
contains only personal/plugin overrides.

| Keys | Action / command family | Source | Dependency | Portable? / exception |
|---|---|---|---|---|
| `SUPER+RETURN`, `SUPER+SHIFT+RETURN` | Omarchy terminal / configured browser | Omarchy applications | Omarchy default applications | Yes; configured defaults |
| `SUPER+SHIFT+ALT+B`, `SUPER+SHIFT+N` | Private browser / configured editor | Omarchy applications | Browser/editor selection | Yes |
| `SUPER+ALT+RETURN`, `SUPER+CTRL+RETURN`, `SUPER+SHIFT+M`, `SUPER+SHIFT+ALT+M`, `SUPER+SHIFT+D`, `SUPER+SHIFT+G`, `SUPER+SHIFT+O`, `SUPER+SHIFT+W`, `SUPER+SHIFT+SLASH` | Tmux, Herdr, Spotify, cliamp, Docker TUI, Signal, Obsidian, Omawrite, 1Password | Omarchy preinstalled-application bindings | Optional app installations | Yes; bindings may lead to the matching Omarchy install/setup path |
| `SUPER+SHIFT+A`, `SUPER+SHIFT+ALT+A`, `SUPER+SHIFT+C`, `SUPER+SHIFT+E`, `SUPER+SHIFT+ALT+E`, `SUPER+SHIFT+Y`, `SUPER+SHIFT+ALT+G`, `SUPER+SHIFT+CTRL+G`, `SUPER+SHIFT+P`, `SUPER+SHIFT+S`, `SUPER+SHIFT+X`, `SUPER+SHIFT+ALT+X` | ChatGPT, Grok, calendar, email/new email, YouTube, WhatsApp, Messages, Photos, Maps, X/post web apps | Omarchy web-app bindings | Configured browser, network; account login as needed | Yes; no session data is in dotfiles |
| `SUPER+SPACE`, `SUPER+ALT+SPACE`, `SUPER+CTRL+E/C/O/H`, `SUPER+SHIFT+code:201`, `SUPER+ESCAPE`, `XF86PowerOff` | Omarchy/apps/menu, emoji, capture/toggle/hardware/system menus | Omarchy utilities | Omarchy Shell and menu commands | Yes; `code:201` and `XF86PowerOff` are keyboard/device dependent |
| `SUPER+K`, `SUPER+ALT+K`, `SUPER+CTRL+K`, `SUPER+CTRL+Q`, `XF86Calculator` | Keybinding menus / calculator | Omarchy utilities | Omarchy menus, `omacalc` | Yes |
| `SUPER+SHIFT+SPACE`, `SUPER+CTRL+SPACE`, `SUPER+SHIFT+CTRL+SPACE` | Bar visibility / background / theme selector | Omarchy utilities | Omarchy Shell and theme system | Yes |
| `SUPER+BACKSPACE`, `SUPER+SHIFT+BACKSPACE`, `SUPER+CTRL+BACKSPACE` | Transparency / gaps / square aspect toggles | Omarchy utilities | Omarchy Hyprland helper commands | Yes |
| `SUPER+comma`, `SUPER+SHIFT+comma`, `SUPER+CTRL+comma`, `SUPER+ALT+comma`, `SUPER+SHIFT+ALT+comma` | Dismiss one/all, silence, invoke last, notification history | Omarchy utilities | Sole first-party `omarchy.notifications` service | Yes; notification service remains enabled |
| `SUPER+CTRL+I/N`, `SUPER+CTRL+DELETE`, `SUPER+CTRL+ALT+DELETE`, `switch:on/off:Lid Switch` | Idle lock, night light, internal display/mirroring, lid behavior | Omarchy utilities | Omarchy idle/nightlight/monitor commands | Generic, but lid/internal-display switches are host/hardware-specific at runtime |
| `PRINT`, `ALT+PRINT`, `SUPER+ALT+code:34/35`, `SUPER+PRINT`, `SUPER+CTRL+PRINT` | Screenshot, recording, webcam resize, color pick, OCR | Omarchy utilities | Omarchy capture helpers, `hyprpicker` | Print is intentionally replaced by Omasnap; webcam keys are hardware-feature dependent |
| `SUPER+CTRL+S`, `SUPER+CTRL+PERIOD`, `SUPER+CTRL+R`, `SUPER+CTRL+ALT+R`, `SUPER+SHIFT+CTRL+R` | Share, transcode, set/show/clear reminders | Omarchy utilities | Omarchy menu/transcode/reminder helpers | Yes |
| `SUPER+CTRL+ALT+T/B/W`, `SUPER+SHIFT+CTRL+A` | Time, battery, weather notifications; agent picker | Omarchy utilities | Omarchy notifications and agent command | Yes; underlying data is runtime/system state |
| `SUPER+CTRL+A/B/D`, `SUPER+CTRL+ALT+D`, `SUPER+CTRL+W/P/T` | Audio, Bluetooth, display, clock/calendar panel, network, power, activity | Omarchy utilities | Stock shell widgets and `btop` | Yes; panel availability follows current shell schema |
| `SUPER+CTRL+code:10..18` | Toggle right-side panels 1–9 | Omarchy utilities | Omarchy Shell right panel ordering | Yes, but panel index meaning follows portable shell ordering |
| `SUPER+CTRL+Z`, `SUPER+CTRL+ALT+Z`, `SUPER+CTRL+L` | Zoom in/reset, lock system | Omarchy utilities | Hyprland config, Omarchy lock | Yes |
| `XF86AudioRaise/LowerVolume`, `XF86AudioMute`, `XF86AudioMicMute`, `ALT+XF86AudioRaise/LowerVolume` | Volume, mute, mic mute, fine volume | Omarchy media | PipeWire/Pulse compatibility and audio devices | Standard consumer audio keys; hardware availability varies |
| `XF86MonBrightnessUp/Down`, `ALT+XF86MonBrightnessUp/Down`, `SHIFT+XF86MonBrightnessUp/Down`, `XF86KbdBrightnessUp/Down`, `XF86KbdLightOnOff` | Display/keyboard brightness | Omarchy media | Brightness provider and device | Hardware-specific availability; host-owned behavior |
| `XF86TouchpadToggle/On/Off`, `XF86Eject`, lid switch bindings | Touchpad and media controls | Omarchy media/utilities | Device switch support | Hardware-specific; inherited, not deployed in portable overrides |
| `XF86AudioNext`, `XF86AudioPause/Play/Prev`, `ALT+XF86AudioPlay`, `ALT+SHIFT+XF86AudioPlay`, `SHIFT+XF86AudioMute/Pause/Play` | MPRIS next/play/pause/previous and audio-device/source switches | Omarchy media | Omarchy Shell media service, PipeWire | Yes where the corresponding media/device exists |
| `SUPER+C/V/X`, `SUPER+CTRL+V` | Universal copy/paste/cut / clipboard manager | Omarchy clipboard module | Clipboard provider and Omarchy clipboard panel | Yes |
| `SUPER+J/P/T/F`, `SUPER+CTRL+F`, `SUPER+ALT+F`, `SUPER+O`, `SUPER+ALT+HOME`, `SUPER+HOME`, `SUPER+L` | Split, pseudo, float, fullscreen variants, pop, save/restore width, workspace layout | Omarchy tiling | Hyprland and Omarchy helpers | Yes |
| `SUPER+LEFT/RIGHT/UP/DOWN`, `SUPER+1..9`, `SUPER+SHIFT+1..9`, `SUPER+SHIFT+ALT+1..9` | Focus windows; switch/move/move-silently workspaces | Omarchy tiling | Hyprland workspaces | Yes; Spaces changes display only, not these behaviors |
| `SUPER+S`, `SUPER+ALT+S`, `SUPER+TAB`, `SUPER+SHIFT+TAB`, `SUPER+CTRL+TAB` | Scratchpad, move-to-scratchpad, next/previous/former workspace | Omarchy tiling | Hyprland | Yes |
| `SUPER+SHIFT+ALT+ARROWS`, `SUPER+SHIFT+ARROWS`, `SUPER+ALT+ARROWS` | Move workspaces between monitors, swap windows, move windows into groups | Omarchy tiling | Hyprland monitor/window topology | Portable commands; monitor direction depends on host layout |
| `CTRL+ALT+TAB`, `CTRL+ALT+SHIFT+TAB`, `SUPER+ALT+TAB`, `SUPER+ALT+SHIFT+TAB` | Focus monitor / cycle within group | Omarchy tiling | Hyprland | Yes; distinct from Fathom's Alt-Tab pair |
| `SUPER+code:20/21` and modifier variants | Resize tiled windows by several increments | Omarchy tiling | Physical keyboard keycodes 20/21 | Hardware/layout-sensitive default, deliberately not copied |
| `SUPER+mouse_down/up`, `SUPER+mouse:272/273`, `SUPER+ALT+mouse_down/up` | Workspace scroll, move/resize, group cycle | Omarchy tiling | Pointer device, Hyprland | Hardware-specific mouse gestures inherited from Omarchy |
| `SUPER+G`, `SUPER+ALT+G`, `SUPER+ALT+ARROWS`, `SUPER+ALT+code:10..18` | Window grouping / leave group / directional group navigation / select group member | Omarchy tiling | Hyprland grouping | Yes; range is generated from the stock Lua module |
| `SUPER+SLASH`, `SUPER+ALT+SLASH` | Monitor scaling up/down | Omarchy tiling | Omarchy monitor scaler | Retained stock behavior; runtime scale is host/display-specific |
| `SUPER+CTRL+X`, `F9` press/release | Dictation toggle / push-to-talk | Omarchy Voxtype module (conditional) | Voxtype setup/device | Conditional and possibly absent; remains Omarchy-owned |

The region-picker overlay also installs temporary unmodified `RETURN`,
`CTRL+RETURN`, `TAB`, `CTRL+TAB`, and arrow bindings only while a capture
selection layer is open; the stock Lua stores handles and unbinds them when the
layer closes. These are transient overlay controls, not persistent shortcuts.

## Collision review

| Key(s) | Omarchy default | Selected current behavior | Assessment |
|---|---|---|---|
| `SUPER+W` | Close active window | Reprieve parks it; `SUPER+ALT+W` is explicit permanent close | Intentional product behavior. Reprieve's supported fenced marker is the single owner; installer must not invoke setup to append another block. |
| `ALT+TAB`, `ALT+SHIFT+TAB` | Each is registered twice by stock tiling (cycle and reveal) | Fathom unloads both and installs its depth-navigation handler | Intentional plugin override; no duplicate survives from stock once Fathom's module is loaded. |
| `SUPER+SHIFT+B` | Omarchy browser | Brave | Intentional override. `SUPER+B` separately opens Zen. |
| `SUPER+SHIFT+F`, `SUPER+ALT+SHIFT+F` | Nautilus and Nautilus in cwd | Strata | Intentional override. |
| `PRINT` | Omarchy screenshot | Omasnap | Intentional override. |
| `SUPER+Z`, `SUPER+Y`, `SUPER+SHIFT+Z` | No exact stock collision found | Reprieve restore/redo/timeline | No conflict. |

No binding references AgentDeck, Daily Islamic Reminder, Omapager,
Notification Center, or an obsolete pre-Quattro `.conf` setting. The Omastorm
command's `omarchy shell shell ...` form is valid: the installed Omarchy wrapper
forwards `shell` arguments to `omarchy-shell`.

## Dependency gaps

Zen (`zen-browser-bin`) and Brave (`brave-bin`) are represented in the
component manifest and are proposed defaults because their shortcuts are
default workflow. Both are AUR packages, so a fresh installer still requires a
reviewed `yay`/`paru` path; unattended AUR installation remains intentionally
blocked.

The current binaries were observed under the live user account; their exact
binary build provenance is not recoverable from the stripped executable.
Strata is third-party software installed through the `strata-bin` AUR package;
its source is `lgse/strata` (the local checkout came from a korex fork). Omasnap
is the Omarchy-supported `omasnap` package, so the package manager owns it and
no duplicate source checkout is declared. Learnomarchy is a third-party shell
project with an exact source lock and is cloned under
`$XDG_DATA_HOME/omarchy-dotfiles/tools/learnomarchy`; its upstream installer is
not run because it deletes/replaces destinations and edits/reloads Hyprland.
Their shortcuts remain in the portable bindings. Learnomarchy progress and
Omasnap temporary working data remain runtime state and are excluded.

Upstream install requirements cross-checked against the current package lists:

| Tool | Required runtime/install dependencies | Manifest gap |
|---|---|---|
| Strata | `bubblewrap`, `fontconfig`, `glibc >= 2.39`, `gstreamer`, `gst-plugins-base`, `gtk4 >= 4.12`, `gtksourceview5`, `gvfs`, `poppler-glib` (AUR metadata; optional media backends are separate) | `strata-bin` package identity is in the default workflow component; `yay`/`paru` review stays interactive. Installed binary had no pacman owner, so its exact binary build source cannot be proven. The local source checkout was a korex fork at `bed0dec`; canonical source is `lgse/strata`. |
| Omasnap | `hyprland`, `layer-shell-qt`, `qt6-base`, `tesseract`, `tesseract-data-eng`, `wayland`, `wl-clipboard` | `omasnap` is available from the installed Omarchy package repository and is managed by package identity. The current binary was built from `/home/dki/omasnap` (CMake source path); upstream is `omacom/omasnap`, observed source revision `7c0da87`. |
| Learnomarchy | `hyprctl`, `jq`, `xdg-terminal-exec`, `pw-play`, `grim`, `wl-copy` | Third-party shell project; installed checkout came from `MaximilianHansen/learnomarchy` at `c8ebb1c`, also the observed `main` tip. Lock-managed detached checkout provides the entry point. Its upstream installer is not used because it removes/replaces its destination and can edit/reload Hyprland. |

These are integration strategies only; the closure pass did not run any
upstream install script or touch live executables. The source-tool installer
clones a tested commit and does not create symlinks or invoke project hooks.

Learnomarchy's `tested_revision` and `tracking_ref` are recorded in
`manifests/source-tools.lock.toml`. Strata and Omasnap use Arch/Omarchy package
identities, so package-manager updates remain available and their binary
versions are not frozen. Source audit revisions above are provenance evidence,
not package binary locks. No source repository is vendored into dotfiles.
