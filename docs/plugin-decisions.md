# Plugin selection and porting decisions

Recorded from explicit user selections through 2026-10-07. Historical inventory stays in
`manifests/plugins.lock.toml`; `enabled` records current live-shell observations,
not install policy and not a future deployment result.

Omarchy's shipped plugins remain owned by the installed Omarchy package. Retain
them and their fallback components without cloning or vendoring their source.
Selected additions, including Tugboat, Hijri Calendar, Reprieve and Spaces, have
`install_policy = "default"`.

## Policy matrix

| Name | Plugin ID | Proposed install policy |
|---|---|---|
| Okomart | `b.okomart` | exclude |
| Capture Shelf | `capture-shelf` | exclude |
| Omastorm | `com.omastorm.radar` | default |
| Active Window + Icon | `crmne.active-window` | default |
| Docker Monitor | `djjeane.docker-monitor` | default |
| Hijri Clock | `dki.clock` | exclude |
| Hijri Calendar | `dki.hijri-calendar` | default |
| Daily Islamic Reminder | `dki.quran-verse-of-the-day` | exclude — separate plugin development; not part of this workstation baseline |
| AgentDeck | `io.github.dki.agentdeck` | exclude — source checkout not found; do not pursue |
| Key Promoter | `fkcodes.key-promoter` | default |
| Habit | `io.github.dki.habit` | exclude — for now; work in progress |
| Tugboat | `io.github.dki.tugboat` | default |
| Omasticky | `io.github.huligabuliga.omasticky` | default |
| Omapop | `io.github.jondkinney.omapop` | default |
| Fathom | `io.github.mtolhuys.fathom` | default |
| Notification Center | `jankeesvw.notification-center` | exclude |
| Prayer Times | `local.prayer-times` | default |
| Burn Bar | `nixfred.burnbar` | default |
| Omapager | `njpatel.omapager` | exclude — custom shell planned; local patch will not block this baseline |
| Omamail | `omamail` | optional |
| omapdf | `omapdf.bar` | optional |
| Plugin Manager | `omaplug` | default |
| Agent Usage | `robzolkos.agent-usage` | optional |
| GitHub | `robzolkos.github` | default |
| Shell Settings | `shell.settings` | default |
| Omaconv | `slcode777.omaconv` | default |
| Galley | `ssandys.galley` | default |
| Theme Picker | `theme-picker` | exclude — canonical source unavailable; user decision 2026-10-07 |
| Reprieve | `tech.greyforge.reprieve` | default |
| Spaces | `tornikegomareli.spaces` | default |
| Workspace Names | `workspace-names` | optional |

Okomart, Capture Shelf, Hijri Clock, Habit and Notification Center were explicitly
excluded by the user during the individual decision round. Omamail, omapdf,
Agent Usage and Workspace Names are optional during installation. The current
inventory retains historical plugins and records explicit policy without
hardcoded totals. Theme Picker is excluded after its recorded GitHub URL
returned 404 and no moved canonical source was established. No historical plugin has been removed from
the historical inventory. An omitted
`install_policy` combined with `selection_status = "undecided"` is a pending
user decision. It must never be interpreted as exclusion or permission to
install. Selection of a name in the keep list means default inclusion for this
proposal; it does not resolve source or runtime blockers.

## Owned projects

Tugboat and Hijri Calendar are preserved as separately maintained software
dependencies with default installation policy. Daily Islamic Reminder remains
a separate project but is excluded from this workstation baseline by explicit
decision on 2026-10-01. Its current live source is clean at `d34335f` with a
GitHub-tracking origin; generated `cache/` remains runtime state and no install
pin is maintained while excluded. Hijri Calendar is pinned at `e02fbfa`; its
earlier local UI changes are committed there.
Hijri Clock is excluded from the dotfiles ecosystem; its independent future
maintenance is unspecified and its live files remain untouched.
Habit is excluded for now because the user considers it a work in progress.
Its separate source repository remains untouched; this does not decide its
future maintenance or permanently forbid reconsideration.
Source remains outside dotfiles in every case. No owned
project has been created, committed, moved, published or altered.

## Reproducibility and integration gates

- Omapager is explicitly excluded from the baseline on 2026-10-01. Its dirty
  `Widget.qml` change remains untouched and is not an installation blocker.
- Historical gaps still include Capture Shelf's local remote, Clock's missing
  Git metadata and Habit's symlink/ahead history. Hijri Calendar is clean and
  pinned; Daily Islamic Reminder and Omapager are excluded. Tugboat's tested revision
  is now fetchable from canonical `main`; its earlier apparent ahead count was
  due to a stale local tracking ref. Theme Picker is excluded by explicit user
  decision because no canonical source was established. See plugin-normalization.md.
- Omastorm's source pin does not lock its separately fetched engine or assets.
  Future artifact/version/checksum validation is needed.
- Credentials for Tugboat, GitHub and provider integrations stay outside the
  manifest and saved selection record. Docker access and printer capabilities
  require host prerequisites; selecting a plugin is not evidence these exist.
- With Omapager and Notification Center excluded, Omarchy's first-party
  `omarchy.notifications` service is the sole notification implementation and
  should load by default. The proposal omits it from `disabledPlugins[]`.
