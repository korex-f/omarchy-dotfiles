"""Static policy regression for the proposed Omarchy Shell v1 layout."""
import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def iter_ids(value):
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            yield value["id"]
        for child in value.values():
            yield from iter_ids(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_ids(child)


class ProposedShellLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = json.loads((ROOT / "docs/proposed-shell-layout.json").read_text())
        cls.plugins = tomllib.loads((ROOT / "manifests/plugins.lock.toml").read_text())["plugin"]
        cls.by_id = {p["id"]: p for p in cls.plugins}

    def test_shell_v1_and_plugin_policies(self):
        self.assertEqual(self.layout["version"], 1)
        for plugin_id in set(iter_ids(self.layout)):
            if plugin_id.startswith("omarchy."):
                continue  # First-party IDs are supplied by the tested Omarchy package.
            self.assertIn(plugin_id, self.by_id, f"Uninventoried plugin: {plugin_id}")
            policy = self.by_id[plugin_id]["install_policy"]
            if plugin_id != "theme-picker":
                self.assertNotIn(policy, {"exclude", "undecided"}, f"Forbidden policy for {plugin_id}")
        self.assertEqual(self.by_id["theme-picker"]["install_policy"], "exclude")
        self.assertNotIn("theme-picker", set(iter_ids(self.layout)))

    def test_excluded_daily_reminder_and_omapager_never_return_from_stale_layout(self):
        referenced = set(iter_ids(self.layout))
        self.assertEqual(self.by_id["dki.quran-verse-of-the-day"]["install_policy"], "exclude")
        self.assertEqual(self.by_id["njpatel.omapager"]["install_policy"], "exclude")
        self.assertNotIn("dki.quran-verse-of-the-day", referenced)
        self.assertNotIn("njpatel.omapager", referenced)

    def test_excluded_or_uninventoried_live_plugins_do_not_leak(self):
        ids = set(iter_ids(self.layout))
        for plugin_id in {
            "io.github.dki.habit", "capture-shelf", "jankeesvw.notification-center",
            "omapdf.bar", "io.github.dki.agentdeck",
        }:
            self.assertNotIn(plugin_id, ids)

    def test_spaces_replaces_stock_workspace_widget(self):
        ids = set(iter_ids(self.layout))
        self.assertIn("tornikegomareli.spaces", ids)
        self.assertNotIn("omarchy.workspaces", ids)
        self.assertEqual(self.by_id["tornikegomareli.spaces"]["install_policy"], "default")

    def test_reprieve_is_default_and_has_one_shell_entry(self):
        self.assertEqual(self.by_id["tech.greyforge.reprieve"]["install_policy"], "default")
        self.assertIn("tech.greyforge.reprieve", [x["id"] for x in self.layout["bar"]["layout"]["right"]])
        self.assertNotIn("tech.greyforge.reprieve", [x["id"] for x in self.layout["plugins"]])
        self.assertEqual(sum(1 for x in iter_ids(self.layout) if x == "tech.greyforge.reprieve"), 1)

    def test_agentdeck_is_excluded_even_though_live_inventory_said_enabled(self):
        self.assertEqual(self.by_id["io.github.dki.agentdeck"]["install_policy"], "exclude")
        self.assertTrue(self.by_id["io.github.dki.agentdeck"]["enabled"])
        self.assertNotIn("io.github.dki.agentdeck", set(iter_ids(self.layout)))

    def test_first_party_notifications_are_not_disabled_without_omapager(self):
        self.assertNotIn("njpatel.omapager", set(iter_ids(self.layout)))
        self.assertNotIn("omarchy.notifications", self.layout.get("disabledPlugins", []))
        self.assertNotIn("jankeesvw.notification-center", set(iter_ids(self.layout)))
        # Stock Omarchy notifications auto-load unless listed in disabledPlugins.


if __name__ == "__main__":
    unittest.main()
