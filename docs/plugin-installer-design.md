# Proposed interactive plugin installer

Phase 2 implementation now follows the core design below. No selector
dependency was installed and no live deployment occurred. See phase-2.md.

## Manifest contract

Read plugins.lock.toml dynamically with a real TOML parser, proposed Python
3.11+ tomllib. Check that the parser exists before doing anything; do not parse
TOML with Bash eval, grep or sed. The terminal selector is independent of the
parser. Python is an explicit future prerequisite, not assumed from bare Arch.

The manifest holds friendly name, category, description, ownership, historical
enabled state, credential_dependency, selection_status and install_policy.
Valid policies are default, optional, host and exclude. Pending decisions have
selection_status = "undecided" and omit install_policy.

The selection round is recorded in the lock manifest; Theme Picker was later
explicitly excluded after its source could not be established. Generate choices from the manifest, not
from this documentation or a hard-coded list.

Only validated IDs, canonical remotes, tested revisions and tracking refs enter
the plan. Audit enabled state must never become the installation choice.
Existing inventory/provenance is preserved. Source availability at a commit
still needs verification before a dependency is declared installable.

## Selection flow

1. Parse and validate policy and compatibility metadata; identify unresolved
   decisions and reproducibility blockers.
2. Require an explicit machine-profile selection when a profile is needed.
3. Include every default plugin. Select host plugins only when their IDs are
   declared required by the chosen profile.
4. Present optional plugins in a categorized checkbox selector, dynamically
   populated from the manifest. Display name, one-line purpose and ID. A detail
   view shows source pin, credentials and prerequisites.
5. Show a review screen with the selected IDs, source pins, host requirements,
   blockers and missing prerequisites. Cancel exits without applying anything.
6. Verify all selected dependencies and layout/service-owner consistency before
   any future deployment writes. Unresolved policy must be resolved or explicitly
   acknowledged as pending and omitted in a saved plan; no silent guesses.
7. A later approved implementation can apply the plan. Any selected dependency
   with an unresolved pin or dirty-source requirement must fail preflight,
   rather than quietly substituting upstream HEAD or copying the live checkout.

## Terminal UI evaluation

| Approach | Strength | Limitation | Role |
|---|---|---|---|
| gum choose --no-limit | Clear checkbox-style multi-selection and confirmations | Must already be available | Preferred |
| fzf --multi | Fast searchable selection; suitable for long lists | More keybinding-oriented | Alternate backend |
| whiptail --checklist | Familiar checklist on a terminal | Size/TERM and stream handling need care | Optional alternate |
| Pure Bash numbered prompts | No extra UI dependency, usable on minimal systems | No full-screen checkbox UI | Required fallback |

Proposed default: use gum when available, otherwise numbered Bash prompts.
fzf and whiptail remain evaluated alternatives, not implemented backends;
the initial implementation keeps only Gum and the required Bash fallback.
Do not install a selector just to ask questions. Handle Escape/Ctrl-C as cancel,
and never turn cancellation into an empty successful selection. Bind choices to
IDs rather than names. Use terminal input and plain output in limited terminals.

Upstream references:
- https://github.com/charmbracelet/gum (choose and confirm)
- https://github.com/junegunn/fzf (multi-selection)
- https://man.archlinux.org/man/whiptail.1.en (checklist)

## Implemented modes

| Mode | Selection semantics |
|---|---|
| Normal interactive | Defaults + required profile hosts + optional checkbox choices |
| --minimal | Defaults + required profile hosts; no optional plugins or optional prompt |
| --all | Defaults + all decided optional plugins + required profile hosts |
| --reproduce | Complete `workstation` profile, non-interactive, tested source revisions |
| --non-interactive | Replay an explicit saved selection, or combine with --minimal/--all; fail if additional input is needed |

--all never overrides exclude, installs hosts outside the chosen profile, or
turns undecided entries into permission. --minimal preserves the user's default
policy. Conflicting mode flags fail validation. Credentials are provisioned
separately; non-interactive mode must not prompt for them or print them.

## Reinstallation record

Proposed future local record:
`~/.config/omarchy-dotfiles/selections.toml`, excluded from this repository by
default. Write it only after successful future application. An explicit export
can produce a reviewed portable selection artifact later.

Record the selection schema, machine-profile ID, manifest digest, selected IDs
and exact revisions, optional choices (including explicit empty selections),
resolved service-owner choices and mode. Also record planned versus actually
applied state separately so a partial failure cannot masquerade as a complete
installation. Store no hostname, machine ID, credentials, account details or
local plugin-source paths.

Replay by IDs and recorded revisions. New optional IDs remain unselected until
reviewed. Excluded or unknown IDs in an old record cause a visible conflict,
not a bypass. Changes to default policy, pins or profile requirements produce a
reviewable plan difference; --non-interactive must fail on an unapproved
difference. Verify record integrity and atomically replace the applied record
only when the future operation succeeds.

## Remaining integration gates

The individual plugin choices are complete. Prove the proposed shell layout,
notification service ownership, workspace display and keybinding integration
in a disposable environment. Excluded
owned projects remain independent and untouched; their future maintenance is
not decided by exclusion from this dotfiles setup.
Phase 2 code is now implemented under explicit authorization, tested only in
isolated fixtures. Real deployment/activation remains a separate approval.
