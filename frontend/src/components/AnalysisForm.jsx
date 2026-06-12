import { useState } from 'react'
import { analyzeInstagram } from '../services/api'
import './AnalysisForm.css'

function AnalysisForm({ onAnalysisStart, onAnalysisComplete, onAnalysisError, isLoading }) {
  const [url, setUrl] = useState('')
  const [analysisType, setAnalysisType] = useState('page')
  const [options, setOptions] = useState({
    includeHistorical: true,
    includeBotAnalysis: true,
    includeBiasDetection: true,
    includeCampaignDetection: true,
  })

  const handleUrlChange = (e) => {
    setUrl(e.target.value)
  }

  const handleAnalysisTypeChange = (e) => {
    setAnalysisType(e.target.value)
  }

  const handleOptionChange = (option) => {
    setOptions(prev => ({
      ...prev,
      [option]: !prev[option]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!url.trim()) {
      onAnalysisError('Please enter an Instagram URL')
      return
    }

    if (!url.includes('instagram.com')) {
      onAnalysisError('Invalid Instagram URL. Please enter a valid Instagram page or post URL.')
      return
    }

    onAnalysisStart()

    try {
      const result = await analyzeInstagram(url, {
        analysisType,
        ...options,
      })
      onAnalysisComplete(result)
    } catch (err) {
      onAnalysisError(err.message || 'Failed to analyze Instagram page. Please try again.')
    }
  }

  return (
    <div className="form-container">
      <div className="form-card">
        <h2>Analyze Instagram Page</h2>
        <p className="form-description">
          Enter an Instagram page URL to analyze for misinformation, bias, bot activity, and coordinated campaigns.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="url">Instagram URL</label>
            <input
              id="url"
              type="text"
              placeholder="https://www.instagram.com/bbcnews/"
              value={url}
              onChange={handleUrlChange}
              disabled={isLoading}
              className="form-input"
            />
            <small className="form-help">Enter the full Instagram URL (e.g., https://instagram.com/username)</small>
          </div>

          <div className="form-group">
            <label htmlFor="analysisType">Analysis Type</label>
            <select
              id="analysisType"
              value={analysisType}
              onChange={handleAnalysisTypeChange}
              disabled={isLoading}
              className="form-select"
            >
              <option value="page">Page</option>
              <option value="post">Post</option>
              <option value="account">Account</option>
            </select>
          </div>

          <div className="form-group">
            <label>Analysis Options</label>
            <div className="options-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={options.includeHistorical}
                  onChange={() => handleOptionChange('includeHistorical')}
                  disabled={isLoading}
                />
                <span>Include Historical Data</span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={options.includeBotAnalysis}
                  onChange={() => handleOptionChange('includeBotAnalysis')}
                  disabled={isLoading}
                />
                <span>Bot Activity Analysis</span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={options.includeBiasDetection}
                  onChange={() => handleOptionChange('includeBiasDetection')}
                  disabled={isLoading}
                />
                <span>Bias Detection</span>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={options.includeCampaignDetection}
                  onChange={() => handleOptionChange('includeCampaignDetection')}
                  disabled={isLoading}
                />
                <span>Campaign Detection</span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="submit-button"
          >
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>

        <div className="example-section">
          <h3>Example URLs to Try</h3>
          <ul className="example-list">
            <li><a href="#" onClick={(e) => { e.preventDefault(); setUrl('https://www.instagram.com/bbcnews/'); }}>https://www.instagram.com/bbcnews/</a></li>
            <li><a href="#" onClick={(e) => { e.preventDefault(); setUrl('https://www.instagram.com/cnn/'); }}>https://www.instagram.com/cnn/</a></li>
            <li><a href="#" onClick={(e) => { e.preventDefault(); setUrl('https://www.instagram.com/nytimes/'); }}>https://www.instagram.com/nytimes/</a></li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default AnalysisForm
