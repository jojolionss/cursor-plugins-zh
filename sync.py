#!/usr/bin/env python3
"""Rebuild Chinese-localized Cursor plugin copies from upstream + translation maps."""

import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
UPSTREAM = os.path.join(ROOT, "upstream")
PLUGINS = os.path.join(ROOT, "plugins")
TRANSLATIONS = os.path.join(ROOT, "translations")
PENDING = os.path.join(TRANSLATIONS, "pending.json")
PLUGIN_NAMES = ("pstack", "thermos")
UPSTREAM_URL = "https://github.com/cursor/plugins"


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def refresh_upstream(offline):
    if offline:
        if not os.path.isdir(UPSTREAM):
            die("upstream/ missing; cannot use --offline")
        return
    if not os.path.isdir(UPSTREAM):
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
             UPSTREAM_URL, "upstream"],
            check=True, cwd=ROOT,
        )
        subprocess.run(
            ["git", "-C", "upstream", "sparse-checkout", "set", "pstack", "thermos"],
            check=True, cwd=ROOT,
        )
    else:
        subprocess.run(["git", "-C", "upstream", "pull", "--ff-only"], check=True, cwd=ROOT)
    out = subprocess.check_output(
        ["git", "-C", UPSTREAM, "log", "-1", "--format=%h %ci"], text=True,
    ).strip()
    print(f"upstream HEAD: {out}")


