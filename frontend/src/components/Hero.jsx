import { Link } from 'react-router-dom'
import './Hero.css'

function Hero() {
  return (
    <section className="hero">
      <div className="hero-background">
        <div className="hero-gradient"></div>
        <div className="hero-particles">
          {[...Array(30)].map((_, i) => (
            <div
              key={i}
              className="particle"
              style={{
                '--delay': `${i * 0.1}s`,
                '--duration': `${3 + Math.random() * 2}s`,
                '--x': `${Math.random() * 100}%`,
                '--y': `${Math.random() * 100}%`
              }}
            ></div>
          ))}
        </div>
      </div>

      <div className="hero-content">
        <div className="hero-badge">AI-Powered Intelligence Platform</div>

        <h1 className="hero-title">
          Detect Misinformation
          <br />
          <span className="gradient-text">with Precision</span>
        </h1>

        <p className="hero-subtitle">
          Multi-agent AI system that analyzes news articles to detect misinformation,
          bias, and coordinated campaigns in real-time
        </p>

        <div className="hero-stats">
          <div className="hero-stat">
            <div className="stat-number">11</div>
            <div className="stat-label">Specialized Agents</div>
          </div>
          <div className="hero-stat">
            <div className="stat-number">3</div>
            <div className="stat-label">External APIs</div>
          </div>
          <div className="hero-stat">
            <div className="stat-number">2</div>
            <div className="stat-label">LLM Models</div>
          </div>
          <div className="hero-stat">
            <div className="stat-number">~8s</div>
            <div className="stat-label">Analysis Time</div>
          </div>
        </div>

        <div className="hero-cta">
          <Link to="/analyze" className="cta-primary">
            Start Analysis
            <span className="arrow">→</span>
          </Link>
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="cta-secondary">
            View API Docs
          </a>
        </div>
      </div>

      <div className="hero-visual">
        <div className="visual-card">
          <div className="visual-header">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
          <div className="visual-content">
            <div className="line short"></div>
            <div className="line"></div>
            <div className="line short"></div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero
