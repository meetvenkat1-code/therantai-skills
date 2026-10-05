#!/usr/bin/env python3
"""build_manifest.py: index skills/ and write MANIFEST.json with absolute raw URLs.

Usage (repo root, file lives at tools/build_manifest.py):
  python tools/build_manifest.py           index skills, write MANIFEST.json + channels/stable.json
  python tools/build_manifest.py --check   fail if MANIFEST.json / channels/stable.json are stale

For each skills/<name>/SKILL.md:
  - description: extracted from YAML frontmatter `description` field
  - sha256 + bytes: computed on LF-normalized content so Windows (CRLF)
    checkouts produce the same hash GitHub serves (blobs are LF)
  - url: absolute raw URL on main branch

MANIFEST.json structure:
  {"version": "v1.1.0", "skills": {name: {url, sha256, bytes, description}}}

channels/stable.json structure:
  {"tag": "v1.1.0", "manifest_url": ".../MANIFEST.json",
   "manifest_sha256": "<sha256 of MANIFEST.json>", "base_url": ".../skills/"}
"""
import hashlib
import json
import pathlib
import re
import sys

REPO_SLUG = "meetvenkat1-code/therantai-skills"
BRANCH = "main"
TAG = "v1.1.0"

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OUT = ROOT / "MANIFEST.json"
STABLE = ROOT / "channels" / "stable.json"

RAW = f"https://raw.githubusercontent.com/{REPO_SLUG}/{BRANCH}"
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")


def raw_bytes(path: pathlib.Path) -> bytes:
    """Bytes as GitHub will serve them: LF-normalized."""
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frontmatter(path: pathlib.Path):
    text = raw_bytes(path).decode("utf-8")
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    meta, last = {}, None
    for line in m.group(1).splitlines():
        if line[:1] in (" ", "\t") and last:
            meta[last] = (meta[last] + " " + line.strip()).strip()
            continue
        key, sep, val = line.partition(":")
        if sep:
            last = key.strip()
            meta[last] = val.strip()
    return meta


def build():
    errors, skills = [], {}
    if not SKILLS.is_dir():
        sys.exit("skills/ directory not found")
    dirs = sorted(
        p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    for d in dirs:
        skill_md = d / "SKILL.md"
        if not NAME.fullmatch(d.name):
            errors.append(f"{d.name}: folder name must be lowercase-hyphen")
            continue
        if not skill_md.is_file():
            errors.append(f"{d.name}: SKILL.md missing")
            continue
        meta = frontmatter(skill_md)
        if meta is None:
            errors.append(f"{d.name}: SKILL.md has no frontmatter")
            continue
        if meta.get("name") != d.name:
            errors.append(
                f"{d.name}: frontmatter name {meta.get('name')!r} != folder name"
            )
        desc = " ".join(meta.get("description", "").split())
        if not desc:
            errors.append(f"{d.name}: description is empty")
            continue
        data = raw_bytes(skill_md)
        skills[d.name] = {
            "url": f"{RAW}/skills/{d.name}/SKILL.md",
            "sha256": sha256_bytes(data),
            "bytes": len(data),
            "description": desc,
        }
    if errors:
        print("LINT FAILED:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)
    manifest = {"version": TAG, "skills": skills}
    manifest_body = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    manifest_sha = sha256_bytes(manifest_body.encode("utf-8"))
    stable = {
        "tag": TAG,
        "manifest_url": f"{RAW}/MANIFEST.json",
        "manifest_sha256": manifest_sha,
        "base_url": f"{RAW}/skills/",
    }
    stable_body = json.dumps(stable, indent=2, sort_keys=True) + "\n"
    return manifest_body, stable_body, len(skills)


def main():
    check = "--check" in sys.argv
    manifest_body, stable_body, n = build()
    if check:
        stale = []
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != manifest_body:
            stale.append("MANIFEST.json")
        if not STABLE.is_file() or STABLE.read_text(encoding="utf-8") != stable_body:
            stale.append("channels/stable.json")
        if stale:
            sys.exit(
                f"stale: {', '.join(stale)}; run python tools/build_manifest.py and commit"
            )
        print(f"manifest current: {n} skills")
    else:
        OUT.write_bytes(manifest_body.encode("utf-8"))
        STABLE.parent.mkdir(parents=True, exist_ok=True)
        STABLE.write_bytes(stable_body.encode("utf-8"))
        print(f"wrote MANIFEST.json: {n} skills")
        print(f"updated channels/stable.json -> {TAG}")


if __name__ == "__main__":
    main()
