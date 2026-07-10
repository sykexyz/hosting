import fs from "node:fs";
import path from "node:path";

const DATA_DIR = path.resolve(import.meta.dirname, "../../data");
const STORE_FILE = path.join(DATA_DIR, "store.json");

export interface User {
  id: number;
  email: string;
  username: string;
  passwordHash: string;
  createdAt: string;
}

export interface Bot {
  id: number;
  userId: number;
  name: string;
  language: string;
  ramMb: number;
  storageMb: number;
  status: "stopped" | "running";
  fileName: string | null;
  filePath: string | null;
  createdAt: string;
}

export interface Log {
  id: number;
  message: string;
  createdAt: string;
}

interface StoreData {
  users: User[];
  bots: Bot[];
  logs: Log[];
  _seq: { users: number; bots: number; logs: number };
}

function ensureDir(): void {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
}

function load(): StoreData {
  ensureDir();
  if (!fs.existsSync(STORE_FILE)) {
    return { users: [], bots: [], logs: [], _seq: { users: 0, bots: 0, logs: 0 } };
  }
  try {
    return JSON.parse(fs.readFileSync(STORE_FILE, "utf-8")) as StoreData;
  } catch (err) {
    // Parse failed — back up the corrupt file and start fresh rather than
    // silently returning an empty store (which would lose data on the next save).
    const backup = STORE_FILE + `.corrupt-${Date.now()}`;
    try { fs.renameSync(STORE_FILE, backup); } catch {}
    console.error("[store] JSON parse failed; backed up to", backup, err);
    return { users: [], bots: [], logs: [], _seq: { users: 0, bots: 0, logs: 0 } };
  }
}

function save(data: StoreData): void {
  ensureDir();
  // Write atomically: temp file + rename so a crash can't corrupt the store.
  const tmp = STORE_FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2));
  fs.renameSync(tmp, STORE_FILE);
}

export const store = {
  users: {
    findByEmailOrUsername(email: string, username: string): User | undefined {
      const d = load();
      return d.users.find((u) => u.email === email || u.username === username);
    },
    findByEmail(email: string): User | undefined {
      return load().users.find((u) => u.email === email);
    },
    findById(id: number): User | undefined {
      return load().users.find((u) => u.id === id);
    },
    findAll(): User[] {
      return load().users;
    },
    insert(data: Omit<User, "id" | "createdAt">): User {
      const d = load();
      const user: User = { ...data, id: ++d._seq.users, createdAt: new Date().toISOString() };
      d.users.push(user);
      save(d);
      return user;
    },
  },

  bots: {
    findByUserId(userId: number): Bot[] {
      return load().bots.filter((b) => b.userId === userId).sort((a, b) => a.id - b.id);
    },
    findByIdAndUserId(id: number, userId: number): Bot | undefined {
      return load().bots.find((b) => b.id === id && b.userId === userId);
    },
    findById(id: number): Bot | undefined {
      return load().bots.find((b) => b.id === id);
    },
    findAll(): Bot[] {
      return load().bots.sort((a, b) => b.id - a.id);
    },
    insert(data: Omit<Bot, "id" | "createdAt">): Bot {
      const d = load();
      const bot: Bot = { ...data, id: ++d._seq.bots, createdAt: new Date().toISOString() };
      d.bots.push(bot);
      save(d);
      return bot;
    },
    update(id: number, patch: Partial<Omit<Bot, "id" | "userId" | "createdAt">>): Bot | undefined {
      const d = load();
      const idx = d.bots.findIndex((b) => b.id === id);
      if (idx === -1) return undefined;
      d.bots[idx] = { ...d.bots[idx]!, ...patch };
      save(d);
      return d.bots[idx];
    },
    deleteByIdAndUserId(id: number, userId: number): Bot | undefined {
      const d = load();
      const idx = d.bots.findIndex((b) => b.id === id && b.userId === userId);
      if (idx === -1) return undefined;
      const [bot] = d.bots.splice(idx, 1);
      save(d);
      return bot;
    },
    deleteById(id: number): Bot | undefined {
      const d = load();
      const idx = d.bots.findIndex((b) => b.id === id);
      if (idx === -1) return undefined;
      const [bot] = d.bots.splice(idx, 1);
      save(d);
      return bot;
    },
  },

  logs: {
    findRecent(limit = 100): Log[] {
      const d = load();
      return d.logs.slice(-limit).reverse();
    },
    insert(message: string): Log {
      const d = load();
      const log: Log = { id: ++d._seq.logs, message, createdAt: new Date().toISOString() };
      d.logs.push(log);
      // keep at most 500 logs
      if (d.logs.length > 500) d.logs = d.logs.slice(-500);
      save(d);
      return log;
    },
  },
};
