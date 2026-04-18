"use client";

import Link from "next/link";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ArrowRight, Database, ShieldCheck, Zap } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--groww-bg)] flex flex-col transition-colors duration-300">
      {/* Navigation */}
      <nav className="p-6 border-b border-[var(--groww-border)] bg-[var(--groww-surface)]/80 backdrop-blur-md sticky top-0 z-50 transition-colors duration-300">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[var(--groww-emerald)] rounded-lg flex items-center justify-center shadow-sm text-white">
                <ShieldCheck className="w-5 h-5" />
            </div>
            <h1 className="font-bold text-xl tracking-tight text-[var(--groww-text)]">Mutual Funds <span className="text-[var(--groww-emerald)]">AI</span></h1>
          </div>
          <ThemeToggle />
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
        
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--groww-emerald)]/10 text-[var(--groww-emerald)] text-sm font-semibold mb-4 border border-[var(--groww-emerald)]/20">
          <Database size={14} />
          <span>Trained on latest SBI Mutual Fund Facts</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-[var(--groww-text)]">
          Zero Hallucinations.<br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--groww-emerald)] to-teal-500">
            Just Facts.
          </span>
        </h1>
        
        <p className="text-lg md:text-xl text-[var(--groww-text-muted)] max-w-2xl px-4 leading-relaxed">
          Ask anything about Exit Loads, SIP procedures, Navs, and Expense ratios. 
          Our RAG engine retrieves data directly from official documentation to provide you with verified answers.
        </p>

        <div className="pt-8 flex flex-col items-center gap-6 w-full">
          <Link 
            href="/chat"
            className="group inline-flex items-center gap-3 bg-[var(--groww-emerald)] hover:bg-teal-500 text-white px-8 py-4 rounded-xl text-lg font-bold transition-all shadow-lg hover:shadow-xl hover:-translate-y-1"
          >
            Launch Assistant
            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
          </Link>

          <div className="flex flex-wrap items-center justify-center gap-3 w-full max-w-3xl">
            <span className="text-sm font-semibold text-[var(--groww-text-muted)] w-full block mb-2">Or quick-launch the most common questions:</span>
            <Link href="/chat?q=What+is+the+exit+load+for+SBI+Bluechip+Fund" className="px-4 py-2 bg-[var(--groww-surface)] border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-full text-sm font-medium transition-colors shadow-sm hover:text-[var(--groww-emerald)]">
              SBI Bluechip Exit Loads
            </Link>
            <Link href="/chat?q=How+to+update+nominee+details" className="px-4 py-2 bg-[var(--groww-surface)] border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-full text-sm font-medium transition-colors shadow-sm hover:text-[var(--groww-emerald)]">
              Nominee Updates
            </Link>
            <Link href="/chat?q=What+is+the+process+for+NRI+investment" className="px-4 py-2 bg-[var(--groww-surface)] border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-full text-sm font-medium transition-colors shadow-sm hover:text-[var(--groww-emerald)]">
              NRI Investment Process
            </Link>
             <Link href="/chat?q=What+is+the+minimum+SIP+amount+for+SBI+Small+Cap" className="px-4 py-2 bg-[var(--groww-surface)] border border-[var(--groww-border)] hover:border-[var(--groww-emerald)] text-[var(--groww-text)] rounded-full text-sm font-medium transition-colors shadow-sm hover:text-[var(--groww-emerald)]">
              SBI Small Cap SIP Details
            </Link>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full pt-16">
          <div className="bg-[var(--groww-surface)] p-6 rounded-2xl border border-[var(--groww-border)] text-left shadow-sm">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/40 rounded-lg flex items-center justify-center mb-4 text-blue-600 dark:text-blue-400">
              <Database size={20} />
            </div>
            <h3 className="font-bold text-[var(--groww-text)] mb-2">261 Verified Data Chunks</h3>
            <p className="text-sm text-[var(--groww-text-muted)]">Vector embeddings across Index funds, Flexicaps, ELSS, and core processes.</p>
          </div>
          
          <div className="bg-[var(--groww-surface)] p-6 rounded-2xl border border-[var(--groww-border)] text-left shadow-sm">
            <div className="w-10 h-10 bg-amber-100 dark:bg-amber-900/40 rounded-lg flex items-center justify-center mb-4 text-amber-600 dark:text-amber-400">
              <Zap size={20} />
            </div>
            <h3 className="font-bold text-[var(--groww-text)] mb-2">Lightning Fast RAG</h3>
            <p className="text-sm text-[var(--groww-text-muted)]">Powered by Llama 3.3 70B & Chroma vector search for sub-second responses.</p>
          </div>

          <div className="bg-[var(--groww-surface)] p-6 rounded-2xl border border-[var(--groww-border)] text-left shadow-sm">
            <div className="w-10 h-10 bg-emerald-100 dark:bg-emerald-900/40 rounded-lg flex items-center justify-center mb-4 text-emerald-600 dark:text-emerald-400">
              <ShieldCheck size={20} />
            </div>
            <h3 className="font-bold text-[var(--groww-text)] mb-2">Strict Policy Guardrails</h3>
            <p className="text-sm text-[var(--groww-text-muted)]">Automatic intent classification refuses unsolicited financial advice.</p>
          </div>
        </div>

      </main>

      {/* Footer */}
      <footer className="py-8 text-center text-sm text-[var(--groww-text-muted)] border-t border-[var(--groww-border)] mt-auto">
        Phase 8.2 Deployment · Built for strict factual retrieval
      </footer>
    </div>
  );
}
