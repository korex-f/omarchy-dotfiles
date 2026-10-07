#!/usr/bin/env python3
"""Manifest-driven planner/application entry. Python 3.11+, standard library only."""
import argparse
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from deploy import (
    Transaction,
    atomic_write,
    checkout_status,
    hash_file,
    rollback,
    stage_checkout,
    target_path,
)
from policy import (
    Failure,
    Inventory,
    files_under,
    identifier,
    load,
    packages,
    remote_valid,
    require,
    safe_content,
    safe_path,
    toml_selection,
)

STEPS = {"packages", "config", "plugins", "themes", "tools"}


def csv(value):
    return [] if value == "none" else list(dict.fromkeys(value.split(",")))


def command(args):
    result = subprocess.run(args, text=True, capture_output=True)
    require(result.returncode == 0, f"Command failed: {args[0]}: {result.stderr.strip()}")
    return result.stdout


class Environment:
    def __init__(self, args):
        self.fixture_path = None
        self.fixture = None
        if args.fixture:
            root = Path(args.fixture).absolute()
            require(str(root).startswith("/tmp/") and root.resolve() == root and root.is_dir(),
                    "Fixtures must be real directories below /tmp")
            self.fixture_path = root / ".omarchy-dotfiles-fixture.json"
            require(self.fixture_path.is_file() and not self.fixture_path.is_symlink(), "Missing explicit fixture marker")
            self.fixture = json.loads(self.fixture_path.read_text())
            self.home = root / "home"
            require(not self.home.is_symlink(), "Fixture home symlink refused")
        else:
            require(os.geteuid() != 0, "Run as your regular user, not root")
            self.home = Path.home().resolve()
            for key, suffix in (("XDG_CONFIG_HOME", ".config"), ("XDG_STATE_HOME", ".local/state")):
                require(not os.getenv(key) or Path(os.environ[key]) == self.home / suffix,
                        f"Nonstandard {key} needs an explicit future path contract")
        require(self.home != Path("/"), "Invalid target home")

    def available(self, name):
        if self.fixture is not None:
            return name in self.fixture.get("commands", [])
        return shutil.which(name) is not None

    def installed(self):
        if self.fixture is not None:
            return set(self.fixture.get("packages", []))
        require(self.available("pacman"), "Requires an already installed Arch/Omarchy system")
        return set(command(["pacman", "-Qq"]).splitlines())

    def versions(self):
        if self.fixture is not None:
            return self.fixture.get("versions", {})
        result = {}
        for name in ("omarchy", "quickshell", "hyprland"):
            proc = subprocess.run(["pacman", "-Q", name], text=True, capture_output=True)
            result[name] = proc.stdout.split()[1] if proc.returncode == 0 else "missing"
        return result

    def tools(self):
        if self.fixture is not None:
            return self.fixture.get("tools", {})
        if not self.available("mise"):
            return {}
        # Run away from the repository/user projects: no repo-local config/tasks.
        with tempfile.TemporaryDirectory(prefix="omarchy-dotfiles-query-") as directory:
            result = subprocess.run(["mise", "ls", "--installed", "--json"], cwd=directory,
                                    text=True, capture_output=True)
        require(result.returncode == 0, "Cannot inspect installed mise versions")
        parsed = json.loads(result.stdout)
        return {name: [entry["version"] for entry in entries] for name, entries in parsed.items()}

    def install_packages(self, native, aur, non_interactive=False):
        if self.fixture is not None:
            self.fixture["packages"] = sorted(set(self.fixture.get("packages", [])) | set(native + aur))
            self.fixture.setdefault("operations", []).append(["packages", native, aur])
            if "mise-bin" in native:
                self.fixture.setdefault("commands", []).append("mise")
            self.save_fixture()
            return
        if native:
            # No -Sy/partial upgrade and no whole-machine upgrade hidden in bootstrap.
            sudo = ["sudo", "-n"] if non_interactive else ["sudo"]
            flags = ["--noconfirm"] if non_interactive else []
            subprocess.run([*sudo, "pacman", "-S", "--needed", *flags, "--", *native], check=True)
        if aur:
            # Building AUR packages executes PKGBUILD code; retain helper review prompts.
            helper = next((tool for tool in ("yay", "paru") if self.available(tool)), None)
            require(helper, "Selected AUR packages need an existing yay/paru; installer does not bootstrap it")
            subprocess.run([helper, "-S", "--needed", "--", *aur], check=True)

    def install_tools(self, pins):
        if self.fixture is not None:
            self.fixture.setdefault("tools", {}).update({k: [v] for k, v in pins.items()})
            self.fixture.setdefault("operations", []).append(["tools", pins])
            self.save_fixture()
            return
        with tempfile.TemporaryDirectory(prefix="omarchy-dotfiles-tools-") as directory:
            subprocess.run(["mise", "install", *[f"{k}@{v}" for k, v in pins.items()]], cwd=directory, check=True)

    def save_fixture(self):
        atomic_write(self.fixture_path, json.dumps(self.fixture, indent=2).encode())


def select(repo, args, title, rows):
    print(title, flush=True)
    if not rows:
        return []
    values = [f"{key}\t{label}" for key, label in rows]
    require(all("\n" not in row for row in values), "Selector labels must be single-line")
    proc = subprocess.run(["bash", str(repo / "scripts/lib/select.sh"), args.ui, *values],
                          text=True, stdout=subprocess.PIPE)
    require(proc.returncode == 0, "Selection cancelled or invalid; no installation")
    chosen = list(dict.fromkeys(proc.stdout.splitlines()))
    require(set(chosen) <= {key for key, _ in rows}, "Selector returned unknown IDs")
    return chosen


def get_selection(inv, env, args):
    repo = inv.repo
    saved = {}
    profile = args.profile
    if args.replay:
        path = target_path(env.home, ".config/omarchy-dotfiles/selections.toml")
        saved = load(path)
        profile = saved["profile_id"]
    elif profile not in (None, "minimal", "custom"):
        require(identifier(profile), "Unsafe profile ID")
        profile_root = repo / "hosts" / profile
        require(not profile_root.is_symlink() and profile_root.resolve().is_relative_to(repo / "hosts"), "Unsafe profile directory")
        path = profile_root / "profile.toml"
        require(not path.is_symlink(), "Profile symlink refused")
        saved = load(path)
        require(saved.get("profile_id") == profile, "Profile directory/ID mismatch")
    elif profile is None:
        if args.minimal:
            profile = "minimal"
        else:
            require(not args.non_interactive, "Non-interactive mode requires --profile, --minimal or --replay")
            rows = [("minimal", "Minimal components; all default plugins"), ("custom", "Choose workstation components")]
            rows.extend((p.parent.name, "Saved machine profile") for p in sorted((repo / "hosts").glob("*/profile.toml")))
            chosen = select(repo, args, "2. Machine profile (select exactly one)", rows)
            require(len(chosen) == 1, "Choose exactly one machine profile")
            args.profile = chosen[0]
            return get_selection(inv, env, args)
    require(not (args.minimal and profile != "minimal"), "--minimal conflicts with a non-minimal profile")
    if saved:
        require(saved.get("schema_version") == 1, "Unsupported profile schema")
        require(not args.all, "--all cannot silently override a saved profile; use --profile custom")
        if saved.get("manifest_digest"):
            require(saved["manifest_digest"] == inv.digest, "Saved profile manifest/config digest changed; review and re-save deliberately")
    steps = csv(args.only) if args.only is not None else saved.get("steps", sorted(STEPS))
    require(isinstance(steps, list) and bool(steps) and set(steps) <= STEPS, "Invalid installation steps")
    print("2. Machine profile:", profile)
    if args.components is not None:
        components = csv(args.components)
    elif "components" in saved:
        components = saved["components"]
    elif profile == "minimal":
        # Core workflow bindings launch both configured browsers; include
        # those explicit browser components even in the minimal profile.
        components = [key for key in ("system", "kitty", "cli", "brave", "zen", "workflow") if key in inv.components]
    elif args.all:
        components = list(inv.components)
    else:
        require(not args.non_interactive, "Custom non-interactive profile needs explicit components")
        base = [key for key, item in inv.components.items() if item["default"]]
        components = base + select(repo, args, "3. Packages: base=" + ",".join(base) + "; select optional components",
                                   [(k, i["name"] + " [" + i["category"] + "]") for k, i in inv.components.items() if not i["default"]])
    require(isinstance(components, list) and set(components) <= set(inv.components), "Unknown component selection")
    print("3. Package components:", ", ".join(components) or "none")
    host_plugins = saved.get("host_plugins", [])
    require(isinstance(host_plugins, list), "host_plugins must be an array")
    require(all(pid in inv.plugins and inv.plugins[pid].get("install_policy") == "host" for pid in host_plugins),
            "Profile host_plugins must contain only host-policy IDs")
    defaults = [k for k, i in inv.plugins.items() if i.get("install_policy") == "default"]
    pending = [k for k, i in inv.plugins.items() if i.get("install_policy", "undecided") == "undecided"]
    if "plugins" in steps:
        require(not pending, "Undecided plugin policies must be resolved before plugin installation: " + ", ".join(pending))
    if "plugins" not in steps:
        optional = []
    elif args.optional_plugins is not None:
        optional = csv(args.optional_plugins)
    elif "optional_plugins" in saved:
        optional = saved["optional_plugins"]
    elif profile == "minimal":
        optional = []
    elif args.all:
        optional = [k for k, i in inv.plugins.items() if i.get("install_policy") == "optional"]
    else:
        require(not args.non_interactive, "Non-interactive custom selection needs optional_plugins, even if empty")
        optional = select(repo, args, "4. Optional plugins", [(k, i["name"] + ": " + i["description"])
                          for k, i in inv.plugins.items() if i.get("install_policy") == "optional"])
    require(isinstance(optional, list) and all(k in inv.plugins and inv.plugins[k].get("install_policy") == "optional"
                                             for k in optional), "Optional selection contains excluded, host, default or unknown plugin")
    selected_plugins = sorted(set(defaults + host_plugins + optional)) if "plugins" in steps else []
    print("4. Plugins:", ", ".join(selected_plugins) or "component skipped")
    if "themes" not in steps:
        themes = []
    elif args.themes is not None:
        themes = csv(args.themes)
    elif "themes" in saved:
        themes = saved["themes"]
    elif profile == "minimal":
        themes = []
    else:
        require(not args.non_interactive, "Non-interactive profile needs explicit themes (none is valid)")
        themes = select(repo, args, "5. Theme sources (no activation)",
                        [(k, k + " [" + i["status"] + "]") for k, i in inv.themes.items()])
    require(isinstance(themes, list) and set(themes) <= set(inv.themes), "Unknown themes")
    print("5. Themes:", ", ".join(themes) or "none")
    host_files = saved.get("files", [])
    require(isinstance(host_files, list), "Host files must be an explicit array")
    profile_root = repo / "hosts" / profile
    overlay_digest = hashlib.sha256()
    for name in ("packages.pacman.txt", "packages.aur.txt"):
        path = profile_root / name
        require(not path.is_symlink(), "Host package list symlink refused")
        if path.exists():
            overlay_digest.update(name.encode() + b"\0" + path.read_bytes())
    for rel in sorted(host_files):
        safe_path(rel)
        source = profile_root / "home" / rel
        require(not source.is_symlink() and source.resolve().is_relative_to(profile_root / "home") and source.is_file(),
                "Missing/unsafe host overlay file: " + rel)
        safe_content(source.read_bytes(), rel, portable=True)
        overlay_digest.update(rel.encode() + b"\0" + source.read_bytes())
    profile_digest = overlay_digest.hexdigest()
    if saved.get("profile_digest"):
        require(saved["profile_digest"] == profile_digest, "Host overlay/package digest changed; review profile deliberately")
    source_tool_ids = (sorted({source_id for component_id in components
                               for source_id in inv.components[component_id].get("source_tools", [])})
                       if "tools" in steps else [])
    selection = {"schema_version": 1, "profile_id": profile, "manifest_digest": inv.digest,
                 "profile_digest": profile_digest,
                 "components": sorted(set(components)), "optional_plugins": sorted(set(optional)),
                 "themes": sorted(set(themes)), "steps": sorted(set(steps)), "host_plugins": sorted(set(host_plugins)),
                 "compatibility_override": bool(args.allow_incompatible),
                 "files": host_files,
                 "plugin_revisions": {key: inv.plugins[key].get("tested_revision", "") for key in selected_plugins},
                 "source_tool_revisions": {key: inv.source_tools[key]["tested_revision"] for key in source_tool_ids}}
    for key, revision in saved.get("plugin_revisions", {}).items():
        require(key in inv.plugins and revision == inv.plugins[key]["tested_revision"], f"Saved pin mismatch: {key}")
    for key, revision in saved.get("source_tool_revisions", {}).items():
        require(key in inv.source_tools and revision == inv.source_tools[key]["tested_revision"], f"Saved source tool pin mismatch: {key}")
    selection["selected_plugins"] = selected_plugins
    selection["host_files"] = host_files
    return selection


