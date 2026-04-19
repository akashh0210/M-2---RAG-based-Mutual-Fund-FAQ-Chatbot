"use client";

import { Plus, MessageSquare, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onNewThread: () => void | Promise<any>;
  activeThreadId: string | null;
  threadHistory: { id: string, title: string, updatedAt: number }[];
  onSelectThread: (id: string) => void | Promise<any>;
}

export default function Sidebar({ onNewThread, activeThreadId, threadHistory, onSelectThread }: SidebarProps) {
  return (
    <div className="w-64 border-r border-[var(--groww-border)] h-full bg-[var(--groww-bg)] flex flex-col hidden md:flex transition-all">
      <div className="p-5 border-b border-[var(--groww-border)] flex items-center gap-2">
        <div className="w-8 h-8 bg-[var(--groww-emerald)] rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white">
            <ShieldCheck className="w-5 h-5" />
        </div>
        <h1 className="font-bold text-base tracking-tight text-[var(--groww-text)] leading-none">Groww Assistant</h1>
      </div>

      <div className="p-4">
        <button 
          onClick={onNewThread}
          className="w-full bg-[var(--groww-emerald)]/10 hover:bg-[var(--groww-emerald)]/20 text-[var(--groww-emerald)] border border-[var(--groww-emerald)]/20 flex items-center justify-center gap-2 py-2.5 rounded-xl font-bold transition-all active:scale-95 text-sm"
        >
          <Plus size={16} />
          <span>New Chat</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-4">
        <div className="text-[10px] font-bold text-[var(--groww-text-muted)] px-4 py-2 uppercase tracking-[0.2em] mb-2 opacity-60">
          Search History
        </div>
        <div className="space-y-1">
          {threadHistory.length > 0 ? (
            threadHistory.map(thread => (
              <div 
                key={thread.id}
                onClick={() => onSelectThread(thread.id)}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold cursor-pointer transition-all",
                  activeThreadId === thread.id
                    ? "bg-[var(--groww-surface)] text-[var(--groww-emerald)] border border-[var(--groww-border)] shadow-sm"
                    : "text-[var(--groww-text-muted)] hover:text-[var(--groww-text)] hover:bg-[var(--groww-surface)]/50"
                )}
              >
                <div className={cn(
                  "w-1.5 h-1.5 rounded-full shrink-0",
                  activeThreadId === thread.id ? "bg-[var(--groww-emerald)]" : "bg-transparent"
                )} />
                <span className="truncate">{thread.title}</span>
              </div>
            ))
          ) : (
            <div className="px-4 py-10 text-center text-[var(--groww-text-muted)] text-xs font-medium opacity-50">
              No history found
            </div>
          )}
        </div>
      </div>

      <div className="p-4 border-t border-[var(--groww-border)]">
        <div className="bg-[var(--groww-surface)] p-3 rounded-xl border border-[var(--groww-border)] flex items-center gap-3">
          <div className="relative">
            <div className="w-2.5 h-2.5 rounded-full bg-[var(--groww-emerald)]" />
            <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-[var(--groww-emerald)] animate-ping" />
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-[var(--groww-text)] leading-none">RAG ENGINE</span>
            <span className="text-[9px] text-[var(--groww-emerald)] font-bold uppercase tracking-widest mt-0.5">Connected</span>
          </div>
        </div>
      </div>
    </div>
  );
}