def load_map(name):
    path = os.path.join(TRANSLATIONS, f"{name}.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def discover(plugin_dir):
    found = []
    for dirpath, _dns, filenames in os.walk(plugin_dir):
        for fn in filenames:
            if fn == "SKILL.md":
                found.append(os.path.relpath(os.path.join(dirpath, fn), plugin_dir))
    agents = os.path.join(plugin_dir, "agents")
    if os.path.isdir(agents):
        for fn in sorted(os.listdir(agents)):
            if fn.endswith(".md"):
                found.append(os.path.join("agents", fn))
    pj = os.path.join(".cursor-plugin", "plugin.json")
    if os.path.isfile(os.path.join(plugin_dir, pj)):
        found.append(pj)
    return sorted(found)


def read_text(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def unescape_quoted(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] in '"\\':
            out.append(s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def escape_quoted(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def parse_md_description(text, path):
    # Only the opening frontmatter; body may hold another description: (setup-pstack).
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        die(f"{path}: missing opening frontmatter")
    lines = text.splitlines(keepends=True)
    close = next((i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"), None)
    if close is None:
        die(f"{path}: missing closing frontmatter")
    desc_idxs = [i for i in range(1, close) if lines[i].startswith("description:")]
    if len(desc_idxs) != 1:
        die(f"{path}: expected one description: in frontmatter, got {len(desc_idxs)}")
    idx = desc_idxs[0]
    raw = lines[idx][len("description:"):].strip()
    if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
        value = unescape_quoted(raw[1:-1])
    else:
        value = raw
    if not value or value[0] in ">|":
        die(f"{path}: unsupported description value")
    return value, idx, lines


def current_en(path, rel):
    if rel.endswith("plugin.json"):
        return json.loads(read_text(path))["description"]
    return parse_md_description(read_text(path), path)[0]


def patch_markdown(path, zh):
    _en, idx, lines = parse_md_description(read_text(path), path)
    nl = "\r\n" if lines[idx].endswith("\r\n") else "\n"
    lines[idx] = f'description: "{escape_quoted(zh)}"{nl}'
    write_text(path, "".join(lines))


def patch_plugin_json(path, zh):
    raw = read_text(path)
    data = json.loads(raw)
    old = data["description"]
    needle = json.dumps(old)
    if raw.count(needle) != 1:
        die(f"{path}: json.dumps(description) occurs {raw.count(needle)} times, expected 1")
    new_raw = raw.replace(needle, json.dumps(zh, ensure_ascii=False), 1)
    new_data = json.loads(new_raw)
    if new_data.get("description") != zh:
        die(f"{path}: description mismatch after patch")
    check = dict(new_data)
    check["description"] = old
    if check != data:
        die(f"{path}: non-description keys changed after patch")
    write_text(path, new_raw)


def file_tree_relpaths(root):
    out = set()
    for dirpath, _dns, filenames in os.walk(root):
        for fn in filenames:
            out.add(os.path.relpath(os.path.join(dirpath, fn), root))
    return out


def validate_plugin(name, patched):
    src, dst = os.path.join(UPSTREAM, name), os.path.join(PLUGINS, name)
    src_set, dst_set = file_tree_relpaths(src), file_tree_relpaths(dst)
    if src_set != dst_set:
        die(f"{name}: relpath set mismatch "
            f"only_upstream={sorted(src_set - dst_set)[:5]} "
            f"only_plugins={sorted(dst_set - src_set)[:5]}")
    for rel in sorted(src_set):
        sp, dp = os.path.join(src, rel), os.path.join(dst, rel)
        if rel not in patched:
            if read_bytes(sp) != read_bytes(dp):
                die(f"{dp}: unpatched file not byte-identical to upstream")
            continue
        zh = patched[rel]
        if len(zh) > 1024:
            die(f"{dp}: zh description length {len(zh)} > 1024")
        if rel.endswith("plugin.json"):
            su, du = json.loads(read_text(sp)), json.loads(read_text(dp))
            if du.get("description") != zh:
                die(f"{dp}: description is not applied zh")
            aa, bb = dict(su), dict(du)
            aa.pop("description", None)
            bb.pop("description", None)
            if aa != bb:
                die(f"{dp}: plugin.json differs beyond description")
        else:
            s_text, d_text = read_text(sp), read_text(dp)
            _e, s_idx, s_lines = parse_md_description(s_text, sp)
            _e, d_idx, d_lines = parse_md_description(d_text, dp)
            restored = list(d_lines)
            restored[d_idx] = s_lines[s_idx]
            if "".join(restored) != s_text:
                die(f"{dp}: restoring description line does not match upstream")


def pending_entry(status, en_current, zh_current, en_translated):
    return {
        "status": status,
        "en_current": en_current,
        "zh_current": zh_current,
        "en_translated": en_translated,
    }


def rebuild_plugin(name, tmap):
    src, dst = os.path.join(UPSTREAM, name), os.path.join(PLUGINS, name)
    if not os.path.isdir(src):
        die(f"upstream/{name} missing")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    discovered = discover(dst)
    patched, pending_entries = {}, {}
    n_ok = n_new = n_stale = 0

    for rel in discovered:
        path = os.path.join(dst, rel)
        en = current_en(path, rel)
        if rel not in tmap:
            n_new += 1
            pending_entries[rel] = pending_entry("new", en, None, None)
            continue
        entry = tmap[rel]
        map_en, zh = entry.get("en"), entry.get("zh")
        if zh is None:
            die(f"{name}/{rel}: map entry missing zh")
        if map_en == en:
            n_ok += 1
        else:
            n_stale += 1
            pending_entries[rel] = pending_entry("stale", en, zh, map_en)
        if rel.endswith("plugin.json"):
            patch_plugin_json(path, zh)
        else:
            patch_markdown(path, zh)
        patched[rel] = zh

    n_removed = 0
    for rel, entry in tmap.items():
        if rel in discovered:
            continue
        n_removed += 1
        pending_entries[rel] = pending_entry("removed", None, entry.get("zh"), entry.get("en"))

    validate_plugin(name, patched)
    print(
        f"{name}: 已翻译 {n_ok}/{len(discovered)}  新增待译 {n_new}  "
        f"原文已变更 {n_stale}  已移除 {n_removed}  校验通过"
    )
    return pending_entries


def write_pending(all_pending):
    payload = {k: v for k, v in all_pending.items() if v}
    if not payload:
        if os.path.isfile(PENDING):
            os.remove(PENDING)
        return
    os.makedirs(TRANSLATIONS, exist_ok=True)
    with open(PENDING, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description="Sync Chinese Cursor plugin copies")
    ap.add_argument("--offline", action="store_true", help="skip git refresh")
    args = ap.parse_args()
    refresh_upstream(args.offline)
    os.makedirs(PLUGINS, exist_ok=True)
    all_pending = {name: rebuild_plugin(name, load_map(name)) for name in PLUGIN_NAMES}
    write_pending(all_pending)


if __name__ == "__main__":
    main()
