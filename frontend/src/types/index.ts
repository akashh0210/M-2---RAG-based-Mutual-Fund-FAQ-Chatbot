export interface Message {
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    intent?: string;
    scheme_name?: string;
    fact_type?: string;
    source_url?: string;
    is_refused?: boolean;
  };
  created_at?: string;
}

export interface Thread {
  thread_id: string;
  history: Message[];
}

export interface MessageResponse {
  answer: string;
  intent: string;
  scheme_name: string | null;
  source_url: string | null;
  thread_id: string;
  is_refused: boolean;
}
