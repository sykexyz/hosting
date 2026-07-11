/**
 * Parses source code to extract third-party package names.
 * Returns only packages that need to be installed — stdlib/builtins are filtered out.
 */

// Python standard library module names (common subset — enough to filter false positives)
const PYTHON_STDLIB = new Set([
  "__future__", "abc", "ast", "asyncio", "atexit", "base64", "binascii",
  "builtins", "calendar", "cgi", "cmath", "cmd", "code", "codecs",
  "collections", "concurrent", "configparser", "contextlib", "copy", "csv",
  "ctypes", "curses", "dataclasses", "datetime", "decimal", "difflib", "dis",
  "email", "enum", "errno", "filecmp", "fnmatch", "fractions", "functools",
  "gc", "getopt", "getpass", "glob", "gzip", "hashlib", "heapq", "hmac",
  "html", "http", "imaplib", "importlib", "inspect", "io", "itertools",
  "json", "keyword", "linecache", "locale", "logging", "math", "mimetypes",
  "multiprocessing", "netrc", "numbers", "operator", "os", "pathlib",
  "pickle", "platform", "pprint", "queue", "random", "re", "shlex", "shutil",
  "signal", "site", "smtplib", "socket", "socketserver", "sqlite3", "ssl",
  "stat", "statistics", "string", "struct", "subprocess", "sys", "sysconfig",
  "tarfile", "tempfile", "textwrap", "threading", "time", "timeit", "token",
  "tokenize", "traceback", "tracemalloc", "types", "typing", "unicodedata",
  "unittest", "urllib", "uuid", "warnings", "weakref", "xml", "xmlrpc",
  "zipfile", "zlib", "zoneinfo", "argparse", "fnmatch", "glob", "io",
  "struct", "pdb", "profile", "cProfile", "timeit", "doctest",
]);

// Node.js built-in module names (without the "node:" prefix)
const NODE_BUILTINS = new Set([
  "assert", "async_hooks", "buffer", "child_process", "cluster", "console",
  "constants", "crypto", "dgram", "diagnostics_channel", "dns", "domain",
  "events", "fs", "http", "http2", "https", "inspector", "module", "net",
  "os", "path", "perf_hooks", "process", "punycode", "querystring",
  "readline", "repl", "stream", "string_decoder", "sys", "timers", "tls",
  "trace_events", "tty", "url", "util", "v8", "vm", "wasi", "worker_threads",
  "zlib",
]);

function normaliseNodePkg(raw: string): string | null {
  // Strip "node:" protocol
  const name = raw.startsWith("node:") ? raw.slice(5) : raw;
  if (NODE_BUILTINS.has(name)) return null;
  // Scoped package → keep @scope/name, else keep first path segment
  if (name.startsWith("@")) {
    const parts = name.split("/");
    return parts.length >= 2 ? `${parts[0]}/${parts[1]}` : null;
  }
  return name.split("/")[0] ?? null;
}

export function detectPythonPackages(source: string): string[] {
  const pkgs = new Set<string>();

  // import X  /  import X.Y.Z  /  import X as Y
  for (const m of source.matchAll(/^\s*import\s+([\w.]+)/gm)) {
    const root = m[1]!.split(".")[0]!;
    if (!PYTHON_STDLIB.has(root)) pkgs.add(root);
  }

  // from X import ...
  for (const m of source.matchAll(/^\s*from\s+([\w.]+)\s+import/gm)) {
    const root = m[1]!.split(".")[0]!;
    if (!PYTHON_STDLIB.has(root)) pkgs.add(root);
  }

  return [...pkgs];
}

export function detectNodePackages(source: string): string[] {
  const pkgs = new Set<string>();

  // require('X') / require("X")
  for (const m of source.matchAll(/\brequire\s*\(\s*['"]([^'"]+)['"]\s*\)/g)) {
    const pkg = normaliseNodePkg(m[1]!);
    if (pkg) pkgs.add(pkg);
  }

  // import ... from 'X' / import 'X' / export ... from 'X'
  for (const m of source.matchAll(/\b(?:import|export)\s+[\s\S]*?from\s+['"]([^'"]+)['"]/gm)) {
    const pkg = normaliseNodePkg(m[1]!);
    if (pkg) pkgs.add(pkg);
  }

  // import('X') — dynamic
  for (const m of source.matchAll(/\bimport\s*\(\s*['"]([^'"]+)['"]\s*\)/g)) {
    const pkg = normaliseNodePkg(m[1]!);
    if (pkg) pkgs.add(pkg);
  }

  return [...pkgs];
}

export function detectPackages(language: string, source: string): string[] {
  switch (language) {
    case "python":     return detectPythonPackages(source);
    case "javascript":
    case "typescript": return detectNodePackages(source);
    default:           return [];
  }
}
