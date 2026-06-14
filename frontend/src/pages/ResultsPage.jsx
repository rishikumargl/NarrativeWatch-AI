import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import TrustScoreGauge from '../components/TrustScoreGauge';

export default function ResultsPage() {
  const { id } = useParams();
  const location = useLocation();
  const [results, setResults] = useState(null);

  useEffect(() => {
    const analysisResult = location.state?.analysisResult;
    if (analysisResult) {
      setResults(analysisResult);
    } else {
      setResults({
        analysis_id: id,
        trustScore: 72,
        riskLevel: "MEDIUM",
        summary: "Article contains some unverified claims and exhibits moderate bias. Generally credible sources but with sensationalist framing.",
        findings: {
          misinformation_risk: 28,
          bias_severity: 35,
          bot_activity: 12,
          campaign_probability: 5
        }
      });
    }
  }, [id, location]);

  if (!results) {
    return <div className="container mx-auto px-4 py-8"><p className="text-white">Loading...</p></div>;
  }

  const isFallback = results?.reflectionLoop?.fallback_triggered;

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black overflow-hidden">
      {/* Background animations */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold text-white mb-8">📋 Analysis Results</h2>

          {isFallback && (
            <div className="mb-8 p-6 bg-red-500/10 border border-red-500/30 rounded-xl">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-red-400 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-bold text-red-300 mb-2">Quality Standards Not Met</h3>
                  <p className="text-red-200">{results.summary}</p>
                  {results.reflectionLoop && (
                    <p className="text-red-300 text-sm mt-3">
                      Analysis went through {results.reflectionLoop.total_iterations} iterations of synthesis and validation.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
            <div className="lg:col-span-2 space-y-6">
              {!isFallback && (
                <>
                  <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                    <h3 className="text-xl font-bold text-white mb-4">Summary</h3>
                    <p className="text-gray-300 leading-relaxed">{results.summary}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {results.findings && Object.entries(results.findings).map(([key, value]) => (
                      typeof value === 'number' && (
                        <div key={key} className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
                          <div className="text-sm text-gray-400 capitalize mb-2">{key.replace('_', ' ')}</div>
                          <div className="text-3xl font-bold text-blue-400">{value}%</div>
                        </div>
                      )
                    ))}
                  </div>
                </>
              )}

              {/* Reflection Loop Info */}
              {results.reflectionLoop && (
                <div className={`p-6 rounded-lg border ${
                  isFallback ? 'bg-red-500/5 border-red-500/30' : 'bg-green-500/5 border-green-500/30'
                }`}>
                  <h4 className={`font-bold mb-3 ${isFallback ? 'text-red-300' : 'text-green-300'}`}>
                    {isFallback ? '⚠ Reflection Loop Status' : '✓ Analysis Quality Verified'}
                  </h4>
                  <div className="space-y-2 text-sm">
                    <p className="text-gray-300">
                      <span className="text-gray-400">Total Iterations:</span> {results.reflectionLoop.total_iterations}
                    </p>
                    {results.reflectionLoop.iteration_approved && (
                      <p className="text-gray-300">
                        <span className="text-gray-400">Approved On:</span> Iteration {results.reflectionLoop.iteration_approved}
                      </p>
                    )}
                    <p className={`${isFallback ? 'text-red-300' : 'text-green-300'}`}>
                      {isFallback ? '✗ Fallback triggered' : `✓ Quality standards met`}
                    </p>
                  </div>
                </div>
              )}

              {!isFallback && (
                <div className="bg-green-500/10 border border-green-500/50 p-6 rounded-lg">
                  <h4 className="text-white font-bold mb-2">✓ Analysis Complete</h4>
                  <p className="text-green-300 text-sm">All agents have completed their analysis</p>
                </div>
              )}
            </div>

            {!isFallback && (
              <div>
                <TrustScoreGauge score={results.trustScore} riskLevel={results.riskLevel} />
              </div>
            )}
          </div>

          <div className="text-center">
            <a href="/" className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition">
              ← Analyze Another Article
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
