"""Checked file copies, detached Git sources and guarded rollback journal."""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid

from policy import Failure, identifier, relative, require, safe_content, safe_path


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_path(home, value):
    rel = safe_path(value)
    target = home / rel
    require(target.is_relative_to(home), "Destination escapes target home")
    for parent in [target, *target.parents]:
        if parent == home.parent:
            break
        require(not parent.is_symlink(), f"Destination symlink refused: {parent}")
    return target


def atomic_write(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".dotfiles-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def git(*args, cwd=None):
    # Ignore inherited Git injection and disable hooks; never recurse submodules.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
    result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=cwd,
                            env=env, text=True, capture_output=True)
    require(result.returncode == 0, f"Git operation failed ({args[0]}): {result.stderr.strip()}")
    return result.stdout.strip()


def validate_plugin(path, expected):
    try:
        manifest = json.loads((path / "manifest.json").read_text())
    except (OSError, ValueError) as exc:
        raise Failure(f"Invalid plugin manifest for {expected}") from exc
    require(manifest.get("schemaVersion") == 1 and manifest.get("id") == expected,
            f"Plugin identity/schema mismatch: expected {expected}")
    require(all(key in manifest for key in ("name", "version", "kinds", "entryPoints")),
            f"Missing plugin metadata: {expected}")
    kinds, entries = manifest["kinds"], manifest["entryPoints"]
    require(isinstance(kinds, list) and bool(kinds) and isinstance(entries, dict), "Invalid kinds/entryPoints")
    required = {"bar": "bar", "bar-widget": "barWidget", "menu": "menu", "overlay": "overlay",
                "panel": "panel", "service": "service"}
    for kind in kinds:
        require(isinstance(kind, str), "Invalid plugin kind")
        if kind in required:
            require(required[kind] in entries, f"Missing entry point for {kind}")
    for value in entries.values():
        require(isinstance(value, str) and ".." not in value, "Unsafe entry point")
        ep = path / relative(value)
        require(ep.is_file() and not ep.is_symlink(), f"Missing/unsafe entry point {value}")
    section = manifest.get("barWidget", {}).get("defaultSection")
    require(section is None or section in ("left", "center", "right"), "Invalid bar section")


def validate_tree(path):
    for item in path.rglob("*"):
        if ".git" in item.relative_to(path).parts:
            continue
        require(not item.is_symlink(), f"Dependency source contains symlink: {item.name}")
        rel = item.relative_to(path)
        safe_path(str(rel))
        if item.is_file():
            safe_content(item.read_bytes(), str(rel))


def checkout_status(path, upstream, revision, plugin_id=None):
    require(path.is_dir() and (path / ".git").is_dir() and not (path / ".git").is_symlink(),
            f"Expected normal Git checkout: {path}")
    require(git("remote", "get-url", "origin", cwd=path) == upstream, f"Remote mismatch: {path}")
    require(not git("status", "--porcelain", "--untracked-files=all", cwd=path), f"Dirty checkout refused: {path}")
    require(git("rev-parse", "HEAD", cwd=path) == revision, f"Revision mismatch: {path}; manual review required")
    validate_tree(path)
    if plugin_id:
        validate_plugin(path, plugin_id)


def stage_checkout(staging, upstream, revision, plugin_id=None):
    git("clone", "--no-checkout", "--", upstream, str(staging))
    # A clone may not contain an orphaned pin. Fetch that exact object, never HEAD fallback.
    try:
        git("cat-file", "-e", revision + "^{commit}", cwd=staging)
    except Failure:
        git("fetch", "origin", revision, cwd=staging)
    git("checkout", "--detach", revision, cwd=staging)
    checkout_status(staging, upstream, revision, plugin_id)


