import { useState } from "react";
import Head from "next/head";
import Link from "next/link";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function FindHelp() {
  const [situation, setSituation] = useState("");
  const [district,  setDistrict]  = useState("");
  const [state,     setState]     = useState("");
  const [loading,   setLoading]   = useState(false);
  const [result,    setResult]    = useState(null);
  const [error,     setError]     = useState(null);

  async function handleFind() {
    if (!situation.trim() || !district.trim()) {
      setError("Please enter your situation and district."); return;
    }
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await axios.post(`${API}/api/find-legal-aid`, { situation, district, state });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head><title>Find Free Lawyer — Nyaya Saathi</title></Head>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-2xl mx-auto flex items-center gap-3">
            <Link href="/" className="text-gray-400 text-xl">←</Link>
            <span className="text-xl">📍</span>
            <div>
              <h1 className="text-base font-semibold">Find Free Lawyer</h1>
              <p className="text-xs text-gray-500">NALSA, NGOs, pro-bono lawyers near you</p>
            </div>
          </div>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">
          <div className="bg-teal-50 border border-teal-200 rounded-xl p-4">
            <p className="text-sm text-teal-800">
              <strong>Emergency?</strong> Call NALSA now: <strong>15100</strong> (free, 24/7)
            </p>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <h2 className="font-semibold text-gray-900">Find legal help near you</h2>
            <textarea rows={3} value={situation}
              onChange={e => setSituation(e.target.value)}
              placeholder="What legal help do you need? e.g. bail for theft case"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:border-teal-500 resize-none" />
            <div className="grid grid-cols-2 gap-3">
              <input value={district} onChange={e => setDistrict(e.target.value)}
                placeholder="Your district (e.g. Nashik)"
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm
                           focus:outline-none focus:border-teal-500" />
              <input value={state} onChange={e => setState(e.target.value)}
                placeholder="State (e.g. Maharashtra)"
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm
                           focus:outline-none focus:border-teal-500" />
            </div>
            <button onClick={handleFind} disabled={loading || !situation.trim() || !district.trim()}
              className="w-full bg-teal-600 text-white py-3 rounded-lg font-semibold
                         text-sm disabled:opacity-40 hover:bg-teal-700 transition-colors">
              {loading ? "Finding help..." : "Find Free Legal Help 📍"}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700">⚠ {error}</p>
            </div>
          )}

          {result?.status === "success" && (
            <div className="space-y-4">
              <div className="bg-teal-50 rounded-xl p-4">
                <p className="text-sm font-medium text-teal-800 mb-1">What to say when you call:</p>
                <p className="text-sm text-teal-700">{result.what_to_say}</p>
              </div>
              <h3 className="font-semibold text-gray-900">
                Top {result.options?.length} free options for you:
              </h3>
              {result.options?.map((org, i) => (
                <div key={i}
                     className="bg-white rounded-xl border-l-4 border-teal-500
                                border border-gray-200 p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-gray-900 text-sm">{org.name}</h4>
                    <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5
                                     rounded-full flex-shrink-0">{org.type}</span>
                  </div>
                  <p className="text-xs text-gray-600">📍 {org.address}</p>
                  <p className="text-xs text-gray-600">🕐 {org.timing}</p>
                  <a href={`tel:${org.phone}`}
                     className="inline-flex items-center gap-1 text-sm font-semibold
                                text-teal-700 hover:text-teal-900">
                    📞 {org.phone}
                  </a>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  );
}