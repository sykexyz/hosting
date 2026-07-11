import { pgTable, text, serial, integer, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const logsTable = pgTable("logs", {
  id: serial("id").primaryKey(),
  message: text("message").notNull(),
  // Tags a log line to the bot it came from, so bot owners can view their own
  // bot's real stdout/stderr/lifecycle logs (not just admins). Null for
  // platform-wide messages (signups, admin logins, etc.)
  botId: integer("bot_id"),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export const insertLogSchema = createInsertSchema(logsTable).omit({
  id: true,
  createdAt: true,
});
export type InsertLog = z.infer<typeof insertLogSchema>;
export type Log = typeof logsTable.$inferSelect;
