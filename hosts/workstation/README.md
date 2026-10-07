# Workstation profile

This profile selects the portable workstation baseline by stable ID; it does
not encode a hostname, monitor identifier, scale, GPU, transient device ID or
runtime state. Default plugins come from `plugins.lock.toml`; no optional
plugins or themes are selected.

Portable preferences are deployed from `home/`. Host-required monitor layout
and scaling remain pending the Omarchy Lua include-contract review. Optional
hardware overrides may later be added under this profile after review, but
none are captured here. Host-only packages and device integrations belong in
profile package lists, not in the portable baseline.
