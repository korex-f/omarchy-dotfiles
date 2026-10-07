"""Isolated integration tests. No real HOME, package manager or mise mutations."""
import argparse
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def run_git(directory, *args, input=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
    return subprocess.run(["git", *args], cwd=directory, input=input, text=True,
                          capture_output=True, env=env, check=True).stdout.strip()


def source_fixture(directory, plugin_id=None, entrypoint=None):
    directory.mkdir()
    run_git(directory, "init", "-q")
    if plugin_id:
        manifest = {"schemaVersion": 1, "id": plugin_id, "name": "Fixture", "version": "1.0.0",
                    "kinds": ["bar-widget"], "entryPoints": {"barWidget": "Widget.qml"}}
        files = {"manifest.json": json.dumps(manifest), "Widget.qml": "import QtQuick\nItem {}\n"}
    elif entrypoint:
        files = {entrypoint: "#!/bin/sh\necho fixture\n"}
    else:
        files = {"colors.toml": '[colors]\nbackground = "#111111"\n'}
    tree_rows = []
    for name, text in sorted(files.items()):
        blob = run_git(directory, "hash-object", "-w", "--stdin", input=text)
        tree_rows.append(f"100644 blob {blob}\t{name}\n")
    tree = run_git(directory, "mktree", input="".join(tree_rows))
    # Synthetic disposable Git objects via plumbing; no git commit, no user repo writes.
    revision = run_git(directory, "commit-tree", tree, input="Isolated fixture\n")
    run_git(directory, "symbolic-ref", "HEAD", "refs/heads/main")
    run_git(directory, "update-ref", "refs/heads/main", revision)
    run_git(directory, "read-tree", "--reset", "-u", "HEAD")
    return revision


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="omarchy-dotfiles-test-")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.home = self.root / "home"
        self.home.mkdir()
        self.marker = self.root / ".omarchy-dotfiles-fixture.json"
        import tomllib
        versions = tomllib.loads((self.repo / "manifests/compatibility.toml").read_text())["desktop"]
        installed = []
        for kind in ("pacman", "aur"):
            installed.extend(line.strip() for line in (self.repo / f"manifests/packages.{kind}.txt").read_text().splitlines()
                             if line.strip() and not line.startswith("#"))
        self.state = {"versions": versions, "packages": installed, "tools": {},
                      "commands": ["git", "pacman", "sudo", "mise", "hyprctl", "quickshell", "omarchy-shell"]}
        self.write_state()
        self.source = self.root / "upstream"
        self.revision = source_fixture(self.source, "fixture.default")
        self.optional_source = self.root / "optional-upstream"
        self.optional_revision = source_fixture(self.optional_source, "fixture.optional")
        self.theme_source = self.root / "theme-upstream"
        self.theme_revision = source_fixture(self.theme_source)
        self.tool_source = self.root / "tool-upstream"
        self.tool_revision = source_fixture(self.tool_source, entrypoint="learnomarchy")
        (self.repo / "manifests/source-tools.lock.toml").write_text(f'''schema_version = 1
[[source_tool]]
id = "learnomarchy"
name = "Fixture trainer"
upstream = "{self.tool_source.as_uri()}"
tested_revision = "{self.tool_revision}"
tracking_ref = "refs/heads/main"
update_policy = "check"
install_path = ".local/share/omarchy-dotfiles/tools/learnomarchy"
entrypoint = "learnomarchy"
''')
        self.write_plugins()
        (self.repo / "manifests/themes.lock.toml").write_text(f'''schema_version = 1
[[theme]]
slug = "fixture-theme"
upstream = "{self.theme_source.as_uri()}"
desired_revision = "{self.theme_revision}"
status = "reproducible"
''')

    def tearDown(self):
        self.temp.cleanup()

    def write_state(self):
        self.marker.write_text(json.dumps(self.state))

    def write_plugins(self, extra=""):
        (self.repo / "manifests/plugins.lock.toml").write_text(f'''schema_version = 1
[[plugin]]
id = "fixture.default"
name = "Default"
description = "Default widget"
selection_status = "decided"
install_policy = "default"
canonical_upstream = "{self.source.as_uri()}"
desired_revision = "{self.revision}"
reproducibility = "reproducible"
credential_dependency = "none-identified"
[[plugin]]
id = "fixture.optional"
name = "Optional"
description = "Optional widget"
selection_status = "decided"
install_policy = "optional"
canonical_upstream = "{self.optional_source.as_uri()}"
desired_revision = "{self.optional_revision}"
reproducibility = "reproducible"
credential_dependency = "account-setup"
[[plugin]]
id = "fixture.excluded"
name = "Excluded"
description = "Must never install"
selection_status = "decided"
install_policy = "exclude"
canonical_upstream = "https://example.invalid/excluded"
desired_revision = ""
reproducibility = "blocked-local-remote"
{extra}''')

    def run_installer(self, *args, input=None, ok=True, env=None, script="install.sh"):
        result = subprocess.run(["bash", str(self.repo / script), "--fixture", str(self.root), *args],
                                cwd=self.repo, text=True, input=input, capture_output=True, env=env)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def minimal(self, *args, **kwargs):
        return self.run_installer("--minimal", "--non-interactive", *args, **kwargs)

    def snapshots(self):
        return {str(p.relative_to(self.home)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.home.rglob("*") if p.is_file()}

    def test_first_and_idempotent_install(self):
        self.minimal()
        target = self.home / ".config/omarchy/plugins/fixture.default"
        self.assertEqual(run_git(target, "rev-parse", "HEAD"), self.revision)
        before = self.snapshots()
        self.minimal()
        after = self.snapshots()
        for key, value in before.items():
            self.assertEqual(after[key], value)
        self.assertFalse((self.home / ".config/omarchy/plugins/fixture.optional").exists())
        journals = sorted((self.home / ".local/state/omarchy-dotfiles/backups").glob("*/journal.json"))
        self.assertEqual(len(journals), 1)
        self.assertTrue(json.loads(journals[0].read_text())["entries"])

    def test_dry_run_no_writes(self):
        before = self.snapshots()
        marker = self.marker.read_bytes()
        self.minimal("--dry-run")
        self.assertEqual(before, self.snapshots())
        self.assertEqual(marker, self.marker.read_bytes())

    def test_minimal_default_and_excluded_policies(self):
        self.minimal()
        self.assertTrue((self.home / ".config/omarchy/plugins/fixture.default").exists())
        self.assertFalse((self.home / ".config/omarchy/plugins/fixture.excluded").exists())

    def test_optional_selection(self):
        result = self.minimal("--optional-plugins", "fixture.optional")
        self.assertTrue((self.home / ".config/omarchy/plugins/fixture.optional").exists())
        self.assertIn("machine-local setup", result.stdout)

    def test_excluded_explicit_selection_rejected(self):
        self.minimal("--optional-plugins", "fixture.excluded", ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_undecided_blocks_even_all(self):
        self.write_plugins('''[[plugin]]
id = "fixture.pending"
selection_status = "undecided"
''')
        result = self.run_installer("--profile", "custom", "--all", "--components", "none", "--themes", "none", "--non-interactive", ok=False)
        self.assertIn("Undecided", result.stderr)
        self.assertEqual(self.snapshots(), {})

    def test_conflict_aborts_before_mutation(self):
        target = self.home / ".config/git/config"
        target.parent.mkdir(parents=True)
        target.write_text("[core]\n  pager = less\n")
        before = self.snapshots()
        self.minimal(ok=False)
        self.assertEqual(before, self.snapshots())

    def test_backup_and_rollback(self):
        target = self.home / ".config/git/config"
        target.parent.mkdir(parents=True)
        original = "[core]\n  pager = less\n"
        target.write_text(original)
        self.minimal("--conflicts", "backup")
        journal = next((self.home / ".local/state/omarchy-dotfiles/backups").glob("*/journal.json"))
        self.assertEqual((journal.parent / "files/.config/git/config").read_text(), original)
        self.run_installer(journal.parent.name, script="scripts/rollback.sh")
        self.assertEqual(target.read_text(), original)
        self.assertFalse((self.home / ".config/omarchy/plugins/fixture.default").exists())
        self.assertTrue((journal.parent / "retired/.config/omarchy/plugins/fixture.default").exists())

    def test_rollback_refuses_subsequent_edits(self):
        self.minimal()
        journal = next((self.home / ".local/state/omarchy-dotfiles/backups").glob("*/journal.json"))
        target = self.home / ".config/git/config"
        target.write_text("[core]\n  pager = less\n")
        self.run_installer(journal.parent.name, script="scripts/rollback.sh", ok=False)
        self.assertTrue((self.home / ".config/omarchy/plugins/fixture.default").exists())

    def test_missing_optional_aur_helper(self):
        self.state["packages"].remove("brave-bin")
        self.write_state()
        result = self.minimal("--components", "brave", ok=False)
        self.assertIn("existing yay/paru", result.stdout)
        self.assertEqual(self.snapshots(), {})

    def test_malformed_manifest(self):
        (self.repo / "manifests/plugins.lock.toml").write_text("[[plugin]\n")
        self.minimal(ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_incompatible_version_handling(self):
        self.state["versions"]["hyprland"] = "0.0.0"
        self.write_state()
        self.minimal(ok=False)
        self.assertEqual(self.snapshots(), {})
        self.minimal("--allow-incompatible")

    def test_dirty_checkout_rejected(self):
        self.minimal()
        (self.home / ".config/omarchy/plugins/fixture.default/Widget.qml").write_text("// local edit\n")
        result = self.minimal(ok=False)
        self.assertIn("Dirty checkout", result.stderr)

    def test_wrong_plugin_identity_blocks_before_config_install(self):
        self.revision = self.optional_revision
        self.source = self.optional_source
        self.write_plugins()
        self.minimal(ok=False)
        self.assertFalse((self.home / ".config/git/config").exists())

    def test_missing_pin_blocks(self):
        path = self.repo / "manifests/plugins.lock.toml"
        path.write_text(path.read_text().replace(f'desired_revision = "{self.revision}"', 'desired_revision = ""'))
        self.minimal(ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_theme_sources(self):
        self.minimal("--themes", "fixture-theme")
        target = self.home / ".config/omarchy/themes/fixture-theme"
        self.assertEqual(run_git(target, "rev-parse", "HEAD"), self.theme_revision)
        self.assertFalse((self.home / ".local/state/omarchy").exists())

    def test_tool_pins_mocked_and_idempotent(self):
        self.minimal("--components", "development", "--only", "tools")
        state = json.loads(self.marker.read_text())
        self.assertEqual(state["tools"]["claude"], ["2.1.281"])
        self.minimal("--components", "development", "--only", "tools")
        self.assertEqual(state["operations"], json.loads(self.marker.read_text())["operations"])

    def test_reproduce_uses_tested_revisions_and_workstation_profile(self):
        profile = self.repo / "hosts/workstation"
        profile.mkdir(exist_ok=True)
        (profile / "profile.toml").write_text('''schema_version = 1
profile_id = "workstation"
components = ["system", "kitty", "cli", "brave", "zen", "workflow"]
optional_plugins = []
themes = []
steps = ["packages", "config", "plugins", "themes", "tools"]
host_plugins = []
files = []
''')
        result = self.run_installer("--reproduce")
        self.assertIn("Machine profile: workstation", result.stdout)
        self.assertEqual(run_git(self.home / ".config/omarchy/plugins/fixture.default", "rev-parse", "HEAD"), self.revision)
        tool = self.home / ".local/share/omarchy-dotfiles/tools/learnomarchy"
        self.assertEqual(run_git(tool, "rev-parse", "HEAD"), self.tool_revision)

    def test_reproduce_rejects_selection_overrides(self):
        self.run_installer("--reproduce", "--all", ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_schema_two_requires_update_metadata_and_preserves_tested_pin(self):
        path = self.repo / "manifests/plugins.lock.toml"
        path.write_text(f'''schema_version = 2
[[plugin]]
id = "fixture.default"
name = "Default"
description = "Default widget"
selection_status = "decided"
install_policy = "default"
canonical_upstream = "{self.source.as_uri()}"
tested_revision = "{self.revision}"
tracking_ref = "refs/heads/main"
update_policy = "check"
reproducibility = "reproducible"
credential_dependency = "none-identified"
''')
        self.minimal("--dry-run")
        path.write_text(path.read_text().replace('tracking_ref = "refs/heads/main"', 'tracking_ref = ""'))
        self.minimal("--dry-run", ok=False)

    def test_package_backend_mocked(self):
        self.state["packages"].remove("kitty")
        self.write_state()
        self.run_installer("--minimal", "--only", "packages", input="install\n")
        self.assertIn("kitty", json.loads(self.marker.read_text())["packages"])

    def test_noninteractive_native_package_backend(self):
        self.state["packages"].remove("kitty")
        self.write_state()
        self.minimal()
        self.assertIn("kitty", json.loads(self.marker.read_text())["packages"])

    def test_profile_save_replay_digest(self):
        self.minimal("--save-profile", "portable-test")
        profile = self.repo / "hosts/portable-test/profile.toml"
        self.assertTrue(profile.is_file())
        self.run_installer("--profile", "portable-test", "--non-interactive")
        self.run_installer("--replay", "--non-interactive")
        path = self.repo / "home/.config/git/config"
        path.write_text(path.read_text() + "\n# intentional changed policy\n")
        result = self.run_installer("--profile", "portable-test", "--non-interactive", ok=False)
        self.assertIn("digest changed", result.stderr)

    def test_doctor(self):
        self.minimal()
        self.run_installer(script="scripts/doctor.sh")
        (self.home / ".config/git/config").unlink()
        self.run_installer(script="scripts/doctor.sh", ok=False)

    def test_runtime_and_secrets_payload_rejected(self):
        path = self.repo / "home/.config/git/config"
        path.write_text("api_key = " + "sk-" + "a" * 40)
        self.minimal(ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_secret_original_not_backed_up(self):
        path = self.home / ".config/git/config"
        path.parent.mkdir(parents=True)
        path.write_text("password = " + "a" * 40)
        self.minimal("--conflicts", "backup", ok=False)
        self.assertFalse((self.home / ".local/state/omarchy-dotfiles").exists())

    def test_absolute_machine_path_refused(self):
        path = self.repo / "home/.config/git/config"
        path.write_text("[core]\n  pager = /home/another-machine/bin/pager\n")
        self.minimal(ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_bash_selector_and_cancellation(self):
        result = self.run_installer("--profile", "custom", "--components", "cli", "--themes", "none",
                                    "--ui", "bash", input="1\ninstall\n")
        self.assertIn("fixture.optional", result.stdout)
        self.assertTrue((self.home / ".config/omarchy/plugins/fixture.optional").exists())
        self.run_installer("--profile", "custom", "--components", "cli", "--themes", "none",
                           "--ui", "bash", input="q\n", ok=False)

    def test_gum_absent_falls_back(self):
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        shutil.copyfile(shutil.which("bash"), bin_dir / "bash")
        os.chmod(bin_dir / "bash", 0o755)
        env = dict(os.environ, PATH=str(bin_dir))
        result = subprocess.run([str(bin_dir / "bash"), str(self.repo / "scripts/lib/select.sh"),
                                 "auto", "fixture.optional\tOptional"], input="1\n", text=True,
                                capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "fixture.optional")

    def test_host_policy_only_for_explicit_profile(self):
        # Reuse optional source but classify it host-specific instead.
        path = self.repo / "manifests/plugins.lock.toml"
        path.write_text(path.read_text().replace('install_policy = "optional"', 'install_policy = "host"'))
        self.minimal()
        self.assertFalse((self.home / ".config/omarchy/plugins/fixture.optional").exists())
        profile = self.repo / "hosts/explicit-machine"
        profile.mkdir()
        (profile / "profile.toml").write_text('''schema_version = 1
profile_id = "explicit-machine"
components = ["cli"]
optional_plugins = []
themes = []
host_plugins = ["fixture.optional"]
''')
        self.run_installer("--profile", "explicit-machine", "--non-interactive")
        self.assertTrue((self.home / ".config/omarchy/plugins/fixture.optional").exists())

    def test_runtime_path_allowlist_refused(self):
        (self.repo / "manifests/deployment.toml").write_text('''schema_version = 1
[[area]]
source = ".local/state/omarchy/current"
component = "cli"
''')
        self.minimal(ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_all_includes_optional_not_excluded(self):
        self.run_installer("--profile", "custom", "--all", "--components", "cli", "--themes", "none", "--non-interactive")
        self.assertTrue((self.home / ".config/omarchy/plugins/fixture.optional").exists())
        self.assertFalse((self.home / ".config/omarchy/plugins/fixture.excluded").exists())

    def test_actual_inventory_blockers_no_writes(self):
        shutil.copyfile(ROOT / "manifests/plugins.lock.toml", self.repo / "manifests/plugins.lock.toml")
        result = self.minimal("--dry-run")
        self.assertNotIn("Unreproducible plugin: dki.quran-verse-of-the-day", result.stdout)
        self.assertNotIn("Unreproducible plugin: njpatel.omapager", result.stdout)
        self.assertNotIn("Unreproducible plugin: io.github.dki.tugboat", result.stdout)
        self.assertNotIn("Unreproducible plugin: theme-picker", result.stdout)
        self.assertNotIn("Unreproducible plugin: io.github.dki.agentdeck", result.stdout)
        self.assertNotIn("Unreproducible plugin: tech.greyforge.reprieve", result.stdout)
        self.assertNotIn("Unreproducible plugin: tornikegomareli.spaces", result.stdout)
        self.assertNotIn("Unreproducible plugin: dki.hijri-calendar", result.stdout)
        self.assertEqual(self.snapshots(), {})
        import tomllib
        calendar = next(p for p in tomllib.loads((self.repo / "manifests/plugins.lock.toml").read_text())["plugin"]
                        if p["id"] == "dki.hijri-calendar")
        self.assertEqual(calendar["tested_revision"], "e02fbfaf2eb9ad741ad9afed68f6cbedb1599cab")
        self.assertEqual(calendar["current_revision"], calendar["tested_revision"])
        self.assertEqual(calendar["reproducibility"], "reproducible")

    def test_excluded_notification_plugins_do_not_block_default_plan(self):
        shutil.copyfile(ROOT / "manifests/plugins.lock.toml", self.repo / "manifests/plugins.lock.toml")
        result = self.minimal("--dry-run")
        self.assertNotIn("dki.quran-verse-of-the-day", result.stdout)
        self.assertNotIn("njpatel.omapager", result.stdout)
        self.assertEqual(self.snapshots(), {})

    def test_config_only_with_actual_inventory(self):
        shutil.copyfile(ROOT / "manifests/plugins.lock.toml", self.repo / "manifests/plugins.lock.toml")
        self.minimal("--only", "config")
        self.assertTrue((self.home / ".config/git/config").exists())
        self.assertTrue((self.home / ".config/hypr/bindings.lua").is_file())
        self.assertFalse((self.home / ".config/hypr/monitors.conf").exists())
        self.assertFalse((self.home / ".config/omarchy/shell.json").exists())
        self.assertFalse((self.home / ".config/omarchy/plugins").exists())

    def test_backup_rollback_dry_run(self):
        self.minimal()
        journal = next((self.home / ".local/state/omarchy-dotfiles/backups").glob("*/journal.json"))
        before = self.snapshots()
        self.run_installer(journal.parent.name, "--dry-run", script="scripts/rollback.sh")
        self.assertEqual(before, self.snapshots())

    def test_aur_noninteractive_review_gate(self):
        self.state["commands"].append("yay")
        self.state["packages"].remove("brave-bin")
        self.write_state()
        result = self.minimal("--components", "brave", ok=False)
        self.assertIn("AUR builds require interactive", result.stdout)

    def test_minimal_includes_default_shortcut_browser_dependencies(self):
        self.state["packages"] = [p for p in self.state["packages"] if p not in {"brave-bin", "zen-browser-bin"}]
        self.state["commands"].append("yay")
        self.write_state()
        result = self.minimal("--dry-run", ok=False)
        self.assertIn("brave-bin", result.stdout)
        self.assertIn("zen-browser-bin", result.stdout)

    def test_stale_agentdeck_shell_reference_is_rejected_not_reintroduced(self):
        manifest = self.repo / "manifests/plugins.lock.toml"
        manifest.write_text(manifest.read_text() + '''
[[plugin]]
id = "io.github.dki.agentdeck"
name = "AgentDeck"
selection_status = "decided"
install_policy = "exclude"
canonical_upstream = ""
desired_revision = ""
reproducibility = "excluded-missing-source"
credential_dependency = "unknown-not-pursued"
''')
        self.minimal()
        path = self.home / ".config/omarchy/shell.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps({"version": 1, "plugins": [{"id": "io.github.dki.agentdeck"}]}))
        result = self.run_installer(script="scripts/doctor.sh", ok=False)
        self.assertIn("Shell references excluded plugin: io.github.dki.agentdeck", result.stdout)
        self.assertFalse((self.home / ".config/omarchy/plugins/io.github.dki.agentdeck").exists())

    def test_neovim_payload_and_lockfile(self):
        self.minimal("--components", "nvim", "--only", "config")
        source = self.repo / "home/.config/nvim/lazy-lock.json"
        target = self.home / ".config/nvim/lazy-lock.json"
        self.assertEqual(target.read_bytes(), source.read_bytes())
        self.assertFalse((target.parent / "README.md").exists())

    def test_pinned_revision_mismatch_refused(self):
        self.minimal()
        path = self.repo / "manifests/plugins.lock.toml"
        path.write_text(path.read_text().replace(self.revision, "a" * 40))
        result = self.minimal(ok=False)
        self.assertIn("Revision mismatch", result.stderr)

    def test_doctor_notification_conflict(self):
        self.minimal()
        path = self.home / ".config/omarchy/shell.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps({"version": 1, "plugins": [{"id": "njpatel.omapager"}], "disabledPlugins": []}))
        result = self.run_installer(script="scripts/doctor.sh", ok=False)
        self.assertIn("Notification ownership conflict", result.stdout)

    def test_unresolved_custom_noninteractive_rejected(self):
        self.run_installer("--profile", "custom", "--non-interactive", ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_theme_with_unresolved_provenance(self):
        path = self.repo / "manifests/themes.lock.toml"
        path.write_text(path.read_text().replace('status = "reproducible"', 'status = "blocked-dirty-worktree"'))
        self.minimal("--themes", "fixture-theme", ok=False)
        self.assertEqual(self.snapshots(), {})

    def test_credential_url_original_refused(self):
        path = self.home / ".config/git/config"
        path.parent.mkdir(parents=True)
        fixture_url = "https://someone" + chr(58) + "example-password@example.invalid/"
        path.write_text("[url]\n  insteadOf = " + fixture_url + "\n")
        self.minimal("--conflicts", "backup", ok=False)
        self.assertFalse((self.home / ".local/state/omarchy-dotfiles").exists())

    def test_host_monitor_overlay_not_silently_deployed(self):
        profile = self.repo / "hosts/display-test"
        (profile / "home/.config/hypr").mkdir(parents=True)
        (profile / "home/.config/hypr/monitors.conf").write_text("monitor = ,preferred,auto,1\n")
        (profile / "profile.toml").write_text('''schema_version = 1
profile_id = "display-test"
components = ["cli"]
optional_plugins = []
themes = []
files = [".config/hypr/monitors.conf"]
''')
        result = self.run_installer("--profile", "display-test", "--non-interactive", ok=False)
        self.assertIn("Lua/conf include-contract review", result.stdout)
        self.assertFalse((self.home / ".config/hypr/monitors.conf").exists())

    def test_failed_partial_copy_has_recoverable_journal(self):
        sys.path.insert(0, str(ROOT / "scripts/lib"))
        from deploy import Transaction
        from engine import Environment, Inventory, Plan, get_selection
        from policy import Failure
        args = argparse.Namespace(fixture=str(self.root), profile="minimal", replay=False,
                                  minimal=True, all=False, only="config", components=None,
                                  optional_plugins=None, themes=None, allow_incompatible=False,
                                  non_interactive=True, ui="bash", conflicts="abort", save_profile=None,
                                  dry_run=False)
        inv, environment = Inventory(self.repo), Environment(args)
        with contextlib.redirect_stdout(io.StringIO()):
            selection = get_selection(inv, environment, args)
            plan = Plan(inv, environment, args, selection)
            original_copy = Transaction.copy
            calls = []
            def fail_second_copy(transaction, *values):
                calls.append(values)
                if len(calls) == 2:
                    raise Failure("Injected fixture copy failure")
                return original_copy(transaction, *values)
            with patch.object(Transaction, "copy", fail_second_copy):
                with self.assertRaises(Failure):
                    plan.apply()
        journal = next((self.home / ".local/state/omarchy-dotfiles/backups").glob("*/journal.json"))
        self.assertEqual(json.loads(journal.read_text())["status"], "failed")
        self.assertTrue((self.home / ".config/git/config").exists())
        self.assertFalse((self.home / ".config/omarchy-dotfiles/selections.toml").exists())
        self.run_installer(journal.parent.name, script="scripts/rollback.sh")
        self.assertFalse((self.home / ".config/git/config").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
