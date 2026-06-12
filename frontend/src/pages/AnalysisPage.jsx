import { useState } from 'react'
import { Link } from 'react-router-dom'
import AnalysisForm from '../components/AnalysisForm'
import ResultsDisplay from '../components/ResultsDisplay'
import { ArrowLeft } from 'lucide-react'

export default function AnalysisPage() {
  const [analysisResult, setAnalysisResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalysis = async (formData) => {
    setLoading(true)
    try {
      let endpoint = 'http://localhost:8000/analyze/article'
      let payload = formData

      if (formData.type === 'search') {
        endpoint = 'http://localhost:8000/search/news'
        payload = {
          query: formData.query,
          num_articles: formData.numArticles || 10,
          detect_misinformation: true,
          detect_bias: true
        }
      } else {
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
    <main className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2 text-gray-900 hover:text-blue-600 transition font-medium">
            <ArrowLeft size={20} />
            Back to Home
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Analyze Article</h1>
          <div className="w-32"></div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        {!analysisResult ? (
          <div className="space-y-8">
            <div className="text-center space-y-4 mb-12">
              <h2 className="text-4xl font-bold text-gray-900">
                Analyze Any Article
              </h2>
              <p className="text-lg text-gray-600">
                Submit an article or search for news to detect misinformation, bias, and credibility scores
              </p>
            </div>

            {/* Form Section */}
            <div className="bg-gray-50 rounded-lg border border-gray-200 p-8">
              <AnalysisForm onAnalysis={handleAnalysis} loading={loading} />
            </div>

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12">
              <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-900 mb-2">🧠 Content Analysis</h3>
                <p className="text-sm text-blue-700">
                  Extract key facts, claims, and narrative elements from the content
                </p>
              </div>
              <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-900 mb-2">⚖️ Bias Detection</h3>
                <p className="text-sm text-blue-700">
                  Identify political, media, and confirmation bias in the article
                </p>
              </div>
              <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-900 mb-2">✅ Trust Score</h3>
                <p className="text-sm text-blue-700">
                  Get an overall credibility score with reasoning and recommendations
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            <button
              onClick={() => setAnalysisResult(null)}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition"
            >
              <ArrowLeft size={20} />
              Analyze Another Article
            </button>

            <ResultsDisplay result={analysisResult} />
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-12 mt-12">
        <div className="max-w-7xl mx-auto px-6 text-center text-gray-600 text-sm">
          <p>&copy; 2026 NarrativeWatch AI. Powered by 11 specialized AI agents.</p>
        </div>
      </footer>
    </main>
  )
}
