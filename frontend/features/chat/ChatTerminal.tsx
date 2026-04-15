"use client";

import { useState, useRef, useEffect } from "react";
import { useChatStore } from "@/stores/chatStore";
import { streamClient } from "@/lib/api/client";
import { Button, Card, Input, Badge } from "@/components/ui/core";
import { Send, Bot, User, Loader2, Info, CheckCircle2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { motion, AnimatePresence } from "framer-motion";

export function ChatTerminal() {
  const [input, setInput] = useState("");
  const { messages, addMessage, updateLastMessage, isStreaming, setStreaming } = useChatStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userQuery = input;
    setInput("");
    
    addMessage({ role: "user", content: userQuery });
    addMessage({ role: "assistant", content: "", confidence: 0.95 }); // Placeholder for streaming
    
    setStreaming(true);
    let fullResponse = "";

    try {
      await streamClient("/api/chat/stream", { query: userQuery }, (token) => {
        fullResponse += token;
        updateLastMessage(token);
      });
    } catch (error) {
      console.error("Chat Error:", error);
      updateLastMessage("\n\n**Error:** Failed to connect to AI engine.");
    } finally {
      setStreaming(false);
    }
  };

  return (
    <Card className="h-[calc(100vh-200px)] flex flex-col bg-card/40 border-border/50 shadow-2xl">
      <div className="p-4 border-b border-border/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="text-primary" size={20} />
          <h2 className="font-bold text-sm uppercase tracking-widest text-muted-foreground">Intelligence Terminal</h2>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="bg-background/50">SQL Engine</Badge>
          <Badge variant="outline" className="bg-background/50">RAG Layer</Badge>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
            <Bot size={48} className="mb-4" />
            <p className="text-lg font-medium">How can I assist your market analysis today?</p>
            <p className="text-sm">Try asking about revenue trends or sentiment analysis.</p>
          </div>
        )}

        {messages.map((m, i) => (
          <motion.div
            key={m.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
              "flex gap-4",
              m.role === "assistant" ? "items-start" : "items-start flex-row-reverse"
            )}
          >
            <div className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-1 shadow-glow",
              m.role === "assistant" ? "bg-primary text-white" : "bg-muted text-foreground"
            )}>
              {m.role === "assistant" ? <Bot size={18} /> : <User size={18} />}
            </div>
            
            <div className={cn(
              "flex flex-col gap-2 max-w-[80%]",
              m.role === "user" && "items-end"
            )}>
              <div className={cn(
                "p-4 rounded-2xl text-sm leading-relaxed",
                m.role === "assistant" 
                  ? "bg-muted/80 text-foreground" 
                  : "bg-primary text-white"
              )}>
                <ReactMarkdown className="prose prose-invert prose-sm">
                  {m.content}
                </ReactMarkdown>
                {m.role === "assistant" && isStreaming && i === messages.length - 1 && (
                  <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse" />
                )}
              </div>

              {m.role === "assistant" && m.content && (
                <AnimatePresence>
                  <motion.div 
                    initial={{ opacity: 0 }} 
                    animate={{ opacity: 1 }}
                    className="flex flex-wrap gap-2"
                  >
                    {m.confidence && (
                      <Badge variant="success" className="gap-1 px-2 py-0.5">
                        <CheckCircle2 size={12} /> {Math.round(m.confidence * 100)}% Confidence
                      </Badge>
                    )}
                    {m.sources && (
                      <div className="flex gap-1">
                        {m.sources.map((s, idx) => (
                          <Badge key={idx} variant="outline" className="cursor-pointer hover:bg-accent hover:text-foreground">
                            {s}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </motion.div>
                </AnimatePresence>
              )}
            </div>
          </motion.div>
        ))}
        {isStreaming && (
          <div className="flex gap-4 opacity-50">
            <div className="w-8 h-8 rounded-lg bg-primary text-white flex items-center justify-center">
              <Loader2 size={18} className="animate-spin" />
            </div>
            <div className="bg-muted/50 p-4 rounded-2xl w-24 h-10 animate-pulse" />
          </div>
        )}
      </div>

      <div className="p-4 bg-muted/30 border-t border-border/50">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="flex gap-3"
        >
          <Input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Query the swarm (e.g. 'Show me NVDA sentiment over the last 7 days')"
            className="flex-1"
          />
          <Button type="submit" disabled={!input.trim() || isStreaming}>
            <Send size={18} />
          </Button>
        </form>
        <div className="mt-2 flex items-center gap-4 text-[10px] text-muted-foreground uppercase tracking-widest font-bold px-2">
          <span>Active Engines</span>
          <span className="flex items-center gap-1 text-green-500"><div className="w-1 h-1 rounded-full bg-green-500 animate-pulse" /> SQL</span>
          <span className="flex items-center gap-1 text-green-500"><div className="w-1 h-1 rounded-full bg-green-500 animate-pulse" /> Vector</span>
          <span className="flex items-center gap-1 text-primary"><div className="w-1 h-1 rounded-full bg-primary animate-pulse" /> LLM-70B</span>
        </div>
      </div>
    </Card>
  );
}

const cn = (...inputs: any[]) => inputs.filter(Boolean).join(" ");
