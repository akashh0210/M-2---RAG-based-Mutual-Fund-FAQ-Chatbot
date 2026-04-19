"use client";

import Link from "next/link";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ArrowRight, Database, ShieldCheck, Zap } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--groww-bg)] flex flex-col transition-colors duration-300">
      {/* Navigation */}
      <nav className="p-4 border-b border-[var(--groww-border)] bg-[var(--groww-surface)]/80 backdrop-blur-md sticky top-0 z-50 transition-colors duration-300">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-[var(--groww-emerald)] rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white">
                <ShieldCheck className="w-6 h-6" />
            </div>
            <h1 className="font-bold text-xl tracking-tight text-[var(--groww-text)]">Groww <span className="text-[var(--groww-emerald)]">MF Assistant</span></h1>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/chat" className="text-sm font-semibold text-[var(--groww-text)] hover:text-[var(--groww-emerald)] transition-colors hidden md:block">
              Launch Bot
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-5xl mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
        
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[var(--groww-emerald)]/10 text-[var(--groww-emerald)] text-xs font-bold border border-[var(--groww-emerald)]/20 tracking-wider uppercase">
          <ShieldCheck size={14} />
          <span>Facts-only • No investment advice</span>
        </div>

        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-[var(--groww-text)] leading-tight">
            Mutual Fund FAQs <br className="hidden md:block" />
            <span className="text-[var(--groww-text-muted)]">from Official Sources</span>
          </h1>
          
          <p className="text-base md:text-lg text-[var(--groww-text-muted)] max-w-2xl px-4 leading-relaxed mx-auto">
            Ask factual questions about selected SBI Mutual Fund schemes and get short answers backed by official public sources. 
            <span className="block mt-2 font-medium text-[var(--groww-text)]">Short answers. One official source link. No recommendations.</span>
          </p>
        </div>

        <div className="flex flex-col items-center gap-8 w-full">
          <Link 
            href="/chat"
            className="group btn-primary text-lg !px-10 !py-4 flex items-center gap-3"
          >
            Launch Assistant
            <ArrowRight size={22} className="group-hover:translate-x-1 transition-transform" />
          </Link>

          <div className="space-y-4 w-full">
            <span className="text-xs font-bold text-[var(--groww-text-muted)] uppercase tracking-widest">Experience the facts-first engine:</span>
            <div className="flex flex-wrap items-center justify-center gap-3 max-w-4xl mx-auto">
              <Link href="/chat?q=What+is+the+exit+load+for+SBI+Bluechip+Fund" className="px-5 py-2.5 bg-[var(--groww-surface)] border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-xl text-sm font-medium transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5">
                SBI Bluechip Exit Loads
              </Link>
              <Link href="/chat?q=How+to+update+nominee+details" className="px-5 py-2.5 bg-[var(--groww-surface)] border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-xl text-sm font-medium transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5">
                Nominee Updates
              </Link>
              <Link href="/chat?q=What+is+the+minimum+SIP+amount+for+SBI+Small+Cap" className="px-5 py-2.5 bg-[var(--groww-surface)] border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-xl text-sm font-medium transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5">
                SBI Small Cap Min SIP
              </Link>
            </div>
          </div>
        </div>

        {/* Value Strip */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 w-full pt-12 border-t border-[var(--groww-border)]">
          <div className="flex items-center gap-3 justify-center md:justify-start">
            <div className="p-2 rounded-lg bg-[var(--groww-emerald)]/10 text-[var(--groww-emerald)]"><Database size={18} /></div>
            <span className="text-xs font-semibold text-[var(--groww-text-muted)]">Official Public Sources Only</span>
          </div>
          <div className="flex items-center gap-3 justify-center md:justify-start">
            <div className="p-2 rounded-lg bg-[var(--groww-emerald)]/10 text-[var(--groww-emerald)]"><ArrowRight size={18} /></div>
            <span className="text-xs font-semibold text-[var(--groww-text-muted)]">One Source Link per Answer</span>
          </div>
          <div className="flex items-center gap-3 justify-center md:justify-start">
            <div className="p-2 rounded-lg bg-[var(--groww-emerald)]/10 text-[var(--groww-emerald)]"><ShieldCheck size={18} /></div>
            <span className="text-xs font-semibold text-[var(--groww-text-muted)]">No Investment Advice</span>
          </div>
          <div className="flex items-center gap-3 justify-center md:justify-start">
            <div className="p-2 rounded-lg bg-[var(--groww-emerald)]/10 text-[var(--groww-emerald)]"><ShieldCheck size={18} /></div>
            <span className="text-xs font-semibold text-[var(--groww-text-muted)]">Zero Personal Data Required</span>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 text-center text-sm text-[var(--groww-text-muted)] border-t border-[var(--groww-border)] mt-auto">
        Groww MF Assistant · Factual Retrieval System
      </footer>
    </div>
  );
}
