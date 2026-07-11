---
name: Running untrusted/user JS from an ESM server
description: A parent server with "type":"module" breaks CommonJS require() in any child .js file it spawns unless the extension is forced.
---

If a Node server's own `package.json` sets `"type": "module"`, that setting applies to
*any* plain `.js` file Node loads by walking up from that file's directory — including
completely unrelated user-uploaded/hosted code, not just the server's own source.

**Why:** Hit this in a bot-hosting platform: user-uploaded Discord/Telegram bot `.js` files
using classic `require(...)` (the overwhelmingly common style for copy-pasted bot code)
crashed immediately with `ReferenceError: require is not defined in ES module scope`,
even though the code was perfectly valid CommonJS and ran fine elsewhere (e.g. via Termux).

**How to apply:** When spawning arbitrary/user `.js` source from a `"type":"module"` server,
don't run the file as-is. Detect whether the source is ESM (`import`/`export` statements) or
CommonJS (`require`/`module.exports`), then execute a copy with an unambiguous extension —
`.mjs` for ESM, `.cjs` for CommonJS — so Node's module resolution is correct regardless of
the parent server's own `package.json` type.