class Transaction:
    def __init__(self, home):
        self.home = home
        self.root = target_path(home, ".local/state/omarchy-dotfiles/backups") / uuid.uuid4().hex
        self.root.mkdir(parents=True, mode=0o700)
        os.chmod(self.root, 0o700)
        self.entries = []
        self.status = "applying"
        self.flush()

    def flush(self):
        atomic_write(self.root / "journal.json", json.dumps({"schema_version": 1, "status": self.status,
                     "entries": self.entries}, indent=2).encode())

    def copy(self, source, rel, expected):
        target = target_path(self.home, rel)
        actual = hash_file(target) if target.is_file() else None
        require(actual == expected, f"Destination changed since plan: {rel}")
        data = source.read_bytes()
        safe_content(data, rel, portable=True)
        old_mode = (target.stat().st_mode & 0o777) if target.exists() else None
        if expected:
            safe_content(target.read_bytes(), rel)
            backup = self.root / "files" / safe_path(rel)
            atomic_write(backup, target.read_bytes(), old_mode)
        entry = {"kind": "file", "path": rel, "before": expected,
                 "after": hashlib.sha256(data).hexdigest(), "mode": old_mode}
        self.entries.append(entry)
        self.flush()  # Persist rollback data before replacement.
        atomic_write(target, data, source.stat().st_mode & 0o777)

    def place_checkout(self, source, rel, upstream, revision, plugin_id):
        target = target_path(self.home, rel)
        require(not target.exists(), f"Checkout appeared since plan: {rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        entry = {"kind": "checkout", "path": rel, "upstream": upstream,
                 "revision": revision, "plugin_id": plugin_id}
        self.entries.append(entry)
        self.flush()
        shutil.move(str(source), str(target))

    def finish(self, status):
        if status == "complete" and not self.entries:
            (self.root / "journal.json").unlink()
            self.root.rmdir()
            print("No changes; no rollback journal needed.")
            return
        self.status = status
        self.flush()
        print(f"Rollback journal: {self.root / 'journal.json'}")


def rollback(home, run_id, dry_run=False):
    require(identifier(run_id) and re_run_id(run_id), "Rollback requires a 32-character run ID")
    root = target_path(home, ".local/state/omarchy-dotfiles/backups/" + run_id)
    journal_path = root / "journal.json"
    require(not journal_path.is_symlink(), "Journal symlink refused")
    journal = json.loads(journal_path.read_text())
    require(journal.get("schema_version") == 1 and journal.get("status") != "rolled-back", "Invalid/already rolled-back journal")
    actions = []
    for entry in reversed(journal["entries"]):
        target = target_path(home, entry["path"])
        if entry["kind"] == "file":
            actual = hash_file(target) if target.is_file() else None
            # Interrupted before replacement: already at the original state.
            if actual == entry["before"]:
                continue
            require(actual == entry["after"], f"Rollback refuses subsequently edited file: {entry['path']}")
            if entry["before"]:
                backup = target_path(root / "files", entry["path"])
                require(not backup.is_symlink() and hash_file(backup) == entry["before"], "Backup integrity failure")
                safe_content(backup.read_bytes(), entry["path"])
            actions.append((entry, target))
        elif entry["kind"] == "checkout":
            if not target.exists():
                continue
            checkout_status(target, entry["upstream"], entry["revision"], entry["plugin_id"])
            actions.append((entry, target))
        else:
            raise Failure("Unknown rollback entry kind")
    for entry, target in actions:
        print("Rollback:", entry["path"])
        if dry_run:
            continue
        if entry["kind"] == "checkout":
            # Recoverable relocation, never recursive deletion of user checkouts.
            retired = target_path(root / "retired", entry["path"])
            retired.parent.mkdir(parents=True, exist_ok=True)
            require(not retired.exists(), "Retired checkout already exists")
            shutil.move(str(target), str(retired))
        elif entry["before"]:
            atomic_write(target, target_path(root / "files", entry["path"]).read_bytes(), entry["mode"])
        else:
            target.unlink()  # Only validated, unchanged, installer-created regular file.
    if not dry_run:
        journal["status"] = "rolled-back"
        atomic_write(journal_path, json.dumps(journal, indent=2).encode())
    print("Package/tool installs are not undone; backups and retired checkouts remain recoverable.")


def re_run_id(value):
    return len(value) == 32 and all(c in "0123456789abcdef" for c in value)