class Plan:
    def __init__(self, inv, env, args, selection):
        self.inv, self.env, self.args, self.selection = inv, env, args, selection
        self.files, self.sources, self.blockers, self.requirements = [], [], [], []
        self.payload_hashes = {}
        self.native, self.aur, self.pins = [], [], {}
        self.existing = env.installed()
        versions = env.versions()
        self.mismatches = [f"{key}: installed {versions.get(key, 'missing')}, tested {value}"
                           for key, value in inv.compat["desktop"].items() if versions.get(key) != value]
        require("omarchy" in self.existing, "Requires an existing Omarchy installation, not bare Arch")
        if self.mismatches and not args.allow_incompatible:
            if args.non_interactive or args.dry_run:
                self.blockers.append("Compatibility mismatch; review then explicitly use --allow-incompatible: " + "; ".join(self.mismatches))
            else:
                print("WARNING:", "; ".join(self.mismatches))
                require(input("Type accept-compatibility-risk to proceed: ").strip() == "accept-compatibility-risk", "Compatibility not accepted")
                selection["compatibility_override"] = True
        self.build()

    def add_file(self, source, rel):
        safe_path(rel)
        require(source.is_file() and not source.is_symlink(), f"Invalid config source: {source}")
        safe_content(source.read_bytes(), rel, portable=True)
        target = target_path(self.env.home, rel)
        require(not target.exists() or target.is_file(), f"Config destination is not a regular file: {rel}")
        expected = hash_file(target) if target.exists() else None
        if expected == hash_file(source):
            return
        if expected:
            safe_content(target.read_bytes(), rel)
            if not self.args.conflicts == "backup":
                self.blockers.append(f"Configuration conflict: {rel}; review then use --conflicts backup")
        require(not any(item[1] == rel for item in self.files), f"Duplicate destination: {rel}")
        self.files.append((source, rel, expected))
        self.payload_hashes[rel] = hash_file(source)

    def add_source(self, kind, item):
        key = item["id"] if kind in ("plugin", "source_tool") else item["slug"]
        upstream = item.get("canonical_upstream", "") if kind == "plugin" else item.get("upstream", "")
        revision = item.get("tested_revision", "") if kind != "theme" else item.get("desired_revision", "")
        status = item.get("reproducibility", "") if kind == "plugin" else item.get("status", "")
        if status.startswith("blocked") or not remote_valid(upstream, self.env.fixture is not None) or not isinstance(revision, str) or len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
            self.blockers.append(f"Unreproducible {kind}: {key} ({status}); canonical immutable pin required")
            return
        rel = (item["install_path"] if kind == "source_tool" else
               f".config/omarchy/{'plugins' if kind == 'plugin' else 'themes'}/{key}")
        target = target_path(self.env.home, rel)
        if target.exists():
            checkout_status(target, upstream, revision, key if kind == "plugin" else None)
        else:
            self.sources.append((rel, upstream, revision, key if kind == "plugin" else None))
        if kind == "plugin" and item.get("credential_dependency") != "none-identified":
            self.requirements.append(key + ": machine-local setup required: " + item.get("credential_dependency", "review"))

    def build(self):
        inv, selection = self.inv, self.selection
        steps = set(selection["steps"])
        comps = selection["components"]
        requested = {kind: [] for kind in ("pacman", "aur")}
        for key in comps:
            for kind in requested:
                requested[kind] += inv.components[key][kind]
        profile_root = inv.repo / "hosts" / selection["profile_id"]
        if profile_root.exists():
            require(not profile_root.is_symlink(), "Host profile directory symlink refused")
            for kind in requested:
                package_path = profile_root / f"packages.{kind}.txt"
                require(not package_path.is_symlink(), "Host package list symlink refused")
                requested[kind] += packages(package_path)
        if "packages" in steps:
            require(not set(requested["pacman"]) & set(requested["aur"]), "Native/AUR package classification conflict")
            self.native = sorted(set(requested["pacman"]) - self.existing)
            self.aur = sorted(set(requested["aur"]) - self.existing)
            if self.native and not self.env.available("sudo"):
                self.blockers.append("Missing sudo for native package installation")
            if self.aur and not any(self.env.available(k) for k in ("yay", "paru")):
                self.blockers.append("Selected AUR packages need existing yay/paru; no helper is installed automatically")
            if self.args.non_interactive and self.aur:
                self.blockers.append("AUR builds require interactive source review; provision reviewed AUR packages separately before --non-interactive")
        if "config" in steps:
            for area in inv.deploy["area"]:
                if area["component"] in comps:
                    root = inv.repo / "home" / safe_path(area["source"])
                    require(root.resolve().is_relative_to(inv.repo / "home"), "Config source escapes repository home")
                    for source in files_under(root):
                        self.add_file(source, str(source.relative_to(inv.repo / "home")))
            for rel in selection["host_files"]:
                safe_path(rel)
                require(rel.startswith(".config/hypr/") or rel.startswith(".config/systemd/user/"), "Host file outside approved overlay contract")
                require(profile_root.exists(), "Host overlay source missing")
                if rel.startswith(".config/hypr/"):
                    self.blockers.append("Host Hyprland overlay held for Lua/conf include-contract review: " + rel)
                    continue
                source = profile_root / "home" / rel
                require(source.resolve().is_relative_to(profile_root / "home"), "Host source escapes overlay")
                self.add_file(source, rel)
                self.requirements.append("Host unit copied but not enabled: " + rel)
        if "plugins" in steps:
            for key in selection["selected_plugins"]:
                self.add_source("plugin", inv.plugins[key])
            self.requirements.append("Plugin sources only: reviewed shell layout/activation and notification owner remain separate gates")
        if "themes" in steps:
            for key in selection["themes"]:
                self.add_source("theme", inv.themes[key])
            if selection["themes"]:
                self.requirements.append("Themes installed as pinned sources; activation/regeneration is explicit, never automatic")
        if "tools" in steps:
            source_tools = sorted({source_id for component_id in comps
                                   for source_id in inv.components[component_id].get("source_tools", [])})
            for key in source_tools:
                self.add_source("source_tool", inv.source_tools[key])
            if "development" in comps:
                installed = self.env.tools()
                self.pins = {key: pin for key, pin in inv.tool_pins.items() if pin not in installed.get(key, [])}
                if self.pins and not self.env.available("mise") and "mise-bin" not in self.native:
                    self.blockers.append("Pinned tools need mise or selected native mise-bin installation")
        if self.sources and not self.env.available("git"):
            self.blockers.append("Git is required for source staging before any package installation")
        if self.args.save_profile:
            require(identifier(self.args.save_profile) and self.args.save_profile not in ("minimal", "custom"), "Invalid saved profile ID")
            require(not selection["host_files"] and not selection["host_plugins"], "Export hardware profile in place; copying its overlay under a new ID is not automatic")
            destination = inv.repo / "hosts" / self.args.save_profile
            require(not destination.exists(), "Saved profile already exists; refusing overwrite")

    def show(self):
        print("6. Configuration plan")
        print("Native packages to install:", ", ".join(self.native) or "none")
        print("AUR packages to review/install:", ", ".join(self.aur) or "none")
        print("Pinned tools to install:", self.pins or "none")
        for source, rel, before in self.files:
            print("BACKUP+COPY" if before else "COPY", rel)
        for rel, _, revision, _ in self.sources:
            print("CLONE TESTED REVISION", rel, revision)
        if self.args.save_profile:
            print("SAVE PORTABLE PROFILE", self.args.save_profile)
        for message in self.requirements:
            print("SETUP:", message)
        for message in self.mismatches:
            print("COMPATIBILITY:", message)
        for message in self.blockers:
            print("BLOCKER:", message)
        print("No package removal, service changes, shell reloads, symlinks or theme activation.")
        print("Backups/journal: ~/.local/state/omarchy-dotfiles/backups/<run-id>/")

    def apply(self):
        home, selection = self.env.home, self.selection
        state = target_path(home, ".local/state/omarchy-dotfiles")
        state.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock_path = target_path(home, ".local/state/omarchy-dotfiles/install.lock")
        with lock_path.open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise Failure("Another installer is running") from exc
            with tempfile.TemporaryDirectory(prefix="omarchy-dotfiles-stage-", dir=state) as directory:
                staged = []
                for index, (rel, upstream, revision, pid) in enumerate(self.sources):
                    path = Path(directory) / str(index)
                    stage_checkout(path, upstream, revision, pid)
                    staged.append((path, rel, upstream, revision, pid))
                transaction = Transaction(home)
                try:
                    require(Inventory(self.inv.repo).digest == self.inv.digest, "Repository policy/payload changed after planning")
                    for source, rel, expected in self.files:
                        require(hash_file(source) == self.payload_hashes[rel], f"Source payload changed after planning: {rel}")
                        target = target_path(home, rel)
                        actual = hash_file(target) if target.is_file() else None
                        require(actual == expected, f"Configuration changed after planning: {rel}")
                    print("8. Installation")
                    if self.native or self.aur:
                        self.env.install_packages(self.native, self.aur, self.args.non_interactive)
                    if self.pins:
                        self.env.install_tools(self.pins)
                    for source, rel, expected in self.files:
                        transaction.copy(source, rel, expected)
                    for path, rel, upstream, revision, pid in staged:
                        transaction.place_checkout(path, rel, upstream, revision, pid)
                    self.verify()
                    # Selections are application state, not agent/Omarchy runtime state.
                    text = toml_selection(selection)
                    record_rel = ".config/omarchy-dotfiles/selections.toml"
                    record = target_path(home, record_rel)
                    with tempfile.TemporaryDirectory(prefix="omarchy-dotfiles-record-") as scratch:
                        source = Path(scratch) / "selection.toml"
                        source.write_text(text)
                        source.chmod(0o600)
                        if not record.exists() or record.read_text() != text:
                            transaction.copy(source, record_rel, hash_file(record) if record.exists() else None)
                    if self.args.save_profile:
                        exported = dict(selection, profile_id=self.args.save_profile)
                        path = self.inv.repo / "hosts" / self.args.save_profile / "profile.toml"
                        atomic_write(path, toml_selection(exported).encode(), 0o644)
                        print("Saved portable profile:", path)
                    transaction.finish("complete")
                except Exception:
                    transaction.finish("failed")
                    raise

    def verify(self):
        print("9. Verification")
        for source, rel, _ in self.files:
            require(hash_file(target_path(self.env.home, rel)) == hash_file(source), f"Config verification failed: {rel}")
        for key in self.selection["selected_plugins"]:
            item = self.inv.plugins[key]
            checkout_status(target_path(self.env.home, f".config/omarchy/plugins/{key}"),
                            item["canonical_upstream"], item["tested_revision"], key)
        for key in self.selection["themes"]:
            item = self.inv.themes[key]
            checkout_status(target_path(self.env.home, f".config/omarchy/themes/{key}"), item["upstream"], item["desired_revision"])
        for key, revision in self.selection["source_tool_revisions"].items():
            item = self.inv.source_tools[key]
            path = target_path(self.env.home, item["install_path"])
            checkout_status(path, item["upstream"], revision)
            require((path / item["entrypoint"]).is_file(), f"Source tool entry point missing: {key}")
        require(set(self.native + self.aur) <= self.env.installed(), "Package verification failed")
        if self.pins:
            installed = self.env.tools()
            require(all(pin in installed.get(key, []) for key, pin in self.pins.items()), "Tool pin verification failed")
        print("Selected payload/source/package/tool verification passed; desktop activation not attempted.")


