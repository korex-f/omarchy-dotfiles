# Reproducibility gaps

## Plugins

- `capture-shelf` has a local Desktop remote, so no canonical upstream is known.
- `dki.clock` lacks Git metadata.
- `dki.hijri-calendar` is now clean and pinned at `e02fbfaf2eb9ad741ad9afed68f6cbedb1599cab`;
  the exact commit was fetched from its canonical remote on 2026-10-01.
- `dki.quran-verse-of-the-day` is excluded by explicit 2026-10-01 policy. Its
  current checkout is clean at `d34335f` with a GitHub origin, but `cache/` is
  runtime state and no pin is maintained for this baseline.
- `io.github.dki.habit` is installed through a symlink to a Desktop checkout.
- `njpatel.omapager` is excluded by explicit 2026-10-01 policy; its dirty local
  patch is preserved but is not an installation blocker.
- `io.github.dki.tugboat` is a selected default; its exact commit
  `73b2071eb14442613bf32abd77424a5a0c4263b9` is fetchable and advertised by
  canonical `main`. The earlier eight-commit local ahead display came from a
  stale local tracking ref. No push was performed.
- `theme-picker` is excluded by the user's 2026-10-07 decision. Its recorded
  source returns GitHub Repository not found; the local revision
  `1ef6fdf335c64dd7707b9bf0cce5c452259048ab` is retained only as provenance.
  It is not a selected-plugin blocker.
- `io.github.dki.agentdeck` is explicitly excluded. It was referenced in stale
  live shell JSON but has no matching source checkout. It cannot enter a future
  install from that stale configuration.
- Reprieve and Spaces are now default with exact canonical fetchable pins.
  Reprieve recovery journal and Spaces' optional Claude hook/session state are
  runtime and must remain excluded.
- Omamail and GitHub widgets can be source-reproducible while still requiring
  credentials supplied outside this repository.

User-owned software repositories identified by naming/provenance are
`dki.clock`, `dki.hijri-calendar`, `dki.quran-verse-of-the-day`,
`io.github.dki.habit`, and `io.github.dki.tugboat`. They remain separate
software repositories/checkouts and are represented only in `plugins.lock.toml`.

## Themes

- `aether` lacks Git metadata.
- `blackgold` has a dirty worktree.
- The active generated theme is intentionally excluded; the audited active
  source theme is `sunset` at the revision in `themes.lock.toml`.

## Tooling and host policy

- The live mise configuration uses `latest`; the repository copy now proposes
  the verified active versions. Upgrade by testing a candidate version on a
  disposable profile, recording compatibility results, then changing the pin
  and lock/documentation in one reviewed change.
- AUR package source/commit pinning policy is undecided.
- Zen and Brave are default components due to default bindings, including in
  `--minimal`; AUR helper absence remains a deliberate preflight blocker.
- Strata and Omasnap are installer-managed by package identity (`strata-bin`
  and `omasnap`). Learnomarchy is source-locked under
  `manifests/source-tools.lock.toml`; all three still need disposable-session
  integration verification. Runtime/package gaps are recorded in
  `keybindings.md`.
- Monitor layout, display scale, hostname, device-specific sync paths, and
  future service units need per-host overlays.
- Remote tool dependency installation and secret provisioning still need
  explicit review; do not copy credentials to satisfy plugin integrations.

See `plugin-normalization.md`, `host-profiles.md`, and
`package-categorization.md` for the resulting contracts and decisions.
