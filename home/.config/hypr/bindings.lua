-- Portable personal bindings for the Omarchy Lua-module configuration.
-- Omarchy defaults load first; explicit hl.unbind() calls preserve current
-- intentional overrides. Host monitor, scaling and device settings live in
-- host profiles and are deliberately absent here.

o.bind("SUPER + B", "Zen Browser", { launch = "zen-browser" })
hl.unbind("SUPER + SHIFT + B")
o.bind("SUPER + SHIFT + B", "Brave", { launch = "brave" })
o.bind("SUPER + A", "Claude", { webapp = "https://claude.ai" })
o.bind("SUPER + ALT + O", "Omaconv", "omarchy-shell shell toggle slcode777.omaconv")
o.bind("SUPER + SHIFT + R", "Omastorm", "omarchy shell shell toggle com.omastorm.radar '{}'")

-- Omasnap replaces Omarchy's stock Print screenshot action.
hl.unbind("PRINT")
hl.unbind("F12")
hl.unbind("ALT + SHIFT + 4")
o.bind("PRINT", "Screenshot", "omasnap")
o.bind("F12", "Screenshot", "omasnap")
o.bind("ALT + SHIFT + 4", "Screenshot", "omasnap")

-- Strata intentionally replaces Omarchy's Nautilus bindings. Resolve through
-- PATH, not this machine's ~/.local/bin path.
hl.unbind("SUPER + SHIFT + F")
hl.unbind("SUPER + ALT + SHIFT + F")
o.bind("SUPER + SHIFT + F", "File manager", { launch = "strata" })
o.bind("SUPER + ALT + SHIFT + F", "File manager (cwd)",
  'uwsm-app -- strata "$(omarchy-cmd-terminal-cwd)"')

o.bind("SUPER + ALT + L", "Learnomarchy", {
  launch = os.getenv("HOME") .. "/.local/share/omarchy-dotfiles/tools/learnomarchy/learnomarchy"
})

-- Fathom intentionally owns Alt+Tab and Alt+Shift+Tab in place of the
-- stock cycling behavior. This remains a guarded plugin integration.
do
  local configHome = os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")
  local fathom = configHome .. "/omarchy/plugins/io.github.mtolhuys.fathom/hypr/fathom.lua"
  local file = io.open(fathom, "r")
  if file then
    file:close()
    pcall(dofile, fathom)
  end
end

-- BEGIN tech.greyforge.reprieve
-- Managed by Reprieve's supported setup/remove-binds mechanism. This portable
-- copy is the single owner; do not run setup to append a second block.
do
  local configHome = os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")
  local reprieve = configHome .. "/omarchy/plugins/tech.greyforge.reprieve/bin/reprieve"
  hl.unbind("SUPER + W")
  o.bind("SUPER + W", "Park window (Reprieve)", reprieve .. " park")
  o.bind("SUPER + ALT + W", "Close window permanently", reprieve .. " close")
  o.bind("SUPER + Z", "Restore parked window", hl.dsp.global("tech.greyforge.reprieve:undo"))
  o.bind("SUPER + Y", "Redo park", hl.dsp.global("tech.greyforge.reprieve:redo"))
  o.bind("SUPER + SHIFT + Z", "Reprieve timeline", hl.dsp.global("tech.greyforge.reprieve:timeline"))
  hl.window_rule({ match = { workspace = "special:reprieve" }, no_anim = true })
  hl.layer_rule({ match = { namespace = "reprieve" }, no_anim = true, animation = "none" })
  hl.layer_rule({ match = { namespace = "reprieve-toast" }, no_anim = true, animation = "none" })
end
-- END tech.greyforge.reprieve
