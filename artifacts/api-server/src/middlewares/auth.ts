import type { Request, Response, NextFunction } from "express";
import {
  USER_COOKIE,
  ADMIN_COOKIE,
  getUserSession,
  isAdminSession,
} from "../lib/sessions";
import type { Bot } from "../lib/store";

export async function requireAuth(
  req: Request,
  res: Response,
  next: NextFunction,
): Promise<void> {
  const token = req.cookies?.[USER_COOKIE] as string | undefined;
  const session = await getUserSession(token);
  if (!session) {
    res.status(401).json({ error: "Not logged in" });
    return;
  }
  req.userId = session.userId;
  next();
}

export function requireAdmin(
  req: Request,
  res: Response,
  next: NextFunction,
): void {
  const token = req.cookies?.[ADMIN_COOKIE] as string | undefined;
  if (!isAdminSession(token)) {
    res.status(401).json({ error: "Not authorized" });
    return;
  }
  next();
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Express {
    interface Request {
      userId?: number;
      bot?: Bot;
    }
  }
}
