import { Router, type IRouter } from "express";
import bcrypt from "bcryptjs";
import { eq, or } from "drizzle-orm";
import { db, usersTable } from "@workspace/db";
import { SignupBody, LoginBody } from "@workspace/api-zod";
import {
  createUserSession,
  destroyUserSession,
  getUserSession,
  USER_COOKIE,
} from "../lib/sessions";
import { logActivity } from "../lib/activity-log";

const router: IRouter = Router();

const GMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@gmail\.com$/i;

function setSessionCookie(res: import("express").Response, token: string) {
  res.cookie(USER_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    maxAge: 30 * 24 * 60 * 60 * 1000,
  });
}

router.post("/auth/signup", async (req, res): Promise<void> => {
  const parsed = SignupBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const { email, username, password, confirmPassword } = parsed.data;

  if (!GMAIL_REGEX.test(email)) {
    res.status(400).json({ error: "Please use a valid Gmail address" });
    return;
  }

  if (password !== confirmPassword) {
    res.status(400).json({ error: "Passwords do not match" });
    return;
  }

  const [existing] = await db
    .select()
    .from(usersTable)
    .where(or(eq(usersTable.email, email), eq(usersTable.username, username)));

  if (existing) {
    res.status(400).json({
      error:
        existing.email === email
          ? "An account with this email already exists"
          : "This username is already taken",
    });
    return;
  }

  const passwordHash = await bcrypt.hash(password, 10);

  const [user] = await db
    .insert(usersTable)
    .values({ email, username, passwordHash })
    .returning();

  if (!user) {
    res.status(400).json({ error: "Could not create account" });
    return;
  }

  const token = createUserSession(user.id);
  setSessionCookie(res, token);
  await logActivity(`New user signed up: ${user.username}`);

  res.status(201).json({
    id: user.id,
    email: user.email,
    username: user.username,
    createdAt: user.createdAt.toISOString(),
  });
});

router.post("/auth/login", async (req, res): Promise<void> => {
  const parsed = LoginBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const { email, password } = parsed.data;

  const [user] = await db
    .select()
    .from(usersTable)
    .where(eq(usersTable.email, email));

  if (!user) {
    res.status(401).json({ error: "Invalid email or password" });
    return;
  }

  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) {
    res.status(401).json({ error: "Invalid email or password" });
    return;
  }

  const token = createUserSession(user.id);
  setSessionCookie(res, token);
  await logActivity(`${user.username} logged in`);

  res.json({
    id: user.id,
    email: user.email,
    username: user.username,
    createdAt: user.createdAt.toISOString(),
  });
});

router.post("/auth/logout", (req, res): void => {
  destroyUserSession(req.cookies?.[USER_COOKIE] as string | undefined);
  res.clearCookie(USER_COOKIE);
  res.sendStatus(204);
});

router.get("/auth/me", async (req, res): Promise<void> => {
  const token = req.cookies?.[USER_COOKIE] as string | undefined;
  const session = getUserSession(token);
  if (!session) {
    res.status(401).json({ error: "Not logged in" });
    return;
  }

  const [user] = await db
    .select()
    .from(usersTable)
    .where(eq(usersTable.id, session.userId));

  if (!user) {
    res.status(401).json({ error: "Not logged in" });
    return;
  }

  res.json({
    id: user.id,
    email: user.email,
    username: user.username,
    createdAt: user.createdAt.toISOString(),
  });
});

export default router;
