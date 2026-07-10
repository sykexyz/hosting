import { store } from "./store";

export async function logActivity(message: string): Promise<void> {
  store.logs.insert(message);
}
