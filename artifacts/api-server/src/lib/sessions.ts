import crypto from "node:crypto";
import { db, sessionsTable } from "@workspace/db";
import { eq } from "drizzle-orm";

export const USER_COOKIE = "bh_session";
export const ADMIN_COOKIE = "bh_admin_session";

const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000; // 30 days

// ---------------------------------------------------------------------------
// User sessions — persisted in PostgreSQL so they survive restarts/redeploys
// ---------------------------------------------------------------------------

export async function createUserSession(userId: number): Promise<string> {
  const token = crypto.randomBytes(32).toString("hex");
  const expiresAt = new Date(Date.now() + SESSION_TTL_MS);
  await db.insert(sessionsTable).values({ token, userId, expiresAt });
  return token;
}

export async function getUserSession(
  token: string | undefined
): Promise<{ userId: number } | undefined> {
  if (!token) return undefined;
  const rows = await db
    .select()
    .from(sessionsTable)
    .where(eq(sessionsTable.token, token))
    .limit(1);
  const session = rows[0];
  if (!session) return undefined;
  // Treat expired sessions as missing
  if (session.expiresAt < new Date()) {
    await db.delete(sessionsTable).where(eq(sessionsTable.token, token));
    return undefined;
  }
  return { userId: session.userId };
}

export async function destroyUserSession(token: string | undefined): Promise<void> {
  if (!token) return;
  await db.delete(sessionsTable).where(eq(sessionsTable.token, token));
}

// ---------------------------------------------------------------------------
// Admin sessions — single-process in-memory (one admin, not critical to persist)
// ---------------------------------------------------------------------------
const adminSessions = new Set<string>();

export function createAdminSession(): string {
  const token = crypto.randomBytes(32).toString("hex");
  adminSessions.add(token);
  return token;
}

export function isAdminSession(token: string | undefined): boolean {
  if (!token) return false;
  return adminSessions.has(token);
}

export function destroyAdminSession(token: string | undefined): void {
  if (!token) return;
  adminSessions.delete(token);
}