def doctor(inv, env, args):
    issues = []
    print("Manifest consistency: valid")
    versions = env.versions()
    for key, version in inv.compat["desktop"].items():
        if versions.get(key) != version:
            issues.append(f"Compatibility: {key}: {versions.get(key, 'missing')} vs tested {version}")
    for key in ("git", "pacman", "omarchy-shell", "hyprctl", "quickshell"):
        if not env.available(key):
            issues.append("Missing required command: " + key)
    for plugin in inv.plugins.values():
        if plugin.get("install_policy") == "undecided" or plugin.get("selection_status") == "undecided":
            issues.append("Undecided plugin: " + plugin["id"])
        if plugin.get("install_policy") == "default" and not plugin.get("tested_revision"):
            issues.append("Default plugin has unresolved source pin: " + plugin["id"])
    record = target_path(env.home, ".config/omarchy-dotfiles/selections.toml")
    if record.exists():
        args.replay = True
        args.non_interactive = True
        selection = get_selection(inv, env, args)
        plan = Plan(inv, env, args, selection)
        issues.extend(plan.blockers)
        if plan.native or plan.aur:
            issues.append("Selected packages missing: " + ", ".join(plan.native + plan.aur))
        if plan.files:
            issues.append("Selected configuration differs/missing: " + ", ".join(x[1] for x in plan.files))
        if plan.sources:
            issues.append("Selected pinned sources missing: " + ", ".join(x[0] for x in plan.sources))
        if plan.pins:
            issues.append("Selected mise pins missing: " + str(plan.pins))
    else:
        issues.append("No applied selection record; no complete installation to verify")
    for area in inv.deploy["area"]:
        root = env.home / safe_path(area["source"])
        if root.is_symlink() and not root.exists():
            issues.append("Broken configuration link: " + area["source"])
        if root.is_dir() and not root.is_symlink():
            for path in root.rglob("*"):
                if path.is_symlink() and not path.exists():
                    issues.append("Broken configuration link: " + str(path.relative_to(env.home)))
    shell_path = target_path(env.home, ".config/omarchy/shell.json")
    if shell_path.exists():
        shell = json.loads(shell_path.read_text())
        if shell.get("version") != inv.compat["contract"]["shell_config_version"]:
            issues.append("Shell configuration schema differs from tested contract")
        disabled = shell.get("disabledPlugins", [])
        active = set()
        def collect(value):
            if isinstance(value, dict):
                if "id" in value:
                    active.add(value["id"])
                for child in value.values():
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)
        collect(shell)
        active -= set(disabled)
        for key in active:
            if key in inv.plugins and inv.plugins[key].get("install_policy") == "exclude":
                issues.append("Shell references excluded plugin: " + key)
            elif key not in inv.plugins and not key.startswith("omarchy."):
                issues.append("Shell references plugin outside lock inventory: " + key)
        if "njpatel.omapager" in active and "omarchy.notifications" not in disabled:
            issues.append("Notification ownership conflict: Omapager and stock notifications may both run")
    if (env.home / ".config/hypr/hyprland.lua").exists() and inv.compat["contract"].get("hyprland_config_format") == "conf-includes":
        issues.append("Installed Hyprland uses Lua; recorded conf-includes contract needs review")
    print("Desktop runtime/IPC and Lua/conf include compatibility require a real session; not inferred from versions.")
    for issue in issues:
        print("ISSUE:", issue)
    require(not issues, "Doctor found unresolved requirements (see above)")
    print("Doctor passed for the applied component scope.")


