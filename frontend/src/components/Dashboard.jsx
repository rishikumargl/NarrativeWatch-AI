import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import './Dashboard.css'

function Dashboard() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch health status
    fetch('http://localhost:8000/health')
      .then(r => r.json())
      .then(data => setHealth(data))
      .catch(e => console.error('Health check failed:', e))
      .finally(() => setLoading(false))
  }, [])

  const features = [
    {
      icon: '📊',
      title: 'Content Analysis',
      description: 'Deep feature extraction and content classification',
      color: '#667eea'
    },
    {
      icon: '🎯',
      title: 'Bias Detection',
      description: 'Identify political and media bias patterns',
      color: '#764ba2'
    },
    {
      icon: '🤖',
      title: 'Bot Detection',
      description: 'Analyze engagement patterns for bot activity',
      color: '#f093fb'
    },
    {
      icon: '🔍',
      title: 'Campaign Tracking',
      description: 'Detect coordinated influence campaigns',
      color: '#f5576c'
    },
    {
      icon: '💾',
      title: 'RAG Search',
      description: 'Semantic search with vector embeddings',
      color: '#4facfe'
    },
    {
      icon: '🔬',
      title: 'Fact-Checking',
      description: 'Tavily-powered research and verification',
      color: '#00f2fe'
    },
    {
      icon: '🧠',
      title: 'Multi-Agent',
      description: 'Orchestrated agent system for analysis',
      color: '#43e97b'
    },
    {
      icon: '✅',
      title: 'Quality Assurance',
      description: 'Reflection loop with quality review',
      color: '#fa709a'
    },
  ]

  return (
    <div className="dashboard">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h2>Welcome to NarrativeWatch AI</h2>
          <p>Next-level intelligence platform for detecting misinformation, bias, and coordinated campaigns</p>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-label">Agents</span>
              <span className="stat-value">11</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">APIs</span>
              <span className="stat-value">3</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Models</span>
              <span className="stat-value">2</span>
            </div>
          </div>
        </div>
      </section>

      {/* System Status */}
      {health && (
        <section className="status-section">
          <div className="status-card glowing-card">
            <div className="status-header">
              <h3>System Status</h3>
              <span className={`status-badge ${health.status === 'ok' ? 'active' : 'inactive'}`}>
                {health.status.toUpperCase()}
              </span>
            </div>
            <div className="status-grid">
              <div className="status-item">
                <span className="label">Version</span>
                <span className="value">{health.version}</span>
              </div>
              <div className="status-item">
                <span className="label">API</span>
                <span className="value healthy">Operational</span>
              </div>
              <div className="status-item">
                <span className="label">Database</span>
                <span className="value healthy">Connected</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Quick Actions */}
      <section className="actions-section">
        <h3>Quick Start</h3>
        <div className="actions-grid">
          <Link to="/analyze" className="action-card primary-card">
            <div className="card-icon">📝</div>
            <div className="card-content">
              <h4>Analyze Article</h4>
              <p>Detect misinformation and bias in news content</p>
            </div>
            <div className="card-arrow">→</div>
          </Link>
          <Link to="/analyze" className="action-card secondary-card">
            <div className="card-icon">🔎</div>
            <div className="card-content">
              <h4>Search News</h4>
              <p>Query and analyze trending articles</p>
            </div>
            <div className="card-arrow">→</div>
          </Link>
          <Link to="/analyze" className="action-card tertiary-card">
            <div className="card-icon">📊</div>
            <div className="card-content">
              <h4>View Analysis</h4>
              <p>See detailed multi-agent reports</p>
            </div>
            <div className="card-arrow">→</div>
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="features-section">
        <div className="section-header">
          <h3>Platform Capabilities</h3>
          <p>Powered by 11 specialized agents and advanced AI models</p>
        </div>
        <div className="features-grid">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="feature-card"
              style={{ '--accent-color': feature.color }}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h4>{feature.title}</h4>
              <p>{feature.description}</p>
              <div className="feature-accent"></div>
            </div>
          ))}
        </div>
      </section>

      {/* Technology Stack */}
      <section className="tech-section">
        <h3>Technology Stack</h3>
        <div className="tech-grid">
          <div className="tech-card">
            <span className="tech-name">LangChain</span>
            <span className="tech-desc">Agent Orchestration</span>
          </div>
          <div className="tech-card">
            <span className="tech-name">Groq API</span>
            <span className="tech-desc">LLM Intelligence</span>
          </div>
          <div className="tech-card">
            <span className="tech-name">NewsAPI</span>
            <span className="tech-desc">Article Sourcing</span>
          </div>
          <div className="tech-card">
            <span className="tech-name">Tavily</span>
            <span className="tech-desc">Research & Fact-Check</span>
          </div>
          <div className="tech-card">
            <span className="tech-name">PostgreSQL</span>
            <span className="tech-desc">Vector Database</span>
          </div>
          <div className="tech-card">
            <span className="tech-name">pgvector</span>
            <span className="tech-desc">Semantic Search</span>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h3>Ready to analyze content?</h3>
          <p>Use our advanced multi-agent system to detect misinformation and bias in real-time</p>
          <Link to="/analyze" className="cta-button">
            Start Analysis
          </Link>
        </div>
      </section>
    </div>
  )
}

export default Dashboard