- Galley is intentionally default per the user's choice and is now enabled in
  the live shell. Missing printer capabilities should be reported
  during planning rather than silently changing its policy to host-only.
- The copied `home/.config/omarchy/shell.json` remains an audit snapshot. It
  refers to plugins without a reviewed layout and `io.github.dki.agentdeck`
  (now explicitly excluded in the lock inventory), and disables stock
  notifications. It must not be deployed as the resolved selection. The new
  portable proposal removes AgentDeck, Daily Islamic Reminder and Omapager and
  uses Spaces instead of stock `omarchy.workspaces`. Future layout planning must match the selected IDs and
  reviewed service-owner policy.
- Reprieve and Spaces are default additions. Their exact requested commits were
  fetched from canonical repositories; Spaces' pin remains fixed at the
  requested historical commit rather than following current `main`.

## Approval boundary

Decision round: Okomart, Capture Shelf, Hijri Clock, Habit and Notification
Center excluded (Habit for now, as a work in progress); Hijri Calendar default;
Daily Islamic Reminder excluded; Omamail, omapdf, Agent Usage and Workspace
Names optional. The individual decision round is complete.
Notification Center and Omapager are excluded. Omarchy's stock notification
service is the sole notification owner and remains enabled by default.
Historical inventory and the live installation are unchanged.

## Current plugin reconciliation (2026-10-01)

Reprieve and Spaces are installed and enabled in the live shell; both are now
default in the manifest. Their exact canonical revisions are verified.
AgentDeck is referenced by the live shell's `plugins` list but no matching
plugin directory or source was found; it is now explicitly excluded, so stale
shell configuration cannot restore it. Workspace Names remains optional
in the historical inventory but is no longer installed. Galley is enabled live
(the historical manifest snapshot had `enabled = false`); its existing policy
remains default. The current shell proposal is not final until the new-plugin
decisions are recorded.

Agent Usage is currently disabled and has a clean, pinned source checkout
(`bf0f97a99f30abb39c35695039d1b59374e28bf4`). It overlaps the selected Burn Bar
and Omarchy's built-in Agents widget. Its service invokes the packaged Claude
and Codex usage collectors with `--limits-only`. In the installed collectors,
that flag permits reuse of cached local statistics; it does not prohibit a
session/transcript scan when the cache needs refreshing. Collectors read local
Claude/Codex session statistics and may also inspect supported pi/omp and
OpenCode sessions, maintaining generated data under `~/.cache/omarchy/agent-usage`.
The Claude collector reads existing CLI OAuth credentials and requests usage
limits; the Codex collector queries the authenticated Codex app-server. None
of these collectors were executed during this inspection. Source is reproducible,
but useful operation depends on compatible Omarchy collectors and per-machine
CLI authentication. Agent credentials, transcripts, histories and usage caches
must not be copied into dotfiles. The user selected optional during installation.

Workspace Names is currently disabled, with a clean source checkout pinned to
`ea13f3b4bb5bc4334986d603ec38679d95f3f1f7`. It provides named bar labels,
renaming and fuzzy workspace navigation. It dispatches renames to Hyprland,
so it changes underlying compositor workspace names rather than only bar text;
names last for the current session, with no separate persistence database.
It overlaps the stock `omarchy.workspaces` display and selected default
`tornikegomareli.spaces` widget. Spaces is the sole workspace-bar owner in the
proposed layout; Workspace Names remains optional and is absent from the default
layout. Its README's proposed `Super+Ctrl+W` shortcut conflicts with Omarchy's
Network shortcut. Source is reproducible and no account or credentials are
required.
The user selected Workspace Names as optional during installation. Spaces is
the selected default workspace-bar owner; the proposed layout omits stock
`omarchy.workspaces` to avoid rendering both. No live layout, workspace state
or keybinding was changed.

Hijri Clock and Hijri Calendar substantially duplicate the same clock/calendar
role. Clock uses tabular Hijri calculation and retains the stock omarchy.clock
moduleName and IPC target despite its dki.clock manifest ID; Calendar uses an
Umm al-Qura conversion table and its own dki.hijri-calendar identity. Clock
therefore also has an unresolved identity/IPC conflict with the stock clock.
No identity fix or source normalization is authorized by the selection round.

The user initially confirmed on 2026-09-28 that all eleven unlisted plugins
must remain undecided until individually reviewed. Each subsequent explicit
answer is now recorded in this matrix and plugins.lock.toml. No exclusion was
inferred from an omission. The decision order was Okomart, Capture Shelf,
Hijri Clock, Hijri Calendar, Daily Islamic
Reminder, Habit, Notification Center, Omamail, omapdf, Agent Usage, Workspace
Names. On 2026-10-01 the user explicitly changed Daily Islamic Reminder and
Omapager to exclude. The Omapager source patch is preserved but no longer blocks
installation; stock Omarchy notifications own the service in the proposed
baseline. Overlaps and dependencies were explained before each choice. See
omapager-decision-evidence.md for the current full diff and remote revision.

The Phase 2 installer now enforces these choices and source gates; see
plugin-installer-design.md and phase-2.md. No live deployment has occurred.
