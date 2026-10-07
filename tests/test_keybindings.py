"""Regression checks for portable Lua bindings and selected app dependencies."""
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINDINGS = ROOT / "home/.config/hypr/bindings.lua"


class KeybindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = BINDINGS.read_text()
        cls.plugins = {
            p["id"]: p
            for p in tomllib.loads((ROOT / "manifests/plugins.lock.toml").read_text())["plugin"]
        }
        cls.components = tomllib.loads((ROOT / "manifests/components.toml").read_text())["component"]

    def test_portable_bindings_have_no_machine_home_paths(self):
        self.assertNotIn("/home/dki", self.source)
        self.assertNotIn("/tmp/", self.source)
        self.assertIn("XDG_CONFIG_HOME", self.source)

    def test_excluded_plugin_shortcuts_cannot_leak_into_baseline(self):
        for plugin_id in (
            "io.github.dki.agentdeck",
            "dki.quran-verse-of-the-day",
            "njpatel.omapager",
        ):
            self.assertEqual(self.plugins[plugin_id]["install_policy"], "exclude")
            self.assertNotIn(plugin_id, self.source)

    def test_reprieve_supported_block_is_the_only_binding_owner(self):
        self.assertEqual(self.source.count("-- BEGIN tech.greyforge.reprieve"), 1)
        self.assertEqual(self.source.count("-- END tech.greyforge.reprieve"), 1)
        for key in ("SUPER + W", "SUPER + ALT + W", "SUPER + Z", "SUPER + Y", "SUPER + SHIFT + Z"):
            self.assertEqual(len(re.findall(r'o\.bind\("' + re.escape(key) + r'"', self.source)), 1, key)
        self.assertEqual(self.source.count('hl.unbind("SUPER + W")'), 1)
        self.assertIn('configHome .. "/omarchy/plugins/tech.greyforge.reprieve/bin/reprieve"', self.source)

    def test_selected_plugin_policy_and_shell_layout_do_not_drift(self):
        self.assertEqual(self.plugins["tech.greyforge.reprieve"]["install_policy"], "default")
        self.assertEqual(self.plugins["tornikegomareli.spaces"]["install_policy"], "default")
        self.assertIn('"id": "tornikegomareli.spaces"', (ROOT / "docs/proposed-shell-layout.json").read_text())

    def test_browser_shortcut_dependencies_are_default_components(self):
        by_id = {c["id"]: c for c in self.components}
        self.assertTrue(by_id["brave"]["default"])
        self.assertTrue(by_id["zen"]["default"])
        self.assertIn("brave-bin", by_id["brave"]["aur"])
        self.assertIn("zen-browser-bin", by_id["zen"]["aur"])

    def test_default_workflow_shortcuts_have_one_installer_owner(self):
        by_id = {c["id"]: c for c in self.components}
        source_tools = tomllib.loads((ROOT / "manifests/source-tools.lock.toml").read_text())["source_tool"]
        tools = {tool["id"]: tool for tool in source_tools}
        self.assertTrue(by_id["workflow"]["default"])
        self.assertIn("omasnap", by_id["workflow"]["pacman"])
        self.assertIn("strata-bin", by_id["workflow"]["aur"])
        self.assertEqual(by_id["workflow"]["source_tools"], ["learnomarchy"])
        self.assertIn('os.getenv("HOME") .. "/.local/share/omarchy-dotfiles/tools/learnomarchy/learnomarchy"', self.source)
        self.assertEqual(tools["learnomarchy"]["tested_revision"], "c8ebb1cece74e75b4d17accd094a4b98280a4bf6")
        self.assertEqual(tools["learnomarchy"]["tracking_ref"], "refs/heads/main")

    def test_no_duplicate_direct_bind_declarations(self):
        keys = re.findall(r'o\.bind\("([^"]+)"', self.source)
        self.assertEqual(len(keys), len(set(keys)), "duplicate direct binding in portable module")


if __name__ == "__main__":
    unittest.main()
