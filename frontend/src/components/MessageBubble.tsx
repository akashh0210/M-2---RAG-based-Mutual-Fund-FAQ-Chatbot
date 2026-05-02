"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Message } from "@/types";
import { ExternalLink, Info, Copy, Check, Share2 } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'SBI MF Fact',
        text: message.content,
      }).catch(console.error);
    } else {
      handleCopy();
    }
  };

  const linkifyText = (text: string) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const parts = text.split(urlRegex);
    return parts.map((part, i) => {
      if (part.match(urlRegex)) {
        return (
          <a key={i} href={part} target="_blank" rel="noreferrer" className="text-blue-200 hover:underline font-medium underline-offset-2">
            {part}
          </a>
        );
      }
      return part;
    });
  };

  const linkifyAssistantText = (text: string) => {
    const urlRegex = /(https?:\/\/[^\s\)]+)/g;
    const parts = text.split(urlRegex);
    return parts.map((part, i) => {
      if (part.match(urlRegex)) {
        return (
          <a key={i} href={part} target="_blank" rel="noreferrer" className="text-teal-600 dark:text-teal-400 hover:underline font-medium">
            {part}
          </a>
        );
      }
      return part;
    });
  };

  return (
    <div className={cn(
      "flex w-full mb-8 relative group items-start gap-3",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      {/* Avatar / Label */}
      <div className={cn(
        "shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold tracking-tighter shadow-sm border",
        isUser 
          ? "bg-[var(--groww-surface)] border-[var(--groww-border)] text-[var(--groww-text-muted)] mt-1" 
          : "bg-[var(--groww-emerald)]/10 border-[var(--groww-emerald)]/20 text-[var(--groww-emerald)] mt-1"
      )}>
        {isUser ? "ME" : "GR"}
      </div>

      <div className={cn(
        "max-w-[85%] md:max-w-[75%] rounded-2xl relative transition-all duration-300",
        isUser 
          ? "bg-gradient-to-br from-[var(--groww-emerald)]/90 to-teal-600 text-white p-4 shadow-lg shadow-emerald-500/5 rounded-tr-none" 
          : "bg-[var(--groww-surface)] border border-[var(--groww-border)] text-[var(--groww-text)] p-0 rounded-tl-none overflow-hidden hover:shadow-xl hover:shadow-emerald-500/5"
      )}>
        
        {/* Content Area */}
        <div className={cn(
          "text-sm md:text-[15px] whitespace-pre-wrap leading-relaxed",
          !isUser ? "p-5" : ""
        )}>
          {isUser ? linkifyText(message.content) : linkifyAssistantText(message.content)}
        </div>

        {!isUser && (
          <div className="absolute top-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={handleCopy} title="Copy facts" className="p-2 bg-[var(--groww-bg)]/50 backdrop-blur-sm border border-[var(--groww-border)] rounded-lg text-[var(--groww-text-muted)] hover:text-[var(--groww-emerald)] hover:bg-[var(--groww-surface)] transition-all active:scale-90">
              {copied ? <Check size={14} /> : <Copy size={14} />}
            </button>
            <button onClick={handleShare} title="Share fact" className="p-2 bg-[var(--groww-bg)]/50 backdrop-blur-sm border border-[var(--groww-border)] rounded-lg text-[var(--groww-text-muted)] hover:text-[var(--groww-emerald)] hover:bg-[var(--groww-surface)] transition-all active:scale-90">
              <Share2 size={14} />
            </button>
          </div>
        )}

        {!isUser && message.metadata && (
          <div className="bg-[var(--groww-bg)]/30 border-t border-[var(--groww-border)] p-4 flex flex-col gap-3">
            {message.metadata.source_url && (
              <a 
                href={message.metadata.source_url} 
                target="_blank" 
                rel="noreferrer"
                className="group/link flex items-center justify-between bg-[var(--groww-surface)] hover:border-[var(--groww-emerald)] border border-[var(--groww-border)] rounded-xl p-3 shadow-sm transition-all text-left"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center shrink-0 border border-slate-100 shadow-[0_2px_4px_rgba(0,0,0,0.04)] overflow-hidden p-1.5 transition-transform group-hover/link:scale-110">
                     <img src="https://www.sbimf.com/favicon.ico" alt="Source" className="w-full h-full object-contain" />
                  </div>
                  <div className="overflow-hidden">
                    <div className="text-[11px] font-bold text-[var(--groww-text)] truncate flex items-center gap-1.5 uppercase tracking-wide">
                       Original Source <Check size={10} className="text-[var(--groww-emerald)]" />
                    </div>
                    <div className="text-[10px] text-[var(--groww-text-muted)] font-medium truncate max-w-[200px] md:max-w-[320px] group-hover/link:text-[var(--groww-emerald)] transition-colors">
                      {(() => {
                        try {
                          return new URL(message.metadata.source_url).href;
                        } catch {
                          return message.metadata.source_url || "Official Source";
                        }
                      })()}
                    </div>
                  </div>
                </div>
                <ExternalLink size={14} className="text-[var(--groww-text-muted)] group-hover/link:text-[var(--groww-emerald)] shrink-0 ml-2 transition-transform group-hover/link:translate-x-0.5" />
              </a>
            )}
            
            <div className="flex items-center gap-2 text-[10px] text-[var(--groww-text-muted)] font-semibold uppercase tracking-wider px-1">
               <Info size={12} className="text-[var(--groww-emerald)]/70" />
               <span>Last updated from official records: 2026-04-19</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
