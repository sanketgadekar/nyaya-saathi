import { useState } from "react";
import Head from "next/head";
import Link from "next/link";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL;

const DOC_TYPES = [
  { id:"bail",             icon:"⚖️",  label:"Bail Application"          },
  { id:"anticipatory",     icon:"🛡️",  label:"Anticipatory Bail"         },
  { id:"rti",              icon:"📋",  label:"RTI Application"           },
  { id:"consumer",         icon:"🛒",  label:"Consumer Complaint"        },
  { id:"police_complaint", icon:"🚔",  label:"Police Complaint"          },
  { id:"dv_complaint",     icon:"🏠",  label:"Domestic Violence Complaint"},
  { id:"maintenance",      icon:"👨‍👩‍👧",  label:"Maintenance Application"   },
  { id:"legal_notice",     icon:"📨",  label:"Legal Notice"              },
  { id:"affidavit",        icon:"📜",  label:"Affidavit"                 },
];

const LANGS = ["English","Hindi","Marathi","Tamil","Telugu","Bengali","Gujarati"];

export default function Documents() {
  const [docType,   setDocType]   = useState("auto");
  const [situation, setSituation] = useState("");
  const [name,      setName]      = useState("");
  const [address,   setAddress]   = useState("");
  const [language,  setLanguage]  = useState("English");
  const [loading,   setLoading]   = useState(false);
  const [result,    setResult]    = useState(null);
  const [error,     setError]     = useState(null);

  async function handleDraft() {
    if (!situation.trim()) { setError("Please describe your situation."); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await axios.post(`${API}/api/draft-document`, {
        situation,
        document_type: docType,
        language,
        user_details:  { name, address },
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head><title>Document Drafter — Nyaya Saathi</title></Head>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-2xl mx-auto flex items-center gap-3">
            <Link href="/" className="text-gray-400 text-xl">←</Link>
            <span className="text-xl">📝</span>
            <div>
              <h1 className="text-base font-semibold">Document Drafter</h1>
              <p className="text-xs text-gray-500">9 document types, AI-generated</p>
            </div>
          </div>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">

          {/* Document type selector */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-3">Select document type</h2>
            <div className="grid grid-cols-3 gap-2">
              <button onClick={() => setDocType("auto")}
                className={`p-3 rounded-lg border text-xs font-medium transition-colors
                  ${docType === "auto"
                    ? "bg-orange-500 text-white border-orange-500"
                    : "border-gray-200 text-gray-600 hover:border-orange-400"}`}>
                🤖 Auto detect
              </button>
              {DOC_TYPES.map(d => (
                <button key={d.id} onClick={() => setDocType(d.id)}
                  className={`p-3 rounded-lg border text-xs font-medium transition-colors
                    ${docType === d.id
                      ? "bg-orange-500 text-white border-orange-500"
                      : "border-gray-200 text-gray-600 hover:border-orange-400"}`}>
                  {d.icon} {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Form */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <h2 className="font-semibold text-gray-900">Describe your situation</h2>
            <textarea rows={4} value={situation}
              onChange={e => setSituation(e.target.value)}
              placeholder="Explain what happened in your own words..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:border-orange-500 resize-none" />
            <input value={name} onChange={e => setName(e.target.value)}
              placeholder="Your full name"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:border-orange-500" />
            <input value={address} onChange={e => setAddress(e.target.value)}
              placeholder="Your address"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:border-orange-500" />
            <select value={language} onChange={e => setLanguage(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:border-orange-500">
              {LANGS.map(l => <option key={l}>{l}</option>)}
            </select>
            <button onClick={handleDraft} disabled={loading || !situation.trim()}
              className="w-full bg-orange-500 text-white py-3 rounded-lg font-semibold
                         text-sm disabled:opacity-40 hover:bg-orange-600 transition-colors">
              {loading ? "Drafting document..." : "Draft Document 📝"}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700">⚠ {error}</p>
            </div>
          )}

          {result?.status === "success" && (
            <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">{result.document_name}</h3>
                <span className={`text-xs font-medium px-2 py-1 rounded-full
                  ${result.confidence >= 0.9 ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                  {Math.round(result.confidence * 100)}% confidence
                </span>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                  {result.draft}
                </pre>
              </div>
              {result.flagged?.length > 0 && (
                <div className="bg-yellow-50 p-3 rounded-lg">
                  <p className="text-xs text-yellow-800">
                    ⚠ {result.flagged.length} section(s) need verification with a lawyer
                  </p>
                </div>
              )}
              <div className="flex gap-3">
                <button
                  onClick={() => navigator.clipboard.writeText(result.draft)}
                  className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg
                             text-sm font-medium hover:bg-gray-50">
                  📋 Copy text
                </button>
              </div>
              <p className="text-xs text-yellow-700 bg-yellow-50 p-2 rounded">
                ⚠ Review with a qualified lawyer before filing. NALSA free help: 15100
              </p>
            </div>
          )}
        </main>
      </div>
    </>
  );
}