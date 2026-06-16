import { useState, useRef } from "react";
import Head from "next/head";
import Link from "next/link";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL;

const LANGUAGES = [
  "English","Hindi","Marathi","Tamil","Telugu",
  "Bengali","Gujarati","Kannada","Malayalam","Punjabi"
];

const URGENCY_CONFIG = {
  HIGH:   { bg: "bg-red-50",    border: "border-red-400",   text: "text-red-800",   label: "🚨 URGENT — Apply for bail before first hearing" },
  MEDIUM: { bg: "bg-yellow-50", border: "border-yellow-400",text: "text-yellow-800",label: "⚠ MEDIUM — Non-bailable, act within 48 hours"     },
  LOW:    { bg: "bg-green-50",  border: "border-green-400", text: "text-green-800", label: "✓ LOW — Bailable offence, apply for bail today"    },
};

export default function FIRExplainer() {
  const [file,      setFile]      = useState(null);
  const [preview,   setPreview]   = useState(null);
  const [language,  setLanguage]  = useState("English");
  const [loading,   setLoading]   = useState(false);
  const [result,    setResult]    = useState(null);
  const [error,     setError]     = useState(null);
  const fileRef = useRef();

  function handleFile(e) {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  }

  function handleDrop(e) {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  }

  async function handleSubmit() {
    if (!file) { setError("Please upload a FIR photo first."); return; }
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const form = new FormData();
      form.append("file",     file);
      form.append("language", language);

      const res = await axios.post(`${API}/api/explain-fir`, form, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,
      });

      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Something went wrong. Make sure the backend is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  const urgency = result?.urgency || "LOW";
  const uc      = URGENCY_CONFIG[urgency] || URGENCY_CONFIG.LOW;

  return (
    <>
      <Head><title>FIR Explainer — Nyaya Saathi</title></Head>
      <div className="min-h-screen bg-gray-50">

        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-2xl mx-auto flex items-center gap-3">
            <Link href="/" className="text-gray-400 hover:text-gray-600 text-xl">←</Link>
            <span className="text-xl">📄</span>
            <div>
              <h1 className="text-base font-semibold text-gray-900">FIR Explainer</h1>
              <p className="text-xs text-gray-500">
                Upload FIR photo — get plain language explanation
              </p>
            </div>
          </div>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">

          {/* Info banner */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <p className="text-sm text-blue-800">
              <strong>How to get your FIR:</strong> You have a legal right to a free copy
              under BNSS Section 173(2). Ask at the police station, or find it online at
              your state police portal. A WhatsApp photo of the FIR also works.
            </p>
          </div>

          {/* Upload */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-3">Upload FIR photo</h2>
            <div
              onClick={() => fileRef.current.click()}
              onDrop={handleDrop}
              onDragOver={e => e.preventDefault()}
              className="border-2 border-dashed border-gray-300 rounded-xl p-8
                         text-center cursor-pointer hover:border-blue-400
                         transition-colors"
            >
              {preview ? (
                <div className="space-y-2">
                  <img
                    src={preview}
                    alt="FIR preview"
                    className="max-h-56 mx-auto rounded-lg object-contain shadow"
                  />
                  <p className="text-xs text-green-600 font-medium">✓ {file.name}</p>
                  <p className="text-xs text-gray-400">Click to change photo</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="text-5xl">📷</div>
                  <p className="text-sm font-medium text-gray-700">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-400">
                    JPG, PNG supported • WhatsApp photos work too
                  </p>
                </div>
              )}
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFile}
            />
          </div>

          {/* Language */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-3">
              Explanation language
            </h2>
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
              {LANGUAGES.map(l => (
                <button
                  key={l}
                  onClick={() => setLanguage(l)}
                  className={`py-2 px-3 rounded-lg text-xs font-bold text-base opacity-100 border transition-colors
                    ${language === l
                      ? "bg-blue-600 text-white border-blue-600"
                      : "border-gray-200 text-gray-600 hover:border-blue-400"}`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700">⚠ {error}</p>
            </div>
          )}

          {/* Result */}
          {result?.status === "success" && (
            <div className="space-y-4">

              {/* Urgency banner */}
              <div className={`${uc.bg} border-l-4 ${uc.border} rounded-xl p-4`}>
                <p className={`font-semibold text-sm ${uc.text}`}>{uc.label}</p>
              </div>

              {/* FIR details */}
              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="font-semibold text-gray-900 mb-3">FIR Details</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {[
                    ["FIR Number",      result.fir_data?.fir_number],
                    ["Police Station",  result.fir_data?.police_station],
                    ["District",        result.fir_data?.district],
                    ["Date of FIR",     result.fir_data?.date_of_fir],
                    ["Accused",         result.fir_data?.accused_name],
                    ["Date of Offence", result.fir_data?.date_of_offence],
                  ].map(([label, val]) => val && (
                    <div key={label} className="bg-gray-50 rounded-lg p-2">
                      <div className="text-xs text-gray-500">{label}</div>
                      <div className="font-medium text-gray-900 mt-0.5">{val}</div>
                    </div>
                  ))}
                </div>

                {/* Sections */}
                {result.fir_data?.sections_charged?.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-gray-500 mb-2">Sections charged</p>
                    <div className="flex flex-wrap gap-2">
                      {result.fir_data.sections_charged.map(s => (
                        <span key={s}
                          className="bg-red-100 text-red-800 text-xs font-semibold
                                     px-3 py-1 rounded-full">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* OCR confidence */}
                <div className="mt-3 flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-green-500 h-1.5 rounded-full"
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">
                    OCR {Math.round(result.confidence * 100)}% confidence
                  </span>
                </div>
              </div>

              {/* Plain language explanation */}
              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="font-semibold text-gray-900 mb-3">
                  What this FIR means — in simple words
                </h3>
                <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {result.explanation}
                </div>
              </div>

              {/* Next steps */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 space-y-2">
                <p className="font-semibold text-blue-900 text-sm">What to do next:</p>
                <div className="space-y-1 text-sm text-blue-800">
                  <p>1. Call NALSA for free lawyer: <strong>15100</strong></p>
                  <p>2. Use Bail Assistant to generate bail application</p>
                  <p>3. Do not sign anything without a lawyer present</p>
                </div>
                <Link href="/bail-help"
                  className="inline-block mt-2 bg-blue-700 text-white text-sm
                             font-semibold px-4 py-2 rounded-lg hover:bg-blue-800">
                  Go to Bail Assistant →
                </Link>
              </div>
            </div>
          )}

          {/* Low confidence message */}
          {result?.status === "low_confidence" && (
            <div className="bg-yellow-50 border border-yellow-300 rounded-xl p-5">
              <p className="font-semibold text-yellow-800">
                ⚠ Image quality too low
              </p>
              <p className="text-sm text-yellow-700 mt-1">
                Could not read all fields clearly. Please try again with:
              </p>
              <ul className="text-sm text-yellow-700 mt-2 space-y-1 list-disc list-inside">
                <li>Better lighting — natural daylight works best</li>
                <li>Hold the phone steady, avoid blur</li>
                <li>Make sure all text is fully visible in frame</li>
              </ul>
            </div>
          )}

          {/* Submit button */}
          <button
            onClick={handleSubmit}
            disabled={loading || !file}
            className="w-full bg-blue-700 text-white py-4 rounded-xl font-semibold
                       text-base disabled:opacity-40 disabled:cursor-not-allowed
                       hover:bg-blue-800 transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent
                                 rounded-full animate-spin" />
                Reading FIR...
              </span>
            ) : (
              "Explain This FIR 📄"
            )}
          </button>

        </main>
      </div>
    </>
  );
}