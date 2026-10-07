# Host overlays

No host configuration was copied in Phase 1. The audited
`~/.config/hypr/monitors.conf` is deliberately excluded: it contains display
scale and monitor policy for this physical workstation. Future host overlays
must contain it under a stable host identifier, never under `home/`.
