# Future controlled update workflow

`update.sh` is a future design, not an implemented command. It should inspect
each selected source's `tracking_ref`, find candidate commits, and show the
tested and candidate revisions with their changes. The user selects candidates;
the tool stages them separately, then runs manifest checks, doctor and the
safe fixture suite before promoting successful candidates to `tested_revision`.

If validation fails, the candidate is discarded and the previous tested
revision remains the recovery point. Promotion should update the source lock
and evidence together. No candidate becomes known-good merely because upstream
advanced. The workflow must not execute plugin setup hooks or activate shell
changes during checking.

Plugins and source tools can use exact tested commits. Normal Arch/AUR packages
continue to track package identity through the package manager; package binary
versions are not frozen here. A future exact-reproduction mode uses tested
source revisions where exact revisions are meaningful, while normal
interactive installation remains appropriate for current package-manager
repositories. Do not add a blind `--latest` mode or build a general package
manager into this repository.
