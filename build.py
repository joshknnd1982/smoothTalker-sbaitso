# -*- coding: utf-8 -*-
"""
Package the add-on as sbaitso-<version>.nvda-addon.

An .nvda-addon is just a zip of the add-on directory with manifest.ini at its
root, so there is nothing to install to run this -- plain CPython will do.
"""

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
#: Never ship compiled bytecode: it is rebuilt on first import anyway, and a
#: stale .pyc that outlives the .py it came from is a genuinely confusing bug.
SKIP_DIRS = {'__pycache__', '.git', '.github'}
SKIP_EXTS = ('.pyc', '.pyo', '.nvda-addon')
#: Repository furniture; it has no business inside an installed add-on.
SKIP_NAMES = {'build.py', '.gitignore', '.gitattributes'}


def version():
    """Read the version out of manifest.ini without a config parser."""
    with open(os.path.join(ROOT, 'manifest.ini'), encoding='utf-8') as f:
        for line in f:
            key, sep, value = line.partition('=')
            if sep and key.strip() == 'version':
                return value.strip().strip('"')
    raise SystemExit('manifest.ini has no version')


def build():
    out = os.path.join(ROOT, 'sbaitso-%s.nvda-addon' % version())
    count = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                if name.endswith(SKIP_EXTS) or name in SKIP_NAMES:
                    continue
                full = os.path.join(dirpath, name)
                z.write(full, os.path.relpath(full, ROOT).replace(os.sep, '/'))
                count += 1
    print('%s\n%d files, %.1f MB' % (out, count, os.path.getsize(out) / 1048576.0))
    return out


if __name__ == '__main__':
    sys.exit(0 if build() else 1)
