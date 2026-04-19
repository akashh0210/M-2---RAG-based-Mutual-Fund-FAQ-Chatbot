"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

interface SourceDoc {
  scheme_name: string | null;
  official_url: string;
  status: string;
  last_crawled_at: string;
}

export default function RightSidebar({ onFundSelect }: { onFundSelect: (fund: string | null) => void }) {
  const [sources, setSources] = useState<SourceDoc[]>([]);
  const [selectedFund, setSelectedFund] = useState<string | "ALL">("ALL");

  useEffect(() => {
    // Initial fetch of sources
    api.listSources().then((data) => {
      setSources(data);
    }).catch((e) => console.error("Failed to load sources", e));
  }, []);

  const handleFundSelect = (fundName: string) => {
    setSelectedFund(fundName);
    onFundSelect(fundName === "ALL" ? null : fundName);
  };

  // Group by status
  const recentUpdates = sources.filter(s => ["updated", "success", "active"].includes(s.status)).slice(0, 6);
  // Get unique funds
  const uniqueFunds = Array.from(new Set(sources.filter(s => s.scheme_name).map(s => s.scheme_name as string))).sort();

  return (
    <div className="w-72 border-l border-[var(--groww-border)] h-full bg-[var(--groww-bg)] flex flex-col hidden lg:flex">
      
      {/* Fund Selector */}
      <div className="p-6 border-b border-[var(--groww-border)]">
        <h3 className="text-[10px] font-bold text-[var(--groww-text-muted)] uppercase tracking-[0.2em] mb-4">Focus Context</h3>
        <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
          <button 
            onClick={() => handleFundSelect("ALL")}
            className={`w-full text-left p-3 rounded-xl text-xs font-bold transition-all border ${
              selectedFund === "ALL" 
              ? "bg-[var(--groww-emerald)] text-white border-[var(--groww-emerald)] shadow-lg shadow-emerald-500/20" 
              : "bg-[var(--groww-surface)] border-[var(--groww-border)] text-[var(--groww-text)] hover:border-[var(--groww-emerald)]/50"
            }`}
          >
            Auto-detect Context
          </button>
          
          {uniqueFunds.map(fund => (
            <button 
              key={fund}
              onClick={() => handleFundSelect(fund)}
              className={`w-full text-left p-3 rounded-xl text-[11px] font-bold transition-all border ${
                selectedFund === fund 
                ? "bg-[var(--groww-emerald)] text-white border-[var(--groww-emerald)] shadow-lg shadow-emerald-500/20" 
                : "bg-[var(--groww-surface)] border-[var(--groww-border)] text-[var(--groww-text)] hover:border-[var(--groww-emerald)]/50 hover:bg-[var(--groww-emerald)]/[0.02]"
              }`}
            >
              {fund}
            </button>
          ))}
        </div>
      </div>

      {/* Recently Ingested / System Status */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
         <h3 className="text-[10px] font-bold text-[var(--groww-text-muted)] uppercase tracking-[0.2em]">Verified Knowledge Base</h3>
         
         <div className="space-y-4">
            {recentUpdates.length > 0 ? recentUpdates.map((src, i) => (
              <div key={i} className="group/item flex flex-col gap-1 transition-all">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[var(--groww-emerald)]" />
                    <div className="text-[11px] font-bold text-[var(--groww-text)] group-hover/item:text-[var(--groww-emerald)] transition-colors line-clamp-1">
                      {src.scheme_name || "Service Portal"}
                    </div>
                  </div>
                  <div className="text-[10px] text-[var(--groww-text-muted)] font-medium pl-3.5 flex items-center justify-between">
                    <span>{new URL(src.official_url).hostname.replace('www.', '')}</span>
                    <span className="opacity-0 group-hover/item:opacity-100 transition-opacity">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    </span>
                  </div>
              </div>
            )) : (
               <div className="text-[10px] text-[var(--groww-text-muted)] font-bold italic tracking-wider opacity-50 uppercase">Loading dataset...</div>
            )}
         </div>
      </div>

      <div className="p-6 mt-auto">
        <div className="bg-[var(--groww-surface)] border border-[var(--groww-border)] rounded-2xl p-4 shadow-sm">
          <div className="text-[10px] font-bold text-[var(--groww-text-muted)] uppercase tracking-widest mb-1 leading-none">Status</div>
          <div className="flex items-center justify-between">
             <span className="text-xs font-bold text-[var(--groww-text)]">Vercel Edge</span>
             <span className="text-[9px] font-black text-white bg-[var(--groww-emerald)] px-1.5 py-0.5 rounded leading-none">PROD</span>
          </div>
        </div>
      </div>

    </div>
  );
}
