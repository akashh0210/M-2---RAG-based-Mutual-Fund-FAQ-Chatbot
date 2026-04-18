import { MessageResponse, Thread } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
  createThread: async (): Promise<string> => {
    const res = await fetch(`${API_BASE_URL}/threads`, {
      method: "POST",
    });
    const data = await res.json();
    return data.thread_id;
  },

  getThread: async (threadId: string): Promise<Thread> => {
    const res = await fetch(`${API_BASE_URL}/threads/${threadId}`);
    return res.json();
  },

  sendMessage: async (threadId: string, query: string): Promise<MessageResponse> => {
    const res = await fetch(`${API_BASE_URL}/threads/${threadId}/messages`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });
    return res.json();
  },

  listSources: async (): Promise<any[]> => {
    const res = await fetch(`${API_BASE_URL}/sources`);
    return res.json();
  },
};
