import crypto from "node:crypto";

// Simple in-memory session stores. This is a single-process dev/staging
// server so an in-memory map is sufficient — sessions reset on restart.
const userSessions = new Map<string, { userId: number }>();
const adminSessions = new Set<string>();

export const USER_COOKIE = "bh_session";
export const ADMIN_COOKIE = "bh_admin_session";

export function createUserSession(userId: number): string {
  const token = crypto.randomBytes(32).toString("hex");
  userSessions.set(token, { userId });
  return token;
}

export function getUserSession(token: string | undefined) {
  if (!token) return undefined;
  return userSessions.get(token);
}

export function destroyUserSession(token: string | undefined) {
  if (!token) return;
  userSessions.delete(token);
}

export function createAdminSession(): string {
  const token = crypto.randomBytes(32).toString("hex");
  adminSessions.add(token);
  return token;
}

export function isAdminSession(token: string | undefined): boolean {
  if (!token) return false;
  return adminSessions.has(token);
}

export function destroyAdminSession(token: string | undefined) {
  if (!token) return;
  adminSessions.delete(token);
}
