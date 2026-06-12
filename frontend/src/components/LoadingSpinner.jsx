import './LoadingSpinner.css'

function LoadingSpinner() {
  const agents = [
    'Content Analysis',
    'RAG Retrieval',
    'External Research',
    'Bias Detection',
    'Bot Analysis',
    'Campaign Detection',
    'Synthesis',
    'Review & Validation'
  ]

  return (
    <div className="loading-overlay">
      <div className="spinner-container">
        <div className="spinner"></div>
        <h2>🔍 Analyzing Instagram Page...</h2>
        <p>Running multi-agent intelligence analysis</p>
        <div className="agent-status">
          {agents.map((agent, index) => (
            <div key={index} className="agent-item" style={{ '--delay': `${index * 0.15}s` }}>
              <span className="agent-dot"></span>
              <span>{agent}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
