import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { Loader, ArrowLeft, AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react'

export default function ResultsPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`http://localhost:8000/results/${id}`)
        if (!response.ok) throw new Error('Results not found')
        const data = await response.json()
        setResult(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    const interval = setInterval(fetchResults, 2000)
    fetchResults()

    return () => clearInterval(interval)
  }, [id])

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 pt-24 pb-16 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader size={48} className="animate-spin text-accent-400 mx-auto" />
          <p className="text-xl text-slate-300">Analyzing article...</p>
          <p className="text-sm text-slate-500">This may take up to 10 seconds</p>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-6">
          <button
            onClick={() => navigate('/analyze')}
            className="flex items-center gap-2 text-accent-400 hover:text-accent-300 mb-8 transition"
          >
            <ArrowLeft size={20} /> Back to Analyze
          </button>

          <div className="card-dark p-8 rounded-xl border-red-500/30 border-2">
            <div className="flex items-start gap-4">
              <AlertCircle size={24} className="text-red-400 mt-1 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-bold text-red-400 mb-2">Analysis Failed</h2>
                <p className="text-slate-300">{error}</p>
                <button
                  onClick={() => navigate('/analyze')}
                  className="btn-primary mt-6"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    )
  }

  if (!result) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <p className="text-slate-300">No results found. Still waiting for analysis...</p>
        </div>
      </main>
    )
  }

  const getTrustColor = (score) => {
    if (score >= 75) return 'text-green-400'
    if (score >= 50) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getTrustBg = (score) => {
    if (score >= 75) return 'bg-green-500/10'
    if (score >= 50) return 'bg-yellow-500/10'
    return 'bg-red-500/10'
  }

  const getRiskIcon = (level) => {
    if (level === 'low') return <CheckCircle size={20} className="text-green-400" />
    if (level === 'high' || level === 'critical') return <AlertTriangle size={20} className="text-red-400" />
    return <AlertCircle size={20} className="text-yellow-400" />
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 pt-24 pb-16">
      <div className="max-w-4xl mx-auto px-6 space-y-8">
        <button
          onClick={() => navigate('/analyze')}
          className="flex items-center gap-2 text-accent-400 hover:text-accent-300 transition"
        >
          <ArrowLeft size={20} /> New Analysis
        </button>

        {/* Header */}
        <div className="space-y-4">
          <h1 className="text-4xl font-bold">{result.article_title || 'Analysis Results'}</h1>
          {result.source && (
            <p className="text-lg text-slate-400">Source: <span className="text-accent-400">{result.source}</span></p>
          )}
        </div>

        {/* Trust Score Card */}
        <div className={`card-dark p-12 rounded-2xl text-center border-2 ${getTrustBg(result.trust_score)} border-accent-500/30`}>
          <p className="text-slate-400 mb-2">Trust Score</p>
          <div className={`text-7xl font-bold mb-4 ${getTrustColor(result.trust_score)}`}>
            {result.trust_score}%
          </div>
          <p className="text-xl text-slate-300 capitalize">
            Risk Level: <span className="text-accent-400">{result.risk_level}</span>
          </p>
        </div>

        {/* Summary */}
        <div className="card-dark p-8 rounded-xl">
          <h2 className="text-2xl font-bold text-white mb-4">Summary</h2>
          <p className="text-slate-300 leading-relaxed text-lg">{result.summary}</p>
        </div>

        {/* Risk Flags */}
        {result.risk_flags && result.risk_flags.length > 0 && (
          <div className="card-dark p-8 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-6">Risk Indicators</h2>
            <div className="space-y-4">
              {result.risk_flags.map((flag, idx) => (
                <div key={idx} className="flex items-start gap-4 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                  <div className="flex-shrink-0 mt-1">
                    {flag.confidence > 0.7 ? (
                      <AlertTriangle size={20} className="text-red-400" />
                    ) : (
                      <AlertCircle size={20} className="text-yellow-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-white capitalize mb-1">{flag.flag}</div>
                    <p className="text-slate-400 text-sm mb-2">{flag.description}</p>
                    <div className="text-xs text-slate-500">
                      Confidence: {Math.round(flag.confidence * 100)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {result.recommendations && result.recommendations.length > 0 && (
          <div className="card-dark p-8 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-6">Recommendations</h2>
            <ul className="space-y-3">
              {result.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-3 text-slate-300">
                  <span className="text-accent-400 mt-1 flex-shrink-0">→</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Additional Details */}
        {result.detected_patterns && Object.keys(result.detected_patterns).length > 0 && (
          <div className="card-dark p-8 rounded-xl">
            <h2 className="text-2xl font-bold text-white mb-6">Detected Patterns</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(result.detected_patterns).map(([key, value], idx) => (
                <div key={idx} className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                  <div className="font-semibold text-white capitalize mb-1">{key}</div>
                  <div className="text-slate-400 text-sm">{String(value)}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <div className="text-center pt-8">
          <button
            onClick={() => navigate('/analyze')}
            className="btn-primary"
          >
            Analyze Another Article
          </button>
        </div>
      </div>
    </main>
  )
}
