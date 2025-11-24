"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import LottiePlayer from "@/components/LottiePlayer";
import { X } from "lucide-react";

export default function ChatPage() {
  const [showChat, setShowChat] = useState(false);
  const [promptVisible, setPromptVisible] = useState(true);

  // Chat state uses variables from backend
  const [messages, setMessages] = useState<Array<{ id: number; from: "bot" | "user"; text: string; time: string }>>([
    { id: 1, from: "bot", text: "Hello! How can I help you?", time: new Date().toLocaleTimeString() },
    { id: 2, from: "user", text: "Find trials for breast cancer", time: new Date().toLocaleTimeString() },
  ]);
  const [inputValue, setInputValue] = useState("");
  const listRef = useRef<HTMLDivElement | null>(null);
  const [scrollPercent, setScrollPercent] = useState(100);
  const [sliderLength, setSliderLength] = useState(240);

  // Auto-scroll to bottom when messages come in
  useEffect(() => {
    const el = listRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
      // after auto-scrolling to bottom, reflect that in the slider
      setScrollPercent(100);
    }
  }, [messages]);

  // Keep slider length in sync with the visible chat area
  useEffect(() => {
    function updateLength() {
      const el = listRef.current;
      if (!el) return;
      setSliderLength(el.clientHeight);
      updateScrollPercent();
    }
    updateLength();
    window.addEventListener("resize", updateLength);
    return () => window.removeEventListener("resize", updateLength);
  }, []);

  function updateScrollPercent() {
    const el = listRef.current;
    if (!el) return;
    const max = el.scrollHeight - el.clientHeight;
    if (max <= 0) {
      setScrollPercent(100);
      return;
    }
    const pct = Math.round((el.scrollTop / max) * 100);
    setScrollPercent(pct);
  }

  function sendMessage(text: string) {
    const userMsg = { id: Date.now(), from: "user" as const, text, time: new Date().toLocaleTimeString() };
    setMessages((m) => [...m, userMsg]);

    // Simulate bot reply after a short delay
    setTimeout(() => {
      const botMsg = {
        id: Date.now() + 1,
        from: "bot" as const,
        text: `I found several trials related to \"${text}\". Would you like me to filter by location or phase?`,
        time: new Date().toLocaleTimeString(),
      };
      setMessages((m) => [...m, botMsg]);
    }, 700);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed) return;
    sendMessage(trimmed);
    setInputValue("");
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 space-y-6">
      {/* Initial Prompt Box */}
      {!showChat && promptVisible && (
        <div className="relative border border-color-teal rounded-2xl shadow-xl p-6 w-full max-w-md text-center space-y-4 animate-fadeIn">
          <button
            type="button"
            aria-label="Close prompt"
            className="absolute top-3 right-3 p-1 rounded-md hover:bg-gray-100"
            onClick={() => setPromptVisible(false)}
          >
            <X className="h-4 w-4" aria-hidden />
          </button>
          <h2 className="text-xl font-semibold text-teal-300">Are you looking for a clinical trial?</h2>

          <Button
            className="w-46 py-3 text-lg rounded-xl bg-red-300 text-teal-100"
            onClick={() => setShowChat(true)}
          >
            Chat with Bot Carrie
          </Button>

          <LottiePlayer
            src="https://lottie.host/a04b146d-7246-4edd-9af3-c8dcd38589e9/UfllrLR1Du.lottie"
            className="mx-auto max-w-xs"
          />
        </div>
      )}

      {/* Chatbox appears when user clicks */}
      {showChat && (
        <>
          <LottiePlayer
            src="https://lottie.host/f780d2ad-49b2-40a2-ba28-0246f06db2f5/M1Mbf5t6r1.lottie"
            className="mx-auto max-w-xs"
          />

          <h1 className="text-2xl font-bold text-center text-teal-300 animate-fadeIn">Chat with Bot Carrie</h1>

          <div className="relative max-w-md mx-auto w-full">
            <Card className="p-2 space-y-2 w-full animate-fadeIn">
              {/* the backend messages will go here */}
              <CardContent ref={listRef} onScroll={updateScrollPercent} className="h-96 overflow-y-auto flex flex-col gap-8">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex items-end ${m.from === "user" ? "justify-end" : "justify-start"}`}>
                  {m.from === "bot" && (
                    <div className="flex-shrink-0 mr-3">
                      <div className="h-12 w-12 rounded-full bg-red-300 flex items-center justify-center text-teal-100 font-semibold">Carrie</div>
                    </div>
                  )}

                  <div className={`px-3 py-2 rounded-2xl max-w-[80%] ${m.from === "user" ? "bg-blue-100" : "bg-red-300"} animate-fadeIn`}> 
                    <div className="whitespace-pre-wrap">{m.text}</div>
                    {/* provides a timestamp of conversation  */}
                    <div className="text-xs text-muted-foreground mt-1 text-right">{m.time}</div>
                  </div>

                  {m.from === "user" && (
                    <div className="flex-shrink-0 ml-3">
                      <div className="h-12 w-12 rounded-full bg-blue-300 flex items-center justify-center text-teal-100 font-semibold">Guest</div>
                    </div>
                  )}
                </div>
              ))}

              </CardContent>

              <form onSubmit={handleSubmit} className="flex gap-2 hover:bg-red-300">
              <Input value={inputValue} onChange={(e) => setInputValue(e.target.value)} placeholder="Ask about a clinical trial..." />
              <Button type="submit" className="text-teal-300 hover:bg-red-300">Send</Button>
              </form>
                        {/* Disclaimer footer below the input */}
                        <div className="mt-3 text-xs text-muted-foreground text-center px-2">
                          <p>
                            <b>Disclaimer:</b> This chatbot does not provide medical advice. We encourage you to discuss all results and further questions with a clinician. Clinical trial information is taken from{' '}
                            <a
                              href="https://clinicaltrials.gov/"
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary underline"
                            >
                              clinicaltrials.gov
                            </a>
                            .
                          </p>
                        </div>
            </Card>

            {/* Vertical slider control on the right to control scroll position */}
            <div className="absolute right-0 top-4 bottom-4 flex items-center pr-2  overflow-visible hidden md:block">
              <input
                aria-label="Scroll chat"
                type="range"
                min={0}
                max={100}
                value={scrollPercent}
                onKeyDown={(e) => {
                  if (e.key === "ArrowUp" || e.key === "ArrowDown") {
                    e.preventDefault();
                    const delta = e.key === "ArrowUp" ? -5 : 5;
                    const next = Math.max(0, Math.min(100, scrollPercent + delta));
                    setScrollPercent(next);
                    const el = listRef.current;
                    if (!el) return;
                    const max = el.scrollHeight - el.clientHeight;
                    el.scrollTop = Math.round((next / 100) * max);
                  }
                }}
                onChange={(e) => {
                  const v = Number(e.target.value);
                  setScrollPercent(v);
                  const el = listRef.current;
                  if (!el) return;
                  const max = el.scrollHeight - el.clientHeight;
                  el.scrollTop = Math.round((v / 100) * max);
                }}
                className="range-slider"
                style={{ width: `${sliderLength}px`, transform: "rotate(-90deg)", transformOrigin: "center right" }}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
