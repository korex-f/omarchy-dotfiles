# Plugin normalization matrix

No plugin source was changed during this audit.

| Plugin | Evidence | Normalization plan |
|---|---|---|
| `capture-shelf` | Clean Git checkout at `f6c0609`; origin is a local Desktop checkout | Identify its canonical upstream or make the source an owned project; set a public/canonical URL and pin a reviewed commit. |
| `dki.clock` | No Git metadata; four source files only | Initialize/identify its independent source repository outside this dotfiles repo, add a proper ignore policy, review, then record canonical remote and commit. |
| `dki.hijri-calendar` | Clean checkout at `e02fbfa`; `origin/master` and `origin/HEAD` point to the same revision. That commit contains the earlier `BarWidget.qml` hover and `Panel.qml` popup-position changes. | Resolved locally: lock `e02fbfaf2eb9ad741ad9afed68f6cbedb1599cab`. GitHub reachability was not rechecked during Phase 3A, so verify the advertised remote ref before fresh-install readiness. |
| `dki.quran-verse-of-the-day` | Historical checkout was dirty at `c1473cf` with `file:///tmp` remote. Current checkout is clean at `d34335f`, tracks `https://github.com/korex-f/daily-islamic-reminder.git`, and still contains generated `cache/`. | Explicitly excluded from the workstation baseline on 2026-10-01. Keep independent plugin development separate; do not normalize or pin it for this build. Retain the old remote/cache history as provenance. |
| `io.github.dki.habit` | Clean `main` at `52f7416`; plugin installation is a symlink to a Desktop checkout; GitHub remote exists but HEAD is now `0947db6` | Keep its source as an independent repository. Replace the deployment symlink only in a future deployment phase with a normal pinned checkout; choose whether to pin `52f7416` or review the newer remote commit. |
| `njpatel.omapager` | Dirty `main` at `6fe51b`; `Widget.qml` modified (+8/-12), primary click opens panel instead of upstream silence-toggle. | Explicitly excluded from the workstation baseline on 2026-10-01. Leave the patch untouched; it is not a current installer blocker. |

| `io.github.dki.tugboat` | Clean `main` at `73b2071`; canonical GitHub now advertises that exact SHA at `refs/heads/main`, and fetching the SHA succeeds. | Resolved for source reproducibility. The local `origin/main` tracking ref was stale and showed the clean local branch eight commits ahead; no plugin changes or push were made. |

## Newly discovered plugins — policy resolved (2026-10-01)

`tech.greyforge.reprieve` and `tornikegomareli.spaces` were installed after the
original inventory and are now explicitly default. Reprieve's exact SHA
`38c6292e7f22e554935c36f6597b8a1bac5e146f` is the canonical `main` and `v1.5.2`
target. Spaces' exact SHA `f8306d763c7b3c89d24172edb0e68fb6dacb68a9` fetches from
the canonical repository even though current `main` has advanced; keep that
historical pin unchanged. Both IDs/manifests were checked in their clean live
checkouts. Reprieve needs Hyprland >=0.56, Python 3 stdlib, `hyprctl`, `pactl`,
and `busctl`; optional native journal support uses a C compiler and json-c
headers. Its `$XDG_STATE_HOME/reprieve` recovery journal is runtime state.
Spaces' core is credential-free; optional Claude activity badges use `jq` and
Claude hook/session runtime state. No Claude settings, auth, sessions, history,
or generated agent state belongs in dotfiles. The current Spaces shell entry
has no settings beyond its ID.

AgentDeck (`io.github.dki.agentdeck`) was present only as a stale reference in
live `shell.json`; no source checkout was found. It is explicitly excluded and
must not be copied to the proposed shell layout.

## Remaining fetch blocker

`theme-picker` at `1ef6fdf335c64dd7707b9bf0cce5c452259048ab` records the installed
checkout. Its configured GitHub repository returns Repository not found; no
moved canonical repository was established. On 2026-10-07 the user explicitly
selected `exclude`. The historical revision and URL remain for provenance, not
installation.

## User-owned publication readiness

| Project | Source / revision | Remote status | Readiness blockers |
|---|---|---|---|
| `dki.clock` | `~/.config/omarchy/plugins/dki.clock`; no revision | No remote or Git metadata | Establish separate repository and provenance; add ignore/tests/release policy. No detected secret/runtime files. |
| `dki.hijri-calendar` | `~/.config/omarchy/plugins/dki.hijri-calendar`; `e02fbfa` | `origin/master` and `origin/HEAD` locally match HEAD | Clean and pinned. The local Git object and tracking refs are present; live GitHub reachability was unavailable for re-verification. No detected secret/runtime files. |
| `dki.quran-verse-of-the-day` | plugin directory; current `d34335f` | Current origin is GitHub; historical origin was temporary local | Excluded from this workstation baseline. Current `cache/{items,editions,state}.json` remains runtime state; no normalization/pin work is authorized for this build. |
| `io.github.dki.habit` | `~/Desktop/open-source/habit`; `52f7416` | GitHub exists; remote HEAD `0947db6` | Installed through a symlink; decide pin vs newer revision. `*.log`, `*.tmp`, and `.DS_Store` are ignored. |
| `io.github.dki.tugboat` | `~/.config/omarchy/plugins/io.github.dki.tugboat`; `73b2071` | Clean local `main`, 8 commits ahead of `origin/main` | Current desired revision is not advertised by origin; preserve the exact pin and resolve in its separate repository before this default can be reproduced. |

GitHub reachability was checked read-only on 2026-09-27 except where explicitly
noted above. “Exists” does not
mean public-release readiness; each project needs its own source review,
license, CI/test, manifest validation, and secrets scan before publication.
