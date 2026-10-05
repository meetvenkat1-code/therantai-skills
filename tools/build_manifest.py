#!/usr/bin/env python3
"""build_manifest.py: lint skills/ and write MANIFEST.json (sha256 per file).

Usage (repo root, file lives at tools/build_manifest.py):
  python tools/build_manifest.py           lint, then write MANIFEST.json
  python tools/build_manifest.py --check   lint, then fail if MANIFEST.json is stale

Skill frontmatter rules:
  name         required, lowercase-hyphen, equal to the folder name
  description  required, non-empty (single line or indented continuation lines)
  requires     optional, e.g. requires: [model-config-contract]; every entry must exist
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS, BOOT, OUT = ROOT / "skills", ROOT / "ssot_boot.py", ROOT / "MANIFEST.json"
IGNORE = {".DS_Store", "Thumbs.db"}
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
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


def main():
    check = "--check" in sys.argv
    errors, skills = [], {}
    if not SKILLS.is_dir():
        sys.exit("skills/ directory not found")
    if not BOOT.is_file():
        errors.append("ssot_boot.py missing at repo root")

    dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith("."))
    names = {d.name for d in dirs}
    for d in dirs:
        skill_md = d / "SKILL.md"
        if not NAME.fullmatch(d.name):
            errors.append(f"{d.name}: folder name must be lowercase-hyphen")
        if not skill_md.is_file():
            errors.append(f"{d.name}: SKILL.md missing")
            continue
        meta = frontmatter(skill_md)
        if meta is None:
            errors.append(f"{d.name}: SKILL.md has no frontmatter")
            continue
        if meta.get("name") != d.name:
            errors.append(f"{d.name}: frontmatter name {meta.get('name')!r} != folder name")
        desc = " ".join(meta.get("description", "").split())
        if not desc:
            errors.append(f"{d.name}: description is empty")
        reqs = [r.strip() for r in meta.get("requires", "").strip("[]").split(",") if r.strip()]
        for r in reqs:
            if r not in names:
                errors.append(f"{d.name}: requires unknown skill {r!r}")
        files = {}
        for f in sorted(d.rglob("*")):
            if f.is_symlink():
                errors.append(f"{d.name}: symlink not allowed: {f.relative_to(d)}")
            elif f.is_file() and f.name not in IGNORE:
                files[f.relative_to(d).as_posix()] = sha(f)
        skills[d.name] = {"description": desc, "files": files}

    if errors:
        print("LINT FAILED:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)

    manifest = {
        "version": 1,
        "boot": {"ssot_boot.py": sha(BOOT)},
        "skills": skills,
    }
    body = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != body:
            sys.exit("MANIFEST.json is stale: run python tools/build_manifest.py and commit it")
        print(f"manifest current: {len(skills)} skills")
    else:
        OUT.write_text(body, encoding="utf-8")
        print(f"wrote MANIFEST.json: {len(skills)} skills")


if __name__ == "__main__":
    main()
