import { useState } from "react";
import Head from "next/head";
import Link from "next/link";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function Reminders() {
  const [cnr,     setCnr]     = useState("");
  const [phone,   setPhone]   = useState("");
  const [name,    setName]    = useState("");
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
  const [error,   setError]   = useState(null);

  async function handleRegister() {
    if (!cnr.trim())   { setError("Please enter your CNR number.");    return; }
    if (!phone.trim()) { setError("Please enter your WhatsApp number.");return; }
    if (!name.trim())  { setError("Please enter your name.");          return; }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await axios.post(`${API}/api/register-reminder`, {
        cnr_number: cnr.trim().toUpperCase(),
        phone:      phone.trim(),
        name:       name.trim(),
      });
      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Could not register. Check CNR number and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head><title>Court Reminders — Nyaya Saathi</title></Head>
      <div className="min-h-screen bg-gray-50">

        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-2xl mx-auto flex items-center gap-3">
            <Link href="/" className="text-gray-400 hover:text-gray-600 text-xl">←</Link>
            <span className="text-xl">🔔</span>
            <div>
              <h1 className="text-base font-semibold text-gray-900">Court Reminders</h1>
              <p className="text-xs text-gray-500">
                Never miss a hearing — WhatsApp alerts before every date
              </p>
            </div>
          </div>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">

          {/* How it works */}
          <div className="bg-pink-50 border border-pink-200 rounded-xl p-5">
            <h2 className="font-semibold text-pink-900 mb-3">How it works</h2>
            <div className="space-y-3">
              {[
                { n:"1", t:"Register your CNR number",       d:"Found on your case documents or at ecourts.gov.in"              },
                { n:"2", t:"We check court dates weekly",     d:"System checks NJDG every week for hearing updates"              },
                { n:"3", t:"Get WhatsApp alerts",             d:"Reminders sent 7 days, 3 days, and 1 day before each hearing"   },
                { n:"4", t:"Never miss a date again",         d:"If date changes, we update your reminder automatically"         },
              ].map(s => (
                <div key={s.n} className="flex gap-3 items-start">
                  <div className="w-6 h-6 bg-pink-500 text-white rounded-full flex
                                  items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    {s.n}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-pink-900">{s.t}</p>
                    <p className="text-xs text-pink-700">{s.d}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* CNR help */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-2">
              What is a CNR number?
            </h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              CNR (Case Number Record) is a unique 16-digit number assigned to every
              court case in India. It looks like: <strong>MHNS010123452024</strong>
            </p>
            <div className="mt-3 bg-gray-50 rounded-lg p-3 space-y-1">
              <p className="text-xs text-gray-600 font-medium">Where to find your CNR:</p>
              <p className="text-xs text-gray-500">• On any court notice or summons paper</p>
              <p className="text-xs text-gray-500">• At ecourts.gov.in → search by party name</p>
              <p className="text-xs text-gray-500">• Ask your lawyer or the court clerk</p>
              <a href="https://ecourts.gov.in" target="_blank" rel="noopener noreferrer"
                 className="text-xs text-blue-600 font-medium hover:underline">
                → Search on eCourts website
              </a>
            </div>
          </div>

          {/* Registration form */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <h2 className="font-semibold text-gray-900">Register for reminders</h2>

            <div>
              <label className="text-sm font-medium text-gray-700">
                CNR Number <span className="text-red-500">*</span>
              </label>
              <input
                value={cnr}
                onChange={e => setCnr(e.target.value.toUpperCase())}
                placeholder="e.g. MHNS010123452024"
                maxLength={16}
                className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2.5
                           text-sm font-mono focus:outline-none focus:border-pink-500
                           tracking-widest uppercase"
              />
              <p className="text-xs text-gray-400 mt-1">16 characters — letters and numbers</p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">
                Your name <span className="text-red-500">*</span>
              </label>
              <input
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Full name"
                className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2.5
                           text-sm focus:outline-none focus:border-pink-500"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700">
                WhatsApp number <span className="text-red-500">*</span>
              </label>
              <div className="flex mt-1">
                <span className="inline-flex items-center px-3 border border-r-0
                                 border-gray-300 rounded-l-lg bg-gray-50 text-sm text-gray-500">
                  +91
                </span>
                <input
                  value={phone}
                  onChange={e => setPhone(e.target.value.replace(/\D/g,""))}
                  placeholder="10-digit number"
                  maxLength={10}
                  type="tel"
                  className="flex-1 border border-gray-300 rounded-r-lg px-3 py-2.5
                             text-sm focus:outline-none focus:border-pink-500"
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Reminders sent to this WhatsApp number
              </p>
            </div>

            <button
              onClick={handleRegister}
              disabled={loading || !cnr.trim() || !phone.trim() || !name.trim()}
              className="w-full bg-pink-600 text-white py-3 rounded-xl font-semibold
                         text-sm disabled:opacity-40 disabled:cursor-not-allowed
                         hover:bg-pink-700 transition-colors"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent
                                   rounded-full animate-spin" />
                  Registering...
                </span>
              ) : (
                "Register for Court Reminders 🔔"
              )}
            </button>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700">⚠ {error}</p>
            </div>
          )}

          {/* Success */}
          {result?.status === "success" && (
            <div className="bg-green-50 border border-green-300 rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✅</span>
                <p className="font-semibold text-green-800">
                  Reminders registered successfully!
                </p>
              </div>

              {result.case_data && (
                <div className="bg-white rounded-lg p-3 space-y-1 text-sm">
                  <p className="text-xs text-gray-500 font-medium">Case details found:</p>
                  <p><strong>CNR:</strong> {cnr}</p>
                  <p><strong>Name:</strong> {name}</p>
                  {result.case_data?.next_hearing && (
                    <p><strong>Next hearing:</strong> {result.case_data.next_hearing}</p>
                  )}
                </div>
              )}

              <div className="bg-green-100 rounded-lg p-3 space-y-1">
                <p className="text-sm font-semibold text-green-800">
                  You will receive WhatsApp reminders at:
                </p>
                <p className="text-sm text-green-700">
                  📱 +91 {phone} — 7 days, 3 days, and 1 day before each hearing
                </p>
              </div>

              <p className="text-xs text-gray-500">
                If your hearing date changes, we will automatically update your reminder.
              </p>
            </div>
          )}

          {/* Case not found */}
          {result?.status === "error" && (
            <div className="bg-yellow-50 border border-yellow-300 rounded-xl p-5">
              <p className="font-semibold text-yellow-800">⚠ Case not found</p>
              <p className="text-sm text-yellow-700 mt-1">
                Could not find this CNR on eCourts. Please check:
              </p>
              <ul className="text-sm text-yellow-700 mt-2 space-y-1 list-disc list-inside">
                <li>CNR number is entered correctly (16 characters)</li>
                <li>The case is registered on eCourts (ecourts.gov.in)</li>
                <li>Try searching your case at ecourts.gov.in first</li>
              </ul>
              <a href="https://ecourts.gov.in" target="_blank" rel="noopener noreferrer"
                 className="inline-block mt-3 text-sm text-blue-600 font-medium hover:underline">
                → Search on eCourts website
              </a>
            </div>
          )}

          {/* Privacy note */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
            <p className="text-xs text-gray-500 leading-relaxed">
              🔒 <strong>Privacy:</strong> Your phone number and case details are only used
              to send court reminders. We do not share your data with anyone.
              You can delete your reminders anytime.
            </p>
          </div>

        </main>
      </div>
    </>
  );
}