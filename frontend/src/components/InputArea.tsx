"use client";

import { useState } from "react";
import { Send, Sparkles } from "lucide-react";

interface InputAreaProps {
  onSendMessage: (query: string) => void;
  isLoading: boolean;
}

const SUGGESTIONS = [
  "What is the exit load for SBI Small Cap?",
  "Tell me about SBI Large Cap Fund",
  "How to start a SIP in SBI MF?",
  "What are the taxes on ELSS funds?"
];

export default function InputArea({ onSendMessage, isLoading }: InputAreaProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (query.trim() && !isLoading) {
      onSendMessage(query.trim());
      setQuery("");
    }
  };

  return (
    <div className="border-t border-[var(--groww-border)] p-4 bg-[var(--groww-surface)] z-10 sticky bottom-0">
      <div className="max-w-4xl mx-auto space-y-4">
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none hidden md:flex">
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              onClick={() => onSendMessage(s)}
              disabled={isLoading}
              className="whitespace-nowrap bg-[var(--groww-bg)] hover:bg-[var(--groww-border)] text-[var(--groww-text)] px-4 py-2 rounded-full text-xs font-medium border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] transition-all"
            >
              {s}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="relative group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            placeholder="Ask anything about SBI Mutual Funds..."
            className="w-full bg-[var(--groww-bg)] border-2 border-[var(--groww-border)] focus:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-xl py-4 pl-5 pr-14 text-sm outline-none transition-all shadow-sm focus:shadow-md placeholder:text-[var(--groww-text-muted)]"
          />
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="absolute right-2 top-2 bottom-2 bg-[var(--groww-emerald)] text-white p-3 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:grayscale transition-all hover:scale-105 active:scale-95"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Send size={18} />
            )}
          </button>
          {!query && (
            <div className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none transition-opacity group-focus-within:opacity-0 hidden lg:flex items-center gap-2">
                 <Sparkles size={16} className="text-[var(--groww-emerald)] opacity-50" />
            </div>
          )}
        </form>
        
        <div className="text-[10px] text-center text-[var(--groww-text-muted)] uppercase tracking-widest font-bold">
            Powered by RAG Engine · SBI Mutual Fund Assistant
        </div>
      </div>
    </div>
  );
}
