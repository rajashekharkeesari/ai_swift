import React, { useState } from "react";
import { screenVisa } from "../api";

const Home = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await screenVisa(trimmed, 3);
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-slate-100 flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-2xl">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-800">SwiftVisa</h1>
          <p className="text-slate-500 mt-1">
            AI-powered visa eligibility screening
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-xl shadow-md p-6 flex flex-col gap-4"
        >
          <label htmlFor="query" className="font-medium text-slate-700">
            Describe your situation
          </label>
          <textarea
            id="query"
            rows={4}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. I'm 24 with a bachelor's degree and want to study in Canada"
            className="p-3 border border-slate-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="bg-blue-600 text-white font-medium p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Checking eligibility..." : "Check Eligibility"}
          </button>
        </form>

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 text-red-700 rounded-lg p-4">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-6 bg-white rounded-xl shadow-md p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-3">
              Result
            </h2>
            <pre className="whitespace-pre-wrap break-words text-slate-700 text-sm leading-relaxed">
              {result.response}
            </pre>

            {result.retrieved_documents?.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-2">
                  Sources
                </h3>
                <ul className="flex flex-col gap-2">
                  {result.retrieved_documents.map((doc, i) => (
                    <li
                      key={i}
                      className="border border-slate-200 rounded-lg p-3 text-sm"
                    >
                      <div className="font-medium text-slate-800">
                        {doc.country} — {doc.visa_type}
                      </div>
                      <div className="text-slate-400 text-xs mt-1">
                        relevance: {doc.score.toFixed(3)}
                      </div>
                      {doc.official_resource && (
                        <a
                          href={doc.official_resource}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline text-xs break-all"
                        >
                          {doc.official_resource}
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.telemetry && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-2">
                  Call Metrics
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                  <div className="border border-slate-200 rounded-lg p-3">
                    <div className="text-slate-400 text-xs">Input tokens</div>
                    <div className="font-medium text-slate-800">
                      {result.telemetry.input_tokens}
                    </div>
                  </div>
                  <div className="border border-slate-200 rounded-lg p-3">
                    <div className="text-slate-400 text-xs">Output tokens</div>
                    <div className="font-medium text-slate-800">
                      {result.telemetry.output_tokens}
                    </div>
                  </div>
                  <div className="border border-slate-200 rounded-lg p-3">
                    <div className="text-slate-400 text-xs">Total cost (USD)</div>
                    <div className="font-medium text-slate-800">
                      ${result.telemetry.total_cost_usd.toFixed(6)}
                    </div>
                  </div>
                  <div className="border border-slate-200 rounded-lg p-3">
                    <div className="text-slate-400 text-xs">Latency</div>
                    <div className="font-medium text-slate-800">
                      {result.telemetry.pipeline_latency_s.toFixed(2)}s
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
