import { AlertCircle, CheckCircle, AlertTriangle, TrendingDown } from 'lucide-react'
import './ResultsDisplay.css'

function ResultsDisplay({ result }) {
  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low':
        return 'risk-low'
      case 'medium':
        return 'risk-medium'
      case 'high':
        return 'risk-high'
      case 'critical':
        return 'risk-critical'
      default:
        return 'risk-medium'
    }
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'low':
        return <CheckCircle size={20} />
      case 'medium':
        return <AlertTriangle size={20} />
      case 'high':
      case 'critical':
        return <AlertCircle size={20} />
      default:
        return <AlertTriangle size={20} />
    }
  }

  const getTrustColor = (score) => {
    if (score >= 80) return '#10b981'
    if (score >= 60) return '#f59e0b'
    if (score >= 40) return '#ef4444'
    return '#dc2626'
  }

  return (
    <div className="results-container">
      <div className="results-card">
        <div className="results-header">
          <h2>Analysis Results</h2>
          <p className="results-url">{result.instagram_url}</p>
        </div>

        {/* Trust Score Section */}
        <div className={`trust-score-section ${getRiskColor(result.risk_level)}`}>
          <div className="trust-score-circle">
            <div className="score-value">{Math.round(result.trust_score)}</div>
            <div className="score-label">Trust Score</div>
          </div>
          <div className="score-info">
            <h3>Overall Risk: <span className="risk-badge">{result.risk_level.toUpperCase()}</span></h3>
            <p className="score-description">{result.summary}</p>
          </div>
        </div>

        {/* Findings Section */}
        <div className="findings-section">
          <h3 className="findings-title">Agent Findings</h3>
          <div className="findings-list">
            {result.findings && result.findings.length > 0 ? (
              result.findings.map((finding, index) => (
                <div key={index} className={`finding-card finding-${finding.severity}`}>
                  <div className="finding-header">
                    <div className="finding-icon">
                      {getSeverityIcon(finding.severity)}
                    </div>
                    <div className="finding-title">
                      <h4>{finding.agent_name}</h4>
                      <p className="finding-category">{finding.category}</p>
                    </div>
                    <div className="finding-confidence">
                      <span className="confidence-badge">{Math.round(finding.confidence * 100)}% confidence</span>
                    </div>
                  </div>
                  <p className="finding-description">{finding.description}</p>
                  {finding.evidence && finding.evidence.length > 0 && (
                    <div className="finding-evidence">
                      <strong>Evidence:</strong>
                      <ul>
                        {finding.evidence.map((ev, i) => (
                          <li key={i}>{ev}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="no-findings">No findings to display</p>
            )}
          </div>
        </div>

        {/* Recommendations Section */}
        {result.recommendations && result.recommendations.length > 0 && (
          <div className="recommendations-section">
            <h3 className="recommendations-title">Recommendations</h3>
            <ul className="recommendations-list">
              {result.recommendations.map((rec, index) => (
                <li key={index} className="recommendation-item">
                  <span className="recommendation-icon">→</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Metadata Section */}
        <div className="metadata-section">
          <h4>Analysis Details</h4>
          <div className="metadata-grid">
            {result.metadata && Object.entries(result.metadata).map(([key, value]) => (
              <div key={key} className="metadata-item">
                <span className="metadata-key">{key.replace(/_/g, ' ')}:</span>
                <span className="metadata-value">
                  {typeof value === 'number' && key.includes('time')
                    ? `${value.toFixed(2)}s`
                    : value}
                </span>
              </div>
            ))}
            <div className="metadata-item">
              <span className="metadata-key">Request ID:</span>
              <span className="metadata-value">{result.request_id}</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-key">Timestamp:</span>
              <span className="metadata-value">
                {new Date(result.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResultsDisplay
