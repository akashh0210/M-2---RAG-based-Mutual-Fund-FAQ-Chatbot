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
    <div className="border-t border-[var(--groww-border)] p-5 bg-[var(--groww-surface)] z-10 sticky bottom-0">
      <div className="max-w-4xl mx-auto space-y-4">
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none hidden md:flex no-scrollbar">
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              onClick={() => onSendMessage(s)}
              disabled={isLoading}
              className="whitespace-nowrap bg-[var(--groww-surface)] hover:bg-[var(--groww-bg)] text-[11px] font-bold uppercase tracking-wider text-[var(--groww-text-muted)] hover:text-[var(--groww-emerald)] px-4 py-2 rounded-xl border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] transition-all active:scale-95"
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
            placeholder="Ask about exit load, minimum SIP, benchmark, or process..."
            className="w-full bg-[var(--groww-bg)] border border-[var(--groww-border)] focus:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-2xl py-5 pl-6 pr-16 text-sm outline-none transition-all shadow-sm focus:shadow-xl focus:shadow-emerald-500/5 placeholder:text-[var(--groww-text-muted)]/60"
          />
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="absolute right-2.5 top-2.5 bottom-2.5 bg-[var(--groww-emerald)] text-white px-5 rounded-xl flex items-center justify-center disabled:opacity-30 disabled:grayscale transition-all hover:brightness-110 active:scale-95 shadow-lg shadow-emerald-500/20"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Send size={18} className="fill-current" />
            )}
          </button>
        </form>
        
        <div className="text-[9px] text-center text-[var(--groww-text-muted)] uppercase tracking-[0.2em] font-bold flex items-center justify-center gap-2">
            <span className="w-8 h-[1px] bg-[var(--groww-border)]"></span>
            Facts Powered • Groww MF Assistant
            <span className="w-8 h-[1px] bg-[var(--groww-border)]"></span>
        </div>
      </div>
    </div>
  );
}
