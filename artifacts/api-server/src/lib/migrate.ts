import { pool } from "@workspace/db";

/**
 * Ensure all required tables exist before the server starts serving requests.
 * Each statement runs independently so a pre-existing table/type on one
 * statement never aborts the rest (handles Railway DB reuse across deploys).
 */
export async function ensureSchema(): Promise<void> {
  const client = await pool.connect();
  try {
    // Run each DDL statement separately so an already-existing table/type on
    // one statement doesn't roll back the others.
    const stmts = [
      `CREATE TABLE IF NOT EXISTS users (
         id SERIAL PRIMARY KEY,
         email TEXT NOT NULL UNIQUE,
         username TEXT NOT NULL UNIQUE,
         password_hash TEXT NOT NULL,
         created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
       )`,
      `CREATE TABLE IF NOT EXISTS bots (
         id SERIAL PRIMARY KEY,
         user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
         name TEXT NOT NULL,
         language TEXT NOT NULL,
         ram_mb INTEGER NOT NULL,
         storage_mb INTEGER NOT NULL,
         status TEXT NOT NULL DEFAULT 'stopped',
         file_name TEXT,
         file_path TEXT,
         created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
       )`,
      `ALTER TABLE bots ADD COLUMN IF NOT EXISTS file_size_bytes INTEGER`,
      `CREATE TABLE IF NOT EXISTS logs (
         id SERIAL PRIMARY KEY,
         message TEXT NOT NULL,
         created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
       )`,
      `ALTER TABLE logs ADD COLUMN IF NOT EXISTS bot_id INTEGER`,
      `CREATE TABLE IF NOT EXISTS sessions (
         token TEXT PRIMARY KEY,
         user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
         created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
         expires_at TIMESTAMPTZ NOT NULL
       )`,
    ];

    for (const sql of stmts) {
      try {
        await client.query(sql);
      } catch (err: unknown) {
        // Ignore "already exists" errors (duplicate_table / duplicate_object /
        // duplicate_column) so redeploying onto an existing DB never crashes.
        const pg = err as { code?: string };
        if (pg.code === "42P07" || pg.code === "42710" || pg.code === "42701" || pg.code === "23505") {
          // 42P07 = duplicate_table, 42710 = duplicate_object,
          // 42701 = duplicate_column, 23505 = unique_violation (pg_type race)
          continue;
        }
        throw err;
      }
    }
  } finally {
    client.release();
  }
}
