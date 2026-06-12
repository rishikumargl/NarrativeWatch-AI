import { useState } from 'react'
import AnalysisForm from './components/AnalysisForm'
import ResultsDisplay from './components/ResultsDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import './styles/App.css'

function App() {
  const [analysisResult, setAnalysisResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalysisStart = () => {
    setIsLoading(true)
    setError(null)
  }

  const handleAnalysisComplete = (result) => {
    setAnalysisResult(result)
    setIsLoading(false)
    setError(null)
  }

  const handleAnalysisError = (errorMsg) => {
    setError(errorMsg)
    setIsLoading(false)
    setAnalysisResult(null)
  }

  const handleReset = () => {
    setAnalysisResult(null)
    setError(null)
    setIsLoading(false)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="title">NarrativeWatch AI</h1>
          <p className="subtitle">Detect Misinformation, Bias, and Influence Campaigns</p>
        </div>
      </header>

      <main className="main-container">
        <div className="content">
          {isLoading && <LoadingSpinner />}

          {error && (
            <div className="error-banner">
              <p className="error-text">{error}</p>
              <button className="error-dismiss" onClick={() => setError(null)}>✕</button>
            </div>
          )}

          {!analysisResult ? (
            <AnalysisForm
              onAnalysisStart={handleAnalysisStart}
              onAnalysisComplete={handleAnalysisComplete}
              onAnalysisError={handleAnalysisError}
              isLoading={isLoading}
            />
          ) : (
            <>
              <ResultsDisplay result={analysisResult} />
              <button className="new-analysis-btn" onClick={handleReset}>
                Analyze Another Page
              </button>
            </>
          )}
        </div>
      </main>

      <footer className="footer">
        <p>© 2026 NarrativeWatch AI. Built with multi-agent intelligence.</p>
      </footer>
    </div>
  )
}

export default App
