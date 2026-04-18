"use client";

import { Plus, MessageSquare, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onNewThread: () => void;
  activeThreadId: string | null;
  threadHistory: { id: string, title: string, updatedAt: number }[];
  onSelectThread: (id: string) => void;
}

export default function Sidebar({ onNewThread, activeThreadId, threadHistory, onSelectThread }: SidebarProps) {
  return (
    <div className="w-64 border-r border-[var(--groww-border)] h-full bg-[var(--groww-bg)] flex flex-col hidden md:flex">
      <div className="p-4 border-b border-[var(--groww-border)] flex items-center gap-2">
        <div className="w-8 h-8 bg-[var(--groww-emerald)] rounded-lg flex items-center justify-center shadow-sm text-white">
            <ShieldCheck className="w-5 h-5" />
        </div>
        <h1 className="font-bold text-lg tracking-tight text-[var(--groww-text)] leading-tight">Mutual Funds <br/><span className="text-[var(--groww-emerald)] text-sm">AI</span></h1>
      </div>

      <div className="p-4">
        <button 
          onClick={onNewThread}
          className="w-full btn-primary flex items-center justify-center gap-2 py-3"
        >
          <Plus size={18} />
          <span>New Chat</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        <div className="text-xs font-semibold text-[var(--groww-text-muted)] px-3 py-2 uppercase tracking-wider">
          Recent History
        </div>
        <div className="space-y-1">
          {threadHistory.length > 0 ? (
            threadHistory.map(thread => (
              <div 
                key={thread.id}
                onClick={() => onSelectThread(thread.id)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium cursor-pointer transition-all",
                  activeThreadId === thread.id
                    ? "bg-[var(--groww-surface)] border border-[var(--groww-emerald)] text-[var(--groww-emerald)] shadow-sm"
                    : "text-[var(--groww-text)] hover:bg-[var(--groww-surface)] border border-transparent"
                )}
              >
                <MessageSquare size={16} className={activeThreadId === thread.id ? "" : "text-[var(--groww-text-muted)]"} />
                <span className="truncate">{thread.title}</span>
              </div>
            ))
          ) : (
            <div className="px-3 py-10 text-center text-[var(--groww-text-muted)] text-xs italic">
              No previous conversations.
            </div>
          )}
        </div>
      </div>

      <div className="p-4 border-t border-[var(--groww-border)] bg-[var(--groww-surface)]">
        <div className="flex items-center gap-2 text-xs text-[var(--groww-text-muted)]">
          <div className="w-2 h-2 rounded-full bg-[var(--groww-emerald)] animate-pulse" />
          <span>RAG Engine Online</span>
        </div>
      </div>
    </div>
  );
}
