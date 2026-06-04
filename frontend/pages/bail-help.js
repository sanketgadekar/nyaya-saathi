import { useState, useRef } from "react";
import Head from "next/head";
import Link from "next/link";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL;

const AGENTS = [
  { id: 1, name: "OCR Agent",           desc: "Reading FIR image..."         },
  { id: 2, name: "Law Router",          desc: "Detecting IPC or BNS..."      },
  { id: 3, name: "RAG Retriever",       desc: "Fetching law sections..."     },
  { id: 4, name: "Section 479 Calc",   desc: "Checking bail eligibility..." },
  { id: 5, name: "Drafter Agent",       desc: "Writing bail application..."  },
  { id: 6, name: "Translator",          desc: "Translating document..."      },
  { id: 7, name: "PDF Generator",       desc: "Creating court PDF..."        },
];

const LANGUAGES = [
  "English","Hindi","Marathi","Tamil","Telugu",
  "Bengali","Gujarati","Kannada","Malayalam","Punjabi"
];

export default function BailHelp() {
  const [file,       setFile]       = useState(null);
  const [preview,    setPreview]    = useState(null);
  const [months,     setMonths]     = useState("");
  const [firstTimer, setFirstTimer] = useState(true);
  const [language,   setLanguage]   = useState("English");
  const [loading,    setLoading]    = useState(false);
  const [activeAgent,setActiveAgent]= useState(0);
  const [result,     setResult]     = useState(null);
  const [error,      setError]      = useState(null);
  const fileRef = useRef();

  function handleFile(e) {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  }

  async function handleSubmit() {
    if (!file)   { setError("Please upload a FIR photo first.");  return; }
    if (!months) { setError("Please enter months in custody.");    return; }

    setLoading(true);
    setError(null);
    setResult(null);

    // Simulate agent progress — each agent takes ~2-3 seconds
    for (let i = 1; i <= 7; i++) {
      setActiveAgent(i);
      await new Promise(r => setTimeout(r, i === 5 ? 3000 : 1500));
    }

    try {
      const form = new FormData();
      form.append("file",              file);
      form.append("months_in_custody", months);
      form.append("is_first_offender", firstTimer);
      form.append("language",          language);

      const res = await axios.post(`${API}/api/bail-application`, form, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000,
      });

      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Something went wrong. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
      setActiveAgent(0);
    }
  }

  return (
    <>
      <Head><title>Bail Assistant — Nyaya Saathi</title></Head>
      <div className="min-h-screen bg-gray-50">

        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-2xl mx-auto flex items-center gap-3">
            <Link href="/" className="text-gray-400 hover:text-gray-600 text-xl">←</Link>
            <span className="text-xl">⚖️</span>
            <div>
              <h1 className="text-base font-semibold text-gray-900">Bail Assistant</h1>
              <p className="text-xs text-gray-500">FIR photo → bail application in 90 seconds</p>
            </div>
          </div>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">

          {/* Upload box */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-3">Step 1 — Upload FIR photo</h2>
            <div
              onClick={() => fileRef.current.click()}
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center
                         cursor-pointer hover:border-blue-400 transition-colors"
            >
              {preview ? (
                <img src={preview} alt="FIR preview"
                     className="max-h-48 mx-auto rounded object-contain" />
              ) : (
                <>
                  <div className="text-4xl mb-2">📷</div>
                  <p className="text-sm text-gray-600">Click to upload FIR photo</p>
                  <p className="text-xs text-gray-400 mt-1">JPG, PNG supported</p>
                </>
              )}
            </div>
            <input ref={fileRef} type="file" accept="image/*"
                   className="hidden" onChange={handleFile} />
            {file && (
              <p className="text-xs text-green-600 mt-2">✓ {file.name} selected</p>
            )}
          </div>

          {/* Details */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <h2 className="font-semibold text-gray-900">Step 2 — Enter details</h2>

            <div>
              <label className="text-sm text-gray-700 font-medium">
                Months in custody
              </label>
              <input
                type="number" min="0" max="300"
                value={months}
                onChange={e => setMonths(e.target.value)}
                placeholder="e.g. 14"
                className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2
                           text-sm focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="firstTimer"
                checked={firstTimer}
                onChange={e => setFirstTimer(e.target.checked)}
                className="w-4 h-4 accent-blue-600"
              />
              <label htmlFor="firstTimer" className="text-sm text-gray-700">
                First-time offender (no prior convictions)
              </label>
            </div>

            <div>
              <label className="text-sm text-gray-700 font-medium">
                Document language
              </label>
              <select
                value={language}
                onChange={e => setLanguage(e.target.value)}
                className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2
                           text-sm focus:outline-none focus:border-blue-500"
              >
                {LANGUAGES.map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Agent pipeline */}
          {loading && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="font-semibold text-gray-900 mb-4">
                Agent pipeline running...
              </h2>
              <div className="space-y-2">
                {AGENTS.map(agent => {
                  const done    = agent.id < activeAgent;
                  const running = agent.id === activeAgent;
                  return (
                    <div key={agent.id}
                         className={`flex items-center gap-3 p-2 rounded-lg transition-all
                           ${running ? "bg-blue-50 border border-blue-200" :
                             done    ? "opacity-60" : "opacity-30"}`}>
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center
                                      text-xs font-bold flex-shrink-0
                                      ${done    ? "bg-green-500 text-white" :
                                        running ? "bg-blue-500 text-white animate-pulse" :
                                                  "bg-gray-200 text-gray-500"}`}>
                        {done ? "✓" : agent.id}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-800">
                          {agent.name}
                        </div>
                        {running && (
                          <div className="text-xs text-blue-600">{agent.desc}</div>
                        )}
                      </div>
                      {running && (
                        <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent
                                        rounded-full animate-spin" />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700">⚠ {error}</p>
            </div>
          )}

          {/* Result */}
          {result?.status === "success" && (
            <div className="bg-green-50 border border-green-300 rounded-xl p-5 space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✅</span>
                <div>
                  <p className="font-semibold text-green-800">Bail application generated!</p>
                  <p className="text-xs text-green-600">
                    Confidence: {Math.round(result.confidence_score * 100)}% •
                    Bail type: {result.bail_type} •
                    Law: {result.applicable_law}
                  </p>
                </div>
              </div>

              {/* Eligibility card */}
              <div className={`rounded-lg p-3 text-sm
                ${result.bail_eligibility?.eligible
                  ? "bg-green-100 text-green-800"
                  : "bg-blue-100 text-blue-800"}`}>
                <strong>
                  {result.bail_eligibility?.eligible
                    ? "⚖ Bail is a RIGHT under " + result.bail_eligibility?.section
                    : "⚖ Standard bail application — " + result.bail_eligibility?.section}
                </strong>
                <p className="text-xs mt-1">{result.bail_eligibility?.reason}</p>
              </div>

              {/* FIR summary */}
              <div className="bg-white rounded-lg p-3 text-xs text-gray-600 space-y-1">
                <p><strong>FIR:</strong> {result.fir_data?.fir_number} — {result.fir_data?.police_station}</p>
                <p><strong>Accused:</strong> {result.fir_data?.accused_name}</p>
                <p><strong>Sections:</strong> {result.fir_data?.sections_charged?.join(", ")}</p>
              </div>

              {/* Download button */}
              <a
                href={`${API}${result.pdf_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center bg-blue-700 text-white py-3
                           rounded-lg font-semibold text-sm hover:bg-blue-800 transition-colors"
              >
                📥 Download Bail Application PDF
              </a>

              <p className="text-xs text-yellow-700 bg-yellow-50 p-2 rounded">
                ⚠ Review with a lawyer before filing. Free lawyers: NALSA 15100
              </p>
            </div>
          )}

          {/* Submit button */}
          {!loading && !result && (
            <button
              onClick={handleSubmit}
              disabled={!file || !months}
              className="w-full bg-blue-700 text-white py-4 rounded-xl font-semibold
                         text-base disabled:opacity-40 disabled:cursor-not-allowed
                         hover:bg-blue-800 transition-colors"
            >
              Generate Bail Application ⚖️
            </button>
          )}

          {loading && (
            <button disabled
              className="w-full bg-gray-300 text-gray-500 py-4 rounded-xl
                         font-semibold text-base cursor-not-allowed">
              Processing... please wait
            </button>
          )}

        </main>
      </div>
    </>
  );
}