import { db, logsTable } from "@workspace/db";

export async function logActivity(message: string): Promise<void> {
  await db.insert(logsTable).values({ message });
}
