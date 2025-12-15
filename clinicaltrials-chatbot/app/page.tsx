"use client";

import { useState, useEffect, useRef } from "react";
import { healthCheck, postChat } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import LottiePlayer from "@/components/LottiePlayer";
import { X } from "lucide-react";

export default function ChatPage() {
  const [showChat, setShowChat] = useState(false);
  const [promptVisible, setPromptVisible] = useState(true);

  // Questionnaire state
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);
  const [formData, setFormData] = useState({
    gender: "",
    age: "",
    state: "",
    cancerType: "",
    cancerStage: "",
    comorbidities: "",
    priorTreatments: "",
  });

  // Chat state uses variables from backend
  type TrialResult = { nctId: string; title: string; condition: string; phase: string; location: string; url: string };
  type UserMessage = { id: number; from: "user"; text: string; time: string };
  type BotMessage = { id: number; from: "bot"; text: string; time: string; results?: TrialResult[] };
  type Message = UserMessage | BotMessage;

  const [messages, setMessages] = useState<Message[]>([
    { id: 1, from: "bot", text: "Hello! I am Carrie, your clinical trial finder chatbot. Let's find you a trial!", time: new Date().toLocaleTimeString() },
  ]);
  const [inputValue, setInputValue] = useState("");
  const listRef = useRef<HTMLDivElement | null>(null);
  const [scrollPercent, setScrollPercent] = useState(100);
  const [sliderLength, setSliderLength] = useState(240);
  const [connectionStatus, setConnectionStatus] = useState<string | null>(null);

  // Greet and trigger questionnaire after chat opens
  useEffect(() => {
    // Check backend health once on mount
    (async () => {
      const res = await healthCheck();
      if (res.ok) {
        console.info("Backend reachable at", res.path, res.status);
        setConnectionStatus(`ok (${res.path})`);
      } else {
        console.warn("Backend not reachable", res);
        setConnectionStatus(`unreachable`);
      }
    })();

    if (showChat && !showQuestionnaire && messages.length === 1) {
      // After 2 seconds, send the explanation message
      const explanationTimeout = setTimeout(() => {
        setMessages((m: Message[]) => [
          ...m,
          {
            id: Date.now(),
            from: "bot",
            text: "First, if you don't mind, let me ask you just seven questions to narrow down our choices. Do your best to answer, and then, press the find a trial button.",
            time: new Date().toLocaleTimeString(),
          },
        ]);
      }, 3000);

      // After 20 seconds total, show the questionnaire form
      const formTimeout = setTimeout(() => {
        setShowQuestionnaire(true);
      }, 15000);

      return () => {
        clearTimeout(explanationTimeout);
        clearTimeout(formTimeout);
      };
    }
  }, [showChat]);

  // Poll dev injection endpoint when chat is open (dev helper)
  useEffect(() => {
    let id: NodeJS.Timeout | null = null;
    async function fetchInject() {
      try {
        const res = await fetch('/api/dev/inject');
        if (!res.ok) return;
        const json = await res.json();
        if (json?.messages && Array.isArray(json.messages) && json.messages.length > 0) {
          // normalize incoming messages and append
          const toAdd = json.messages.map((m: any) => ({
            id: m.id || Date.now() + Math.floor(Math.random() * 1000),
            from: m.from || 'bot',
            text: m.text || '',
            time: m.time || new Date().toLocaleTimeString(),
            results: m.results || undefined,
          }));
          setMessages((prev: Message[]) => [...prev, ...toAdd]);
        }
      } catch (e) {
        // ignore
      }
    }

    if (showChat) {
      // immediate check
      fetchInject();
      // poll every 3s while chat open
      id = setInterval(fetchInject, 3000);
    }

    return () => {
      if (id) clearInterval(id);
    };
  }, [showChat]);

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

  function handleFormChange(field: string, value: string) {
    setFormData((prev: typeof formData) => ({ ...prev, [field]: value }));
  }

  function submitQuestionnaire() {
    // Validate all fields are filled
    if (!formData.gender || !formData.age || !formData.state || !formData.cancerType || !formData.cancerStage || !formData.comorbidities || !formData.priorTreatments) {
      alert("Please fill in all fields before submitting.");
      return;
    }
    // Log form data (in production, send to backend)
    console.log("Questionnaire submitted:", formData);
    // Add user's summary message to chat
    const summaryText = `Age: ${formData.age}, Gender: ${formData.gender}, State: ${formData.state}, Cancer Type: ${formData.cancerType}, Stage: ${formData.cancerStage}, Comorbidities: ${formData.comorbidities}, Prior Treatments: ${formData.priorTreatments}`;
    setMessages((m: Message[]) => [...m, { id: Date.now(), from: "user", text: summaryText, time: new Date().toLocaleTimeString() }]);
    // Send questionnaire to backend and show response (fallback to simulated reply)
    (async () => {
      try {
        const res = await postChat({ type: 'questionnaire', data: formData });
        if (res?.results && Array.isArray(res.results) && res.results.length > 0) {
          const results: TrialResult[] = res.results.map((r: any) => ({
            nctId: r.nctId || '',
            title: r.title || '',
            condition: r.condition || '',
            phase: r.phase || '',
            location: r.location || '',
            url: r.url || '',
          }));
          setMessages((prev: Message[]) => [
            ...prev,
            { id: Date.now() + 1, from: 'bot', text: `I found ${results.length} trials that might match. Click to view details.`, time: new Date().toLocaleTimeString(), results },
          ]);
        } else {
          const reply = res?.reply || 'Thank you — we received your information and are searching for matches.';
          setMessages((prev: Message[]) => [...prev, { id: Date.now() + 1, from: 'bot', text: reply, time: new Date().toLocaleTimeString() }]);
        }
      } catch (err) {
        setTimeout(() => {
          const botMsg: BotMessage = {
            id: Date.now() + 1,
            from: 'bot',
            text: 'Thank you for providing that information! I am now searching for clinical trials that match your profile. Please wait a moment...',
            time: new Date().toLocaleTimeString(),
          };
          setMessages((prev: Message[]) => [...prev, botMsg]);
        }, 700);
      }
    })();
    // Hide form and return to chat
    setShowQuestionnaire(false);
  }

  function sendMessage(text: string) {
    const userMsg = { id: Date.now(), from: "user" as const, text, time: new Date().toLocaleTimeString() };
    setMessages((m: Message[]) => [...m, userMsg]);

    // Send to backend and append reply (fallback to simulated reply)
    (async () => {
      try {
        const res = await postChat({ type: 'message', text });
        if (res?.results && Array.isArray(res.results) && res.results.length > 0) {
          const results: TrialResult[] = res.results.map((r: any) => ({
            nctId: r.nctId || '',
            title: r.title || '',
            condition: r.condition || '',
            phase: r.phase || '',
            location: r.location || '',
            url: r.url || '',
          }));
          setMessages((prev: Message[]) => [...prev, { id: Date.now() + 1, from: 'bot', text: `I found ${results.length} trials for "${text}".`, time: new Date().toLocaleTimeString(), results }]);
        } else {
          const botText = res?.reply || `I found several trials related to \"${text}\". Would you like me to filter by location or phase?`;
          setMessages((prev: Message[]) => [...prev, { id: Date.now() + 1, from: 'bot', text: botText, time: new Date().toLocaleTimeString() }]);
        }
      } catch (err) {
        // Fallback simulated reply
        setTimeout(() => {
          const botMsg: BotMessage = {
            id: Date.now() + 1,
            from: 'bot',
            text: `I found several trials related to \"${text}\". Would you like me to filter by location or phase?`,
            time: new Date().toLocaleTimeString(),
          };
          setMessages((prev: Message[]) => [...prev, botMsg]);
        }, 700);
      }
    })();
  }

  function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    // Check if all questionnaire fields are filled and form is visible
    if (showQuestionnaire && (formData.gender && formData.age && formData.state && formData.cancerType && formData.cancerStage && formData.comorbidities && formData.priorTreatments)) {
      // User is submitting the questionnaire via send button
      submitQuestionnaire();
      setInputValue("");
      return;
    }

    // Otherwise, send as regular chat message
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
          <h2 className="text-xl font-semibold text-[#1159af]">Are you looking for a clinical trial?</h2>

          <Button
            className="w-46 py-3 text-lg rounded-xl bg-[#1159af] hover:bg-red-300 text-teal-300"
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

          <h1 className="text-2xl font-bold text-center text-[#1159af] animate-fadeIn">Chat with Bot Carrie</h1>

          <div className="relative max-w-md mx-auto w-full">
            <Card className="p-2 space-y-2 w-full animate-fadeIn">
              {/* Chat messages */}
              <CardContent ref={listRef} onScroll={updateScrollPercent} className={`h-96 overflow-y-auto flex flex-col gap-8 ${showQuestionnaire ? "hidden" : ""}`}>
              {messages.map((m: Message) => (
                <div key={m.id} className={`flex items-end ${m.from === "user" ? "justify-end" : "justify-start"}`}>
                  {m.from === "bot" && (
                    <div className="flex-shrink-0 mr-3">
                      <div className="h-12 w-12 rounded-full bg-red-300 flex items-center justify-center text-teal-100 font-semibold">Carrie</div>
                    </div>
                  )}

                  <div className={`px-3 py-2 rounded-2xl max-w-[80%] ${m.from === "user" ? "bg-blue-100" : "bg-red-300"} animate-fadeIn`}>
                    <div className="whitespace-pre-wrap">{m.text}</div>
                    <div className="text-xs text-muted-foreground mt-1 text-right">{m.time}</div>

                    {/* Render structured results if present (bot messages only) */}
                    {'results' in m && m.results && m.results.length > 0 && (
                      <div className="mt-3 grid grid-cols-1 gap-2">
                        {m.results.map((r: TrialResult) => (
                          <a key={r.nctId} href={r.url} target="_blank" rel="noopener noreferrer" className="block p-3 bg-white/20 rounded-lg hover:bg-white/30">
                            <div className="font-semibold">{r.title || r.nctId}</div>
                            <div className="text-xs mt-1">{r.condition}</div>
                            <div className="text-xs mt-1">Phase: {r.phase || 'N/A'} — Location: {r.location || 'N/A'}</div>
                          </a>
                        ))}
                      </div>
                    )}
                  </div>

                  {m.from === "user" && (
                    <div className="flex-shrink-0 ml-3">
                      <div className="h-12 w-12 rounded-full bg-blue-300 flex items-center justify-center text-teal-100 font-semibold">Guest</div>
                    </div>
                  )}
                </div>
              ))}

              </CardContent>

              {/* Questionnaire Form */}
              {showQuestionnaire && (
                <CardContent className="h-96 overflow-y-auto flex flex-col gap-4 p-4">
                  <div className="flex flex-col gap-4">
                    {/* Gender */}
                    <div>
                      <label className="block text-sm font-semibold mb-2">1. What is the gender assigned to you at birth?</label>
                      <div className="flex gap-4">
                        <label className="flex items-center gap-2">
                          <input type="radio" name="gender" value="Female" onChange={(e) => handleFormChange("gender", e.target.value)} required />
                          Female
                        </label>
                        <label className="flex items-center gap-2">
                          <input type="radio" name="gender" value="Male" onChange={(e) => handleFormChange("gender", e.target.value)} required />
                          Male
                        </label>
                      </div>
                    </div>

                    {/* Age */}
                    <div>
                      <label className="block text-sm font-semibold mb-2">2. How old are you?</label>
                      <Input type="number" placeholder="Enter your age" value={formData.age} onChange={(e) => handleFormChange("age", e.target.value)} required />
                    </div>

                    {/* State */}
                    <div>
                      <label className="block text-sm font-semibold mb-2">3. What city and state are you located in?</label>
                      <Input type="text" placeholder="Enter your state" value={formData.state} onChange={(e) => handleFormChange("state", e.target.value)} required />
                    </div>

                    {/* Cancer Type */}
                    <div>
                      <label className="block text-sm font-semibold mb-2">4. Select the type of cancer are you looking for a trial for?</label>
                      <select value={formData.cancerType} onChange={(e) => handleFormChange("cancerType", e.target.value)} className="w-full border rounded px-3 py-2" required>
                        <option value="">Select cancer type...</option>
                        <option value="Lung">Lung</option>
                        <option value="Prostate">Prostate</option>
                        <option value="Breast">Breast</option>
                      </select>
                    </div>

                    {/* Cancer Stage */}
                    <div>
                      <label className="block text-sm font-semibold mb-2">5. What stage of cancer?</label>
                      <select value={formData.cancerStage} onChange={(e) => handleFormChange("cancerStage", e.target.value)} className="w-full border rounded px-3 py-2" required>
                        <option value="">Select stage...</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                      </select>
                    </div>

                    {/* Comorbidities */}
                    <div>
                      <label className="block text-sm font-semibold mb-2">6. List any other diseases or medical conditions you have:</label>
                      <Input type="text" placeholder="Enter medical condition" value={formData.comorbidities} onChange={(e) => handleFormChange("comorbidities", e.target.value)} required />
                    </div>

                    {/* Prior Treatments */}
                    <div>
                      <label className="block text-sm font-semibold mb-2">7. What kind of treatments have you done for your current cancer?</label>
                      <Input type="text" placeholder="Enter prior treatments" value={formData.priorTreatments} onChange={(e) => handleFormChange("priorTreatments", e.target.value)} required />
                    </div>
                    <Button className="mt-4 w-full bg-[#1159af] text-teal-300 hover:bg-red-300" onClick={submitQuestionnaire}>Find a Trial</Button>
                  </div>
                </CardContent>
              )}

              <form onSubmit={handleSubmit} className="flex gap-2">
              <Input value={inputValue} onChange={(e) => setInputValue(e.target.value)} placeholder="Ask about a clinical trial..." />
              <Button type="submit" className="bg-[#1159af] text-teal-300 hover:bg-red-300">Send</Button>
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

            {/* Hidden input for arrow key scroll control */}
            <input
              aria-label="Scroll chat with arrow keys"
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
              className="sr-only"
              tabIndex={-1}
            />
          </div>
        </>
      )}
    </div>
  );
}
