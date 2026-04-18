import { MessageResponse, Thread } from "../types";

const getBaseUrl = () => {
  const url = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  return url.replace(/\/+$/, ""); // Remove trailing slashes
};

const API_BASE_URL = getBaseUrl();

export const api = {
  createThread: async (): Promise<string> => {
    const res = await fetch(`${API_BASE_URL}/threads`, {
      method: "POST",
    });
    if (!res.ok) throw new Error(`Backend Error: ${res.status}`);
    const data = await res.json();
    return data.thread_id;
  },

  getThread: async (threadId: string): Promise<Thread> => {
    const res = await fetch(`${API_BASE_URL}/threads/${threadId}`);
    if (!res.ok) throw new Error(`Backend Error: ${res.status}`);
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
    if (!res.ok) throw new Error(`Backend Error: ${res.status}`);
    return res.json();
  },

  listSources: async (): Promise<any[]> => {
    const res = await fetch(`${API_BASE_URL}/sources`);
    if (!res.ok) return [];
    return res.json();
  },
};
