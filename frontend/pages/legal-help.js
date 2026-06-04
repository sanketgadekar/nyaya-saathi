import { useState, useRef, useEffect } from "react";
import Head from "next/head";
import Link from "next/link";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function LegalHelp() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Namaste! I am Nyaya Saathi. Ask me any legal question in Hindi, English, Marathi or any Indian language. I will answer based on Indian law.",
    },
  ]);
  const [input,   setInput]   = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");

    const history = messages
      .filter(m => m.role !== "assistant" || messages.indexOf(m) > 0)
      .map(m => ({
        [m.role === "user" ? "user" : "assistant"]: m.text
      }));

    setMessages(prev => [...prev, { role: "user", text: userMsg }]);
    setLoading(true);

    try {
      const res = await axios.post(`${API}/api/legal-chat`, {
        message:  userMsg,
        history:  history,
        language: "auto",
      });

      setMessages(prev => [
        ...prev,
        { role: "assistant", text: res.data.answer },
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: "assistant", text: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head><title>Legal Help Chat — Nyaya Saathi</title></Head>
      <div className="min-h-screen bg-gray-50 flex flex-col">

        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-2xl mx-auto flex items-center gap-3">
            <Link href="/" className="text-gray-400 hover:text-gray-600 text-xl">←</Link>
            <span className="text-xl">💬</span>
            <div>
              <h1 className="text-base font-semibold text-gray-900">Legal Help Chat</h1>
              <p className="text-xs text-gray-500">Ask in any Indian language</p>
            </div>
            <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
              Online
            </span>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 max-w-2xl w-full mx-auto px-4 py-4 space-y-3 overflow-y-auto">
          {messages.map((m, i) => (
            <div key={i}
                 className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-xs sm:max-w-sm lg:max-w-md rounded-2xl px-4 py-3 text-sm
                              leading-relaxed whitespace-pre-wrap
                              ${m.role === "user"
                                ? "bg-green-600 text-white rounded-br-sm"
                                : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm"}`}>
                {m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm
                              px-4 py-3 text-sm text-gray-500">
                <span className="animate-pulse">Nyaya Saathi is thinking...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="bg-white border-t border-gray-200 px-4 py-3">
          <div className="max-w-2xl mx-auto flex gap-2">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="Type in Hindi, English, Marathi..."
              className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm
                         focus:outline-none focus:border-green-500"
            />
            <button onClick={handleSend} disabled={loading || !input.trim()}
              className="bg-green-600 text-white px-4 py-2.5 rounded-xl font-medium
                         text-sm disabled:opacity-40 hover:bg-green-700 transition-colors">
              Send
            </button>
          </div>
          <p className="text-xs text-gray-400 text-center mt-2">
            Powered by Groq Llama 3.3 70B + Indian legal knowledge base
          </p>
        </div>
      </div>
    </>
  );
}