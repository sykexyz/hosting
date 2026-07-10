import { store } from "./store";

export async function logActivity(message: string): Promise<void> {
  await store.logs.insert(message);
}
