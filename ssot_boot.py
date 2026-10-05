#!/usr/bin/env python3
"""ssot_boot.py: resolve, download, verify, cache and activate the canonical skill set.

Environment
  SSOT_REPO     owner/name of the public skills repo           (required)
  SSOT_REF      'stable' | 'next' | vX.Y.Z                      (default: stable)
  SSOT_HOME     cache directory                                 (default: ~/.ssot)
  SSOT_OFFLINE  set to 1 to skip the network and keep the active set

No tokens and no API calls: only raw.githubusercontent.com and codeload.github.com.
Python 3.8+ standard library only.
"""
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request

REPO = os.environ.get("SSOT_REPO", "")
REF = os.environ.get("SSOT_REF", "stable")
ROOT = pathlib.Path(os.environ.get("SSOT_HOME", "~/.ssot")).expanduser()
STORE, CUR = ROOT / "store", ROOT / "current"
TAG = re.compile(r"v\d+\.\d+\.\d+")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ssot-boot"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def resolve():
    """Return (tag, manifest_sha256_pin or None)."""
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", REPO):
        raise ValueError("SSOT_REPO must look like owner/name")
    if TAG.fullmatch(REF):
        return REF, None
    if not re.fullmatch(r"[a-z][a-z0-9-]*", REF):
        raise ValueError(f"bad SSOT_REF: {REF}")
    j = json.loads(get(f"https://raw.githubusercontent.com/{REPO}/main/channels/{REF}.json"))
    if not TAG.fullmatch(j["tag"]):
        raise ValueError(f"channel {REF} names a bad tag: {j['tag']}")
    return j["tag"], j["manifest_sha256"]


def inside(base, rel):
    base = pathlib.Path(base).resolve()
    p = (base / rel).resolve()
    if base not in p.parents:
        raise ValueError(f"path escapes tree: {rel}")
    return p


def verify(tree, pin):
    tree = pathlib.Path(tree)
    manifest = tree / "MANIFEST.json"
    if not manifest.is_file():
        raise ValueError("MANIFEST.json missing")
    if pin and sha256(manifest) != pin:
        raise ValueError("manifest does not match the channel pin")
    man = json.loads(manifest.read_text(encoding="utf-8"))
    for name, meta in man["skills"].items():
        for rel, want in meta["files"].items():
            f = inside(tree, f"skills/{name}/{rel}")
            if not f.is_file() or sha256(f) != want:
                raise ValueError(f"hash mismatch: {name}/{rel}")
    for rel, want in man.get("boot", {}).items():
        f = inside(tree, rel)
        if not f.is_file() or sha256(f) != want:
            raise ValueError(f"hash mismatch: {rel}")
    return man


def extract(tgz, dest):
    kw = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
    with tarfile.open(tgz) as t:
        for m in t.getmembers():
            parts = pathlib.PurePosixPath(m.name).parts
            if m.name.startswith("/") or ".." in parts or m.issym() or m.islnk():
                raise ValueError(f"unsafe archive member: {m.name}")
        t.extractall(dest, **kw)


def load(tag, pin):
    """Return (tree, manifest); reuse a verified cache entry or download a fresh one."""
    tree = STORE / tag
    if tree.exists():
        try:
            return tree, verify(tree, pin)
        except (ValueError, OSError, KeyError):
            shutil.rmtree(tree, ignore_errors=True)
    url = f"https://codeload.github.com/{REPO}/tar.gz/refs/tags/{tag}"
    with tempfile.TemporaryDirectory() as td:
        tgz = pathlib.Path(td) / "skills.tgz"
        tgz.write_bytes(get(url))
        extract(tgz, td)
        root = next(p for p in pathlib.Path(td).iterdir() if p.is_dir())
        man = verify(root, pin)
        shutil.move(str(root), str(tree))
    return tree, man


def index(tree, man, tag):
    lines = [
        f"# Active skill set {tag}",
        f"Skills root: {CUR}/skills",
        "Read <root>/<name>/SKILL.md before using a skill.",
        "",
    ]
    for name in sorted(man["skills"]):
        desc = man["skills"][name].get("description", "")
        lines.append(f"- {name}: {desc[:240]}")
    (pathlib.Path(tree) / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def activate(tree):
    tmp = ROOT / ".current.tmp"
    if tmp.is_symlink() or tmp.exists():
        tmp.unlink()
    tmp.symlink_to(tree)
    os.replace(tmp, CUR)  # atomic swap of the symlink


def self_update(tree, man):
    """Refresh the cached loader from the release, but only if its hash is in the manifest."""
    want = man.get("boot", {}).get("ssot_boot.py")
    src, dst = pathlib.Path(tree) / "ssot_boot.py", ROOT / "ssot_boot.py"
    if want and src.is_file() and sha256(src) == want and (not dst.exists() or sha256(dst) != want):
        tmp = ROOT / "ssot_boot.py.tmp"
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)


def prune():
    keep = CUR.resolve()
    olds = sorted(
        (p for p in STORE.iterdir() if p.is_dir() and p != keep),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for p in olds[2:]:
        shutil.rmtree(p, ignore_errors=True)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    STORE.mkdir(exist_ok=True)
    try:
        if os.environ.get("SSOT_OFFLINE") == "1":
            raise RuntimeError("SSOT_OFFLINE=1")
        tag, pin = resolve()
        tree, man = load(tag, pin)
        index(tree, man, tag)
        activate(tree)
        self_update(tree, man)
        print(f"ssot: active {tag} ({REF}) -> {CUR}/INDEX.md")
    except Exception as e:  # offline, rate-limited, bad release: never block the session
        if CUR.exists():
            print(f"ssot: WARNING {str(e)[:140]}; staying on {CUR.resolve().name}", file=sys.stderr)
        else:
            print(f"ssot: FATAL no cached set and fetch failed: {e}", file=sys.stderr)
            sys.exit(1)
    prune()


if __name__ == "__main__":
    main()
