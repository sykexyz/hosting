import { db, usersTable, botsTable, logsTable } from "@workspace/db";
import { eq, and, desc, sql } from "drizzle-orm";

export type User = typeof usersTable.$inferSelect;
export type Bot = typeof botsTable.$inferSelect;
export type Log = typeof logsTable.$inferSelect;

export const store = {
  users: {
    async findByEmailOrUsername(email: string, username: string): Promise<User | undefined> {
      const rows = await db
        .select()
        .from(usersTable)
        .where(
          sql`${usersTable.email} = ${email} OR ${usersTable.username} = ${username}`
        )
        .limit(1);
      return rows[0];
    },
    async findByEmail(email: string): Promise<User | undefined> {
      const rows = await db
        .select()
        .from(usersTable)
        .where(eq(usersTable.email, email))
        .limit(1);
      return rows[0];
    },
    async findById(id: number): Promise<User | undefined> {
      const rows = await db
        .select()
        .from(usersTable)
        .where(eq(usersTable.id, id))
        .limit(1);
      return rows[0];
    },
    async findAll(): Promise<User[]> {
      return db.select().from(usersTable).orderBy(desc(usersTable.id));
    },
    async insert(data: Omit<User, "id" | "createdAt">): Promise<User> {
      const rows = await db.insert(usersTable).values(data).returning();
      return rows[0]!;
    },
  },

  bots: {
    async findByUserId(userId: number): Promise<Bot[]> {
      return db
        .select()
        .from(botsTable)
        .where(eq(botsTable.userId, userId))
        .orderBy(botsTable.id);
    },
    async findByIdAndUserId(id: number, userId: number): Promise<Bot | undefined> {
      const rows = await db
        .select()
        .from(botsTable)
        .where(and(eq(botsTable.id, id), eq(botsTable.userId, userId)))
        .limit(1);
      return rows[0];
    },
    async findById(id: number): Promise<Bot | undefined> {
      const rows = await db
        .select()
        .from(botsTable)
        .where(eq(botsTable.id, id))
        .limit(1);
      return rows[0];
    },
    async findAll(): Promise<Bot[]> {
      return db.select().from(botsTable).orderBy(desc(botsTable.id));
    },
    async insert(data: Omit<Bot, "id" | "createdAt">): Promise<Bot> {
      const rows = await db.insert(botsTable).values(data).returning();
      return rows[0]!;
    },
    async update(id: number, patch: Partial<Omit<Bot, "id" | "userId" | "createdAt">>): Promise<Bot | undefined> {
      const rows = await db
        .update(botsTable)
        .set(patch)
        .where(eq(botsTable.id, id))
        .returning();
      return rows[0];
    },
    async deleteByIdAndUserId(id: number, userId: number): Promise<Bot | undefined> {
      const rows = await db
        .delete(botsTable)
        .where(and(eq(botsTable.id, id), eq(botsTable.userId, userId)))
        .returning();
      return rows[0];
    },
    async deleteById(id: number): Promise<Bot | undefined> {
      const rows = await db
        .delete(botsTable)
        .where(eq(botsTable.id, id))
        .returning();
      return rows[0];
    },
  },

  logs: {
    async findRecent(limit = 100): Promise<Log[]> {
      const rows = await db
        .select()
        .from(logsTable)
        .orderBy(desc(logsTable.id))
        .limit(limit);
      return rows;
    },
    async insert(message: string): Promise<Log> {
      const rows = await db.insert(logsTable).values({ message }).returning();
      // Prune old logs asynchronously (keep last 500)
      db.execute(
        sql`DELETE FROM ${logsTable} WHERE id NOT IN (SELECT id FROM ${logsTable} ORDER BY id DESC LIMIT 500)`
      ).catch(() => {});
      return rows[0]!;
    },
  },
};
