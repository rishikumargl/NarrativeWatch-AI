import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import AnalysisForm from './components/AnalysisForm'
import ResultsDisplay from './components/ResultsDisplay'
import Dashboard from './components/Dashboard'
import './styles/App.css'

function App() {
  const [analysisResult, setAnalysisResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalysis = async (formData) => {
    setLoading(true)
    try {
      const response = await fetch('/api/analyze/post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      console.error('Analysis failed:', error)
      setAnalysisResult({ error: 'Analysis failed. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <h1>NarrativeWatch AI</h1>
          <p>Multi-Agent Social Media Intelligence Platform</p>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={
              <div className="analyze-container">
                <AnalysisForm onAnalysis={handleAnalysis} loading={loading} />
                {analysisResult && <ResultsDisplay result={analysisResult} />}
              </div>
            } />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>&copy; 2026 NarrativeWatch AI. Multi-Agent Social Media Intelligence Platform.</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
