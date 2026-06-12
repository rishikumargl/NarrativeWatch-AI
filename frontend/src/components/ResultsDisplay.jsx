import './ResultsDisplay.css'

function ResultsDisplay({ result }) {
  if (!result) return null

  if (result.error) {
    return (
      <div className="results-container error">
        <h3>Error</h3>
        <p>{result.error}</p>
      </div>
    )
  }

  const getTrustScoreClass = (score) => {
    if (score >= 70) return 'trust-high'
    if (score >= 40) return 'trust-medium'
    return 'trust-low'
  }

  return (
    <div className="results-container">
      <h2>Analysis Results</h2>

      {/* Trust Score */}
      {result.trust_score && (
        <div className={`trust-score ${getTrustScoreClass(result.trust_score)}`}>
          <div className="score-value">{result.trust_score}%</div>
          <div className="score-label">Trust Score</div>
        </div>
      )}

      {/* Risk Level */}
      {result.risk_level && (
        <div className="result-section">
          <h3>Risk Assessment</h3>
          <p className={`risk-level risk-${result.risk_level.toLowerCase()}`}>
            {result.risk_level}
          </p>
        </div>
      )}

      {/* Key Findings */}
      {result.key_findings && (
        <div className="result-section">
          <h3>Key Findings</h3>
          <ul className="findings-list">
            {result.key_findings.map((finding, idx) => (
              <li key={idx}>{finding}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Flags */}
      {result.flags && result.flags.length > 0 && (
        <div className="result-section">
          <h3>Detected Flags</h3>
          <div className="flags-container">
            {result.flags.map((flag, idx) => (
              <span key={idx} className="flag-badge">{flag}</span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {result.recommendations && (
        <div className="result-section">
          <h3>Recommendations</h3>
          <ol className="recommendations-list">
            {result.recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ol>
        </div>
      )}

      {/* Raw Data */}
      <details className="result-section raw-data">
        <summary>Raw Analysis Data</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </div>
  )
}

export default ResultsDisplay
