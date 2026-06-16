import { useState } from "react";
import Head from "next/head";
import Link from "next/link";
import axios from "axios";

const API       = process.env.NEXT_PUBLIC_API_URL;
const LANGUAGES = ["English","Hindi","Marathi","Tamil","Telugu","Bengali"];
const SITUATIONS = [
  "Police arrested me and won't tell me why",
  "I was arrested and police won't let me call my family",
  "Police are holding me for more than 24 hours",
  "I cannot afford a lawyer",
  "Police want to question me without a lawyer",
  "My wife was arrested after sunset",
  "My child under 18 was arrested",
];

export default function MyRights() {
  const [situation, setSituation] = useState("");
  const [language,  setLanguage]  = useState("English");
  const [loading,   setLoading]   = useState(false);
  const [result,    setResult]    = useState(null);
  const [error,     setError]     = useState(null);

  async function handleSubmit() {
    if (!situation.trim()) { setError("Please describe your situation."); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await axios.post(`${API}/api/my-rights`, { situation, language });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }

  // Parse rights output into individual cards
  function parseRights(text) {
    if (!text) return [];
    return text.split("---").map(r => r.trim()).filter(Boolean);
  }

  return (
    <>
      <Head><title>My Rights — Nyaya Saathi</title></Head>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-2xl mx-auto flex items-center gap-3">
            <Link href="/" className="text-gray-400 hover:text-gray-600 text-xl">←</Link>
            <span className="text-xl">🛡️</span>
            <div>
              <h1 className="text-base font-semibold text-gray-900">My Rights</h1>
              <p className="text-xs text-gray-500">Know your rights right now</p>
            </div>
          </div>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">

          <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <h2 className="font-semibold text-gray-900">What is happening right now?</h2>

            {/* Quick situation buttons */}
            <div className="flex flex-wrap gap-2">
              {SITUATIONS.map(s => (
                <button key={s}
                  onClick={() => { setSituation(s); setResult(null); }}
                  className={`text-xs px-3 py-1.5 rounded-full border transition-colors
                    ${situation === s
                      ? "bg-purple-600 text-white border-purple-600"
                      : "border-gray-300 text-black hover:border-purple-400"}`}>
                  {s}
                </button>
              ))}
            </div>

            <textarea
              rows={3}
              value={situation}
              onChange={e => { setSituation(e.target.value); setResult(null); }}
              placeholder="Or describe your situation here in any language..."
                           className="w-full border border-gray-300 rounded-lg px-3 py-2 py-2
                           text-gray-900
                           placeholder:text-gray-500
                           focus:outline-none focus:border-purple-500 resize-none"
            />

            <select
              value={language}
              onChange={e => setLanguage(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2
                         bg-white text-gray-500
                         focus:outline-none focus:border-purple-500">
              {LANGUAGES.map(l => <option key={l}>{l}</option>)}
            </select>

            <button onClick={handleSubmit} disabled={loading || !situation.trim()}
              className="w-full bg-purple-600 text-white py-3 rounded-lg font-bold
                         text-base opacity-100 hover:bg-purple-800 transition-colors">
              {loading ? "Finding your rights..." : "Show My Rights 🛡️"}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700">⚠ {error}</p>
            </div>
          )}

          {result?.status === "success" && (
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-900">
                Your rights in this situation:
              </h3>
              {parseRights(result.rights).map((right, i) => (
                <div key={i}
                     className="bg-white rounded-xl border-l-4 border-purple-500
                                border border-gray-200 p-4">
                  <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                    {right}
                  </p>
                </div>
              ))}
              <div className="bg-purple-50 rounded-xl p-4 text-sm text-purple-800">
                <strong>Need a free lawyer?</strong> Call NALSA: <strong>15100</strong>
                (free, available in all states)
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}