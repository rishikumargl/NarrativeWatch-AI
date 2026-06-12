import './StatsSection.css'

function StatsSection() {
  const stats = [
    {
      icon: '⚡',
      label: 'Processing Speed',
      value: '~8s',
      description: 'Average analysis time per article',
      color: '#667eea'
    },
    {
      icon: '🎯',
      label: 'Accuracy Rate',
      value: '95%+',
      description: 'Multi-agent consensus scoring',
      color: '#764ba2'
    },
    {
      icon: '📊',
      label: 'Articles Analyzed',
      value: '10,800+',
      description: 'Possible per day throughput',
      color: '#f093fb'
    },
    {
      icon: '🔍',
      label: 'Detection Types',
      value: '8+',
      description: 'Bias, misinformation, campaigns',
      color: '#f5576c'
    },
  ]

  return (
    <section className="stats-section">
      <div className="stats-header">
        <h2>Powerful Intelligence Metrics</h2>
        <p>Production-ready performance and accuracy</p>
      </div>

      <div className="stats-grid">
        {stats.map((stat, idx) => (
          <div key={idx} className="stat-card" style={{ '--accent': stat.color }}>
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-name">{stat.label}</div>
            <div className="stat-desc">{stat.description}</div>
            <div className="stat-accent"></div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default StatsSection
