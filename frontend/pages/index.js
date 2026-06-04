import { useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";

const FEATURES = [
  {
    id:    "fir-explainer",
    icon:  "📄",
    title: "FIR Explainer",
    desc:  "Upload FIR photo — get plain language explanation of every charge in your language",
    color: "border-blue-500",
    bg:    "bg-blue-50",
  },
  {
    id:    "my-rights",
    icon:  "🛡️",
    title: "My Rights",
    desc:  "Know your exact legal rights the moment you or a family member is arrested",
    color: "border-purple-500",
    bg:    "bg-purple-50",
  },
  {
    id:    "legal-help",
    icon:  "💬",
    title: "Legal Help Chat",
    desc:  "Ask any legal question in Hindi, Marathi, Tamil or English — get instant answers",
    color: "border-green-500",
    bg:    "bg-green-50",
  },
  {
    id:    "documents",
    icon:  "📝",
    title: "Document Drafter",
    desc:  "Generate bail applications, RTI requests, consumer complaints and more",
    color: "border-orange-500",
    bg:    "bg-orange-50",
  },
  {
    id:    "bail-help",
    icon:  "⚖️",
    title: "Bail Assistant",
    desc:  "FIR photo in — court-ready bail application PDF out — in 90 seconds",
    color: "border-blue-700",
    bg:    "bg-blue-50",
  },
  {
    id:    "find-help",
    icon:  "📍",
    title: "Find Free Lawyer",
    desc:  "Locate the nearest free legal aid centre matched to your case type",
    color: "border-teal-500",
    bg:    "bg-teal-50",
  },
  {
    id:    "reminders",
    icon:  "🔔",
    title: "Court Reminders",
    desc:  "Register your case number — get WhatsApp reminders before every hearing",
    color: "border-pink-500",
    bg:    "bg-pink-50",
  },
];

export default function Home() {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>Nyaya Saathi — AI Legal Accessibility Platform</title>
        <meta name="description" content="Free AI legal help for every Indian" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50">

        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">⚖️</span>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">Nyaya Saathi</h1>
                <p className="text-xs text-gray-500">AI Legal Accessibility Platform</p>
              </div>
            </div>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
              Free • No signup
            </span>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-8">

          {/* Hero */}
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Justice should not depend on your wallet
            </h2>
            <p className="text-gray-600 max-w-xl mx-auto text-sm leading-relaxed">
              4 in 5 Indians do not know their free legal rights. 3.75 lakh people sit in
              prison without conviction. Nyaya Saathi gives everyone the legal tools
              that previously only money could buy — free, in your language, in 90 seconds.
            </p>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-4 mb-10">
            {[
              { n: "3.75L+", l: "undertrials need bail" },
              { n: "10",     l: "Indian languages" },
              { n: "₹0",     l: "completely free" },
            ].map((s) => (
              <div key={s.n} className="bg-white rounded-xl border border-gray-200 p-4 text-center">
                <div className="text-xl font-bold text-blue-700">{s.n}</div>
                <div className="text-xs text-gray-500 mt-1">{s.l}</div>
              </div>
            ))}
          </div>

          {/* Feature grid */}
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Choose what you need
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {FEATURES.map((f) => (
              <button
                key={f.id}
                onClick={() => router.push(`/${f.id}`)}
                className={`text-left bg-white rounded-xl border-l-4 ${f.color} border border-gray-200 p-5
                           hover:shadow-md transition-all duration-150 hover:-translate-y-0.5`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{f.icon}</span>
                  <div>
                    <div className="font-semibold text-gray-900 mb-1">{f.title}</div>
                    <div className="text-xs text-gray-500 leading-relaxed">{f.desc}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Disclaimer */}
          <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-xl p-4">
            <p className="text-xs text-yellow-800 leading-relaxed">
              <strong>Disclaimer:</strong> Nyaya Saathi generates AI-assisted legal drafts and
              information. All documents must be reviewed by a qualified advocate before filing.
              This is not legal advice. For free legal help call NALSA: <strong>15100</strong>
            </p>
          </div>
        </main>
      </div>
    </>
  );
}