def main():
    parser = argparse.ArgumentParser(description="Omarchy Dotfiles: plan first, explicit confirmation, pinned sources")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reproduce", action="store_true", help="Apply a saved profile using its tested revisions")
    parser.add_argument("--minimal", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--profile")
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--components", help="Comma-separated IDs; none means explicit empty")
    parser.add_argument("--optional-plugins", help="Comma-separated optional IDs or none")
    parser.add_argument("--themes", help="Comma-separated source slugs or none")
    parser.add_argument("--only", help="Comma-separated packages,config,plugins,themes,tools")
    parser.add_argument("--conflicts", choices=("abort", "backup"), default="abort")
    parser.add_argument("--allow-incompatible", action="store_true")
    parser.add_argument("--save-profile", metavar="ID")
    parser.add_argument("--ui", choices=("auto", "bash"), default="auto")
    parser.add_argument("--doctor", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--rollback", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("run_id", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--fixture", metavar="TMP_DIRECTORY", help="Isolated tests only: explicit fixture marker; mocked packages/tools")
    args = parser.parse_args()
    if args.reproduce:
        require(not (args.minimal or args.all or args.replay or args.components is not None or
                     args.optional_plugins is not None or args.themes is not None or args.only is not None or
                     args.save_profile), "--reproduce uses a complete profile and cannot take selection overrides")
        args.profile = args.profile or "workstation"
        args.non_interactive = True
    require(not (args.minimal and args.all), "--minimal and --all conflict")
    require(not (args.replay and (args.profile or args.components or args.optional_plugins or args.themes or args.all or args.minimal)),
            "--replay cannot be combined with selection overrides")
    require(not (args.doctor and args.rollback), "Doctor and rollback conflict")
    repo = Path(__file__).resolve().parents[2]
    env = Environment(args)
    if args.rollback:
        require(args.run_id is not None, "Rollback requires a run ID")
        lock_path = target_path(env.home, ".local/state/omarchy-dotfiles/install.lock")
        with lock_path.open("r") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise Failure("Installer/rollback already running") from exc
            rollback(env.home, args.run_id, args.dry_run)
        return
    require(args.run_id is None, "Unexpected positional argument")
    inv = Inventory(repo)
    if args.doctor:
        doctor(inv, env, args)
        return
    print("Omarchy Dotfiles\n1. Environment check")
    require(args.non_interactive or args.dry_run or sys.stdin.isatty() or env.fixture is not None,
            "No interactive terminal; use --non-interactive with explicit decisions")
    selection = get_selection(inv, env, args)
    plan = Plan(inv, env, args, selection)
    plan.show()
    require(not plan.blockers, "Preflight blocked; no deployment or package/tool installation performed")
    if args.dry_run:
        print("Dry run: no writes, clones, package/tool installation or saved selections.")
        return
    if args.non_interactive:
        print("7. Confirmation: explicit non-interactive plan")
    else:
        require(input("7. Type install to apply this plan: ").strip() == "install", "Not confirmed")
    plan.apply()


if __name__ == "__main__":
    try:
        main()
    except (Failure, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    except (KeyboardInterrupt, EOFError):
        print("Cancelled; inspect any printed rollback journal if application had started.", file=sys.stderr)
        sys.exit(130)
