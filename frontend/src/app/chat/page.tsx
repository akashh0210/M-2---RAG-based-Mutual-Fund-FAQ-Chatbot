"use client";

import { useState, useEffect, useRef } from "react";
import Sidebar from "@/components/Sidebar";
import MessageBubble from "@/components/MessageBubble";
import InputArea from "@/components/InputArea";
import RightSidebar from "@/components/RightSidebar";
import { ThemeToggle } from "@/components/ThemeToggle";
import { api } from "@/lib/api";
import { Message } from "@/types";
import { Sparkles, MessageSquare, Zap } from "lucide-react";

const QUICK_PROMPTS = [
  "What is the exit load for SBI Bluechip Fund?",
  "How to update nominee details?",
  "What is the minimum SIP amount?",
  "Procedure for NRI to invest?",
];

type ThreadMeta = { id: string, title: string, updatedAt: number };

export default function Home() {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [threadHistory, setThreadHistory] = useState<ThreadMeta[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFundContext, setSelectedFundContext] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Helper: Create new thread
  async function handleNewThread(): Promise<string | null> {
    try {
      const newId = await api.createThread();
      setThreadId(newId);
      setMessages([]);
      localStorage.setItem("rag_active_thread_id", newId);
      return newId;
    } catch (e) {
      console.error("Failed to create thread", e);
      return null;
    }
  }

  // Helper: Load specific thread
  async function loadThread(id: string) {
    setThreadId(id);
    localStorage.setItem("rag_active_thread_id", id);
    try {
      const thread = await api.getThread(id);
      setMessages(thread.history || []);
    } catch (e) {
      console.error("Failed to fetch history:", e);
      setMessages([]);
    }
  }

  // Helper: Update history list
  function updateThreadHistory(id: string, newMessage: string) {
    setThreadHistory(prev => {
      const filtered = prev.filter(t => t.id !== id);
      const updated = [{ id, title: newMessage.substring(0, 30) + "...", updatedAt: Date.now() }, ...filtered].slice(0, 20);
      localStorage.setItem("rag_threads", JSON.stringify(updated));
      return updated;
    });
  }

  // Core: Processing message
  async function triggerMessage(tid: string, query: string, curHistory: ThreadMeta[]) {
    const queryWithContext = selectedFundContext 
      ? `[Context: ${selectedFundContext}] ${query}` 
      : query;

    const userMessage: Message = { role: "user", content: query };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    if (messages.length === 0 && curHistory.length === 0) {
      updateThreadHistory(tid, query);
    } else {
      updateThreadHistory(tid, curHistory.find(t => t.id === tid)?.title || query);
    }

    try {
      const resp = await api.sendMessage(tid, queryWithContext);
      const assistantMessage: Message = {
        role: "assistant",
        content: resp.answer,
        metadata: {
          intent: resp.intent,
          scheme_name: resp.scheme_name || undefined,
          source_url: resp.source_url || undefined,
          is_refused: resp.is_refused
        }
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (e) {
      console.error("Send failed:", e);
      setMessages((prev) => [...prev, { 
        role: "assistant", 
        content: "I'm sorry, I'm having trouble connecting to the service." 
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  // Core: Send message from UI
  async function handleSendMessage(query: string) {
    if (!threadId || isLoading) return;
    await triggerMessage(threadId, query, threadHistory);
  }

  // Effect: Initialization
  useEffect(() => {
    const savedThreads = JSON.parse(localStorage.getItem("rag_threads") || "[]") as ThreadMeta[];
    setThreadHistory(savedThreads);

    async function init() {
      const urlParams = new URLSearchParams(window.location.search);
      const autoQuery = urlParams.get('q');
      let currentThreadId = localStorage.getItem("rag_active_thread_id");

      if (currentThreadId && savedThreads.find(t => t.id === currentThreadId) && !autoQuery) {
        await loadThread(currentThreadId);
      } else {
        currentThreadId = await handleNewThread();
      }

      if (autoQuery && currentThreadId) {
        window.history.replaceState({}, '', '/chat');
        setTimeout(() => {
           triggerMessage(currentThreadId!, autoQuery, savedThreads);
        }, 100);
      }
    }
    init();
  }, []);

  // Effect: Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="flex h-screen bg-[var(--groww-border)] p-0 md:p-4 transition-colors duration-300">
      <div className="flex w-full max-w-[1400px] mx-auto bg-[var(--groww-surface)] md:rounded-3xl shadow-2xl overflow-hidden border border-[var(--groww-border)] transition-colors duration-300">
        
        {/* Left Sidebar */}
        <Sidebar 
          onNewThread={handleNewThread} 
          activeThreadId={threadId}
          threadHistory={threadHistory}
          onSelectThread={loadThread}
        />
        
        {/* Center Canvas */}
        <main className="flex-1 flex flex-col min-w-0 bg-[var(--groww-bg)] transition-colors duration-300 relative">
          {/* Header */}
          <div className="p-4 border-b border-[var(--groww-border)] bg-[var(--groww-surface)]/80 backdrop-blur-md flex items-center justify-between z-10">
            <div className="flex items-center gap-3">
               <div className="w-10 h-10 rounded-full bg-[var(--groww-emerald)]/10 flex items-center justify-center border border-[var(--groww-emerald)]/20">
                  <MessageSquare className="text-[var(--groww-emerald)] w-5 h-5" />
               </div>
               <div>
                 <h2 className="font-bold text-[var(--groww-text)]">MF Assistant</h2>
                 <p className="text-[10px] text-[var(--groww-emerald)] font-bold uppercase tracking-wider">Session Active</p>
               </div>
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
            </div>
          </div>

          {/* Chat Messages */}
          <div 
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-4 md:p-8 space-y-2 scroll-smooth"
          >
            {messages.length === 0 && !isLoading ? (
              <div className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto space-y-8 animate-in fade-in zoom-in duration-500">
                <div className="w-20 h-20 bg-[var(--groww-emerald)]/10 rounded-3xl flex items-center justify-center shadow-inner">
                    <Sparkles size={40} className="text-[var(--groww-emerald)]" />
                </div>
                <div>
                   <h3 className="text-2xl font-bold text-[var(--groww-text)]">Hello! I'm your SBI MF Expert.</h3>
                   <p className="text-sm text-[var(--groww-text-muted)] mt-2">
                     Ask me anything about fund details, exit loads, expense ratios, or SIP processes. I only speak in facts!
                   </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full mt-8">
                  {QUICK_PROMPTS.map((prompt, i) => (
                    <button 
                      key={i} 
                      onClick={() => handleSendMessage(prompt)}
                      className="text-left px-4 py-3 rounded-xl border border-[var(--groww-border)] bg-[var(--groww-surface)] hover:border-[var(--groww-emerald)] hover:shadow-sm transition-all text-sm text-[var(--groww-text)] flex items-center gap-3 group"
                    >
                      <Zap size={16} className="text-[var(--groww-emerald)] opacity-50 group-hover:opacity-100" />
                      <span>{prompt}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m, i) => (
                <MessageBubble key={i} message={m} />
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start mb-6">
                <div className="bg-[var(--groww-surface)] border border-[var(--groww-border)] rounded-2xl rounded-bl-none p-4 flex gap-2">
                   <div className="w-2 h-2 bg-[var(--groww-emerald)] rounded-full animate-bounce [animation-delay:-0.3s]" />
                   <div className="w-2 h-2 bg-[var(--groww-emerald)] rounded-full animate-bounce [animation-delay:-0.15s]" />
                   <div className="w-2 h-2 bg-[var(--groww-emerald)] rounded-full animate-bounce" />
                </div>
              </div>
            )}
          </div>

          <InputArea 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading} 
          />
        </main>

        {/* Right Sidebar */}
        <RightSidebar onFundSelect={setSelectedFundContext} />
      </div>
    </div>
  );
}
