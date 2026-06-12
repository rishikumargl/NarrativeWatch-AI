import { useState } from 'react'
import LoadingSpinner from './LoadingSpinner'
import './AnalysisForm.css'

function AnalysisForm({ onAnalysis, loading }) {
  const [analysisType, setAnalysisType] = useState('article')
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    content: '',
    source: '',
    author: '',
    publishedAt: new Date().toISOString().split('T')[0],
    url: '',
    query: '',
    numArticles: 10
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (analysisType === 'article') {
      if (!formData.title || !formData.content) {
        alert('Please enter article title and content')
        return
      }
    } else if (analysisType === 'search') {
      if (!formData.query) {
        alert('Please enter a search query')
        return
      }
    }

    onAnalysis({
      type: analysisType,
      ...formData
    })
  }

  return (
    <form className="analysis-form" onSubmit={handleSubmit}>
      <h2>📰 Analyze News Articles</h2>

      <div className="form-group">
        <label htmlFor="analysisType">Analysis Type</label>
        <select
          id="analysisType"
          value={analysisType}
          onChange={(e) => setAnalysisType(e.target.value)}
        >
          <option value="article">Analyze Single Article</option>
          <option value="search">Search & Analyze News</option>
        </select>
      </div>

      {analysisType === 'article' ? (
        <>
          <div className="form-group">
            <label htmlFor="title">Article Title *</label>
            <input
              id="title"
              type="text"
              name="title"
              placeholder="Enter article title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <input
              id="description"
              type="text"
              name="description"
              placeholder="Brief description"
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="content">Article Content *</label>
            <textarea
              id="content"
              name="content"
              placeholder="Paste full article content here..."
              value={formData.content}
              onChange={handleChange}
              rows="8"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="source">News Source</label>
              <input
                id="source"
                type="text"
                name="source"
                placeholder="e.g., BBC News, Reuters"
                value={formData.source}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="author">Author</label>
              <input
                id="author"
                type="text"
                name="author"
                placeholder="Author name"
                value={formData.author}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="publishedAt">Published Date</label>
              <input
                id="publishedAt"
                type="date"
                name="publishedAt"
                value={formData.publishedAt}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="url">Article URL</label>
              <input
                id="url"
                type="url"
                name="url"
                placeholder="https://..."
                value={formData.url}
                onChange={handleChange}
              />
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="form-group">
            <label htmlFor="query">Search Query *</label>
            <input
              id="query"
              type="text"
              name="query"
              placeholder="e.g., climate change, election 2024, vaccines"
              value={formData.query}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="numArticles">Number of Articles</label>
            <select
              id="numArticles"
              name="numArticles"
              value={formData.numArticles}
              onChange={handleChange}
            >
              <option value="5">5 articles</option>
              <option value="10">10 articles</option>
              <option value="20">20 articles</option>
              <option value="50">50 articles</option>
            </select>
          </div>

          <div className="info-box">
            <p>🔍 System will automatically fetch and analyze news articles matching your query</p>
            <p>Analyzes: misinformation, bias, source credibility, and coordinated narratives</p>
          </div>
        </>
      )}

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? (
          <>
            <LoadingSpinner /> Analyzing...
          </>
        ) : analysisType === 'article' ? (
          'Analyze Article'
        ) : (
          'Search & Analyze'
        )}
      </button>
    </form>
  )
}

export default AnalysisForm
