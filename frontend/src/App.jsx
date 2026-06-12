import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import AnalysisForm from './components/AnalysisForm'
import ResultsDisplay from './components/ResultsDisplay'
import Dashboard from './components/Dashboard'
import Hero from './components/Hero'
import StatsSection from './components/StatsSection'
import Home from './pages/Home'
import './styles/App.css'
import './styles/index.css'

function App() {
  const [analysisResult, setAnalysisResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalysis = async (formData) => {
    setLoading(true)
    try {
      let endpoint = 'http://localhost:8000/analyze/article'
      let payload = formData

      // Check if it's a search request
      if (formData.type === 'search') {
        endpoint = 'http://localhost:8000/search/news'
        payload = {
          query: formData.query,
          num_articles: formData.numArticles || 10,
          detect_misinformation: true,
          detect_bias: true
        }
      } else {
        // Single article analysis
        payload = {
          title: formData.title || 'Untitled Article',
          description: formData.description || '',
          content: formData.content || '',
          source: formData.source || 'Unknown',
          author: formData.author || '',
          published_at: formData.publishedAt || new Date().toISOString(),
          url: formData.url || ''
        }
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      console.error('Analysis failed:', error)
      setAnalysisResult({ error: `Analysis failed: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <h1>🔍 NarrativeWatch AI</h1>
          <p>News Misinformation & Bias Detection Platform</p>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analyze" element={
              <div className="analyze-container">
                <AnalysisForm onAnalysis={handleAnalysis} loading={loading} />
                {analysisResult && <ResultsDisplay result={analysisResult} />}
              </div>
            } />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>&copy; 2026 NarrativeWatch AI. News Intelligence & Misinformation Detection.</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
