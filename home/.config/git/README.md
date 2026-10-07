# Git split policy

`config` contains portable presentation and merge preferences from the audited
global Git config. It intentionally omits `user.name`, `user.email`, signing
configuration, all credential sections, and the source machine's absolute
GitHub CLI helper path. A future machine should supply those through a
machine-local include file excluded from this repository.
