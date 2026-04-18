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
          <a key={i} href={part} target="_blank" rel="noreferrer" className="text-blue-200 hover:underline font-medium underline underline-offset-2">
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
      "flex w-full mb-6 relative group",
      isUser ? "justify-end" : "justify-start"
    )}>
      <div className={cn(
        "max-w-[90%] md:max-w-[80%] rounded-2xl p-4 shadow-sm relative transition-colors duration-300",
        isUser 
          ? "bg-gradient-to-br from-[var(--groww-emerald)] to-teal-500 text-white rounded-br-none" 
          : "bg-[var(--groww-surface)] border border-[var(--groww-border)] text-[var(--groww-text)] rounded-bl-none"
      )}>
        <div className="text-sm md:text-base whitespace-pre-wrap leading-relaxed">
          {isUser ? linkifyText(message.content) : linkifyAssistantText(message.content)}
        </div>

        {!isUser && (
          <div className="absolute -right-12 top-0 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={handleCopy} className="p-2 bg-[var(--groww-surface)] border border-[var(--groww-border)] rounded-full text-[var(--groww-text-muted)] hover:text-[var(--groww-emerald)] shadow-sm">
              {copied ? <Check size={14} /> : <Copy size={14} />}
            </button>
            <button onClick={handleShare} className="p-2 bg-[var(--groww-surface)] border border-[var(--groww-border)] rounded-full text-[var(--groww-text-muted)] hover:text-[var(--groww-emerald)] shadow-sm">
              <Share2 size={14} />
            </button>
          </div>
        )}

        {!isUser && message.metadata && (
          <div className="mt-5 pt-4 border-t border-[var(--groww-border)] flex flex-col gap-3">
            {message.metadata.source_url && (
              <a 
                href={message.metadata.source_url} 
                target="_blank" 
                rel="noreferrer"
                className="flex items-center justify-between bg-[var(--groww-bg)] hover:bg-[var(--groww-border)] border border-[var(--groww-border)] rounded-xl p-3 transition-colors text-left"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center shrink-0 shadow-sm overflow-hidden p-1">
                     <img src="https://www.sbimf.com/favicon.ico" alt="SBI MF" className="w-full h-full object-contain" onError={(e) => { e.currentTarget.style.display='none'; }} />
                  </div>
                  <div className="overflow-hidden">
                    <div className="text-xs font-semibold text-[var(--groww-text)] truncate flex items-center gap-2">
                       Verified Fact Card <Check size={12} className="text-[var(--groww-emerald)]" />
                    </div>
                    <div className="text-[10px] text-[var(--groww-emerald)] truncate max-w-[200px] md:max-w-[400px]">
                      {new URL(message.metadata.source_url).hostname.replace('www.', '')}
                    </div>
                  </div>
                </div>
                <ExternalLink size={16} className="text-[var(--groww-text-muted)] shrink-0 ml-2" />
              </a>
            )}
            
            <div className="flex items-center gap-2 text-[10px] text-[var(--groww-text-muted)] font-medium px-1">
               <Info size={12} className="text-[var(--groww-emerald)]" />
               <span>Answers are synthesized only from official SBI Mutual Fund documentation.</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
