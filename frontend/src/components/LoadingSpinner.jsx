import './LoadingSpinner.css'

function LoadingSpinner() {
  return (
    <div className="loading-overlay">
      <div className="spinner-container">
        <div className="spinner"></div>
        <h2>Analyzing Instagram Page...</h2>
        <p>Running multi-agent intelligence analysis</p>
        <div className="agent-status">
          <div className="agent-item">
            <span className="agent-dot"></span>
            <span>Content Analysis</span>
          </div>
          <div className="agent-item">
            <span className="agent-dot"></span>
            <span>RAG Retrieval</span>
          </div>
          <div className="agent-item">
            <span className="agent-dot"></span>
            <span>External Research</span>
          </div>
          <div className="agent-item">
            <span className="agent-dot"></span>
            <span>Bias Detection</span>
          </div>
          <div className="agent-item">
            <span className="agent-dot"></span>
            <span>Bot Analysis</span>
          </div>
          <div className="agent-item">
            <span className="agent-dot"></span>
            <span>Campaign Detection</span>
          </div>
          <div className="agent-item">
            <span className="agent-dot"></span>
            <span>Synthesis</span>
          </div>
          <div className="agent-item">
            <span className="agent-dot"></span>
            <span>Review & Validation</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
