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
  const recentUpdates = sources.filter(s => s.status === "updated" || s.status === "success").slice(0, 5);
  // Get unique funds
  const uniqueFunds = Array.from(new Set(sources.filter(s => s.scheme_name).map(s => s.scheme_name as string))).sort();

  return (
    <div className="w-72 border-l border-[var(--groww-border)] h-full bg-[var(--groww-surface)] flex flex-col hidden lg:flex">
      
      {/* Fund Selector */}
      <div className="p-4 border-b border-[var(--groww-border)]">
        <h3 className="text-sm font-bold text-[var(--groww-text)] mb-3">Context Filter</h3>
        <select 
          className="w-full bg-[var(--groww-bg)] border border-[var(--groww-border)] text-sm rounded-lg p-2.5 outline-none focus:border-[var(--groww-emerald)] text-[var(--groww-text)]"
          value={selectedFund}
          onChange={(e) => handleFundSelect(e.target.value)}
        >
          <option value="ALL">All Funds (Auto-detect)</option>
          {uniqueFunds.map(fund => (
            <option key={fund} value={fund}>{fund}</option>
          ))}
        </select>
        <p className="text-[10px] text-[var(--groww-text-muted)] mt-2">
          Selecting a specific fund guides the AI to prioritize that context.
        </p>
      </div>

      {/* Recently Ingested / System Status */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
         <h3 className="text-sm font-bold text-[var(--groww-text)] uppercase tracking-tight">System Knowledge</h3>
         
         <div className="space-y-3">
            {recentUpdates.length > 0 ? recentUpdates.map((src, i) => (
              <div key={i} className="bg-[var(--groww-bg)] border border-[var(--groww-border)] p-3 rounded-xl">
                 <div className="flex justify-between items-start mb-1">
                   <div className="text-xs font-semibold text-[var(--groww-text)] line-clamp-2">
                     {src.scheme_name || "General Guidelines"}
                   </div>
                   <div className="w-2 h-2 rounded-full bg-[var(--groww-emerald)] mt-1 shrink-0" />
                 </div>
                 <div className="text-[10px] text-[var(--groww-text-muted)] mb-2 break-words">
                   {new URL(src.official_url).pathname.substring(0, 30)}...
                 </div>
                 <div className="text-[9px] text-[var(--groww-text-muted)] font-mono">
                   {new Date(src.last_crawled_at).toLocaleDateString()} {new Date(src.last_crawled_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                 </div>
              </div>
            )) : (
               <div className="text-xs text-[var(--groww-text-muted)]">No recent updates.</div>
            )}
         </div>
      </div>

    </div>
  );
}
