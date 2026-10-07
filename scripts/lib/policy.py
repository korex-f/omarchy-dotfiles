"""Strict policy parsing and payload checks; no deployment side effects."""
import hashlib
import json
import re
import tomllib
from pathlib import Path
from urllib.parse import urlsplit


class Failure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Failure(message)


def load(path):
    try:
        return tomllib.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        raise Failure(f"Cannot parse {path}: {exc}") from exc


def identifier(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value)) and ".." not in value


def relative(value):
    require(isinstance(value, str) and value and "\n" not in value, "Invalid relative path")
    path = Path(value)
    require(not path.is_absolute() and ".." not in path.parts, f"Unsafe path: {value}")
    return path


DENIED = {".ssh", ".gnupg", ".aws", ".pki", ".docker", ".codex", ".claude", ".mozilla",
          ".cache", "cache", "caches", "bravesoftware", "zen", "profiles", "cookies", "history",
          "sessions", "archived_sessions", "credentials", ".credentials.json", "auth.json", "machine-id"}
SECRET = re.compile(rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY(?: BLOCK)?-----|(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{30,}|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{30,}|AKIA[0-9A-Z]{16}|https?://[^/@\s]+:[^/@\s]+@|(?i:password|access_token|api_key|secret)[\"']?\s*[=:]\s*[\"']?[A-Za-z0-9_+/=-]{16,}")


def safe_path(value):
    path = relative(value)
    lowered = [part.lower() for part in path.parts]
    require(not any(part in DENIED or part.startswith((".env", "id_rsa", "id_ed25519", "id_ecdsa")) or
                    ".bak." in part or part.endswith((".pem", ".key", ".sqlite", ".sqlite3", ".db", "-wal", "-shm", ".wal", ".shm", ".bak"))
                    for part in lowered), f"Sensitive/runtime path refused: {value}")
    text = "/".join(lowered)
    require(".local/state/omarchy/" not in text + "/" and
            ".config/omarchy/current" not in text and
            ".local/share/uv" not in text and ".local/share/mise" not in text,
            f"Generated/credential path refused: {value}")
    return path


def safe_content(data, label, portable=False):
    require(not SECRET.search(data), f"Possible secret/private key in {label}; refusing to copy/back up")
    if portable:
        require(not re.search(rb"/home/[^\s/\"']+|/Users/[^\s/\"']+", data),
                f"Absolute machine home path in {label}")


def files_under(root):
    require(not root.is_symlink(), f"Source symlink refused: {root}")
    require(root.exists(), f"Source missing: {root}")
    paths = [root] if root.is_file() else sorted(root.rglob("*"))
    for path in paths:
        require(not path.is_symlink(), f"Source symlink refused: {path}")
        if path.is_file() and path.name not in ("README.md", "LICENSE", ".gitignore"):
            yield path


def packages(path):
    if not path.exists():
        return []
    result = [line.split("#", 1)[0].strip() for line in path.read_text().splitlines()]
    result = [line for line in result if line]
    require(all(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9@+_.-]*", p) for p in result),
            f"Invalid package name in {path}")
    require(len(set(result)) == len(result), f"Duplicate packages in {path}")
    return result


def remote_valid(value, fixture=False):
    if fixture and isinstance(value, str) and value.startswith("file:///tmp/"):
        return True
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return (parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and
            not parsed.password and not parsed.query and not parsed.fragment and
            not any(c.isspace() for c in value))


class Inventory:
    def __init__(self, repo):
        self.repo = repo
        self.plugins_doc = load(repo / "manifests/plugins.lock.toml")
        self.themes_doc = load(repo / "manifests/themes.lock.toml")
        self.source_tools_doc = load(repo / "manifests/source-tools.lock.toml")
        self.compat = load(repo / "manifests/compatibility.toml")
        self.components_doc = load(repo / "manifests/components.toml")
        self.deploy = load(repo / "manifests/deployment.toml")
        for doc in (self.themes_doc, self.source_tools_doc, self.compat, self.components_doc, self.deploy):
            require(doc.get("schema_version") == 1, "Unsupported manifest schema")
        require(self.plugins_doc.get("schema_version") in (1, 2), "Unsupported plugin manifest schema")
        plugin_items = []
        for original in self.plugins_doc.get("plugin", []):
            item = dict(original)
            # Schema 1 profiles and fixture manifests keep working during migration.
            item.setdefault("tested_revision", item.get("desired_revision", ""))
            item.setdefault("tracking_ref", "")
            item.setdefault("update_policy", "disabled" if item.get("install_policy") == "exclude" else "check")
            plugin_items.append(item)
        self.plugins = self.index(plugin_items, "id")
        self.themes = self.index(self.themes_doc.get("theme", []), "slug")
        self.source_tools = self.index(self.source_tools_doc.get("source_tool", []), "id")
        self.components = self.index(self.components_doc.get("component", []), "id")
        require(self.compat.get("dotfiles_schema_version") == 1, "Unsupported dotfiles schema")
        for key in ("omarchy", "quickshell", "hyprland"):
            require(isinstance(self.compat.get("desktop", {}).get(key), str), f"Missing compatibility {key}")
        for item in self.plugins.values():
            policy = item.get("install_policy", "undecided")
            require(policy in ("default", "optional", "host", "exclude", "undecided"), "Unknown plugin policy")
            require(item.get("selection_status") in ("decided", "undecided"), "Missing selection status")
            require((policy == "undecided") == (item["selection_status"] == "undecided"), "Inconsistent plugin decision")
            require(not item["id"].startswith("omarchy."), "Stock plugins must stay Omarchy-managed")
            require(item.get("update_policy") in ("check", "disabled"), "Unknown plugin update policy")
            require((policy == "exclude") == (item["update_policy"] == "disabled"), "Plugin update policy conflicts with install policy")
            revision = item.get("tested_revision", "")
            require(not revision or (isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}", revision)), "Invalid tested plugin revision")
            require(not item.get("tracking_ref") or item["tracking_ref"].startswith("refs/heads/") or item["tracking_ref"].startswith("refs/tags/"), "Invalid plugin tracking ref")
            if policy in ("default", "optional", "host") and item.get("canonical_upstream"):
                require(bool(revision), "Managed plugin needs tested_revision")
                if self.plugins_doc.get("schema_version") == 2:
                    require(bool(item.get("tracking_ref")), "Managed plugin needs tracking_ref")
        for item in self.source_tools.values():
            require(item.get("update_policy") in ("check", "disabled"), "Unknown source tool update policy")
            require(bool(re.fullmatch(r"[0-9a-f]{40}", item.get("tested_revision", ""))), "Source tool needs a tested revision")
            require(item.get("tracking_ref", "").startswith(("refs/heads/", "refs/tags/")), "Source tool needs a tracking ref")
            safe_path(item["install_path"])
            relative(item["entrypoint"])
        self.tool_pins = load(repo / "home/.config/mise/config.toml")["tools"]
        require(all(identifier(k) and isinstance(v, str) and re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", v)
                    for k, v in self.tool_pins.items()), "Tool versions must be explicit pins, never latest")
        for kind in ("pacman", "aur"):
            found = []
            for component in self.components.values():
                require(isinstance(component.get("default"), bool), "Component default must be Boolean")
                require(isinstance(component.get(kind), list), "Component packages must be arrays")
                found.extend(component[kind])
            expected = packages(repo / f"manifests/packages.{kind}.txt")
            require(len(set(found)) == len(found) and set(found) == set(expected),
                    f"Component coverage does not match packages.{kind}.txt")
        for area in self.deploy.get("area", []):
            safe_path(area["source"])
            require(area["component"] in self.components, "Unknown deployment component")
            require(not any(relative(area["source"]).is_relative_to(relative(path))
                            for path in self.deploy.get("quarantine", {}).get("paths", [])), "Quarantined payload")
        source_components = [source_id for component in self.components.values()
                             for source_id in component.get("source_tools", [])]
        require(len(source_components) == len(set(source_components)) and set(source_components) <= set(self.source_tools),
                "Unknown or multiply-owned source tool")
        require(set(source_components) == set(self.source_tools), "Every source tool must have one package component owner")
        digest = hashlib.sha256()
        for path in sorted((repo / "manifests").glob("*")):
            if path.is_file():
                digest.update(path.name.encode() + b"\0" + path.read_bytes())
        for path in sorted((repo / "home").rglob("*")):
            if path.is_file() and not path.is_symlink():
                digest.update(str(path.relative_to(repo)).encode() + b"\0" + path.read_bytes())
        self.digest = digest.hexdigest()

    @staticmethod
    def index(items, key):
        require(isinstance(items, list), f"{key} inventory must be an array")
        result = {}
        for item in items:
            require(identifier(item.get(key)), f"Unsafe/missing {key}")
            require(item[key] not in result, f"Duplicate {key}: {item[key]}")
            result[item[key]] = item
        return result


def toml_selection(selection):
    # JSON strings/arrays are a valid subset of TOML; no shell interpolation.
    lines = []
    for key in ("schema_version", "profile_id", "manifest_digest", "profile_digest", "components", "optional_plugins",
                "themes", "steps", "host_plugins", "files", "compatibility_override"):
        value = selection[key]
        lines.append(f"{key} = {str(value).lower() if isinstance(value, bool) else json.dumps(value)}")
    lines.append("\n[plugin_revisions]")
    lines.extend(f"{json.dumps(k)} = {json.dumps(v)}" for k, v in selection["plugin_revisions"].items())
    lines.append("\n[source_tool_revisions]")
    lines.extend(f"{json.dumps(k)} = {json.dumps(v)}" for k, v in selection.get("source_tool_revisions", {}).items())
    return "\n".join(lines) + "\n"
