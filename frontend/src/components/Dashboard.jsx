import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    // Fetch health status
    fetch('/api/health')
      .then(r => r.json())
      .then(data => setHealth(data))
      .catch(e => console.error('Health check failed:', e))

    // Fetch statistics
    fetch('/api/stats')
      .then(r => r.json())
      .then(data => setStats(data))
      .catch(e => console.error('Stats fetch failed:', e))
  }, [])

  return (
    <div className="dashboard">
      <section className="dashboard-intro">
        <h2>Welcome to NarrativeWatch AI</h2>
        <p>Multi-Agent Social Media Intelligence Platform for detecting misinformation, bias, and coordinated campaigns</p>
      </section>

      {health && (
        <section className="dashboard-section">
          <h3>System Status</h3>
          <div className="status-card">
            <p><strong>Status:</strong> {health.status}</p>
            <p><strong>Version:</strong> {health.version}</p>
          </div>
        </section>
      )}

      {stats && (
        <section className="dashboard-section">
          <h3>Platform Statistics</h3>
          <div className="stats-grid">
            {Object.entries(stats).map(([key, value]) => (
              <div key={key} className="stat-card">
                <h4>{key}</h4>
                <p className="stat-value">{value}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="dashboard-section">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <Link to="/analyze" className="action-btn">
            Analyze Post
          </Link>
          <Link to="/analyze" className="action-btn">
            Analyze Page
          </Link>
        </div>
      </section>

      <section className="dashboard-section features">
        <h3>Platform Capabilities</h3>
        <ul className="features-list">
          <li>Content Analysis & Classification</li>
          <li>Bias & Misinformation Detection</li>
          <li>Bot Activity Analysis</li>
          <li>Campaign Detection & Correlation</li>
          <li>Retrieval-Augmented Generation (RAG)</li>
          <li>Web Research & Fact-Checking</li>
          <li>Multi-Agent Orchestration</li>
          <li>Quality Assurance with Reflection Loop</li>
        </ul>
      </section>
    </div>
  )
}

export default Dashboard
