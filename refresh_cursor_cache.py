#!/usr/bin/env python3
"""Copy this repo's plugins into Cursor's SHA-pinned local-marketplace cache.

Cursor records the git SHA of a local marketplace at add time
(marketplaceId cursor-plugins-zh-*, gitRef = that SHA) and keeps a detached
clone under ~/.cursor/plugins/marketplaces/_/users/<you>/<sha>/. Uninstalling
and reinstalling the plugins reuses that gitRef. This script copies the
current plugins/ tree into every matching cache dir and clone so a new chat
can load skills that landed after the original SHA.
"""

import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PLUGINS = os.path.join(ROOT, "plugins")
PLUGIN_NAMES = ("pstack", "thermos")
CACHE_ROOT = os.path.expanduser("~/.cursor/plugins/cache/cursor-plugins-zh")
MARKET_ROOT = os.path.join(
    os.path.expanduser("~/.cursor/plugins/marketplaces/_/users"),
    os.environ.get("USER") or os.environ.get("LOGNAME") or "",
)


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def plugin_version(plugin_dir):
    path = os.path.join(plugin_dir, ".cursor-plugin", "plugin.json")
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return json.load(f).get("version")


def has_bro(plugin_dir):
    return os.path.isfile(os.path.join(plugin_dir, "skills", "bro", "SKILL.md"))


def has_comment_sicko(plugin_dir):
    return os.path.isfile(os.path.join(plugin_dir, "agents", "comment-sicko.md"))


def replace_dir(src, dest):
    parent = os.path.dirname(dest)
    os.makedirs(parent, exist_ok=True)
    tmp = dest + ".refresh-tmp"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp, symlinks=True)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.rename(tmp, dest)


def iter_cache_dirs(name):
    root = os.path.join(CACHE_ROOT, name)
    if not os.path.isdir(root):
        return
    for sha in sorted(os.listdir(root)):
        dest = os.path.join(root, sha)
        if os.path.isdir(dest):
            yield dest


def iter_clone_plugin_dirs(name):
    if not os.path.isdir(MARKET_ROOT):
        return
    for sha in sorted(os.listdir(MARKET_ROOT)):
        dest = os.path.join(MARKET_ROOT, sha, "plugins", name)
        if os.path.isdir(dest):
            yield dest


def report(label, dest, name):
    ver = plugin_version(dest)
    extra = ""
    if name == "pstack":
        extra = " bro=%s comment-sicko=%s" % (
            has_bro(dest),
            has_comment_sicko(dest),
        )
    print("  %s %s version=%s%s" % (label, dest, ver, extra))


def main():
    for name in PLUGIN_NAMES:
        src = os.path.join(PLUGINS, name)
        if not os.path.isdir(src):
            die("missing %s" % src)

    print("source %s" % ROOT)
    for name in PLUGIN_NAMES:
        src = os.path.join(PLUGINS, name)
        print("  plugins/%s version=%s bro=%s comment-sicko=%s" % (
            name,
            plugin_version(src),
            has_bro(src) if name == "pstack" else "n/a",
            has_comment_sicko(src) if name == "pstack" else "n/a",
        ))

    copied = 0
    for name in PLUGIN_NAMES:
        src = os.path.join(PLUGINS, name)
        targets = list(iter_cache_dirs(name)) + list(iter_clone_plugin_dirs(name))
        if not targets:
            print("no Cursor %s cache/clone dirs found" % name)
            continue
        for dest in targets:
            print("before")
            report(" ", dest, name)
            replace_dir(src, dest)
            print("after")
            report(" ", dest, name)
            copied += 1

    if copied == 0:
        die("nothing copied. Add ~/cursor-plugins-zh as a local marketplace first.")

    pstack_ok = any(
        has_bro(d) and has_comment_sicko(d) and plugin_version(d) == plugin_version(os.path.join(PLUGINS, "pstack"))
        for d in iter_cache_dirs("pstack")
    )
    if not pstack_ok:
        die("pstack cache still missing bro/comment-sicko or version mismatch")
    print("ok. Open a new chat. This session already loaded the old snapshot.")


if __name__ == "__main__":
    main()
