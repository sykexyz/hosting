---
name: Bot-hosting sandbox pip installs
description: Why pip install fails inside a per-project/per-bot Python venv on Replit, and the fix.
---

Replit's workspace-level `pip.conf` (pointed to via `PIP_CONFIG_FILE`) sets `user = yes`
globally, because it's tuned for installing into the main Replit Python environment.

**Why:** Any code that shells out to `<venv>/bin/pip install ...` inherits this env var by
default. Pip then tries a `--user` install, which is invalid inside a virtualenv and fails with:
`ERROR: Can not perform a '--user' install. User site-packages are not visible in this virtualenv.`
This is a silent-looking failure — the app can catch/log the error and continue, so the bot
"starts" but crashes with `ModuleNotFoundError` for the dependency that never actually installed.

**How to apply:** When spawning `pip install` targeting an isolated venv (e.g. a bot-hosting
platform that gives each user bot its own venv), override the environment for that `exec`/`spawn`
call: unset `PIP_CONFIG_FILE` and set `PIP_USER=0`. Don't rely on the default inherited env.
