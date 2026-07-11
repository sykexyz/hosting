---
name: Python/npm import → package name mapping
description: Raw import root names often differ from the real PyPI package name; naive detection installs the wrong thing.
---

When auto-detecting dependencies from source code to `pip install` them (e.g. for a bot-hosting
or code-execution platform), the import root name is frequently NOT the PyPI package name.

**Why:** e.g. `import discord` needs PyPI package `discord.py`, not the unrelated abandoned
`discord` package. Similar mismatches: `cv2`→`opencv-python`, `PIL`→`Pillow`, `yaml`→`PyYAML`,
`bs4`→`beautifulsoup4`, `sklearn`→`scikit-learn`, `dotenv`→`python-dotenv`,
`dateutil`→`python-dateutil`, `Crypto`→`pycryptodome`, `nacl`→`PyNaCl`, `jwt`→`PyJWT`. Installing
the naive/wrong package looks like a successful install (no error) but the real import still
fails at runtime — very confusing to debug from the outside, looks like "the site is broken."

**How to apply:** Maintain an explicit import-root → PyPI-package lookup table for auto-detected
Python dependencies; only fall back to using the import name verbatim when it's not in the table.
