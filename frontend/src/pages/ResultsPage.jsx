import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { Home, Play, ExternalLink } from 'lucide-react';
import TrustScoreGauge from '../components/TrustScoreGauge';

export default function ResultsPage() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);

  useEffect(() => {
    const analysisResult = location.state?.analysisResult;
    if (analysisResult) {
      setResults(analysisResult);
    }
  }, [id, location]);

  if (!results) {
    return <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black flex items-center justify-center"><p className="text-white text-xl">Loading...</p></div>;
  }

  const getMetricColor = (value, type) => {
    if (type === 'sentiment') {
      return value === 'NEGATIVE' ? 'text-red-400' : value === 'POSITIVE' ? 'text-green-400' : 'text-gray-400';
    }
    if (type === 'bias') {
      return value === 'LOW' ? 'text-green-400' : value === 'MEDIUM' ? 'text-yellow-400' : 'text-red-400';
    }
    if (type === 'bot') {
      return parseFloat(value) < 30 ? 'text-green-400' : parseFloat(value) < 60 ? 'text-yellow-400' : 'text-red-400';
    }
  };

  // Helper to get metric value safely
  const getMetricValue = (key) => {
    return results.findings?.[key] ?? results.findings?.['synthesis']?.findings?.[key] ?? 'N/A';
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black overflow-hidden">
      {/* Background animations */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 border-b border-gray-800/30 bg-gray-900/20 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-white">Analysis Results</h1>
          <p className="text-gray-400 text-sm mt-1">Detailed credibility assessment</p>
        </div>
      </nav>

      <div className="relative z-10 container mx-auto px-4 py-12">
        <div className="max-w-7xl mx-auto">
          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
            {/* Left Column - Summary and Details */}
            <div className="lg:col-span-2 space-y-6">
              {/* Article Info & Summary Card */}
              <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-xl p-8">
                <div className="mb-6 pb-6 border-b border-gray-700">
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-semibold">
                      {results.findings?.article_category?.replace('_', ' ').toUpperCase() || 'ARTICLE'}
                    </span>
                    {results.findings?.source_credibility === 'reputable' && (
                      <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-xs font-semibold">
                        ✓ Reputable Source
                      </span>
                    )}
                    {results.findings?.source_credibility === 'tabloid' && (
                      <span className="px-3 py-1 bg-yellow-500/20 text-yellow-300 rounded-full text-xs font-semibold">
                        ⚠ Tabloid Source
                      </span>
                    )}
                  </div>
                </div>

                <h2 className="text-xl font-bold text-white mb-4">📋 Detailed Assessment</h2>
                <p className="text-gray-300 leading-relaxed text-base">{results.summary}</p>
              </div>

              {/* Cross-Source Validation */}
              {results.crossSourceVerification?.matching_sources && results.crossSourceVerification.matching_sources.length > 0 && (
                <div className="bg-cyan-500/5 border border-cyan-500/30 rounded-xl p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-2xl">🔗</span>
                    <div>
                      <h3 className="text-lg font-semibold text-cyan-300">Cross-Source Validation</h3>
                      <p className="text-cyan-200 text-sm">Verified by {results.crossSourceVerification.total_sources_reporting} independent sources</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {results.crossSourceVerification.matching_sources.slice(0, 4).map((source, idx) => (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block bg-gray-800/40 hover:bg-gray-800/60 rounded-lg p-4 transition-colors border border-gray-700/30 hover:border-cyan-500/50"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-cyan-400 mb-1">{source.source}</p>
                            <p className="text-gray-300 font-medium text-sm line-clamp-1">{source.title}</p>
                            {source.published_at && (
                              <p className="text-gray-500 text-xs mt-1">
                                {new Date(source.published_at).toLocaleDateString()}
                              </p>
                            )}
                          </div>
                          <ExternalLink className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-1" />
                        </div>
                      </a>
                    ))}
                  </div>

                  {results.crossSourceVerification.matching_sources.length > 4 && (
                    <p className="text-gray-400 text-sm mt-3 pt-3 border-t border-gray-700">
                      +{results.crossSourceVerification.matching_sources.length - 4} more sources reporting this story
                    </p>
                  )}
                </div>
              )}

              {/* Quality Badge */}
              {results.reflectionLoop?.approved && (
                <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">✓</span>
                    <div>
                      <h3 className="text-lg font-semibold text-green-300">Quality Verified</h3>
                      <p className="text-green-200 text-sm">Approved on iteration {results.reflectionLoop.iteration} of {results.reflectionLoop.total_iterations}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Trust Score & Metrics */}
            <div className="space-y-6">
              {/* Trust Score Gauge */}
              <div className="lg:sticky lg:top-24">
                <TrustScoreGauge
                  score={results.trustScore}
                  riskLevel={results.riskLevel}
                  validationScore={results.validationScore}
                  combinedScore={results.combinedTrustScore}
                />
              </div>

              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-lg p-4">
                  <p className="text-gray-400 text-xs mb-2">Sentiment</p>
                  <p className={`text-xl font-bold ${getMetricColor(getMetricValue('sentiment'), 'sentiment')}`}>
                    {getMetricValue('sentiment') || 'NEUTRAL'}
                  </p>
                </div>

                <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-lg p-4">
                  <p className="text-gray-400 text-xs mb-2">Toxicity</p>
                  <p className={`text-xl font-bold ${parseFloat(getMetricValue('toxicity_score')) > 50 ? 'text-red-400' : 'text-green-400'}`}>
                    {Math.round(parseFloat(getMetricValue('toxicity_score')) || 0)}/100
                  </p>
                </div>

                <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-lg p-4">
                  <p className="text-gray-400 text-xs mb-2">Bias Score</p>
                  <p className={`text-xl font-bold ${parseFloat(getMetricValue('bias_score')) > 50 ? 'text-red-400' : parseFloat(getMetricValue('bias_score')) > 30 ? 'text-yellow-400' : 'text-green-400'}`}>
                    {Math.round(parseFloat(getMetricValue('bias_score')) || 0)}/100
                  </p>
                </div>

                <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-lg p-4">
                  <p className="text-gray-400 text-xs mb-2">Bot Risk</p>
                  <p className={`text-xl font-bold ${parseFloat(getMetricValue('bot_probability')) > 50 ? 'text-red-400' : parseFloat(getMetricValue('bot_probability')) > 30 ? 'text-yellow-400' : 'text-green-400'}`}>
                    {Math.round(parseFloat(getMetricValue('bot_probability')) || 0)}%
                  </p>
                </div>

                <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-lg p-4">
                  <p className="text-gray-400 text-xs mb-2">Propaganda</p>
                  <p className={`text-xl font-bold ${parseFloat(getMetricValue('propaganda_score')) > 50 ? 'text-red-400' : 'text-yellow-400'}`}>
                    {Math.round(parseFloat(getMetricValue('propaganda_score')) || 0)}/100
                  </p>
                </div>

                <div className="bg-gray-900/40 backdrop-blur border border-gray-800/50 rounded-lg p-4">
                  <p className="text-gray-400 text-xs mb-2">Emotional Manipulation</p>
                  <p className={`text-xl font-bold ${parseFloat(getMetricValue('emotional_manipulation')) > 50 ? 'text-red-400' : parseFloat(getMetricValue('emotional_manipulation')) > 30 ? 'text-yellow-400' : 'text-green-400'}`}>
                    {Math.round(parseFloat(getMetricValue('emotional_manipulation')) || 0)}/100
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8 border-t border-gray-800">
            <button
              onClick={() => navigate('/projects')}
              className="flex items-center justify-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-blue-500/50 transition-all"
            >
              <Play className="w-5 h-5" />
              View All Projects
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex items-center justify-center gap-2 px-8 py-3 bg-gray-800/50 hover:bg-gray-700/50 text-white font-semibold rounded-lg transition-colors"
            >
              <Home className="w-5 h-5" />
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}