import { store } from "./store";

export async function logActivity(message: string, botId?: number): Promise<void> {
  await store.logs.insert(message, botId);
}
